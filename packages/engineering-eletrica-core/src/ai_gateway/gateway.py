# -*- coding: utf-8 -*-
"""
AIGatewayService: Orquestrador Central de Inteligência Artificial Multiprovedor
para Engenharia Elétrica, Eficiência Energética e Renováveis.
Gerencia roteamento entre Google Gemini, OpenAI ChatGPT, Anthropic Claude,
DeepSeek, Ollama Local e o Motor de Inferência Analítico Offline.
"""

from __future__ import annotations
import os
import time
from typing import Dict, Any, List, Optional
from .models import RequisicaoAI, RespostaAI, InfoProvedor, InfoModelo
from .key_manager import AIKeyManager
from .base_provider import BaseAIProvider
from .providers.gemini_provider import GeminiProvider
from .providers.openai_provider import OpenAIProvider
from .providers.claude_provider import ClaudeProvider
from .providers.deepseek_provider import DeepSeekProvider
from .providers.ollama_provider import OllamaProvider
from .providers.offline_expert_provider import OfflineExpertProvider
try:
    from engineering_eletrica_core.assistente_engenharia_eletrica_ai import AssistenteEngenhariaEletricaAI
except ImportError:
    from assistente_engenharia_eletrica_ai import AssistenteEngenhariaEletricaAI

class AIGatewayService:
    """Gateway unificado para comunicação com modelos de IA e copiloto elétrico."""

    def __init__(self):
        self.provedores: Dict[str, BaseAIProvider] = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "claude": ClaudeProvider(),
            "deepseek": DeepSeekProvider(),
            "ollama": OllamaProvider(),
            "offline": OfflineExpertProvider()
        }
        self.assistente_offline = AssistenteEngenhariaEletricaAI()

    def listar_provedores(self) -> List[InfoProvedor]:
        """Retorna o catálogo completo de provedores suportados com status de chaves."""
        status_chaves = AIKeyManager.listar_status_chaves()

        return [
            InfoProvedor(
                id="offline",
                nome="Motor Offline Antigravity",
                icone="⚡",
                empresa="Antigravity Core",
                chave_configurada=True,
                env_var="",
                suporta_visao=False,
                suporta_raciocinio_cot=True,
                modelos=[
                    InfoModelo(
                        id="expert-analytical-eletrica-v1",
                        nome="Motor Analítico NBR 5410/5419/16690",
                        descricao="Motor determinístico embutido sem internet ou chaves de API externas.",
                        contexto_max="Ilimitado / Local",
                        recomendado_para="Uso 100% offline em campo, auditoria de normas e verificação rápida."
                    )
                ]
            ),
            InfoProvedor(
                id="gemini",
                nome="Google Gemini",
                icone="✨",
                empresa="Google",
                chave_configurada=status_chaves.get("gemini", False),
                env_var="GEMINI_API_KEY",
                suporta_visao=True,
                suporta_raciocinio_cot=True,
                modelos=[
                    InfoModelo(
                        id="gemini-3.8-flash",
                        nome="Gemini 3.8 Flash (Recomendado - Mais Novo)",
                        descricao="Modelo de última geração com alta velocidade, raciocínio multimodal e 1M tokens.",
                        contexto_max="1.048.576 tokens",
                        recomendado_para="Consultas técnicas, copiloto de engenharia e análise de projetos."
                    ),
                    InfoModelo(
                        id="gemini-3.5-flash",
                        nome="Gemini 3.5 Flash",
                        descricao="Alta estabilidade e velocidade para conferência de normas e projetos elétricos.",
                        contexto_max="1.048.576 tokens",
                        recomendado_para="Resumos executivos e conferência de tabelas."
                    ),
                    InfoModelo(
                        id="gemini-2.0-flash",
                        nome="Gemini 2.0 Flash",
                        descricao="Versão ultra estável de alta disponibilidade.",
                        contexto_max="1.048.576 tokens",
                        recomendado_para="Resumos executivos e conferência de tabelas."
                    ),
                    InfoModelo(
                        id="gemini-1.5-flash",
                        nome="Gemini 1.5 Flash",
                        descricao="Versão ultra leve de alta disponibilidade.",
                        contexto_max="1.048.576 tokens",
                        recomendado_para="Cálculos diretos e validação de parâmetros."
                    )
                ]
            ),
            InfoProvedor(
                id="openai",
                nome="OpenAI ChatGPT",
                icone="🟢",
                empresa="OpenAI",
                chave_configurada=status_chaves.get("openai", False),
                env_var="OPENAI_API_KEY",
                suporta_visao=True,
                suporta_raciocinio_cot=True,
                modelos=[
                    InfoModelo(
                        id="gpt-4o",
                        nome="GPT-4o (Omni)",
                        descricao="Modelo multimodal topo de linha com alto rigor matemático.",
                        contexto_max="128.000 tokens",
                        recomendado_para="Auditoria completa, minutas de ART e conferência técnica."
                    ),
                    InfoModelo(
                        id="gpt-4o-mini",
                        nome="GPT-4o Mini",
                        descricao="Versão rápida e econômica para esclarecimentos conceituais.",
                        contexto_max="128.000 tokens",
                        recomendado_para="Perguntas rápidas e termos normativos."
                    ),
                    InfoModelo(
                        id="o3-mini",
                        nome="o3-mini (Reasoning)",
                        descricao="Raciocínio lógico aprofundado para deduções matemáticas.",
                        contexto_max="200.000 tokens",
                        recomendado_para="Equações de transitórios elétricos e golpe de aríete."
                    )
                ]
            ),
            InfoProvedor(
                id="claude",
                nome="Anthropic Claude",
                icone="🟣",
                empresa="Anthropic",
                chave_configurada=status_chaves.get("claude", False),
                env_var="ANTHROPIC_API_KEY",
                suporta_visao=True,
                suporta_raciocinio_cot=False,
                modelos=[
                    InfoModelo(
                        id="claude-3-5-sonnet-20241022",
                        nome="Claude 3.5 Sonnet",
                        descricao="Excelente em redação de laudos técnicos e documentação executiva.",
                        contexto_max="200.000 tokens",
                        recomendado_para="Elaboração de memoriais descritivos e pareceres regulatórios."
                    ),
                    InfoModelo(
                        id="claude-3-5-haiku-20241022",
                        nome="Claude 3.5 Haiku",
                        descricao="Inferência de alta velocidade com baixo tempo de resposta.",
                        contexto_max="200.000 tokens",
                        recomendado_para="Consultas rápidas e formatação de dados."
                    )
                ]
            ),
            InfoProvedor(
                id="deepseek",
                nome="DeepSeek AI",
                icone="🐋",
                empresa="DeepSeek",
                chave_configurada=status_chaves.get("deepseek", False),
                env_var="DEEPSEEK_API_KEY",
                suporta_visao=False,
                suporta_raciocinio_cot=True,
                modelos=[
                    InfoModelo(
                        id="deepseek-chat",
                        nome="DeepSeek V3",
                        descricao="Excelente custo-benefício em tarefas de engenharia e codificação.",
                        contexto_max="64.000 tokens",
                        recomendado_para="Análise geral e cálculos normativos."
                    ),
                    InfoModelo(
                        id="deepseek-reasoner",
                        nome="DeepSeek R1 (Reasoning)",
                        descricao="Motor de raciocínio passo a passo com Chain-of-Thought aberto.",
                        contexto_max="64.000 tokens",
                        recomendado_para="Dedução de equações de seletividade e balanço energético."
                    )
                ]
            ),
            InfoProvedor(
                id="ollama",
                nome="Ollama Local",
                icone="🦙",
                empresa="Localhost:11434",
                chave_configurada=True,
                env_var="OLLAMA_HOST",
                suporta_visao=False,
                suporta_raciocinio_cot=True,
                modelos=[
                    InfoModelo(
                        id="llama3.2",
                        nome="Meta LLaMA 3.2 (Local)",
                        descricao="Modelo open-weights executado na própria máquina.",
                        contexto_max="128.000 tokens",
                        recomendado_para="Privacidade total de dados e operação sem internet."
                    ),
                    InfoModelo(
                        id="qwen2.5-coder",
                        nome="Qwen 2.5 Coder (Local)",
                        descricao="Especialista em algoritmos e análise lógica matemática.",
                        contexto_max="32.000 tokens",
                        recomendado_para="Otimização de rotinas e scripts de automação."
                    ),
                    InfoModelo(
                        id="deepseek-r1:8b",
                        nome="DeepSeek R1 8B (Local)",
                        descricao="Versão compacta com raciocínio Chain-of-Thought no Ollama.",
                        contexto_max="32.000 tokens",
                        recomendado_para="Resolução matemática local."
                    )
                ]
            )
        ]

    def consultar(self, requisicao: RequisicaoAI) -> RespostaAI:
        """
        Roteia a consulta técnica para o provedor selecionado com fallback automático
        para o Motor Offline se a chave faltar ou a conexão falhar.
        """
        prov_id = requisicao.provedor.lower() if requisicao.provedor else "offline"
        provedor = self.provedores.get(prov_id)

        # Se solicitou offline ou provedor não cadastrado
        if not provedor or prov_id == "offline":
            return self.provedores["offline"].gerar_resposta(requisicao)

        # Obter chave de API
        chave = AIKeyManager.obter_chave(prov_id, requisicao.api_key_override)
        if not chave and prov_id != "ollama":
            # Sem chave: fallback transparente para o motor offline com aviso amigável
            resp = self.provedores["offline"].gerar_resposta(requisicao)
            resp.aviso = (
                f"Chave para o provedor '{prov_id.upper()}' não configurada. "
                "A resposta foi gerada pelo Motor Analítico Offline Antigravity Elétrica."
            )
            return resp

        try:
            return provedor.gerar_resposta(requisicao, api_key=chave or "")
        except Exception as ex:
            # Fallback resiliente em caso de falha de conexão externa
            resp = self.provedores["offline"].gerar_resposta(requisicao)
            resp.aviso = (
                f"Falha de conexão com '{prov_id.upper()}' ({str(ex)}). "
                "Ativado fallback automático para o Motor Analítico Offline Antigravity Elétrica."
            )
            return resp

    def auditar_projeto(self, dados_projeto: Dict[str, Any], provedor: str = "offline", modelo: Optional[str] = None) -> RespostaAI:
        """Realiza auditoria de conformidade técnica do projeto elétrico."""
        if provedor == "offline" or not AIKeyManager.obter_chave(provedor):
            res_off = self.assistente_offline.auditar_instalacao_completa(dados_projeto)
            return RespostaAI(
                texto=res_off.resposta_tecnica,
                provedor_usado="offline",
                modelo_usado="expert-analytical-audit-v1",
                status="sucesso",
                normas_referenciadas=res_off.normas_referenciadas,
                formulas_aplicadas=res_off.formulas_aplicadas,
                recomendacoes=res_off.recomendacoes_engenharia,
                latencia_ms=10,
                tokens_estimados=len(res_off.resposta_tecnica.split()) * 2
            )

        prompt_auditoria = (
            "Audite a conformidade da seguinte instalação elétrica de baixa tensão e usina de renováveis "
            f"conforme ABNT NBR 5410, NBR 5419, NBR 16690 e Lei 14.300/2022:\n{json.dumps(dados_projeto, indent=2, ensure_ascii=False)}"
        )
        req = RequisicaoAI(
            pergunta=prompt_auditoria,
            provedor=provedor,
            modelo=modelo,
            contexto_engenharia=dados_projeto
        )
        return self.consultar(req)
