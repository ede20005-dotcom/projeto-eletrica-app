# -*- coding: utf-8 -*-
"""
Gerenciador de Credenciais e Chaves de API para os Agentes de IA Elétrica.
Permite ler de variáveis de ambiente (.env) ou de arquivo local persistido com segurança.
"""

from __future__ import annotations
import os
import json
from typing import Dict, Optional, List

PROVEDOR_ENV_MAP = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "ollama": "OLLAMA_HOST"
}

def _get_candidate_credential_paths() -> List[str]:
    candidatos = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "config", "ai_credentials.json")),
        r"C:\projeto-engenharia-eletrica\config\ai_credentials.json",
        r"C:\projeto-engenharia-antigravity\config\ai_credentials.json",
        os.path.join(os.getcwd(), "config", "ai_credentials.json"),
    ]
    unicos = []
    for c in candidatos:
        if c not in unicos:
            unicos.append(c)
    return unicos

class AIKeyManager:
    """Gerencia leitura e persistência local de chaves de API dos provedores de IA."""

    @staticmethod
    def _ler_arquivo_local() -> Dict[str, str]:
        dados_totais: Dict[str, str] = {}
        for caminho in _get_candidate_credential_paths():
            if os.path.exists(caminho):
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        conteudo = json.load(f)
                        if isinstance(conteudo, dict):
                            for k, v in conteudo.items():
                                if k not in dados_totais and isinstance(v, str) and v.strip():
                                    dados_totais[k.lower()] = v.strip()
                except Exception:
                    pass
        return dados_totais

    @staticmethod
    def obter_chave(provedor: str, chave_override: Optional[str] = None) -> Optional[str]:
        """Obtém a chave de API para o provedor indicado."""
        provedor_key = provedor.lower()

        # 1. Se foi enviado override explícito com valor não vazio
        if chave_override and chave_override.strip():
            return chave_override.strip()

        # 2. Verificar Variáveis de Ambiente
        env_var = PROVEDOR_ENV_MAP.get(provedor_key)
        if env_var:
            val_env = os.environ.get(env_var, "").strip()
            if val_env:
                return val_env

        # 3. Ler de arquivo de configuração local
        chaves_locais = AIKeyManager._ler_arquivo_local()
        if provedor_key in chaves_locais:
            return chaves_locais[provedor_key]

        return None

    @staticmethod
    def salvar_chave(provedor: str, chave: str) -> bool:
        """Persiste uma chave localmente em config/ai_credentials.json."""
        if not chave or not chave.strip():
            return False

        caminho_alvo = r"C:\projeto-engenharia-eletrica\config\ai_credentials.json"
        try:
            os.makedirs(os.path.dirname(caminho_alvo), exist_ok=True)
            dados = {}
            if os.path.exists(caminho_alvo):
                try:
                    with open(caminho_alvo, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                except Exception:
                    dados = {}

            dados[provedor.lower()] = chave.strip()

            with open(caminho_alvo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)

            # Também injetar no os.environ para consumo imediato
            env_var = PROVEDOR_ENV_MAP.get(provedor.lower())
            if env_var:
                os.environ[env_var] = chave.strip()

            return True
        except Exception:
            return False

    @staticmethod
    def listar_status_chaves() -> Dict[str, bool]:
        """Retorna dicionário indicando se cada provedor possui chave configurada."""
        chaves_locais = AIKeyManager._ler_arquivo_local()
        status = {}
        for prov, env_var in PROVEDOR_ENV_MAP.items():
            tem_env = bool(os.environ.get(env_var, "").strip())
            tem_arq = bool(chaves_locais.get(prov, "").strip())
            status[prov] = tem_env or tem_arq

        status["offline"] = True
        return status
