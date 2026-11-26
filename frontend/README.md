# Portefólio de Frederico Zito

Sítio estático em HTML, CSS e JavaScript. Estrutura:

```
index.html
assets/estilos/estilo.css
assets/javascript/script.js
assets/imagens/  (foto-perfil.jpeg, favicon.png, og-imagem.jpg)
assets/icones/   (linkedin.png, github.png)
assets/documentos/cv-frederico-zito.pdf
backend/         (API FastAPI de contacto: ver backend/README.md)
```

## O que estava errado e o que foi feito

### SEO
| Antes | Depois |
|---|---|
| `lang="pt-Br"` | `lang="pt-PT"` |
| Título genérico ("Portfolio Web - Profissional") | Título com nome e função |
| `meta keywords` (ignorada pelo Google) | Removida |
| `h1` escondido com `visibility: hidden` e texto vago | `h1` visível, com nome e função |
| Sem canonical, Open Graph, favicon nem dados estruturados | Adicionados (incluindo JSON-LD do tipo `Person`) |
| Imagens sem dimensões nem carregamento diferido | `width`, `height` e `loading="lazy"` |
| Cabeçalho fixo tapava os títulos nas âncoras | `scroll-padding-top` |

### Conteúdo
- Novas secções: **Competências**, currículo para descarregar e contactos diretos (email, telefone, WhatsApp).
- Chamadas à ação no hero ("Fale comigo", "Ver projetos").
- Projetos descritos em termos gerais, sem dados internos da Beyond Limits.
- Ligações sociais a `#` foram removidas ou marcadas com `TODO`.
- Bloco "Recomendações" reescrito de forma neutra, com `youtube-nocookie.com`, `loading="lazy"` e sem `frameborder`.

### Português
Corrigidos, entre outros: *estágiario, nemhuma, próprinas, bbastante, obsecado, desenvoler, Inicio, mais sim, Robby, Full-Stack´s, cyber´s, "Sessão" (por Secção), "Tel" (por Telemóvel)*. Removido o tratamento por "você", resolvida a contradição "estudante... formado" e adotada uma só grafia (AO90).

### Nomes de classes e IDs
- Os `id` deixaram de ser usados para estilizar; ficam só para âncoras e ligações `for`/`aria-controls`.
- Classes renomeadas segundo **BEM**, em português (`cartao__titulo`, `menu--aberto`, `campo__erro`). Corrigido o erro `redes-socias` e removidos nomes de frameworks (`row`, `card`).
- Comentários passaram a explicar o porquê das decisões.

### CSS e responsividade
- Reescrito **mobile-first**; as grelhas usam `auto-fit`, por isso não há cartões espremidos entre 730px e 1000px.
- Corrigido o contraste do laranja sobre branco (de cerca de 2:1 para ≥ 4,5:1, usando `--laranja-texto`).
- Removida a regra morta `div#faq summary p.p-summary` e a borda de depuração do hero.
- Campos com 48px de altura e `font-size` de 16px; foco visível em todos os elementos interativos.
- `rem` em vez de `pt`; transições específicas em vez de `all`; respeito por `prefers-reduced-motion`.
- Adicionada ligação "Saltar para o conteúdo".

### JavaScript
- `aria-label` do botão fixo (o estado é dado por `aria-expanded`).
- Lógica de abrir e fechar unificada na função `definirMenu`.
- ESC devolve o foco ao botão; clicar fora fecha o menu; o menu repõe-se ao redimensionar.
- Script carregado com `defer` no `<head>`.

### Formulário
- Estava sem destino (`action=""`) e sem validação. Passou a enviar por `fetch` (JSON) para a API FastAPI em `backend/`, que valida outra vez e envia o email.
- Validação em JS e HTML: nome, email, telemóvel angolano (9 dígitos, começa por 9), serviço obrigatório e mensagem com tamanho mínimo e máximo.
- Corrigido o `select` (`value=""` numa opção e `<abbr>` dentro de `<option>`, que é inválido).
- Nomes de campos claros, `autocomplete`, honeypot anti-spam, botão bloqueado após o envio.
- Aviso de privacidade junto ao botão.

### Backend (`backend/`)
- API FastAPI com `POST /contacto` e `GET /saude`.
- Validação no servidor com Pydantic (tamanhos, email, telemóvel e serviço de uma lista fechada), remoção de caracteres de controlo (previne injeção de cabeçalhos de email) e honeypot.
- Limite de pedidos (5/hora por IP e 30/hora no total) e CORS restrito ao domínio do site.
- Email enviado pela API HTTP da Brevo em texto simples, porque o Render gratuito bloqueia o SMTP.
- Segredos em variáveis de ambiente (`.env` fora do Git) e documentação automática da API desligada.

