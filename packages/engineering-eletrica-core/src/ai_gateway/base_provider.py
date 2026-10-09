# -*- coding: utf-8 -*-
"""
Classe Base Abstrata para Provedores de IA - Antigravity Engenharia Elétrica.
"""

from __future__ import annotations
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from .models import RequisicaoAI, RespostaAI

class BaseAIProvider(ABC):
    """Classe base para adaptadores de provedores de IA."""

    def __init__(self, id_provedor: str):
        self.id_provedor = id_provedor

    @abstractmethod
    def gerar_resposta(self, requisicao: RequisicaoAI, api_key: str = "") -> RespostaAI:
        """Gera resposta síncrona a partir da requisição recebida."""
        pass

    def montar_system_prompt_engenharia(self, contexto: Dict[str, Any]) -> str:
        """Constrói as diretrizes de sistema especializadas em Engenharia Elétrica e Renováveis."""
        prompt = (
            "Você é o ANTIGRAVITY ELECTRICAL & RENEWABLE AI COPILOT, um Engenheiro Eletricista Sênior "
            "com titulação de Especialista e Perito Normativo, com mais de 25 anos de experiência "
            "em Projetos de Instalações Elétricas de Baixa e Média Tensão (ABNT NBR 5410, NBR 5419, "
            "NBR 14039, NR-10), Usinas Solares Fotovoltaicas e Stringbox CC (ABNT NBR 16690, NBR 10899), "
            "Aerogeradores Eólicos (IEC 61400), Biodigestores e Cogeração CHP a Biogás, "
            "Pequenas Centrais Hidrelétricas (PCHs Rurais / Microgeração Hidráulica), "
            "Marco Legal da Micro e Minigeração Distribuída (Lei 14.300/2022) e "
            "Orçamentação Paramétrica com BDI (Acórdão TCU 2622/2013 e SINAPI).\n\n"
            "DIRETRIZES FUNDAMENTAIS DE RESPOSTA:\n"
            "1. RIGOR MATEMÁTICO E NORMATIVO: Justifique sempre seus dimensionamentos indicando artigos, tabelas "
            "e equações das normas técnicas pertinentes (ex: ABNT NBR 5410 Tabela 36 para método de instalação B1, "
            "equação de queda de tensão, limite de 4% em terminais, dimensionamento de condutores de proteção PE);\n"
            "2. SEGURANÇA OPERACIONAL: Enfatize critérios de proteção contra choques (seccionamento automático, "
            "dispositivo DR de 30 mA, equipotencialização BEP), coordenação de disjuntores DIN e proteção contra arcos elétricos CC;\n"
            "3. RENOVAÇÕES AGROINDUSTRIAIS: Considere sempre o balanço energético integrado entre consumo da propriedade "
            "e o despacho otimizado de fontes solares, eólicas, biogás (digestão anaeróbia) e hídricas;\n"
            "4. CLAREZA E DIDÁTICA: Formate suas respostas em tópicos bem estruturados, utilizando negrito para parâmetros "
            "chave e blocos de código para fórmulas matemáticas.\n"
        )

        if contexto:
            prompt += f"\nCONTEXTO ANALÍTICO DO PROJETO CARREGADO NO SISTEMA:\n{contexto}\n"

        return prompt

    def _extrair_normas(self, texto: str) -> List[str]:
        """Extrai menções normativas do texto gerado."""
        padroes = [
            r'NBR\s+\d+[\-\d]*',
            r'NR\-\d+',
            r'IEC\s+\d+[\-\d]*',
            r'Lei\s+\d+[\.\d]*\/\d+',
            r'TCU\s+\d+[\/\d]*',
            r'REN\s+\d+[\/\d]*'
        ]
        normas = []
        for p in padroes:
            matches = re.findall(p, texto, flags=re.IGNORECASE)
            for m in matches:
                m_limpo = m.upper().strip()
                if m_limpo not in normas:
                    normas.append(m_limpo)
        return normas

    def _extrair_formulas(self, texto: str) -> List[str]:
        """Extrai expressões de fórmulas no texto."""
        matches = re.findall(r'`([^`]+=[^`]+)`', texto)
        return [m.strip() for m in matches if len(m) > 4][:5]
