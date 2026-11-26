"use strict";

/* ==========================================================
   1. MENU HAMBÚRGUER
   Uma única função (definirMenu) controla o estado, para o
   clique, a tecla ESC e o redimensionamento partilharem a
   mesma lógica. O aria-label é fixo: quem comunica o estado
   ao leitor de ecrã é o aria-expanded.
   ========================================================== */
const botaoMenu = document.querySelector(".menu__botao");
const menu = document.querySelector("#menu");

function definirMenu(aberto) {
    menu.classList.toggle("menu--aberto", aberto);
    botaoMenu.setAttribute("aria-expanded", String(aberto));
}

if (botaoMenu && menu) {
    botaoMenu.addEventListener("click", () => {
        definirMenu(botaoMenu.getAttribute("aria-expanded") !== "true");
    });

    // Fecha ao escolher uma ligação
    menu.querySelectorAll("a").forEach((ligacao) => {
        ligacao.addEventListener("click", () => definirMenu(false));
    });

    // ESC fecha o menu e devolve o foco ao botão (essencial para teclado)
    document.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape" && botaoMenu.getAttribute("aria-expanded") === "true") {
            definirMenu(false);
            botaoMenu.focus();
        }
    });

    // Clicar fora do menu fecha-o
    document.addEventListener("click", (evento) => {
        const dentro = menu.contains(evento.target) || botaoMenu.contains(evento.target);
        if (!dentro) definirMenu(false);
    });

    // Ao passar para o ecrã grande, repõe o estado (o CSS já mostra o menu)
    window.matchMedia("(min-width: 900px)").addEventListener("change", (e) => {
        if (e.matches) definirMenu(false);
    });
}

/* ==========================================================
   2. FORMULÁRIO DE CONTACTO
   A validação aqui melhora a experiência, mas NÃO protege:
   a API (backend/main.py) valida tudo outra vez. Todo o texto de mensagens é inserido
   com textContent, nunca com innerHTML (previne XSS).
   ========================================================== */
const formulario = document.querySelector("#formulario");
const estado = document.querySelector("#formulario-estado");

// Regras por campo: devolvem a mensagem de erro, ou "" se estiver válido
const regras = {
    nome: (v) => (v.trim().length < 2 ? "Indique o seu nome (mínimo 2 letras)." : ""),
    email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? "" : "Indique um email válido."),
    // Telemóvel angolano: 9 dígitos a começar por 9. Campo opcional.
    telemovel: (v) => (v === "" || /^9\d{8}$/.test(v) ? "" : "Use 9 dígitos, a começar por 9."),
    servico: (v) => (v === "" ? "Escolha um serviço." : ""),
    mensagem: (v) => (v.trim().length < 10 ? "Escreva pelo menos 10 caracteres." : "")
};

function validarCampo(campo) {
    const regra = regras[campo.name];
    if (!regra) return true;
    const mensagem = regra(campo.value);
    const bloco = campo.closest(".campo");
    bloco.classList.toggle("campo--invalido", mensagem !== "");
    bloco.querySelector(".campo__erro").textContent = mensagem;
    campo.setAttribute("aria-invalid", String(mensagem !== ""));
    return mensagem === "";
}

function mostrarEstado(texto, tipo) {
    estado.textContent = texto;
    estado.className = "formulario__estado formulario__estado--" + tipo;
}

if (formulario) {
    // Revalida cada campo quando o utilizador sai dele
    formulario.querySelectorAll("input, select, textarea").forEach((campo) => {
        campo.addEventListener("blur", () => validarCampo(campo));
    });

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        // Valida tudo e leva o foco ao primeiro erro
        const campos = Array.from(formulario.elements).filter((c) => regras[c.name]);
        const invalidos = campos.filter((c) => !validarCampo(c));
        if (invalidos.length > 0) {
            invalidos[0].focus();
            mostrarEstado("Corrija os campos assinalados.", "erro");
            return;
        }

        // Honeypot preenchido = robô. Finge sucesso e não envia nada.
        if (formulario.elements.website.value !== "") {
            mostrarEstado("Mensagem enviada. Obrigado!", "ok");
            formulario.reset();
            return;
        }

        const botao = formulario.querySelector("button[type=submit]");
        botao.disabled = true;                       // evita envios duplicados
        mostrarEstado("A enviar... (se for a primeira vez, o servidor pode demorar a acordar)", "ok");

        // Corta o pedido ao fim de 60 s: o servidor gratuito pode demorar a arrancar
        const controlo = new AbortController();
        const temporizador = setTimeout(() => controlo.abort(), 60000);

        try {
            const resposta = await fetch(formulario.dataset.apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(Object.fromEntries(new FormData(formulario))),
                signal: controlo.signal
            });
            if (resposta.status === 429) {
                mostrarEstado("Enviou muitas mensagens seguidas. Tente de novo mais tarde.", "erro");
            } else if (!resposta.ok) {
                throw new Error("Resposta " + resposta.status);
            } else {
                mostrarEstado("Mensagem enviada. Responderei em breve.", "ok");
                formulario.reset();
            }
        } catch (erro) {
            mostrarEstado("Não foi possível enviar. Tente de novo ou contacte-me por email.", "erro");
        } finally {
            clearTimeout(temporizador);
            // Pequena pausa antes de permitir novo envio
            setTimeout(() => { botao.disabled = false; }, 5000);
        }
    });
}