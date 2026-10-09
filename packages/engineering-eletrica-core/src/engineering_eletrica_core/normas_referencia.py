"""
Repositório Estruturado de Normas Técnicas para Engenharia Elétrica
Base Normativa ABNT / Ministério do Trabalho / Regulamentações Técnicas Brasileiras
"""

from typing import Dict, List, Any

NORMAS_ELETRICA_BRASIL: Dict[str, Dict[str, Any]] = {
    "NBR_5410": {
        "codigo": "ABNT NBR 5410:2004",
        "titulo": "Instalações elétricas de baixa tensão",
        "status": "Em vigor (com emendas e revisões pontuais)",
        "ambito": "Residencial, Comercial, Predial e Industrial em Baixa Tensão (até 1000V CA ou 1500V CC)",
        "principais_topicos": [
            "Critérios de estimativa de cargas de iluminação e TUG por área e perímetro (Subitem 9.5.2)",
            "Divisão de circuitos e independência de circuitos de iluminação e força (Subitem 9.5.3)",
            "6 Critérios de dimensionamento de condutores de fase, neutro e condutor de proteção (PE)",
            "Capacidade de condução de corrente (Tabelas 36 a 39) com fatores de temperatura (Tab. 40) e agrupamento (Tab. 42)",
            "Queda de tensão máxima permitida (4% em circuitos terminais a partir do QDC)",
            "Proteção contra sobrecorrentes (Sobrecarga e Curto-circuito adiabatico k²S² >= I²t)",
            "Proteção contra choques elétricos por seccionamento automático (Dispositivo DR 30mA obrigatório)",
            "Dimensionamento e taxa de ocupação máxima em eletrodutos (40% para 3 ou mais cabos)",
            "Proteção contra sobretensões transitórias (Dispositivos DPS Classe II)"
        ],
        "aplicacao_direta": "Dimensionamento de toda a instalação elétrica residencial, comercial e predial em BT."
    },
    "NBR_14039": {
        "codigo": "ABNT NBR 14039:2021",
        "titulo": "Instalações elétricas de média tensão de 1,0 kV a 36,2 kV",
        "status": "Em vigor",
        "ambito": "Subestações abrigadas, transformadores a seco e a óleo, cubículos blindados e cabines primárias",
        "principais_topicos": [
            "Critérios de projeto e montagem de subestações de entrada de energia em média tensão (13,8 kV a 34,5 kV)",
            "Dimensionamento de barramentos de cobre e cabos isolados de MT (EPR/XLPE 12/20 kV ou 15/25 kV)",
            "Seccionamento sob carga, disjuntores a vácuo e SF6",
            "Proteção por relés secundários microprocessados (funções ANSI 50/51, 50N/51N, 27, 59)",
            "Malha de aterramento de subestação e tensões de passo e toque"
        ],
        "aplicacao_direta": "Projetos de edifícios de grande porte com transformador próprio e indústrias."
    },
    "NBR_5419": {
        "codigo": "ABNT NBR 5419:2015 (Partes 1 a 4)",
        "titulo": "Proteção contra descargas atmosféricas (SPDA e MPS)",
        "status": "Em vigor",
        "ambito": "Sistemas de Proteção contra Descargas Atmosféricas e Medidas de Proteção contra Surtos",
        "principais_topicos": [
            "Parte 1: Princípios gerais e parâmetros das correntes de raio",
            "Parte 2: Gerenciamento de risco rigoroso (Risco R1 perda de vidas, R2 serviços essenciais, R3 patrimônio, R4 perdas econômicas)",
            "Parte 3: Danos físicos a estruturas e perigos à vida (Método Franklin, Gaiola de Faraday e Esfera Rolante/Eletrogeométrico)",
            "Parte 4: Sistemas elétricos e eletrônicos internos (MPS, Zonas de Proteção LPZ 0A, 0B, 1, 2 e coordenação de DPS Classe I, II e III)"
        ],
        "aplicacao_direta": "Proteção externa de telhados, captores, descidas, anéis de aterramento e DPS para residências e prédios."
    },
    "NR_10": {
        "codigo": "NR-10 (Portaria MTP)",
        "titulo": "Segurança em Instalações e Serviços em Eletricidade",
        "status": "Norma Regulamentadora Federal Obrigatória",
        "ambito": "Segurança de trabalhadores, usuários e intervenções em sistemas elétricos",
        "principais_topicos": [
            "Prontuário das Instalações Elétricas (PIE) obrigatório para instalações acima de 75 kW",
            "Desenergização com as 6 etapas de segurança (Seccionamento, Impedimento, Constatação de ausência de tensão, Aterramento temporário, Proteção dos elementos vivos e Sinalização)",
            "Uso de EPIs e EPCs adequados com laudo de ensaio dielétrico",
            "Análise Preliminar de Risco (APR) e Ordem de Serviço (OS)",
            "Trabalho em áreas classificadas e atmosferas explosivas"
        ],
        "aplicacao_direta": "Requisitos obrigatórios de conformidade legal de segurança e elaboração de laudos periciais."
    },
    "NBR_5444": {
        "codigo": "ABNT NBR 5444:1989",
        "titulo": "Símbolos gráficos para instalações elétricas prediais",
        "status": "Referência clássica e padrão consagrado na engenharia nacional",
        "ambito": "Desenho técnico e simbologia de plantas elétricas prediais e residenciais",
        "principais_topicos": [
            "Símbolos de caixas no teto (pontos de luz) com circuitos, potência e comandos",
            "Símbolos de tomadas baixas, médias e altas, interruptores simples, paralelos (tree-way) e intermediários (four-way)",
            "Traços de fiação em eletroduto: Fase (traço transversal cheio), Neutro (traço em gancho/L invertido), Terra (traço em T invertido) e Retorno (meio traço transversal)",
            "Eletrodutos no teto (linha contínua) e eletrodutos no piso/parede (linha tracejada)"
        ],
        "aplicacao_direta": "Geração automatizada de plantas baixas unifilares 2D em DXF e pranchas de projeto."
    },
    "NBR_16690": {
        "codigo": "ABNT NBR 16690:2019",
        "titulo": "Instalações elétricas de arranjos fotovoltaicos - Requisitos de projeto",
        "status": "Em vigor",
        "ambito": "Geração solar fotovoltaica distribuída conectada à rede (on-grid) e isolada (off-grid)",
        "principais_topicos": [
            "Dimensionamento de cabos solares em CC resistentes a UV (tensão até 1500V CC)",
            "String box CC com fusíveis gPV, chaves seccionadoras e DPS CC",
            "Inversores de frequência interligados à rede de distribuição BT/MT",
            "Coordenação de proteções e aterramento de carcaças dos módulos"
        ],
        "aplicacao_direta": "Projetos de energia solar residencial e predial integrados ao QDC."
    }
}
