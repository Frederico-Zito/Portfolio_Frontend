"""API de contacto do portefólio de Frederico Zito.

Fluxo: o formulário (navegador) envia JSON para POST /contacto -> esta API
valida tudo outra vez (nunca confiar no navegador) -> envia o email pela API
HTTP da Brevo. Usa-se HTTPS (porta 443) e não SMTP, porque os planos gratuitos
de vários alojamentos (como o Render) bloqueiam as portas SMTP.

Os segredos vêm de variáveis de ambiente, nunca do código.
"""
import logging
import os
import unicodedata

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()  # lê o ficheiro .env em desenvolvimento local
log = logging.getLogger("contacto")
logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------------
# Configuração (falha logo ao arrancar se algo essencial faltar)
# ----------------------------------------------------------
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE", "")   # tem de estar verificado na Brevo
EMAIL_DESTINO = os.environ.get("EMAIL_DESTINO", "")       # onde recebe as mensagens
ORIGENS = [o.strip() for o in os.environ.get("ORIGENS_PERMITIDAS", "").split(",") if o.strip()]
# Confirmação ao visitante: desligada por defeito. Quem pode escrever qualquer
# email no formulário pode usar o seu domínio para enviar spam a terceiros.
ENVIAR_CONFIRMACAO = os.environ.get("ENVIAR_CONFIRMACAO", "false").lower() == "true"

for nome_var, valor in {"BREVO_API_KEY": BREVO_API_KEY, "EMAIL_REMETENTE": EMAIL_REMETENTE,
                        "EMAIL_DESTINO": EMAIL_DESTINO, "ORIGENS_PERMITIDAS": ORIGENS}.items():
    if not valor:
        raise RuntimeError(f"Variável de ambiente em falta: {nome_var}")

# Lista fechada (whitelist): o serviço escolhido tem de ser um destes.
# Assim nunca entra texto livre no assunto do email.
SERVICOS = {
    "Instalação e configuração de sistemas operativos",
    "Criação e configuração de máquinas virtuais",
    "Panfletos, cartazes e faixas",
    "Desenvolvimento de loja online",
    "Desenvolvimento de sistema de gestão",
    "Formação em lógica de programação",
    "Reparação de computadores",
    "Formação em computação em nuvem",
}

# ----------------------------------------------------------
# Aplicação, CORS e limite de pedidos
# ----------------------------------------------------------
# Documentação automática desligada: não há motivo para a expor em produção.
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# CORS: só os domínios listados podem chamar a API a partir de um navegador.
# Atenção: a origem NÃO leva caminho (https://utilizador.github.io, sem /portfolio).
# O CORS não impede curl nem robôs; quem os trava é a validação e o limite.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ----------------------------------------------------------
# Validação dos dados recebidos
# ----------------------------------------------------------
def limpar(texto: str, permitir_quebras: bool = False) -> str:
    """Remove caracteres de controlo (incluindo quebras de linha, que permitiriam
    injeção de cabeçalhos de email) e apara espaços."""
    permitidos = {"\n"} if permitir_quebras else set()
    return "".join(c for c in texto
                   if c in permitidos or not unicodedata.category(c).startswith("C")).strip()


class Contacto(BaseModel):
    nome: str = Field(min_length=2, max_length=60)
    email: EmailStr
    telemovel: str = Field(default="", pattern=r"^(9\d{8})?$")  # opcional: 9 dígitos, começa por 9
    servico: str
    mensagem: str = Field(min_length=10, max_length=1000)
    website: str = Field(default="", max_length=200)             # honeypot: humanos deixam vazio

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v: str) -> str:
        v = limpar(v)
        if len(v) < 2:
            raise ValueError("Nome demasiado curto.")
        return v

    @field_validator("mensagem")
    @classmethod
    def validar_mensagem(cls, v: str) -> str:
        v = limpar(v, permitir_quebras=True)
        if len(v) < 10:
            raise ValueError("Mensagem demasiado curta.")
        return v

    @field_validator("servico")
    @classmethod
    def validar_servico(cls, v: str) -> str:
        if v not in SERVICOS:
            raise ValueError("Serviço inválido.")
        return v


# ----------------------------------------------------------
# Envio de email (API HTTP da Brevo)
# ----------------------------------------------------------
async def enviar_email(payload: dict) -> None:
    async with httpx.AsyncClient(timeout=15) as cliente:
        resposta = await cliente.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": BREVO_API_KEY, "accept": "application/json"},
            json=payload,
        )
        resposta.raise_for_status()


# ----------------------------------------------------------
# Rotas
# ----------------------------------------------------------
@app.get("/saude")
async def saude():
    """Verificação de estado (útil para testar e para acordar o servidor gratuito)."""
    return {"estado": "ok"}


@app.post("/contacto")
# Dois limites: por IP e um global. O global protege a quota de emails
# mesmo que alguém falsifique o IP.
@limiter.limit("5/hour")
@limiter.limit("30/hour", key_func=lambda request: "global")
async def contacto(request: Request, dados: Contacto):
    # Honeypot preenchido = robô. Responde "ok" sem enviar nada.
    if dados.website:
        return {"ok": True}

    texto = (
        f"Nome: {dados.nome}\n"
        f"Email: {dados.email}\n"
        f"Telemóvel: {dados.telemovel or '(não indicado)'}\n"
        f"Serviço: {dados.servico}\n\n"
        f"Mensagem:\n{dados.mensagem}\n"
    )
    notificacao = {
        "sender": {"name": "Portefólio", "email": EMAIL_REMETENTE},
        "to": [{"email": EMAIL_DESTINO}],
        "replyTo": {"email": dados.email, "name": dados.nome},  # "Responder" vai para o visitante
        "subject": f"Novo contacto no portefólio: {dados.servico}",
        "textContent": texto,   # só texto simples: sem HTML, sem risco de injeção
    }

    try:
        await enviar_email(notificacao)
    except httpx.HTTPError as erro:
        # Regista o tipo de erro, nunca o conteúdo da mensagem (dados pessoais).
        log.error("Falha ao enviar email: %s", type(erro).__name__)
        return JSONResponse({"ok": False, "detail": "Não foi possível enviar."}, status_code=502)

    if ENVIAR_CONFIRMACAO:
        confirmacao = {
            "sender": {"name": "Frederico Zito", "email": EMAIL_REMETENTE},
            "to": [{"email": dados.email, "name": dados.nome}],
            "subject": "Recebi a sua mensagem",
            "textContent": f"Olá, {dados.nome}.\n\nRecebi a sua mensagem e respondo em breve.\n\nFrederico Zito",
        }
        try:
            await enviar_email(confirmacao)
        except httpx.HTTPError as erro:
            # A mensagem principal já foi entregue: não falha o pedido por isto.
            log.warning("Falha na confirmação: %s", type(erro).__name__)

    return {"ok": True}