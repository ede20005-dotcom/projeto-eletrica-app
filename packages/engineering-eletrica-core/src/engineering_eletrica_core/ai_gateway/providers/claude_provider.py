# -*- coding: utf-8 -*-
"""
Provedor Anthropic Claude (Claude 3.5 Sonnet, Claude 3.5 Haiku).
Suporta API REST da Anthropic via urllib.
"""

from __future__ import annotations
import time
import json
import urllib.request
import urllib.error
from ..base_provider import BaseAIProvider
from ..models import RequisicaoAI, RespostaAI

class ClaudeProvider(BaseAIProvider):
    def __init__(self):
        super().__init__("claude")

    def gerar_resposta(self, requisicao: RequisicaoAI, api_key: str) -> RespostaAI:
        t0 = time.time()
        modelo = requisicao.modelo or "claude-3-5-sonnet-20241022"
        if not api_key:
            raise ValueError("Chave de API da Anthropic Claude não configurada.")

        url = "https://api.anthropic.com/v1/messages"
        system_instruction = self.montar_system_prompt_engenharia(requisicao.contexto_engenharia)

        messages = []
        for msg in requisicao.historico:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": requisicao.pergunta})

        payload = {
            "model": modelo,
            "system": system_instruction,
            "messages": messages,
            "max_tokens": requisicao.max_tokens,
            "temperature": requisicao.temperatura
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                contents = resp_json.get("content", [])
                texto = "".join([c.get("text", "") for c in contents if c.get("type") == "text"])
        except urllib.error.HTTPError as ex:
            err_body = ex.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Erro na API da Anthropic (HTTP {ex.code}): {err_body}")

        latencia = int((time.time() - t0) * 1000)
        return RespostaAI(
            texto=texto,
            provedor_usado="claude",
            modelo_usado=modelo,
            status="sucesso",
            normas_referenciadas=self._extrair_normas(texto),
            formulas_aplicadas=self._extrair_formulas(texto),
            latencia_ms=latencia,
            tokens_estimados=len(texto.split()) * 2
        )
