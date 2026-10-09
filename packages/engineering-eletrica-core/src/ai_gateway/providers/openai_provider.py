# -*- coding: utf-8 -*-
"""
Provedor OpenAI ChatGPT (GPT-4o, GPT-4o Mini, o3-mini).
Totalmente compatível com REST HTTP nativo sem dependências obrigatórias.
"""

from __future__ import annotations
import time
import json
import urllib.request
import urllib.error
from ..base_provider import BaseAIProvider
from ..models import RequisicaoAI, RespostaAI

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        super().__init__("openai")

    def gerar_resposta(self, requisicao: RequisicaoAI, api_key: str) -> RespostaAI:
        t0 = time.time()
        modelo = requisicao.modelo or "gpt-4o"
        if not api_key:
            raise ValueError("Chave de API da OpenAI não configurada.")

        url = "https://api.openai.com/v1/chat/completions"
        system_instruction = self.montar_system_prompt_engenharia(requisicao.contexto_engenharia)

        messages = [{"role": "system", "content": system_instruction}]
        for msg in requisicao.historico:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": requisicao.pergunta})

        payload = {
            "model": modelo,
            "messages": messages,
            "temperature": requisicao.temperatura,
            "max_tokens": requisicao.max_tokens
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                choices = resp_json.get("choices", [])
                if choices:
                    texto = choices[0].get("message", {}).get("content", "")
                else:
                    texto = "Sem resposta da OpenAI."
        except urllib.error.HTTPError as ex:
            err_body = ex.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Erro na API da OpenAI (HTTP {ex.code}): {err_body}")

        latencia = int((time.time() - t0) * 1000)
        return RespostaAI(
            texto=texto,
            provedor_usado="openai",
            modelo_usado=modelo,
            status="sucesso",
            normas_referenciadas=self._extrair_normas(texto),
            formulas_aplicadas=self._extrair_formulas(texto),
            latencia_ms=latencia,
            tokens_estimados=len(texto.split()) * 2
        )
