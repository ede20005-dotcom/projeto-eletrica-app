# -*- coding: utf-8 -*-
"""
Provedor Google Gemini (Gemini 3.8 Flash, Gemini 3.5 Flash, Gemini 2.0 Flash).
Utiliza o SDK oficial google-genai com auto-fallback resiliente contra descontinuações e 404.
Suporta fallback direto via REST HTTP urllib.request com zero dependência externa.
"""

from __future__ import annotations
import time
import json
import urllib.request
import urllib.error
from typing import List, Any
from ..base_provider import BaseAIProvider
from ..models import RequisicaoAI, RespostaAI

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        super().__init__("gemini")

    def gerar_resposta(self, requisicao: RequisicaoAI, api_key: str) -> RespostaAI:
        t0 = time.time()
        modelo_solicitado = requisicao.modelo or "gemini-3.8-flash"
        if not api_key:
            raise ValueError("Chave de API do Google Gemini não configurada.")

        # Mapeamento preventivo de modelos legados ou depreciados para novas contas
        MAPA_MIGRACAO = {
            "gemini-2.5-flash": "gemini-3.8-flash",
            "gemini-2.5-pro": "gemini-3.8-flash",
            "models/gemini-2.5-flash": "gemini-3.8-flash",
            "models/gemini-2.5-pro": "gemini-3.8-flash",
        }
        modelo_alvo = MAPA_MIGRACAO.get(modelo_solicitado, modelo_solicitado)

        # Ordem de tentativa com fallback automático caso um modelo retorne 404
        candidatos = [modelo_alvo]
        for f in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
            if f not in candidatos:
                candidatos.append(f)

        system_instruction = self.montar_system_prompt_engenharia(requisicao.contexto_engenharia)

        # 1. Tentar via google-genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            contents: List[Any] = []
            for msg in requisicao.historico:
                contents.append(f"{msg.role.upper()}: {msg.content}")
            contents.append(f"Pergunta do Usuário: {requisicao.pergunta}")

            prompt_completo = "\n\n".join(contents)
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=requisicao.temperatura,
                max_output_tokens=requisicao.max_tokens
            )

            response = None
            modelo_usado = modelo_alvo
            ultimo_erro = None
            for m in candidatos:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt_completo,
                        config=config
                    )
                    modelo_usado = m
                    break
                except Exception as ex_m:
                    ultimo_erro = ex_m
                    msg_erro = str(ex_m).lower()
                    if "404" in msg_erro or "not_found" in msg_erro or "no longer available" in msg_erro or "not supported" in msg_erro:
                        continue
                    else:
                        raise ex_m

            if response and response.text:
                texto = response.text
                latencia = int((time.time() - t0) * 1000)
                return RespostaAI(
                    texto=texto,
                    provedor_usado="gemini",
                    modelo_usado=modelo_usado,
                    status="sucesso",
                    normas_referenciadas=self._extrair_normas(texto),
                    formulas_aplicadas=self._extrair_formulas(texto),
                    latencia_ms=latencia,
                    tokens_estimados=len(texto.split()) * 2
                )
        except ImportError:
            pass  # SDK não instalado, usa fallback REST HTTP nativo abaixo

        # 2. Fallback REST Nativo via urllib (100% nativo)
        contents_payload = []
        for msg in requisicao.historico:
            role = "user" if msg.role == "user" else "model"
            contents_payload.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        contents_payload.append({
            "role": "user",
            "parts": [{"text": requisicao.pergunta}]
        })

        payload_dict = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": contents_payload,
            "generationConfig": {
                "temperature": requisicao.temperatura,
                "maxOutputTokens": requisicao.max_tokens
            }
        }

        data_bytes = json.dumps(payload_dict).encode("utf-8")
        texto = None
        modelo_usado_final = modelo_alvo
        ultimo_erro_rest = None

        for m in candidatos:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
            req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    cands = resp_json.get("candidates", [])
                    if cands:
                        part = cands[0].get("content", {}).get("parts", [{}])[0]
                        texto = part.get("text", "Sem texto na resposta.")
                    else:
                        texto = "Nenhuma resposta gerada pela API do Gemini."
                    modelo_usado_final = m
                    break
            except urllib.error.HTTPError as ex:
                err_body = ex.read().decode("utf-8", errors="ignore")
                ultimo_erro_rest = ex
                if ex.code in (404, 400) and ("not found" in err_body.lower() or "not supported" in err_body.lower()):
                    continue
                raise RuntimeError(f"Erro na API do Google Gemini (HTTP {ex.code}): {err_body}")
            except Exception as ex_gen:
                ultimo_erro_rest = ex_gen
                continue

        if texto is None:
            if ultimo_erro_rest:
                raise ultimo_erro_rest
            raise RuntimeError("Não foi possível obter resposta de nenhum modelo do Google Gemini.")

        latencia = int((time.time() - t0) * 1000)
        return RespostaAI(
            texto=texto,
            provedor_usado="gemini",
            modelo_usado=modelo_usado_final,
            status="sucesso",
            normas_referenciadas=self._extrair_normas(texto),
            formulas_aplicadas=self._extrair_formulas(texto),
            latencia_ms=latencia,
            tokens_estimados=len(texto.split()) * 2
        )
