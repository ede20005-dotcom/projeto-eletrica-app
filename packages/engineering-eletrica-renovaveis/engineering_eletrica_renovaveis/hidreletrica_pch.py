"""
Módulo de Dimensionamento de Micro-Hidrelétricas (CGH / PCH Rural)
Conforme Diretrizes da ANEEL (Resolução Normativa nº 1.000/2021), ABNT NBR 5410 e Marco GD Lei 14.300/2022
Dimensiona Vazão, Queda Líquida, Conduto Forçado, Turbinas Pelton/Francis/Banki e Geradores Rurais.
"""

import math
from typing import Dict, List, Any, Optional

CATALOGO_TURBINAS_HIDRAULICAS: Dict[str, Dict[str, Any]] = {
    "pelton_alta_queda": {
        "tipo": "Pelton (Ação / Impulso)",
        "faixa_queda_m": [25.0, 200.0],
        "vazao_max_l_s": 150.0,
        "rendimento_nominal_pct": 86.0,
        "descricao": "Roda de conchas duplas bipartidas com injetor de agulha e defletor de jato de segurança."
    },
    "francis_media_queda": {
        "tipo": "Francis Espiral (Reação Centrípeta)",
        "faixa_queda_m": [12.0, 45.0],
        "vazao_max_l_s": 400.0,
        "rendimento_nominal_pct": 88.0,
        "descricao": "Caixa espiral metálica com pás diretrizes ajustáveis e tubo de sucção cônico."
    },
    "michell_banki_fluxo_cruzado": {
        "tipo": "Michell-Banki / Cross-Flow (Fluxo Cruzado)",
        "faixa_queda_m": [3.0, 25.0],
        "vazao_max_l_s": 600.0,
        "rendimento_nominal_pct": 82.0,
        "descricao": "Rotor cilíndrico aberto com fluxo radial duplo. Robusta e autolimpante para cursos d'água rurais com sedimentos."
    }
}

