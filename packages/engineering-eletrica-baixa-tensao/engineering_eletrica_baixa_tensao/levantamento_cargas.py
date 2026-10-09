"""
Módulo de Levantamento de Cargas Residenciais e Prediais conforme ABNT NBR 5410:2004
Subitem 9.5.2 - Previsão de cargas de iluminação e tomadas (TUG e TUE)
"""

import math
from typing import Dict, List, Any, Optional

# Catálogo de Cargas Típicas de TUE (Tomadas de Uso Específico)
CATALOGO_TUE_RESIDENCIAL: Dict[str, Dict[str, Any]] = {
    "chuveiro_eletrico_5500": {
        "nome": "Chuveiro Elétrico 5500W",
        "potencia_w": 5500,
        "potencia_va": 5500,
        "fp": 1.0,
        "tensao_v": 220,
        "comodo_sugerido": "banheiro",
        "categoria": "aquecimento"
    },
    "chuveiro_eletrico_7500": {
        "nome": "Chuveiro Elétrico Turbo 7500W",
        "potencia_w": 7500,
        "potencia_va": 7500,
        "fp": 1.0,
        "tensao_v": 220,
        "comodo_sugerido": "banheiro",
        "categoria": "aquecimento"
    },
    "torneira_eletrica_4500": {
        "nome": "Torneira Elétrica 4500W",
        "potencia_w": 4500,
        "potencia_va": 4500,
        "fp": 1.0,
        "tensao_v": 220,
        "comodo_sugerido": "copa_cozinha",
        "categoria": "aquecimento"
    },
    "ar_condicionado_9000_btu": {
        "nome": "Ar Condicionado Inverter 9000 BTU/h (1100W)",
        "potencia_w": 1100,
        "potencia_va": 1294,
        "fp": 0.85,
        "tensao_v": 220,
        "comodo_sugerido": "quarto",
        "categoria": "climatizacao"
    },
    "ar_condicionado_12000_btu": {
        "nome": "Ar Condicionado Inverter 12000 BTU/h (1450W)",
        "potencia_w": 1450,
        "potencia_va": 1705,
        "fp": 0.85,
        "tensao_v": 220,
        "comodo_sugerido": "quarto",
        "categoria": "climatizacao"
    },
    "ar_condicionado_18000_btu": {
        "nome": "Ar Condicionado Inverter 18000 BTU/h (2100W)",
        "potencia_w": 2100,
        "potencia_va": 2470,
        "fp": 0.85,
        "tensao_v": 220,
        "comodo_sugerido": "sala",
        "categoria": "climatizacao"
    },
    "forno_eletrico_2500": {
        "nome": "Forno Elétrico de Embutir 2500W",
        "potencia_w": 2500,
        "potencia_va": 2500,
        "fp": 1.0,
        "tensao_v": 220,
        "comodo_sugerido": "copa_cozinha",
        "categoria": "eletrodomestico"
    },
    "cooktop_inducao_7000": {
        "nome": "Cooktop por Indução 4 Bocas 7000W",
        "potencia_w": 7000,
        "potencia_va": 7368,
        "fp": 0.95,
        "tensao_v": 220,
        "comodo_sugerido": "copa_cozinha",
        "categoria": "eletrodomestico"
    },
    "microondas_1500": {
        "nome": "Forno Micro-ondas 1500W",
        "potencia_w": 1500,
        "potencia_va": 1765,
        "fp": 0.85,
        "tensao_v": 127,
        "comodo_sugerido": "copa_cozinha",
        "categoria": "eletrodomestico"
    },
    "lava_loucas_1800": {
        "nome": "Máquina Lava-Louças 1800W",
        "potencia_w": 1800,
        "potencia_va": 1895,
        "fp": 0.95,
        "tensao_v": 220,
        "comodo_sugerido": "copa_cozinha",
        "categoria": "lavanderia"
    },
    "lava_e_seca_2000": {
        "nome": "Lavadora e Secadora de Roupas 2000W",
        "potencia_w": 2000,
        "potencia_va": 2222,
        "fp": 0.90,
        "tensao_v": 127,
        "comodo_sugerido": "area_servico",
        "categoria": "lavanderia"
    },
    "bomba_recalque_1cv": {
        "nome": "Motobomba de Recalque 1 CV (750W)",
        "potencia_w": 750,
        "potencia_va": 937,
        "fp": 0.80,
        "tensao_v": 220,
        "comodo_sugerido": "garagem",
        "categoria": "motor"
    }
}

