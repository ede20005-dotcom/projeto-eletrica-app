# -*- coding: utf-8 -*-
"""
Provedor DeepSeek (DeepSeek V3, DeepSeek R1 Reasoning).
Suporta API compatível com OpenAI da DeepSeek.
"""

from __future__ import annotations
import time
import json
import urllib.request
import urllib.error
from ..base_provider import BaseAIProvider
from ..models import RequisicaoAI, RespostaAI

class DeepSeekProvider(BaseAIProvider):
    def __init__(self):
        super().__init__("deepseek")

    def gerar_resposta(self, requisicao: RequisicaoAI, api_key: str) -> RespostaAI:
        t0 = time.time()
        modelo = requisicao.modelo or "deepseek-chat"
        if not api_key:
            raise ValueError("Chave de API da DeepSeek não configurada.")

        url = "https://api.deepseek.com/chat/completions"
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
            with urllib.request.urlopen(req, timeout=45) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                choices = resp_json.get("choices", [])
                if choices:
                    msg_obj = choices[0].get("message", {})
                    texto = msg_obj.get("content", "")
                    cot = msg_obj.get("reasoning_content", None)
                else:
                    texto = "Sem resposta da DeepSeek."
                    cot = None
        except urllib.error.HTTPError as ex:
            err_body = ex.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Erro na API da DeepSeek (HTTP {ex.code}): {err_body}")

        latencia = int((time.time() - t0) * 1000)
        return RespostaAI(
            texto=texto,
            provedor_usado="deepseek",
            modelo_usado=modelo,
            status="sucesso",
            normas_referenciadas=self._extrair_normas(texto),
            formulas_aplicadas=self._extrair_formulas(texto),
            raciocinio_cot=cot,
            latencia_ms=latencia,
            tokens_estimados=len(texto.split()) * 2
        )
