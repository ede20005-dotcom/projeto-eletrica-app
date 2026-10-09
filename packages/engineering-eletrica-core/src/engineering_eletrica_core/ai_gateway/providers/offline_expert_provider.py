# -*- coding: utf-8 -*-
"""
Provedor Especialista Offline (Motor Heurístico e Raciocínio Normativo Determinado).
Permite operar o copiloto de engenharia elétrica com 100% de funcionalidade offline.
"""

from __future__ import annotations
import time
from typing import List
from ..base_provider import BaseAIProvider
from ..models import RequisicaoAI, RespostaAI
try:
    from engineering_eletrica_core.assistente_engenharia_eletrica_ai import AssistenteEngenhariaEletricaAI
except ImportError:
    from assistente_engenharia_eletrica_ai import AssistenteEngenhariaEletricaAI

class OfflineExpertProvider(BaseAIProvider):
    def __init__(self):
        super().__init__("offline")
        self.motor = AssistenteEngenhariaEletricaAI()

    def gerar_resposta(self, requisicao: RequisicaoAI, api_key: str = "") -> RespostaAI:
        t0 = time.time()

        if requisicao.contexto_engenharia:
            self.motor.atualizar_contexto(requisicao.contexto_engenharia)

        res_motor = self.motor.consultar(requisicao.pergunta)
        latencia = int((time.time() - t0) * 1000)

        texto = f"### [Motor Analítico Antigravity Elétrica - Modo 100% Offline]\n\n"
        texto += f"**Domínio Especializado:** {res_motor.dominio_detectado}\n\n"
        texto += f"{res_motor.resposta_tecnica}\n\n"

        if res_motor.formulas_aplicadas:
            texto += "#### Equações e Limites Normativos Aplicados:\n"
            for f in res_motor.formulas_aplicadas:
                texto += f"- `{f}`\n"
            texto += "\n"

        if res_motor.recomendacoes_engenharia:
            texto += "#### Recomendações Executivas de Projeto & ART:\n"
            for r in res_motor.recomendacoes_engenharia:
                texto += f"- {r}\n"

        return RespostaAI(
            texto=texto,
            provedor_usado="offline",
            modelo_usado="expert-analytical-eletrica-v1",
            status="sucesso",
            normas_referenciadas=res_motor.normas_referenciadas,
            formulas_aplicadas=res_motor.formulas_aplicadas,
            recomendacoes=res_motor.recomendacoes_engenharia,
            latencia_ms=latencia,
            tokens_estimados=len(texto.split()) * 2,
            confianca_rag=1.00
        )