class ComodoResidencial:
    """Representa um compartimento residencial com suas dimensões e cálculo normativo de cargas."""
    def __init__(self, id_comodo: str, nome: str, tipo: str, largura: float, comprimento: float, pe_direito: float = 2.8):
        self.id = id_comodo
        self.nome = nome
        self.tipo = tipo.lower()  # sala, quarto, suite, copa_cozinha, area_servico, banheiro, lavabo, varanda, garagem, circulacao
        self.largura = float(largura)
        self.comprimento = float(comprimento)
        self.pe_direito = float(pe_direito)
        self.area = round(self.largura * self.comprimento, 2)
        self.perimetro = round(2 * (self.largura + self.comprimento), 2)
        
        # Cargas calculadas
        self.iluminacao_min_va = 0
        self.qtd_pontos_iluminacao = 1
        self.tug_min_qtd = 0
        self.tug_pontos: List[Dict[str, Any]] = [] # [{pot_va, tipo_posicao}]
        self.tue_cargas: List[Dict[str, Any]] = []
        
        self._calcular_cargas_normativas()
        
    def _calcular_cargas_normativas(self):
        """Aplica os critérios do subitem 9.5.2 da NBR 5410:2004"""
        # 1. Iluminação (Subitem 9.5.2.1)
        if self.area <= 6.0:
            self.iluminacao_min_va = 100
            self.qtd_pontos_iluminacao = 1
        else:
            # 100 VA para os primeiros 6 m² + 60 VA para cada aumento de 4 m² inteiros
            area_excedente = self.area - 6.0
            fracoes_4m2 = math.floor(area_excedente / 4.0)
            self.iluminacao_min_va = int(100 + fracoes_4m2 * 60)
            # Para áreas muito grandes (> 18 m²), sugerir 2 ou mais pontos
            if self.area > 24.0:
                self.qtd_pontos_iluminacao = 3
            elif self.area > 14.0:
                self.qtd_pontos_iluminacao = 2
            else:
                self.qtd_pontos_iluminacao = 1

        # 2. Tomadas de Uso Geral - TUG (Subitem 9.5.2.2)
        self.tug_pontos = []
        if self.tipo in ["copa_cozinha", "cozinha", "copa", "area_servico", "lavanderia"]:
            # 1 tomada para cada 3.5m de perímetro ou fração
            qtd = max(2, math.ceil(self.perimetro / 3.5))
            self.tug_min_qtd = qtd
            # Potências: primeiras 3 tomadas com 600 VA cada, excedentes com 100 VA cada
            for i in range(qtd):
                pot = 600 if i < 3 else 100
                posicao = "media" if i < 3 else "baixa"
                self.tug_pontos.append({"id": f"TUG_{self.id}_{i+1}", "potencia_va": pot, "posicao": posicao, "uso": "Bancada/Geral"})
                
        elif self.tipo in ["banheiro", "lavabo"]:
            # No mínimo 1 tomada junto ao lavatório de 600 VA (média / 1.20m)
            self.tug_min_qtd = 1
            self.tug_pontos.append({"id": f"TUG_{self.id}_1", "potencia_va": 600, "posicao": "media", "uso": "Lavatorio"})
            if self.area >= 6.0:
                self.tug_min_qtd += 1
                self.tug_pontos.append({"id": f"TUG_{self.id}_2", "potencia_va": 100, "posicao": "baixa", "uso": "Geral"})
                
        elif self.tipo in ["sala", "quarto", "suite", "dormitorio", "escritorio"]:
            # 1 tomada para cada 5.0m de perímetro ou fração, espaçadas uniformemente
            # Se área for menor ou igual a 6m², no mínimo 1 ponto
            if self.area <= 6.0:
                qtd = 1
            else:
                qtd = max(1, math.ceil(self.perimetro / 5.0))
            self.tug_min_qtd = qtd
            for i in range(qtd):
                self.tug_pontos.append({"id": f"TUG_{self.id}_{i+1}", "potencia_va": 100, "posicao": "baixa", "uso": "Geral"})
                
        elif self.tipo in ["varanda", "sacada"]:
            # No mínimo 1 tomada de 100 VA
            self.tug_min_qtd = 1
            self.tug_pontos.append({"id": f"TUG_{self.id}_1", "potencia_va": 100, "posicao": "media", "uso": "Varanda"})
            
        elif self.tipo in ["garagem", "estacionamento"]:
            self.tug_min_qtd = max(1, math.ceil(self.perimetro / 10.0))
            for i in range(self.tug_min_qtd):
                self.tug_pontos.append({"id": f"TUG_{self.id}_{i+1}", "potencia_va": 100, "posicao": "baixa", "uso": "Garagem"})
                
        else: # Circulação, hall, corredor
            if self.area >= 6.0 or self.perimetro >= 10.0:
                self.tug_min_qtd = 1
                self.tug_pontos.append({"id": f"TUG_{self.id}_1", "potencia_va": 100, "posicao": "baixa", "uso": "Circulacao"})
            else:
                self.tug_min_qtd = 0

    def adicionar_tue(self, chave_catalogo: str, tensao_v: Optional[int] = None, potencia_w: Optional[float] = None):
        """Adiciona uma carga de TUE ao cômodo"""
        if chave_catalogo in CATALOGO_TUE_RESIDENCIAL:
            item = CATALOGO_TUE_RESIDENCIAL[chave_catalogo].copy()
            if tensao_v is not None:
                item["tensao_v"] = tensao_v
            if potencia_w is not None:
                item["potencia_w"] = potencia_w
                item["potencia_va"] = round(potencia_w / item["fp"], 1)
            item["id"] = f"TUE_{self.id}_{len(self.tue_cargas)+1}"
            self.tue_cargas.append(item)
            return item
        else:
            item_custom = {
                "id": f"TUE_{self.id}_{len(self.tue_cargas)+1}",
                "nome": chave_catalogo,
                "potencia_w": potencia_w or 2000,
                "potencia_va": round((potencia_w or 2000) / 0.9, 1),
                "fp": 0.9,
                "tensao_v": tensao_v or 220,
                "comodo_sugerido": self.tipo,
                "categoria": "especial"
            }
            self.tue_cargas.append(item_custom)
            return item_custom

    def obter_potencia_total_va(self) -> float:
        total = self.iluminacao_min_va
        for t in self.tug_pontos:
            total += t["potencia_va"]
        for tue in self.tue_cargas:
            total += tue["potencia_va"]
        return float(total)

    def obter_potencia_total_w(self) -> float:
        # Iluminação e TUG com fp médio da NBR 5410: fp=1.0 para ilum residencial LED e TUG fp=1.0 ou 0.8
        w_ilum = self.iluminacao_min_va * 1.0
        w_tug = sum(t["potencia_va"] * 0.8 for t in self.tug_pontos) # convenção NBR 5410 (TUG cos phi = 0.8 ou 1.0)
        w_tue = sum(t["potencia_w"] for t in self.tue_cargas)
        return float(round(w_ilum + w_tug + w_tue, 1))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "largura": self.largura,
            "comprimento": self.comprimento,
            "pe_direito": self.pe_direito,
            "area_m2": self.area,
            "perimetro_m": self.perimetro,
            "iluminacao": {
                "potencia_va": self.iluminacao_min_va,
                "qtd_pontos": self.qtd_pontos_iluminacao
            },
            "tug": {
                "qtd": len(self.tug_pontos),
                "pontos": self.tug_pontos,
                "potencia_total_va": sum(t["potencia_va"] for t in self.tug_pontos)
            },
            "tue": self.tue_cargas,
            "potencia_total_va": self.obter_potencia_total_va(),
            "potencia_total_w": self.obter_potencia_total_w()
        }
