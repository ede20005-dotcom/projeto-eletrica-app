# -*- coding: utf-8 -*-
"""
Provedor Local Ollama (LLaMA 3, Qwen 2.5, DeepSeek R1 Local, Mistral).
Permite executar modelos de linguagem localmente em http://localhost:11434 sem custo ou internet.
"""

from __future__ import annotations
import time
import json
import urllib.request
import urllib.error
from ..base_provider import BaseAIProvider
from ..models import RequisicaoAI, RespostaAI

class OllamaProvider(BaseAIProvider):
    def __init__(self):
        super().__init__("ollama")

    def gerar_resposta(self, requisicao: RequisicaoAI, api_key: str = "") -> RespostaAI:
        t0 = time.time()
        modelo = requisicao.modelo or "llama3.2"
        host = api_key.strip() if api_key.strip() else "http://localhost:11434"
        if not host.startswith("http"):
            host = f"http://{host}"

        url = f"{host.rstrip('/')}/api/chat"
        system_instruction = self.montar_system_prompt_engenharia(requisicao.contexto_engenharia)

        messages = [{"role": "system", "content": system_instruction}]
        for msg in requisicao.historico:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": requisicao.pergunta})

        payload = {
            "model": modelo,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": requisicao.temperatura,
                "num_predict": requisicao.max_tokens
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                texto = resp_json.get("message", {}).get("content", "Sem resposta do Ollama.")
        except Exception as ex:
            raise RuntimeError(
                f"Falha ao conectar ao Ollama local em '{host}'. "
                f"Certifique-se de que o Ollama está rodando (`ollama run {modelo}`). Detalhes: {ex}"
            )

        latencia = int((time.time() - t0) * 1000)
        return RespostaAI(
            texto=texto,
            provedor_usado="ollama",
            modelo_usado=modelo,
            status="sucesso",
            normas_referenciadas=self._extrair_normas(texto),
            formulas_aplicadas=self._extrair_formulas(texto),
            latencia_ms=latencia,
            tokens_estimados=len(texto.split()) * 2
        )
