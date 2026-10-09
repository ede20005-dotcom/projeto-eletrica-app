"""
Módulo de Dimensionamento de Sistemas Solares Fotovoltaicos (On-Grid e Híbridos)
Conforme ABNT NBR 16690:2019, ABNT NBR 16274 e Marco Legal da GD (Lei 14.300/2022)
Suporta Modelos: Residencial, Predial (EMUC) e Fazenda / Agroindustrial
"""

import math
from typing import Dict, List, Any, Optional

# Catálogo de Módulos Fotovoltaicos Comerciais Homologados no INMETRO
CATALOGO_MODULOS_SOLARES: Dict[str, Dict[str, Any]] = {
    "modulo_550w_monocristalino": {
        "modelo": "Módulo Monocristalino Half-Cell 550W",
        "potencia_stc_w": 550,
        "vmp_v": 41.95,
        "imp_a": 13.12,
        "voc_v": 49.80,
        "isc_a": 13.98,
        "coef_temp_voc_pct_c": -0.27, # %/°C
        "eficiencia_pct": 21.3,
        "comprimento_m": 2.278,
        "largura_m": 1.134,
        "area_m2": 2.58,
        "peso_kg": 27.5
    },
    "modulo_650w_bifacial": {
        "modelo": "Módulo Bifacial N-Type TOPCon 650W",
        "potencia_stc_w": 650,
        "vmp_v": 45.40,
        "imp_a": 14.32,
        "voc_v": 55.10,
        "isc_a": 15.15,
        "coef_temp_voc_pct_c": -0.25,
        "eficiencia_pct": 22.8,
        "comprimento_m": 2.384,
        "largura_m": 1.303,
        "area_m2": 3.10,
        "peso_kg": 34.0
    }
}

# Catálogo de Inversores Grid-Tie / Híbridos Padronizados
CATALOGO_INVERSORES: Dict[str, Dict[str, Any]] = {
    "inv_residencial_5kw": {
        "modelo": "Inversor String Monofásico/Bifásico 5 kW",
        "potencia_nominal_ca_w": 5000,
        "potencia_max_pico_cc_w": 7500,
        "tensao_saida_ca_v": 220,
        "num_mppt": 2,
        "v_max_cc_v": 600,
        "faixa_mppt_v": [90, 520],
        "corrente_max_mppt_a": 15.0,
        "eficiencia_max_pct": 97.8
    },
    "inv_predial_30kw": {
        "modelo": "Inversor String Trifásico 30 kW (380V/220V)",
        "potencia_nominal_ca_w": 30000,
        "potencia_max_pico_cc_w": 45000,
        "tensao_saida_ca_v": 380,
        "num_mppt": 3,
        "v_max_cc_v": 1100,
        "faixa_mppt_v": [200, 1000],
        "corrente_max_mppt_a": 30.0,
        "eficiencia_max_pct": 98.5
    },
    "inv_agro_75kw": {
        "modelo": "Inversor Centralizado / Usina de Solo 75 kW (380V)",
        "potencia_nominal_ca_w": 75000,
        "potencia_max_pico_cc_w": 112500,
        "tensao_saida_ca_v": 380,
        "num_mppt": 6,
        "v_max_cc_v": 1100,
        "faixa_mppt_v": [200, 1000],
        "corrente_max_mppt_a": 30.0,
        "eficiencia_max_pct": 98.7
    }
}