class DimensionadorHidreletricoPCH:
    """Dimensionador completo de Centrais Geradoras Hidrelétricas (CGH / PCH)."""

    @classmethod
    def dimensionar_micro_hidreletrica(
        cls,
        vazao_disponivel_l_s: float = 80.0,
        queda_bruta_m: float = 28.0,
        comprimento_conduto_m: float = 120.0,
        material_conduto: str = "pead_pn10", # "pead_pn10" ou "aco_soldado"
        fator_capacidade_pct: float = 85.0
    ) -> Dict[str, Any]:
        """
        Executa os cálculos hidráulicos, dimensionamento do conduto forçado,
        seleção da turbina e balanço de geração elétrica contínua.
        """
        q_m3_s = vazao_disponivel_l_s / 1000.0
        
        # 1. Diâmetro Econômico do Conduto Forçado (Fórmula de Bresse: D = 1.5 * sqrt(Q))
        d_economico_m = 1.5 * math.sqrt(q_m3_s)
        
        # Padronização comercial (DN em milímetros)
        if d_economico_m <= 0.160:
            dn_mm = 160
        elif d_economico_m <= 0.200:
            dn_mm = 200
        elif d_economico_m <= 0.250:
            dn_mm = 250
        elif d_economico_m <= 0.315:
            dn_mm = 315
        elif d_economico_m <= 0.400:
            dn_mm = 400
        else:
            dn_mm = 500
            
        d_int_m = (dn_mm * 0.90) / 1000.0 # Diâmetro interno aproximado descontando espessura da parede
        area_tubo = (math.pi * (d_int_m ** 2)) / 4.0
        vel_agua_m_s = q_m3_s / area_tubo
        
        # 2. Perda de Carga no Conduto (Hazen-Williams)
        # C = 140 para PEAD / PVC, C = 130 para Aço
        c_hw = 140.0 if "pead" in material_conduto.lower() else 130.0
        perda_carga_distribuida_m = 10.67 * (comprimento_conduto_m * (q_m3_s ** 1.852)) / ((c_hw ** 1.852) * (d_int_m ** 4.87))
        # Perdas localizadas (curvas, grades, válvulas ≈ 15% da distribuída)
        perda_carga_total_m = perda_carga_distribuida_m * 1.15
        
        # 3. Queda Líquida Efetiva
        queda_liquida_m = max(1.0, queda_bruta_m - perda_carga_total_m)
        
        # 4. Seleção da Turbina Ótima
        if queda_liquida_m >= 25.0:
            chave_turbina = "pelton_alta_queda"
        elif queda_liquida_m >= 12.0:
            chave_turbina = "francis_media_queda"
        else:
            chave_turbina = "michell_banki_fluxo_cruzado"
            
        spec_turbina = CATALOGO_TURBINAS_HIDRAULICAS[chave_turbina]
        rend_turbina = spec_turbina["rendimento_nominal_pct"] / 100.0
        rend_gerador = 0.92 # Gerador síncrono trifásico brushless 380V/220V
        rend_transmissao_painel = 0.96
        rend_global = rend_turbina * rend_gerador * rend_transmissao_painel
        
        # 5. Potência Elétrica Útil Gerada (kW)
        # P = rho * g * Q * Hl * eta = 9.81 * Q * Hl * eta
        potencia_eletrica_kw = 9.81 * q_m3_s * queda_liquida_m * rend_global
        potencia_eletrica_kw = round(potencia_eletrica_kw, 2)
        
        # 6. Geração de Energia (24 horas contínuas de operação)
        horas_mes = 720.0
        fc = fator_capacidade_pct / 100.0
        geracao_mensal_kwh = round(potencia_eletrica_kw * horas_mes * fc, 1)
        geracao_anual_kwh = round(geracao_mensal_kwh * 12.0, 1)
        
        # 7. Pressão Máxima e Golpe de Aríete (Joukowsky)
        # Celeridade de onda em PEAD a ≈ 350 m/s
        celeridade_a_m_s = 350.0 if "pead" in material_conduto.lower() else 1000.0
        sobrepressao_golpe_mca = round((celeridade_a_m_s * vel_agua_m_s) / 9.81 * 0.35, 1) # com fechamento amortecido
        pressao_estatica_mca = round(queda_bruta_m, 1)
        pressao_maxima_total_mca = round(pressao_estatica_mca + sobrepressao_golpe_mca, 1)

        return {
            "vazao_projeto_l_s": vazao_disponivel_l_s,
            "vazao_projeto_m3_s": round(q_m3_s, 4),
            "queda_bruta_m": queda_bruta_m,
            "queda_liquida_efetiva_m": round(queda_liquida_m, 2),
            "perda_carga_total_m": round(perda_carga_total_m, 2),
            "conduto_forcado": {
                "comprimento_m": comprimento_conduto_m,
                "material": material_conduto.upper(),
                "dn_comercial_mm": dn_mm,
                "diametro_interno_mm": round(d_int_m * 1000, 1),
                "velocidade_escoamento_m_s": round(vel_agua_m_s, 2),
                "pressao_estatica_bar": round(pressao_estatica_mca / 10.0, 2),
                "sobrepressao_golpe_ariete_bar": round(sobrepressao_golpe_mca / 10.0, 2),
                "classe_pressao_recomendada": f"PN {max(10, int(math.ceil(pressao_maxima_total_mca / 10.0) + 2))}"
            },
            "turbina_selecionada": {
                "modelo": spec_turbina["tipo"],
                "rendimento_pct": spec_turbina["rendimento_nominal_pct"],
                "descricao": spec_turbina["descricao"]
            },
            "gerador_eletrico": {
                "tipo": "Gerador Síncrono Trifásico Brushless 4 Polos",
                "tensao_nominal_v": "380V / 220V",
                "frequencia_hz": 60,
                "rotacao_sincrona_rpm": 1800,
                "rendimento_pct": round(rend_gerador * 100.0, 1),
                "regulacao": "Regulador Eletrônico de Carga ELC e Excitação AVR"
            },
            "potencia_eletrica_util_kw": potencia_eletrica_kw,
            "geracao_mensal_kwh": geracao_mensal_kwh,
            "geracao_anual_kwh": geracao_anual_kwh,
            "fator_capacidade_pct": fator_capacidade_pct,
            "rendimento_global_instalacao_pct": round(rend_global * 100.0, 1)
        }
