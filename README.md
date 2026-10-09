# ⚡ Antigravity — Engenharia Elétrica & Renováveis (App)

[![Licença](https://img.shields.io/badge/Normas-ABNT%20NBR%205410%20%7C%205419%20%7C%2016690-blue.svg)](https://www.abnt.org.br/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-yellow.svg)](https://www.python.org/)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL%203D-black.svg)](https://threejs.org/)
[![AI-Copilot](https://img.shields.io/badge/AI%20Copilot-Gemini%203.8%20%7C%20ChatGPT%20%7C%20DeepSeek%20%7C%20Offline-orange.svg)](#-7-agente-de-ia--copilot-flutuante)
[![Plataforma](https://img.shields.io/badge/Windows-Portable%20%7C%20Installer-0078D6.svg)](#-3-como-executar-o-aplicativo)

**Aplicativo Completo de Engenharia Elétrica de Alta Performance e Microrredes Renováveis** desenvolvido em conformidade rigorosa com as normas técnicas brasileiras e internacionais:
- **ABNT NBR 5410:2004** — Instalações Elétricas de Baixa Tensão
- **NR-10 (Portaria MTP)** — Segurança em Instalações e Serviços em Eletricidade
- **ABNT NBR 5419:2015 (Partes 1 a 4)** — Proteção contra Descargas Atmosféricas (SPDA e MPS)
- **ABNT NBR 16690:2019** — Instalações Elétricas de Arranjos Fotovoltaicos
- **IEC 61400-2** — Aerogeradores e Turbinas Eólicas de Pequeno Porte
- **Acórdão TCU 2622/2013 & Lei 14.133/2021** — Diretrizes de BDI e Orçamentação Pública

---

## 🎯 Visão Geral do Aplicativo

O **Antigravity Elétrica App** foi projetado para engenheiros eletricistas, projetistas, técnicos e consultores de energia que precisam dimensionar, auditar, desenhar e emitir laudos técnicos de instalações elétricas completas em minutos.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ANTIGRAVITY ENGENHARIA ELÉTRICA                      │
├─────────────────────┬───────────────────────────┬──────────────────────┤
│  ⚡ BAIXA TENSÃO     │  ☀️ RENOVÁVEIS & AGRO      │  🧠 INTELIGÊNCIA IA  │
│  • Cargas & Demanda │  • Solar Fotovoltaico     │  • Gemini 3.8 Flash  │
│  • 6 Critérios Cabos│  • Stringbox CC 1000V     │  • Inspetor de Tela  │
│  • Disjuntores DIN  │  • Eólica (Betz)          │  • NBR 5410 Offline  │
│  • Seletividade Log │  • Biogás & Motogerador   │  • Minuta de ART     │
│  • Planta Baixa 2D  │  • Micro-Hidrelétrica PCH │  • Multi-Provedores  │
│  • Maquete 3D WebGL │  • BDI Orçamentário TCU   │  • Widget Flutuante  │
└─────────────────────┴───────────────────────────┴──────────────────────┘
```

---

## 🚀 Como Executar o Aplicativo

### Opção 1: Inicialização em 1 Clique (Sem Instalação)
Dê **dois cliques** no arquivo:
```cmd
INICIAR_APP.bat
```
- Se você tiver Python instalado: ele inicializa o servidor local autônomo e abre uma **janela nativa sem moldura do Edge** (`--app`).
- Se não tiver Python: ele abre diretamente o arquivo `index.html` em qualquer navegador moderno com **100% dos recursos funcionais offline**!

---

### Opção 2: Pelo Navegador Web Diretamente
Basta abrir o arquivo **[`index.html`](index.html)** com um duplo clique no Google Chrome, Microsoft Edge, Firefox ou Safari. Todo o motor matemático, visualizadores 2D/3D e regras analíticas funcionam diretamente no seu navegador.

---

### Opção 3: Execução com Servidor Python Standalone
Se desejar utilizar o backend multithread e os exportadores de arquivos DXF e laudos em Word:
```powershell
# 1. Instalar as dependências mínimas (ezdxf, python-docx)
pip install -r requirements.txt

# 2. Iniciar a aplicação desktop
python desktop_launcher.py
```

---

## ⚡ Módulos & Recursos Disponíveis

### 1. Dimensionamento NBR 5410 & NR-10
- Levantamento de iluminação ($VA$) e tomadas ($VA$) por cômodo.
- **Os 6 Critérios Normativos de Condutores:** Seção Mínima, Capacidade de Corrente (fatores de agrupamento e temperatura), Queda de Tensão ($\le 4\%$), Sobrecarga ($I_b \le I_n \le I_z$), Condutores Neutro/Terra e Proteção contra Choques (IDR $30\text{ mA}$).
- Taxa de ocupação de eletrodutos ($40\%$).
- Estudo de Demanda da Instalação e determinação do padrão de entrada da concessionária.

### 2. Esquemas Técnicos 2D e Maquete 3D Interativa WebGL
- **Planta Baixa 2D:** Renderização em Canvas com simbologia da ABNT NBR 5444 (traços de fase, neutro, terra e retorno, caixas octogonais e tomadas).
- **Maquete 3D WebGL (Three.js):** Modelo espacial das paredes, piso, portas, janelas, eletrodutos corrugados e fiação colorida por fase/neutro/terra.

### 3. Usinas e Microrredes Renováveis Integradas
- **Solar Fotovoltaico (NBR 16690):** Módulos FV, inversores, geração média mensal/anual e Payback estimado.
- **Stringbox CC:** Dimensionamento de fusíveis gPV ($1000\text{ V}$ CC), seccionadora sob carga e DPS Classe II CC.
- **Aerogerador Eólico (IEC 61400):** Cálculo aerodinâmico pelo Limite de Betz, potência nominal e curvas de vento.
- **Biodigestor & Cogeração CHP a Biogás:** Dimensionamento de digestores anaeróbios, produção diária de metano ($\text{m}^3/\text{dia}$) e motogerador CHP (eletricidade + calor para agroindústria).
- **Micro-Hidrelétrica PCH:** Cálculo de potência de eixo $P = \rho \cdot g \cdot Q \cdot H \cdot \eta$, conduto forçado e seleção de turbinas hidráulicas (Pelton, Francis, Banki).

### 4. Estudo de Seletividade e Proteções Elétricas
- Gráfico bilogarítmico (log-log) comparando as curvas de atuação a frio dos disjuntores DIN Curva B e Curva C.
- Coordenação de seletividade total/parcial contra curto-circuitos e atuação diferencial com IDR $30\text{ mA}$.

### 5. Orçamento Paramétrico & BDI (TCU)
- Levantamento quantitativo automático de cabos, disjuntores, eletrodutos, módulos solares, inversores e componentes.
- Cálculo de BDI analítico parametrizado conforme a fórmula oficial do Acórdão 2622/2013 do TCU.

---

## 🧠 Agente de IA & Copilot Flutuante

O sistema conta com um **Copilot Flutuante persistente** acessível por um botão no canto inferior direito e pelo atalho de teclado global **`Ctrl + I`**:

- **Inspetor Dinâmico de Circuito:** Lê em tempo real as tensões, cargas, correntes e potências preenchidas na tela ativa e as adiciona automaticamente ao contexto da IA.
- **Provedores Suportados:**
  - ⚡ **Motor Offline Antigravity:** 100% determinístico e embutido, auditando NBR 5410, NR-10 e NBR 5419 sem internet e sem custos de API.
  - ✨ **Google Gemini 3.8 Flash:** A versão mais recente e veloz do Google, com auto-fallback resiliente anti-404.
  - 🟢 **OpenAI ChatGPT (GPT-4o)**
  - 🟣 **Anthropic Claude 3.5 Sonnet**
  - 🐋 **DeepSeek AI (V3 / R1)**
  - 🦙 **Ollama Local (100% offline no seu computador)**
- **Ações Rápidas de 1 Clique:**
  - Auditoria NBR 5410 / NR-10
  - Auditoria de Queda de Tensão
  - Estudo de Seletividade DIN / DR
  - Stringbox NBR 16690
  - Biogás CHP & PCH
  - Geração de Minuta de ART do CREA/CFT

---

## 📐 Pranchas CAD DXF & Laudo em Word Incluídos

O aplicativo inclui na pasta [`cad_export/`](cad_export/) e [`exports_docx/`](exports_docx/) pranchas técnicas prontas para abrir no AutoCAD/Revit/FreeCAD:

1. `planta_baixa_residencial.dxf` — Planta baixa com traçados e quadro de cargas (NBR 5410)
2. `diagrama_unifilar_qdc.dxf` — Diagrama unifilar do QDC com barramento e disjuntores DIN
3. `curvas_seletividade_protecoes.dxf` — Curvas tempo-corrente em escala log-log
4. `diagrama_stringbox_solar_cc.dxf` — Esquema elétrico da stringbox fotovoltaica CC
5. `usina_solar_fotovoltaica.dxf` — Arranjo unifilar da usina solar com inversor
6. `aerogerador_eolica.dxf` — Elevação da torre e circuito do aerogerador
7. `biodigestor_usina_biogas.dxf` — Planta do biodigestor, gasômetro e motogerador CHP
8. `micro_hidreletrica_pch.dxf` — Arranjo hidráulico da barragem, conduto forçado e turbina
9. `memorial_descritivo_eletrico_nbr5410.docx` — Memorial descritivo completo com minuta de ART

---

## 📁 Estrutura de Arquivos

```
C:\projeto-eletrica-app\
├── INICIAR_APP.bat                   # Launcher em 1 clique para Windows
├── index.html                        # Aplicação web mestre consolidada
├── dossie_engenharia_eletrica_consolidado.html
├── ia_central_agentes_eletrica.html  # Central de Agentes de IA
├── desktop_launcher.py               # Launcher desktop nativo em Edge App Mode
├── requirements.txt                  # Dependências Python
├── static/
│   └── js/
│       └── antigravity_copilot.js    # Widget de IA flutuante
├── cad_export/                       # Pranchas DXF técnicas
├── exports_docx/                     # Laudo técnico em Word DOCX
├── apps/                             # Servidor HTTP standalone
├── packages/                         # Motores de cálculo de engenharia
└── tools/                            # Ferramentas de consolidação de template
```

---

## 📜 Licença e Responsabilidade Técnica

Este software é destinado a engenharia elétrica, projetos prediais e instalações agroindustriais de energias renováveis.  
Os cálculos obedecem às normas técnicas brasileiras (ABNT, ANEEL, CONFEA/CREA e CFT).