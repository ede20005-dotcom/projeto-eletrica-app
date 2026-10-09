"""
Módulo de Dimensionamento de Motogeradores a Biogás e Sistemas de Cogeração Térmica (CHP)
Converte o biogás do biodigestor em Energia Elétrica (kW) e Calor Residual Útil (CHP)
Conforme ANEEL (Cogeração Qualificada), NBR 5410 e Marco Legal da GD (Lei 14.300/2022)
"""

import math
from typing import Dict, List, Any, Optional

CATALOGO_MOTOGERADORES_BIOGAS: Dict[str, Dict[str, Any]] = {
    "gerador_biogas_15kw": {
        "modelo": "Grupo Motogerador a Biogás Ciclo Otto 15 kW (18,75 kVA)",
        "potencia_eletrica_kw": 15.0,
        "potencia_termica_chp_kw": 24.0,
        "consumo_biogas_m3_h": 2.8, # biogás com 65% CH4 a 100% de carga
        "tensao_v": 380,
        "frequencia_hz": 60,
        "rendimento_eletrico_pct": 32.0,
        "rendimento_termico_chp_pct": 48.0,
        "rpm": 1800,
        "vazao_agua_arrefecimento_m3_h": 1.8,
        "temp_agua_saida_c": 85.0
    },
    "gerador_biogas_35kw": {
        "modelo": "Grupo Motogerador a Biogás Ciclo Otto 35 kW (43,75 kVA)",
        "potencia_eletrica_kw": 35.0,
        "potencia_termica_chp_kw": 52.0,
        "consumo_biogas_m3_h": 6.2,
        "tensao_v": 380,
        "frequencia_hz": 60,
        "rendimento_eletrico_pct": 33.5,
        "rendimento_termico_chp_pct": 49.0,
        "rpm": 1800,
        "vazao_agua_arrefecimento_m3_h": 3.6,
        "temp_agua_saida_c": 88.0
    },
    "gerador_biogas_75kw": {
        "modelo": "Grupo Motogerador a Biogás Heavy-Duty 75 kW (93,75 kVA)",
        "potencia_eletrica_kw": 75.0,
        "potencia_termica_chp_kw": 105.0,
        "consumo_biogas_m3_h": 13.0,
        "tensao_v": 380,
        "frequencia_hz": 60,
        "rendimento_eletrico_pct": 35.0,
        "rendimento_termico_chp_pct": 50.0,
        "rpm": 1800,
        "vazao_agua_arrefecimento_m3_h": 7.5,
        "temp_agua_saida_c": 90.0
    }
}


class DimensionadorTermeletricaBiogas:
    """Calcula a geração elétrica, consumo e cogeração térmica a partir do biogás disponível."""

    @classmethod
    def dimensionar_gerador_por_biogas(
        cls,
        producao_biogas_dia_m3: float,
        teor_metano_ch4_pct: float = 65.0,
        regime_operacao: str = "continuo_24h", # "continuo_24h" ou "ponta_5h"
        horas_operacao_dia: Optional[float] = None
    ) -> Dict[str, Any]:
        """Dimensiona a potência do grupo motogerador e o potencial de calor recuperado (CHP)."""
        if regime_operacao == "continuo_24h":
            horas_dia = 24.0
        elif regime_operacao == "ponta_5h":
            horas_dia = 5.0 # Operação durante o horário de ponta da concessionária
        else:
            horas_dia = horas_operacao_dia or 12.0

        vazao_disponivel_m3_h = producao_biogas_dia_m3 / horas_dia
        
        # Seleciona o motogerador que melhor se ajusta à vazão
        if vazao_disponivel_m3_h <= 4.0:
            dados = CATALOGO_MOTOGERADORES_BIOGAS["gerador_biogas_15kw"]
        elif vazao_disponivel_m3_h <= 9.0:
            dados = CATALOGO_MOTOGERADORES_BIOGAS["gerador_biogas_35kw"]
        else:
            dados = CATALOGO_MOTOGERADORES_BIOGAS["gerador_biogas_75kw"]

        pot_elec_kw = dados["potencia_eletrica_kw"]
        pot_term_kw = dados["potencia_termica_chp_kw"]
        rend_eletrico = dados["rendimento_eletrico_pct"] / 100.0
        rend_termico = dados["rendimento_termico_chp_pct"] / 100.0
        
        # Energia Elétrica Gerada
        # PCI do biogás em kWh/m³
        pci_kwh_m3 = (35.8 * (teor_metano_ch4_pct / 100.0)) / 3.6
        energia_eletrica_dia_kwh = round(producao_biogas_dia_m3 * pci_kwh_m3 * rend_eletrico, 1)
        energia_eletrica_mes_kwh = round(energia_eletrica_dia_kwh * 30.0, 1)
        
        # Energia Térmica Recuperável (Cogeração CHP)
        energia_termica_dia_kwh = round(producao_biogas_dia_m3 * pci_kwh_m3 * rend_termico, 1)
        energia_termica_mcal_dia = round(energia_termica_dia_kwh * 860.0, 1) # 1 kWh = 860 kcal

        # Economia em Equivalente GLP (Gás de Cozinha) ou Lenha
        glp_equivalente_kg_dia = round(energia_termica_dia_kwh / 12.5, 1) # PCI GLP ≈ 12.5 kWh/kg

        return {
            "regime_operacao": regime_operacao,
            "horas_operacao_diarias": horas_dia,
            "modelo_motogerador": dados["modelo"],
            "potencia_nominal_eletrica_kw": pot_elec_kw,
            "potencia_nominal_termica_kw": pot_term_kw,
            "balanco_energetico_eletrico": {
                "geracao_eletrica_diaria_kwh": energia_eletrica_dia_kwh,
                "geracao_eletrica_mensal_kwh": energia_eletrica_mes_kwh,
                "consumo_especifico_biogas_m3_kwh": round(dados["consumo_biogas_m3_h"] / pot_elec_kw, 2),
                "tensao_gerada_v": dados["tensao_v"],
                "fator_potencia": 0.8
            },
            "cogeracao_termica_chp": {
                "calor_recuperado_diario_kwh": energia_termica_dia_kwh,
                "calor_recuperado_diario_mcal": energia_termica_mcal_dia,
                "equivalente_glp_kg_dia": glp_equivalente_kg_dia,
                "temperatura_agua_chp_c": dados["temp_agua_saida_c"],
                "aplicacoes_agroindustriais": [
                    "Aquecimento das câmaras do biodigestor a 37°C no inverno para manter a produção bacteriana",
                    "Secadores mecânicos de grãos (café, milho, soja) substituindo fornalhas a lenha",
                    "Aquecimento de berçários de leitões ou galpões de frangos de corte",
                    "Água quente para higienização e esterilização de salas de ordenha mecânica"
                ]
            },
            "protecoes_e_sincronismo": {
                "modulo_comando": "Controlador Microprocessado para Paralelismo e Divisão de Carga (Deep Sea / ComAp)",
                "protecoes_ansi": ["27 (Subtensão)", "59 (Sobretensão)", "81U/81O (Sub/Sobrefrequência)", "32 (Potência Reversa)", "50/51 (Sobrecorrente)"],
                "interligacao": "Chave de paralelismo motorizada com a rede da concessionária (Grid-Tie) ou QTA para modo ilha"
            }
        }