### Segurança
- **CSP** na `meta`, `referrer` controlado e mensagens inseridas com `textContent` (prevenção de XSS).
- `rel="noopener noreferrer"` nas ligações externas (havia um espaço a mais no atributo).

## O que ainda tem de fazer (não consegui fazer por si)

1. Configurar e alojar o backend seguindo `backend/README.md` e substituir `https://SEU-BACKEND.onrender.com` no `index.html` (formulário e CSP).
2. Trocar `www.exemplo.com` pelo domínio real (canonical, Open Graph e JSON-LD).
3. Colocar os URLs reais do LinkedIn e do GitHub, e criar `favicon.png`, `og-imagem.jpg` (1200×630) e o PDF do currículo.
4. Indicar as tecnologias do projeto de deteção de fraudes.
5. Converter as imagens para WebP.
6. Configurar no servidor: **HTTPS** e os cabeçalhos `X-Content-Type-Options`, `Permissions-Policy` e `frame-ancestors` (a `meta` do CSP não cobre este último). Criar `robots.txt` e `sitemap.xml` e registar o sítio no Google Search Console.
7. Ativar autenticação de dois fatores no GitHub e no alojamento.

> Nota: um sítio estático não apanha vírus nem ransomware. Esses riscos estão no seu computador, no alojamento e nas suas contas, por isso o ponto 7 é tão importante como o código.
# Backend de contacto (FastAPI)

O GitHub Pages só serve ficheiros estáticos, por isso o Python não corre lá. O site fica no GitHub Pages e esta API fica noutro serviço gratuito (por exemplo, o Render). Como têm domínios diferentes, a API tem de autorizar o domínio do site (CORS).

```
Navegador (github.io) --JSON--> API FastAPI (onrender.com) --HTTPS--> Brevo --> o seu email
```

## Porquê Brevo por HTTPS e não SMTP

Os serviços gratuitos do Render bloqueiam as portas SMTP (25, 465 e 587). Uma API de email por HTTPS usa a porta 443, que nunca é bloqueada. A Brevo tem um plano gratuito com limite diário de envios.

## 1. Conta na Brevo

1. Crie conta em brevo.com.
2. Em **Remetentes** (Senders), adicione e **verifique** o email que será o remetente (pode ser o seu Gmail).
3. Em **SMTP e API > Chaves de API**, crie uma chave. Guarde-a: só a vê uma vez.

## 2. Testar no seu computador

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows (em Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # preencha o .env
uvicorn main:app --reload --port 8000
```

Abra `http://127.0.0.1:8000/saude`: deve ver `{"estado":"ok"}`. Para testar o envio, sirva o site (por exemplo com a extensão Live Server do VS Code, porta 5500, já incluída em `ORIGENS_PERMITIDAS`) e coloque `data-api-url="http://127.0.0.1:8000/contacto"` no formulário. Também precisa de acrescentar `http://127.0.0.1:8000` ao `connect-src` do CSP no `index.html`, só durante o teste.

## 3. Publicar no Render

1. Envie o projeto para o GitHub (confirme que o `.env` **não** vai: está no `.gitignore`).
2. No Render: **New > Web Service**, escolha o repositório e use:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'`
3. Em **Environment**, crie as variáveis do `.env.example` com os valores reais. `ORIGENS_PERMITIDAS` deve ser `https://O-SEU-UTILIZADOR.github.io` (sem caminho e sem barra final).
4. Depois do primeiro *deploy*, copie o endereço do serviço.

## 4. Ligar o site à API

No `index.html`, substitua `https://SEU-BACKEND.onrender.com` em **dois sítios**: no `data-api-url` do formulário e no `connect-src` do CSP. Se só mudar um, o navegador bloqueia o pedido.

## 5. Testar em produção

```bash
curl https://SEU-BACKEND.onrender.com/saude
```

Depois envie uma mensagem pelo site e confirme que chega ao seu email. Clicar em "Responder" deve abrir uma resposta dirigida ao visitante.

## Limitações a conhecer

- **Arranque lento:** no plano gratuito do Render, o serviço adormece após cerca de 15 minutos sem pedidos, e o primeiro pedido pode demorar até um minuto. O formulário já espera até 60 s e avisa o visitante.
- **Limites de pedidos:** 5 por hora por IP e 30 por hora no total. Ajuste em `main.py` (`@limiter.limit`).
- **Confirmação ao visitante:** vem desligada (`ENVIAR_CONFIRMACAO=false`). Se a ligar, qualquer pessoa pode fazer a sua conta enviar emails para terceiros, o que prejudica a reputação do remetente.
- **Segredos:** se a chave da Brevo alguma vez for exposta (por exemplo, enviada para o GitHub), apague-a na Brevo e crie outra.
- **Versões:** o `requirements.txt` usa versões mínimas. Quando tudo funcionar, execute `pip freeze` para fixar as versões que testou.