class DimensionadorSolarFotovoltaico:
    """Calcula arranjos solares fotovoltaicos para diferentes portes conforme NBR 16690."""
    
    @classmethod
    def dimensionar_por_consumo(
        cls,
        consumo_mensal_kwh: float,
        irradiacao_hsp: float = 5.2, # Horas de Sol Pleno diárias médias no Brasil
        tipo_aplicacao: str = "residencial", # "residencial", "predial", "fazenda"
        tipo_instalacao: str = "telhado", # "telhado_ceramico", "telhado_metalico", "solo"
        temp_min_local_c: float = 10.0,
        temp_max_modulo_c: float = 65.0
    ) -> Dict[str, Any]:
        """Dimensiona a usina solar fotovoltaica para atender ao consumo alvo."""
        # 1. Performance Ratio (PR) médio considerando perdas térmicas, sujeira e cabos (NBR 16274)
        pr = 0.80 if tipo_aplicacao == "residencial" else (0.82 if tipo_aplicacao == "predial" else 0.83)
        
        # Potência de pico requerida em kWp: P_pico = E_mensal / (30 * HSP * PR)
        p_pico_requerida_kwp = consumo_mensal_kwh / (30.0 * irradiacao_hsp * pr)
        p_pico_requerida_w = p_pico_requerida_kwp * 1000.0
        
        # 2. Seleção de Módulo e Inversor conforme porte
        if tipo_aplicacao == "residencial":
            modulo_info = CATALOGO_MODULOS_SOLARES["modulo_550w_monocristalino"]
            inversor_info = CATALOGO_INVERSORES["inv_residencial_5kw"]
        elif tipo_aplicacao == "predial":
            modulo_info = CATALOGO_MODULOS_SOLARES["modulo_550w_monocristalino"]
            inversor_info = CATALOGO_INVERSORES["inv_predial_30kw"]
        else: # Fazenda
            modulo_info = CATALOGO_MODULOS_SOLARES["modulo_650w_bifacial"]
            inversor_info = CATALOGO_INVERSORES["inv_agro_75kw"]

        pot_mod = modulo_info["potencia_stc_w"]
        qtd_modulos = math.ceil(p_pico_requerida_w / pot_mod)
        p_pico_real_kwp = round((qtd_modulos * pot_mod) / 1000.0, 2)
        
        # 3. Verificação de Strings conforme NBR 16690
        # Tensão máxima de circuito aberto em dia mais frio (T_min)
        coef_temp = modulo_info["coef_temp_voc_pct_c"] / 100.0
        delta_t_frio = temp_min_local_c - 25.0
        voc_max_modulo = modulo_info["voc_v"] * (1.0 + coef_temp * delta_t_frio)
        
        # Tensão MPPT em dia mais quente
        delta_t_quente = temp_max_modulo_c - 25.0
        vmp_min_modulo = modulo_info["vmp_v"] * (1.0 + coef_temp * delta_t_quente)
        
        v_max_inv = inversor_info["v_max_cc_v"]
        mppt_min_inv = inversor_info["faixa_mppt_v"][0]
        mppt_max_inv = inversor_info["faixa_mppt_v"][1]
        
        # Quantidade máxima de módulos por string (não pode exceder V_max_inversor)
        max_mod_string = math.floor(v_max_inv / voc_max_modulo)
        # Quantidade mínima de módulos por string (para atingir tensão MPPT mínima)
        min_mod_string = math.ceil(mppt_min_inv / vmp_min_modulo)
        
        # Distribuir módulos entre os MPPTs
        num_mppts = inversor_info["num_mppt"]
        modulos_por_string = min(max_mod_string, max(min_mod_string, math.ceil(qtd_modulos / num_mppts)))
        qtd_strings = math.ceil(qtd_modulos / modulos_por_string)
        
        # 4. Área Ocupada e Peso Estrutural
        area_total_m2 = round(qtd_modulos * modulo_info["area_m2"], 1)
        peso_total_kg = round(qtd_modulos * modulo_info["peso_kg"], 1)
        
        # 5. Geração Estimada de Energia (Mensal e Anual)
        geracao_mensal_kwh = round(p_pico_real_kwp * irradiacao_hsp * 30.0 * pr, 1)
        geracao_anual_kwh = round(geracao_mensal_kwh * 12.0, 1)
        
        # 6. Proteções da String Box (NBR 16690)
        tensao_string_max_v = round(modulos_por_string * voc_max_modulo, 1)
        isc_string_a = modulo_info["isc_a"]
        # Fusível gPV NBR 16690: In_fusivel >= 1.4 * Isc
        corrente_fusivel_gpv = math.ceil(1.4 * isc_string_a)
        # DPS CC: Uc >= 1.2 * Voc_max
        dps_cc_uc_min = math.ceil(1.2 * tensao_string_max_v)

        return {
            "tipo_aplicacao": tipo_aplicacao,
            "potencia_pico_kwp": p_pico_real_kwp,
            "consumo_alvo_kwh_mes": consumo_mensal_kwh,
            "geracao_estimada_kwh_mes": geracao_mensal_kwh,
            "geracao_estimada_kwh_ano": geracao_anual_kwh,
            "cobertura_consumo_pct": round((geracao_mensal_kwh / consumo_mensal_kwh) * 100.0, 1),
            "modulos": {
                "modelo": modulo_info["modelo"],
                "quantidade_total": qtd_modulos,
                "potencia_unitaria_w": pot_mod,
                "area_total_m2": area_total_m2,
                "peso_total_kg": peso_total_kg,
                "arranjo_strings": f"{qtd_strings} strings com {modulos_por_string} módulos cada"
            },
            "inversor": {
                "modelo": inversor_info["modelo"],
                "potencia_ca_kw": inversor_info["potencia_nominal_ca_w"] / 1000.0,
                "tensao_ca_v": inversor_info["tensao_saida_ca_v"],
                "fdr_overload_pct": round((p_pico_real_kwp / (inversor_info["potencia_nominal_ca_w"] / 1000.0)) * 100.0, 1)
            },
            "protecoes_nbr16690": {
                "string_box_cc": f"String Box CC {qtd_strings} Entradas / {num_mppts} Saídas",
                "fusivel_gpv_a": f"{corrente_fusivel_gpv} A (1000V CC)",
                "chave_seccionadora_cc": f"Chave Seccionadora sob carga {math.ceil(qtd_strings * isc_string_a * 1.25)}A / {round(v_max_inv)}V CC",
                "dps_cc": f"DPS Classe II CC, Uc >= {dps_cc_uc_min}V CC, In 20kA, Imax 40kA",
                "cabo_solar_cc": "# 6.0 mm² Cobre Estanhado 1.8kV resistente a UV (Preto/Vermelho com conectores MC4)"
            },
            "estrutura_fixacao": {
                "tipo": tipo_instalacao,
                "inclinacao_graus": 18, # Tilt angle típico para o Brasil
                "orientacao": "Norte Geográfico (Azimute 0°)",
                "material": "Alumínio Estrutural 6063-T6 com fixadores em Aço Inox 304"
            }
        }
