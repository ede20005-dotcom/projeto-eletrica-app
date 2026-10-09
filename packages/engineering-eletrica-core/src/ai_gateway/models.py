# -*- coding: utf-8 -*-
"""
Modelos de dados para o Gateway Unificado de IA - Antigravity Engenharia Elétrica.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class MensagemChat:
    role: str  # "user", "assistant", "system"
    content: str

@dataclass
class RequisicaoAI:
    pergunta: str
    provedor: str = "offline"
    modelo: Optional[str] = None
    contexto_engenharia: Dict[str, Any] = field(default_factory=dict)
    historico: List[MensagemChat] = field(default_factory=list)
    temperatura: float = 0.2
    max_tokens: int = 2048
    api_key_override: Optional[str] = None

@dataclass
class RespostaAI:
    texto: str
    provedor_usado: str
    modelo_usado: str
    status: str = "sucesso"
    normas_referenciadas: List[str] = field(default_factory=list)
    formulas_aplicadas: List[str] = field(default_factory=list)
    recomendacoes: List[str] = field(default_factory=list)
    raciocinio_cot: Optional[str] = None
    latencia_ms: int = 0
    tokens_estimados: int = 0
    confianca_rag: float = 1.00
    aviso: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "texto": self.texto,
            "provedor_usado": self.provedor_usado,
            "modelo_usado": self.modelo_usado,
            "status": self.status,
            "normas_referenciadas": self.normas_referenciadas,
            "formulas_aplicadas": self.formulas_aplicadas,
            "recomendacoes": self.recomendacoes,
            "raciocinio_cot": self.raciocinio_cot,
            "latencia_ms": self.latencia_ms,
            "tokens_estimados": self.tokens_estimados,
            "confianca_rag": self.confianca_rag,
            "aviso": self.aviso
        }

@dataclass
class InfoModelo:
    id: str
    nome: str
    descricao: str
    contexto_max: str
    recomendado_para: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "contexto_max": self.contexto_max,
            "recomendado_para": self.recomendado_para
        }

@dataclass
class InfoProvedor:
    id: str
    nome: str
    icone: str
    empresa: str
    chave_configurada: bool
    env_var: str
    modelos: List[InfoModelo]
    suporta_visao: bool = False
    suporta_raciocinio_cot: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "icone": self.icone,
            "empresa": self.empresa,
            "chave_configurada": self.chave_configurada,
            "env_var": self.env_var,
            "suporta_visao": self.suporta_visao,
            "suporta_raciocinio_cot": self.suporta_raciocinio_cot,
            "modelos": [m.to_dict() for m in self.modelos]
        }
