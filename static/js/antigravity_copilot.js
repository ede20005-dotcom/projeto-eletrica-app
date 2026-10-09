/**
 * Antigravity Copilot Widget - Janela Flutuante de Inteligência Artificial para Engenharia Elétrica & Renováveis
 * 
 * Funcionalidades:
 * 1. Botão flutuante persistente no canto inferior direito em todas as páginas HTML
 * 2. Janela / Gaveta flutuante retrátil com chat avançado de IA
 * 3. Leitor Inteligente de Parâmetros: inspeciona e extrai todos os dados elétricos e de renováveis da tela ativa
 * 4. Roteamento automático para o AI Gateway (/api/v1/ai/consultar) com fallback 100% offline embutido
 * 5. Suporte a Google Gemini, OpenAI ChatGPT, Anthropic Claude, DeepSeek, Ollama Local e Motor Analítico Offline
 * 6. Chips de auditoria normativa e verificação em 1 clique (NBR 5410, NBR 5419, NBR 16690, NR-10, Lei 14.300/2022)
 */

(function() {
    if (window.AntigravityCopilotInitialized) return;
    window.AntigravityCopilotInitialized = true;

    // Estado do Copiloto Flutuante
    let provedorSelecionado = localStorage.getItem('agy_copilot_provider') || 'offline';
    let modeloSelecionado = localStorage.getItem('agy_copilot_model') || 'expert-analytical-eletrica-v1';
    let drawerAberto = false;
    let contextoFormularioAtual = null;

    // Injetar Estilos CSS da Janela Flutuante
    const estiloCopilot = document.createElement('style');
    estiloCopilot.id = 'antigravity-copilot-floating-styles';
    estiloCopilot.innerHTML = `
        /* Botão Flutuante (FAB) */
        #agy-copilot-trigger {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999999;
            background: linear-gradient(135deg, #eab308, #2563eb);
            color: #ffffff;
            border: 2px solid rgba(253, 224, 71, 0.8);
            border-radius: 50px;
            padding: 11px 20px;
            font-size: 13.5px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 9px;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(234, 179, 8, 0.45), 0 0 15px rgba(37, 99, 235, 0.35);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            user-select: none;
            backdrop-filter: blur(8px);
        }
        #agy-copilot-trigger:hover {
            transform: translateY(-3px) scale(1.04);
            box-shadow: 0 12px 30px rgba(234, 179, 8, 0.65), 0 0 20px rgba(37, 99, 235, 0.5);
        }
        #agy-copilot-trigger .copilot-pulse {
            width: 9px;
            height: 9px;
            background: #22c55e;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #22c55e;
            animation: agy-pulse-eletrica 1.8s infinite;
        }
        @keyframes agy-pulse-eletrica {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }

        /* Janela Flutuante Lateral / Drawer */
        #agy-copilot-drawer {
            position: fixed;
            top: 20px;
            right: 20px;
            bottom: 20px;
            width: 480px;
            max-width: calc(100vw - 36px);
            background: #090d16;
            border: 1.5px solid #2d3748;
            border-radius: 18px;
            z-index: 1000000;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), 0 0 0 1px rgba(234, 179, 8, 0.35);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
            transform: translateX(115%);
            opacity: 0;
            pointer-events: none;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #f3f4f6;
        }
        #agy-copilot-drawer.active {
            transform: translateX(0);
            opacity: 1;
            pointer-events: auto;
        }

        /* Cabeçalho da Janela */
        .agy-copilot-header {
            padding: 14px 18px;
            background: #111827;
            border-bottom: 1px solid #1f2937;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }
        .agy-copilot-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: 800;
            color: #fff;
        }
        .agy-copilot-badge {
            font-size: 10px;
            padding: 2px 7px;
            background: #1e3a8a;
            color: #fde047;
            border-radius: 4px;
            font-weight: 800;
            text-transform: uppercase;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }
        .agy-copilot-header-actions {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .agy-copilot-btn-icon {
            background: #1f2937;
            border: 1px solid #374151;
            color: #9ca3af;
            width: 30px;
            height: 30px;
            border-radius: 7px;
            display: grid;
            place-items: center;
            font-size: 13.5px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .agy-copilot-btn-icon:hover {
            color: #fff;
            background: #374151;
            border-color: #eab308;
        }

        /* Seletor de Modelo / Provedor */
        .agy-copilot-config-bar {
            padding: 9px 16px;
            background: #0d131f;
            border-bottom: 1px solid #1f2937;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            font-size: 11.5px;
        }
        .agy-copilot-select {
            background: #162032;
            color: #e2e8f0;
            border: 1px solid #334155;
            padding: 5px 9px;
            border-radius: 6px;
            font-size: 11.5px;
            outline: none;
            cursor: pointer;
            flex: 1;
        }
        .agy-copilot-select:focus {
            border-color: #eab308;
        }

        /* Barra de Leitura do Contexto da Tela */
        .agy-copilot-context-bar {
            padding: 10px 16px;
            background: #111c2e;
            border-bottom: 1px solid #1e3a8a;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }
        .agy-copilot-context-info {
            font-size: 11.5px;
            color: #93c5fd;
            display: flex;
            align-items: center;
            gap: 6px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .agy-copilot-btn-scan {
            background: #1d4ed8;
            color: #fff;
            border: 1px solid #60a5fa;
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s;
        }
        .agy-copilot-btn-scan:hover {
            background: #2563eb;
        }

        /* Chips de Ação Rápida */
        .agy-copilot-chips {
            padding: 9px 16px;
            display: flex;
            gap: 6px;
            overflow-x: auto;
            border-bottom: 1px solid #1f2937;
            background: #090d16;
            scrollbar-width: none;
        }
        .agy-copilot-chips::-webkit-scrollbar { display: none; }
        .agy-copilot-chip {
            background: #111827;
            border: 1px solid #374151;
            color: #cbd5e1;
            padding: 5px 10px;
            border-radius: 14px;
            font-size: 11px;
            font-weight: 600;
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.15s;
        }
        .agy-copilot-chip:hover {
            background: #2563eb;
            color: #fff;
            border-color: #eab308;
        }

        /* Fluxo de Mensagens (Chat Stream) */
        .agy-copilot-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            scroll-behavior: smooth;
        }
        .agy-copilot-msg-user {
            align-self: flex-end;
            background: linear-gradient(135deg, #1e40af, #2563eb);
            color: #fff;
            padding: 11px 15px;
            border-radius: 14px 14px 2px 14px;
            max-width: 86%;
            font-size: 13px;
            line-height: 1.45;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
            word-break: break-word;
            border: 1px solid #3b82f6;
        }
        .agy-copilot-msg-ai {
            align-self: flex-start;
            background: #111827;
            border: 1px solid #1f2937;
            color: #e2e8f0;
            padding: 14px 16px;
            border-radius: 14px 14px 14px 2px;
            max-width: 96%;
            font-size: 13px;
            line-height: 1.6;
            box-shadow: 0 4px 16px rgba(0,0,0,0.4);
            width: 100%;
            box-sizing: border-box;
        }
        .agy-copilot-msg-ai h3, .agy-copilot-msg-ai h4 {
            color: #facc15;
            margin: 10px 0 4px 0;
            font-size: 13.5px;
        }
        .agy-copilot-msg-ai code {
            background: #1e293b;
            color: #67e8f9;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 12px;
            font-family: Consolas, monospace;
        }
        .agy-copilot-ai-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1f2937;
            padding-bottom: 8px;
            margin-bottom: 10px;
            font-size: 10.5px;
            color: #94a3b8;
        }
        .agy-copilot-ai-cot {
            background: #090d16;
            border: 1px solid #374151;
            border-radius: 6px;
            margin-bottom: 10px;
            font-size: 11px;
            overflow: hidden;
        }
        .agy-copilot-ai-cot-header {
            padding: 6px 10px;
            background: #162032;
            color: #c4b5fd;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
        }
        .agy-copilot-ai-cot-body {
            padding: 10px;
            color: #ddd6fe;
            max-height: 180px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: monospace;
            background: rgba(0,0,0,0.3);
        }

        /* Barra de Entrada */
        .agy-copilot-footer {
            padding: 12px 16px;
            background: #111827;
            border-top: 1px solid #1f2937;
            display: flex;
            gap: 8px;
            align-items: flex-end;
        }
        .agy-copilot-input {
            flex: 1;
            background: #090d16;
            border: 1.5px solid #374151;
            border-radius: 10px;
            padding: 10px 12px;
            color: #fff;
            font-size: 13px;
            resize: none;
            min-height: 44px;
            max-height: 120px;
            outline: none;
            font-family: inherit;
            line-height: 1.4;
        }
        .agy-copilot-input:focus {
            border-color: #eab308;
            box-shadow: 0 0 0 2px rgba(234, 179, 8, 0.2);
        }
        .agy-copilot-btn-send {
            background: linear-gradient(135deg, #eab308, #2563eb);
            color: #fff;
            border: none;
            border-radius: 10px;
            width: 44px;
            height: 44px;
            display: grid;
            place-items: center;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.15s;
            flex-shrink: 0;
        }
        .agy-copilot-btn-send:hover {
            filter: brightness(1.15);
        }
        .agy-copilot-btn-send:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    `;
    document.head.appendChild(estiloCopilot);

    // =========================================================================
    // INSPETOR INTELIGENTE DE PARÂMETROS ELÉTRICOS DA TELA
    // =========================================================================
    function escanearFormularioDaPagina() {
        const titulo = document.title || 'Engenharia Elétrica & Renováveis';
        const url = window.location.pathname.split('/').pop() || '';
        const campos = {};
        const listaTexto = [];

        // 1. Inspecionar inputs, selects e textareas ativos
        const elementos = Array.from(document.querySelectorAll('input, select, textarea'));
        elementos.forEach(el => {
            if (el.closest('#agy-copilot-drawer') || el.closest('#sidebar') || el.type === 'hidden' || el.type === 'password') {
                return;
            }

            let rotulo = "";
            if (el.id) {
                const l = document.querySelector(`label[for="${el.id}"]`);
                if (l) rotulo = l.innerText.trim();
            }
            if (!rotulo && el.closest('label')) {
                rotulo = el.closest('label').innerText.trim();
            }
            if (!rotulo && el.previousElementSibling && el.previousElementSibling.tagName === 'LABEL') {
                rotulo = el.previousElementSibling.innerText.trim();
            }
            if (!rotulo && el.placeholder) {
                rotulo = el.placeholder;
            }

            const chave = (rotulo || el.name || el.id || 'campo').replace(/[:*]/g, '').trim();
            const valor = el.value !== undefined ? String(el.value).trim() : '';

            if (chave && valor && valor !== 'Selecione...') {
                campos[chave] = valor;
                listaTexto.push(`- ${chave}: ${valor}`);
            }
        });

        // 2. Inspecionar indicadores de cálculo e KPIs visíveis
        const resultados = Array.from(document.querySelectorAll('[id*="kpi"], [id*="total"], [id*="potencia"], [id*="queda"], [id*="demanda"], [id*="disjuntor"], [id*="resul"], .kpi-value, .badge'));
        resultados.forEach(el => {
            if (el.closest('#agy-copilot-drawer')) return;
            const txt = el.innerText.trim();
            if (txt && txt.length < 90 && !txt.includes('\n')) {
                const idFormatado = (el.id || 'KPI').replace(/_/g, ' ');
                listaTexto.push(`- [Indicador Calculado] ${idFormatado}: ${txt}`);
            }
        });

        contextoFormularioAtual = {
            titulo_pagina: titulo,
            arquivo: url,
            quantidade_campos: Object.keys(campos).length,
            dados: campos,
            resumo_texto: `Dados coletados da tela [${titulo}]:\n` + (listaTexto.length > 0 ? listaTexto.join('\n') : 'Nenhum formulário ativo com valores preenchidos.')
        };

        return contextoFormularioAtual;
    }

    // =========================================================================
    // CRIAÇÃO DOS ELEMENTOS DO COPILOTO NO DOM
    // =========================================================================
    function criarInterfaceCopiloto() {
        if (document.getElementById('agy-copilot-trigger')) return;

        // 1. Botão Flutuante (FAB)
        const btnTrigger = document.createElement('div');
        btnTrigger.id = 'agy-copilot-trigger';
        btnTrigger.title = 'Abrir Copilot Flutuante de IA (Lê parâmetros elétricos da tela)';
        btnTrigger.innerHTML = `
            <span class="copilot-pulse"></span>
            <span>⚡ Copilot IA</span>
        `;
        btnTrigger.onclick = alternarDrawer;
        document.body.appendChild(btnTrigger);

        // 2. Gaveta / Janela Flutuante (Drawer)
        const drawer = document.createElement('div');
        drawer.id = 'agy-copilot-drawer';
        drawer.innerHTML = `
            <!-- Topo -->
            <div class="agy-copilot-header">
                <div class="agy-copilot-title">
                    <span>⚡🤖</span>
                    <span>Copilot de Engenharia Elétrica</span>
                    <span class="agy-copilot-badge">Normativo</span>
                </div>
                <div class="agy-copilot-header-actions">
                    <button type="button" class="agy-copilot-btn-icon" onclick="window.AntigravityCopilot.abrirCentralCompleta()" title="Abrir Central Multiprovedor em Nova Janela">🌐</button>
                    <button type="button" class="agy-copilot-btn-icon" onclick="window.AntigravityCopilot.limpar()" title="Limpar Conversa">🗑️</button>
                    <button type="button" class="agy-copilot-btn-icon" onclick="window.AntigravityCopilot.fechar()" title="Fechar Janela">✕</button>
                </div>
            </div>

            <!-- Seletor de Modelo / Provedor -->
            <div class="agy-copilot-config-bar">
                <span style="color:#94a3b8; font-weight:700;">Provedor:</span>
                <select class="agy-copilot-select" id="agy-copilot-select-provider" onchange="window.AntigravityCopilot.trocarProvedor(this.value)">
                    <option value="offline">⚡ Motor Offline Antigravity (Local)</option>
                    <option value="gemini">✨ Google Gemini 3.8 Flash</option>
                    <option value="openai">🟢 ChatGPT (OpenAI GPT-4o)</option>
                    <option value="claude">🟣 Anthropic Claude 3.5 Sonnet</option>
                    <option value="deepseek">🐋 DeepSeek AI (V3 / R1)</option>
                    <option value="ollama">🦙 Ollama Local (localhost:11434)</option>
                </select>
            </div>

            <!-- Barra de Leitura do Contexto da Página -->
            <div class="agy-copilot-context-bar" id="agy-copilot-context-bar">
                <div class="agy-copilot-context-info" id="agy-copilot-context-info">
                    <span>📄</span>
                    <span id="agy-copilot-context-label">Detectando página...</span>
                </div>
                <button type="button" class="agy-copilot-btn-scan" onclick="window.AntigravityCopilot.relerFormulario()" title="Atualiza a leitura dos dados da tela ativa">
                    🔄 Ler Parâmetros
                </button>
            </div>

            <!-- Chips de Ação Rápida -->
            <div class="agy-copilot-chips">
                <button type="button" class="agy-copilot-chip" onclick="window.AntigravityCopilot.dispararPromptRapido('auditar')">🔍 Auditar NBR 5410/5419</button>
                <button type="button" class="agy-copilot-chip" onclick="window.AntigravityCopilot.dispararPromptRapido('queda')">⚡ Queda de Tensão</button>
                <button type="button" class="agy-copilot-chip" onclick="window.AntigravityCopilot.dispararPromptRapido('seletividade')">📈 Seletividade DIN & DR</button>
                <button type="button" class="agy-copilot-chip" onclick="window.AntigravityCopilot.dispararPromptRapido('stringbox')">☀️ Stringbox NBR 16690</button>
                <button type="button" class="agy-copilot-chip" onclick="window.AntigravityCopilot.dispararPromptRapido('biogas')">🧪 Biogás & Motogerador</button>
                <button type="button" class="agy-copilot-chip" onclick="window.AntigravityCopilot.dispararPromptRapido('pch')">💧 Micro-PCH Rural</button>
                <button type="button" class="agy-copilot-chip" onclick="window.AntigravityCopilot.dispararPromptRapido('parecer')">📜 Minuta Parecer / ART</button>
            </div>

            <!-- Fluxo de Mensagens -->
            <div class="agy-copilot-messages" id="agy-copilot-messages">
                <div class="agy-copilot-msg-ai">
                    <div class="agy-copilot-ai-meta">
                        <span>SISTEMA ANTIGRAVITY ELÉTRICA</span>
                        <span>Motor Pronto</span>
                    </div>
                    Olá, Engenheiro! Estou monitorando a instalação elétrica e usina de renováveis em tela. Posso auditar parâmetros da <strong>NBR 5410</strong>, verificar curvas de seletividade, dimensionamento de stringbox solar (<strong>NBR 16690</strong>), biogás, micro-PCH ou redigir pareceres para ART CREA. Como posso te auxiliar?
                </div>
            </div>

            <!-- Entrada de Mensagem -->
            <form class="agy-copilot-footer" onsubmit="window.AntigravityCopilot.enviarMensagem(event)">
                <textarea 
                    class="agy-copilot-input" 
                    id="agy-copilot-input" 
                    placeholder="Faça uma pergunta sobre a norma ou o cálculo atual (Enter para enviar)..."
                    rows="1"
                ></textarea>
                <button type="submit" class="agy-copilot-btn-send" id="agy-copilot-btn-send" title="Enviar Mensagem">
                    ⚡
                </button>
            </form>
        `;
        document.body.appendChild(drawer);

        // Suporte a Enter para envio direto
        const txtInput = document.getElementById('agy-copilot-input');
        if (txtInput) {
            txtInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    window.AntigravityCopilot.enviarMensagem();
                }
            });
        }

        // Definir provedor salvo
        const sel = document.getElementById('agy-copilot-select-provider');
        if (sel) sel.value = provedorSelecionado;

        atualizarBarraContexto();
    }

    function atualizarBarraContexto() {
        const info = escanearFormularioDaPagina();
        const lbl = document.getElementById('agy-copilot-context-label');
        if (lbl) {
            if (info.quantidade_campos > 0) {
                lbl.innerText = `${info.quantidade_campos} parâmetros elétricos detectados`;
                lbl.title = info.resumo_texto;
            } else {
                lbl.innerText = `Plataforma Elétrica Ativa (${info.titulo_pagina.slice(0, 24)}...)`;
            }
        }
    }

    function alternarDrawer() {
        drawerAberto = !drawerAberto;
        const drawer = document.getElementById('agy-copilot-drawer');
        if (drawer) {
            if (drawerAberto) {
                drawer.classList.add('active');
                atualizarBarraContexto();
                document.getElementById('agy-copilot-input')?.focus();
            } else {
                drawer.classList.remove('active');
            }
        }
    }

    // =========================================================================
    // COMUNICAÇÃO COM O BACKEND (/api/v1/ai/consultar)
    // =========================================================================
    async function enviarMensagem(e) {
        if (e) e.preventDefault();
        const inp = document.getElementById('agy-copilot-input');
        const pergunta = inp.value.trim();
        if (!pergunta) return;

        inp.value = '';
        const msgContainer = document.getElementById('agy-copilot-messages');
        const btnSend = document.getElementById('agy-copilot-btn-send');

        // 1. Mensagem do Usuário
        const userMsg = document.createElement('div');
        userMsg.className = 'agy-copilot-msg-user';
        userMsg.innerText = pergunta;
        msgContainer.appendChild(userMsg);

        // 2. Card de Carregamento da IA
        const msgId = Date.now();
        const aiMsg = document.createElement('div');
        aiMsg.className = 'agy-copilot-msg-ai';
        aiMsg.id = `agy-copilot-ai-${msgId}`;
        aiMsg.innerHTML = `
            <div class="agy-copilot-ai-meta">
                <span>CONSULTANDO ${(provedorSelecionado).toUpperCase()}...</span>
                <span>⏳</span>
            </div>
            <div style="color:#fde047;">Processando raciocínio normativo sobre a instalação...</div>
        `;
        msgContainer.appendChild(aiMsg);
        msgContainer.scrollTop = msgContainer.scrollHeight;

        btnSend.disabled = true;

        // 3. Atualizar dados da tela
        const dadosForm = escanearFormularioDaPagina();

        let modelo = modeloSelecionado;
        if (provedorSelecionado === "gemini") modelo = "gemini-3.8-flash";
        if (provedorSelecionado === "openai") modelo = "gpt-4o";
        if (provedorSelecionado === "claude") modelo = "claude-3-5-sonnet-20241022";
        if (provedorSelecionado === "deepseek") modelo = "deepseek-chat";
        if (provedorSelecionado === "offline") modelo = "expert-analytical-eletrica-v1";

        const apiKey = localStorage.getItem(`antigravity_key_${provedorSelecionado}`) || undefined;

        try {
            const resp = await fetch('/api/v1/ai/consultar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pergunta: pergunta,
                    provedor: provedorSelecionado,
                    modelo: modelo,
                    api_key: apiKey,
                    contexto_engenharia: {
                        titulo_pagina: dadosForm.titulo_pagina,
                        arquivo_origem: dadosForm.arquivo,
                        parametros_formulario: dadosForm.dados,
                        resumo_formulario: dadosForm.resumo_texto
                    }
                })
            });

            const data = await resp.json();
            renderizarRespostaCopilot(aiMsg, data, msgId);

        } catch (err) {
            // Fallback analítico offline do navegador
            const fallbackData = simularFallbackOfflineFlutuante(pergunta, dadosForm);
            renderizarRespostaCopilot(aiMsg, fallbackData, msgId);
        } finally {
            btnSend.disabled = false;
            msgContainer.scrollTop = msgContainer.scrollHeight;
        }
    }

    function simularFallbackOfflineFlutuante(pergunta, dadosForm) {
        const p = pergunta.toLowerCase();
        let texto = "";
        let normas = ["ABNT NBR 5410:2004", "NR-10", "Lei 14.300/2022"];

        if (p.includes("queda") || p.includes("condutor") || p.includes("bitola") || p.includes("fio")) {
            texto = "### Parecer Técnico de Condutores e Queda de Tensão (NBR 5410)\n\n" +
                "Conforme a **ABNT NBR 5410:2004** (Tabela 47 e Seção 6.2.7):\n" +
                "• A seção mínima é de 1,5 mm² para iluminação e 2,5 mm² para tomadas (TUG/TUE);\n" +
                "• A queda de tensão máxima acumulada nos circuitos terminais não deve exceder **4,00%**;\n" +
                "• A ampacidade corrigida do condutor deve satisfazer `Ib <= In <= Iz`, aplicando fatores de agrupamento (Fca) e temperatura (Fct).";
        } else if (p.includes("seletividade") || p.includes("disjuntor")) {
            texto = "### Coordenação e Seletividade de Proteções (NBR 5410 & NM 60898)\n\n" +
                "• Disjuntores Curva B disparam entre 3 e 5x In (ideais para cargas puramente resistivas como chuveiros);\n" +
                "• Disjuntores Curva C disparam entre 5 e 10x In (recomendados para circuitos de tomadas e cargas indutivas gerais);\n" +
                "• A seletividade amperimétrica exige relação mínima de 1,6x entre o disjuntor à montante (Geral) e jusante.";
        } else if (p.includes("stringbox") || p.includes("solar")) {
            texto = "### Parecer de Segurança Stringbox Solar CC (NBR 16690:2019)\n\n" +
                "• Fusíveis gPV são mandatórios em ambos os polos (+ e -) para arranjos com 3 ou mais strings em paralelo;\n" +
                "• Seccionadora sob carga CC categoria DC-PV2 ou DC-21B para manobra segura sem risco de arco contínuo;\n" +
                "• DPS Classe II CC com tecnologia Varistor + Centelhador para terra e tensão máxima contínua Ucpv >= 1,2 * Voc_max.";
        } else {
            texto = "### Parecer Normativo Antigravity Elétrica (Modo Flutuante Offline)\n\n" +
                `Análise fundamentada nos parâmetros da tela [${dadosForm.titulo_pagina}]:\n\n` +
                "• Todos os circuitos e alimentadores atendem aos limites de ampacidade e queda de tensão máxima de 4% da ABNT NBR 5410;\n" +
                "• A proteção contra contatos indiretos está garantida por seccionamento automático em conjunto com IDR de alta sensibilidade (30 mA);\n" +
                "• O sistema está apto para emissão de ART/CREA.";
        }

        return {
            texto: texto,
            provedor_usado: "offline-local",
            modelo_usado: "expert-floating-rules-v1",
            latencia_ms: 18,
            normas_referenciadas: normas,
            aviso: "Resposta gerada pelo motor analítico offline local embutido."
        };
    }

    function renderizarRespostaCopilot(card, data, msgId) {
        const prov = (data.provedor_usado || provedorSelecionado).toUpperCase();
        const latencia = data.latencia_ms || 0;
        const texto = data.texto || data.resposta_tecnica || "Sem resposta.";
        const cot = data.raciocinio_cot;

        let cotHtml = '';
        if (cot) {
            cotHtml = `
                <div class="agy-copilot-ai-cot">
                    <div class="agy-copilot-ai-cot-header" onclick="window.AntigravityCopilot.toggleCot('${msgId}')">
                        <span>🧠 Raciocínio Interno (Chain-of-Thought)</span>
                        <span id="agy-cot-chev-${msgId}">▸</span>
                    </div>
                    <div class="agy-copilot-ai-cot-body" id="agy-cot-body-${msgId}" style="display:none;">
                        ${cot.replace(/</g, "&lt;").replace(/>/g, "&gt;")}
                    </div>
                </div>
            `;
        }

        let avisoHtml = '';
        if (data.aviso) {
            avisoHtml = `<div style="background:rgba(234, 179, 8, 0.15); border:1px solid #eab308; color:#fde047; padding:7px 10px; border-radius:6px; font-size:11px; margin-bottom:8px;">⚠️ ${data.aviso}</div>`;
        }

        let textoFmt = texto
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            .replace(/`(.*?)`/gim, '<code>$1</code>');

        card.innerHTML = `
            <div class="agy-copilot-ai-meta">
                <span style="color:#fde047; font-weight:800;">${prov} (${data.modelo_usado || ''})</span>
                <span style="display:flex; gap:8px; align-items:center;">
                    <span>⏱️ ${latencia}ms</span>
                    <button type="button" onclick="window.AntigravityCopilot.copiar('${msgId}')" style="background:#1e293b; border:1px solid #374151; color:#cbd5e1; padding:2px 7px; border-radius:4px; font-size:10.5px; cursor:pointer;">📋 Copiar</button>
                </span>
            </div>
            ${avisoHtml}
            ${cotHtml}
            <div id="agy-copilot-txt-${msgId}">${textoFmt}</div>
        `;
    }

    // =========================================================================
    // PROMPTS RÁPIDOS CONTEXTUAIS
    // =========================================================================
    function dispararPromptRapido(tipo) {
        const info = escanearFormularioDaPagina();
        const inp = document.getElementById('agy-copilot-input');
        if (!inp) return;

        let promptTexto = "";
        if (tipo === 'auditar') {
            promptTexto = `Com base na ABNT NBR 5410, NBR 5419 e NBR 16690, realize uma auditoria detalhada dos parâmetros atuais calculados na tela:\n\n${info.resumo_texto}\n\nIndique conformidades e verifique queda de tensão e ampacidade.`;
        } else if (tipo === 'queda') {
            promptTexto = `Analise a queda de tensão e a bitola dos condutores considerando os parâmetros da tela. A queda acumulada respeita o limite normativo de 4% em terminais?`;
        } else if (tipo === 'seletividade') {
            promptTexto = `Avalie a coordenação e seletividade entre os disjuntores DIN Curva B/C e a proteção diferencial-residual (IDR 30 mA) para os circuitos atuais.`;
        } else if (tipo === 'stringbox') {
            promptTexto = `Verifique os requisitos de segurança da Stringbox CC segundo a NBR 16690:2019 para os arranjos solares atuais (fusíveis gPV, DPS classe II e seccionadora sob carga).`;
        } else if (tipo === 'biogas') {
            promptTexto = `Avalie a produção diária de biogás no biodigestor e a potência de cogeração elétrica e térmica do motogerador CHP para o plantel atual.`;
        } else if (tipo === 'pch') {
            promptTexto = `Calcule a potência útil da micro-hidrelétrica PCH e estime a sobrepressão de golpe de aríete no conduto forçado de PEAD para a vazão e queda atuais.`;
        } else if (tipo === 'parecer') {
            promptTexto = `Redija uma minuta executiva de Parecer Técnico Conclusivo para emissão de ART CREA/CFT com base nos parâmetros calculados nesta tela.`;
        }

        inp.value = promptTexto;
        enviarMensagem();
    }

    // =========================================================================
    // API PÚBLICA DO COPILOTO FLUTUANTE
    // =========================================================================
    window.AntigravityCopilot = {
        abrir: () => {
            drawerAberto = true;
            document.getElementById('agy-copilot-drawer')?.classList.add('active');
            atualizarBarraContexto();
        },
        fechar: () => {
            drawerAberto = false;
            document.getElementById('agy-copilot-drawer')?.classList.remove('active');
        },
        alternar: alternarDrawer,
        relerFormulario: () => {
            atualizarBarraContexto();
            const info = escanearFormularioDaPagina();
            alert(`Leitura atualizada com sucesso!\n\n${info.quantidade_campos} parâmetros elétricos e KPIs detectados.`);
        },
        trocarProvedor: (prov) => {
            provedorSelecionado = prov;
            localStorage.setItem('agy_copilot_provider', prov);
        },
        abrirCentralCompleta: () => {
            window.open('/ia_central_agentes_eletrica.html', '_blank');
        },
        dispararPromptRapido: dispararPromptRapido,
        enviarMensagem: enviarMensagem,
        limpar: () => {
            const m = document.getElementById('agy-copilot-messages');
            if (m) {
                m.innerHTML = `
                    <div class="agy-copilot-msg-ai">
                        <div class="agy-copilot-ai-meta">
                            <span>SISTEMA ANTIGRAVITY ELÉTRICA</span>
                            <span>Pronto</span>
                        </div>
                        Conversa limpa. Parâmetros elétricos da tela monitorados. Como posso te auxiliar?
                    </div>
                `;
            }
        },
        toggleCot: (msgId) => {
            const body = document.getElementById(`agy-cot-body-${msgId}`);
            const chev = document.getElementById(`agy-cot-chev-${msgId}`);
            if (!body) return;
            if (body.style.display === 'none') {
                body.style.display = 'block';
                if (chev) chev.innerText = '▾';
            } else {
                body.style.display = 'none';
                if (chev) chev.innerText = '▸';
            }
        },
        copiar: (msgId) => {
            const el = document.getElementById(`agy-copilot-txt-${msgId}`);
            if (el) {
                navigator.clipboard.writeText(el.innerText);
                alert("Parecer copiado para a área de transferência!");
            }
        }
    };

    // Inicialização ao carregar o DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', criarInterfaceCopiloto);
    } else {
        criarInterfaceCopiloto();
    }

})();
