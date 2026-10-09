"""
Módulo de Dimensionamento de Stringbox Solar CC e Proteções
Conforme ABNT NBR 16690:2019, IEC 60269-6 (gPV), IEC 61643-31 (DPS CC) e IEC 60947-3 (Seccionadoras CC)
Dimensiona Fusíveis gPV (+/-), Chave Seccionadora CC, DPS Classe II em Y e Cabos Solares.
"""

import math
from typing import Dict, List, Any, Optional

class DimensionadorStringboxCC:
    """Dimensiona e especifica a Stringbox de Corrente Contínua para arranjos fotovoltaicos."""

    @classmethod
    def dimensionar_stringbox(
        cls,
        potencia_modulo_w: float = 550.0,
        voc_stc_v: float = 49.80,
        isc_stc_a: float = 13.98,
        vmp_stc_v: float = 41.95,
        imp_stc_a: float = 13.12,
        coef_temp_voc_pct_c: float = -0.27,
        modulos_por_string_serie: int = 18,
        quantidade_strings_paralelo: int = 2,
        temp_minima_ambiente_c: float = 5.0,
        temp_maxima_operacao_c: float = 70.0
    ) -> Dict[str, Any]:
        """Calcula tensões, correntes críticas e especifica todos os componentes da Stringbox CC."""
        
        # 1. Tensão Máxima de Circuito Aberto com Temperatura Mínima (NBR 16690 item 5.1.2)
        delta_t_min = temp_minima_ambiente_c - 25.0
        fator_correcao_temp = 1.0 + (coef_temp_voc_pct_c / 100.0) * delta_t_min
        voc_max_modulo_v = voc_stc_v * fator_correcao_temp
        voc_max_arranjo_v = round(voc_max_modulo_v * modulos_por_string_serie, 1)
        
        # Tensão de operação em ponto de máxima potência
        vmp_arranjo_v = round(vmp_stc_v * modulos_por_string_serie, 1)
        
        # 2. Correntes de Projeto do Arranjo
        # Fator de irradiância extrema de 1.25x conforme NBR 16690
        isc_arranjo_a = round(isc_stc_a * quantidade_strings_paralelo, 2)
        isc_max_arranjo_a = round(isc_arranjo_a * 1.25, 2)
        imp_arranjo_a = round(imp_stc_a * quantidade_strings_paralelo, 2)
        
        # 3. Dimensionamento dos Fusíveis gPV
        # Fusíveis obrigatórios se houver 3 ou mais strings em paralelo
        fusiveis_obrigatorios = quantidade_strings_paralelo >= 3
        # In_fusivel >= 1.4 * Isc_stc
        in_fusivel_calc_a = 1.4 * isc_stc_a
        # Padronização de fusíveis gPV comerciais: 15A, 20A, 25A, 30A
        padroes_fusiveis = [15.0, 20.0, 25.0, 30.0]
        in_fusivel_a = next((f for f in padroes_fusiveis if f >= in_fusivel_calc_a), 25.0)
        
        tensao_nominal_fusivel_v = 1000.0 if voc_max_arranjo_v <= 1000.0 else 1500.0
        
        # 4. Dimensionamento da Chave Seccionadora CC
        # Ue >= Voc_max e Ie >= 1.25 * Isc_arranjo
        ie_min_seccionadora_a = isc_max_arranjo_a
        padroes_seccionadoras = [16.0, 25.0, 32.0, 40.0, 63.0, 100.0]
        ie_seccionadora_a = next((s for s in padroes_seccionadoras if s >= ie_min_seccionadora_a), 63.0)
        ue_seccionadora_v = 1000.0 if voc_max_arranjo_v <= 1000.0 else 1500.0
        
        # 5. Dimensionamento do DPS CC Classe II
        # Ucpv >= 1.2 * Voc_max
        ucpv_min_v = voc_max_arranjo_v * 1.20
        ucpv_dps_v = 1000.0 if ucpv_min_v <= 1000.0 else 1200.0
        
        # 6. Condutores Solares CC
        # Iz >= 1.25 * Isc_string
        iz_min_cabo_a = isc_stc_a * 1.25
        secao_cabo_solar_mm2 = 4.0 if iz_min_cabo_a <= 35.0 else 6.0
        secao_cabo_principal_mm2 = 6.0 if isc_max_arranjo_a <= 45.0 else 10.0
        
        return {
            "parametros_arranjo": {
                "potencia_pico_arranjo_kwp": round((potencia_modulo_w * modulos_por_string_serie * quantidade_strings_paralelo) / 1000.0, 2),
                "quantidade_strings": quantidade_strings_paralelo,
                "modulos_por_string": modulos_por_string_serie,
                "total_modulos": modulos_por_string_serie * quantidade_strings_paralelo,
                "voc_max_temperatura_minima_v": voc_max_arranjo_v,
                "vmp_nominal_v": vmp_arranjo_v,
                "isc_total_arranjo_a": isc_arranjo_a,
                "isc_max_projeto_a": isc_max_arranjo_a,
                "imp_nominal_arranjo_a": imp_arranjo_a
            },
            "fusiveis_gpv": {
                "obrigatorios_norma": fusiveis_obrigatorios,
                "in_nominal_a": in_fusivel_a,
                "tensao_nominal_v": tensao_nominal_fusivel_v,
                "tipo": "gPV Cilíndrico 10x38 mm Cerâmico",
                "quantidade_polos": quantidade_strings_paralelo * 2, # Polo Positivo (+) e Negativo (-)
                "justificativa": f"Protege contra correntes reversas entre strings paralelas (In = {in_fusivel_a}A >= 1.4 * {isc_stc_a:.1f}A)."
            },
            "chave_seccionadora_cc": {
                "corrente_nominal_ie_a": ie_seccionadora_a,
                "tensao_nominal_ue_v": ue_seccionadora_v,
                "categoria_emprego": "DC-PV2 / DC-21B (Abertura sob Carga em CC)",
                "numero_polos": 2, # Bipolar rotativa
                "manopla": "Rotativa Vermelha/Amarela com Bloqueio por Cadeado (LOTO)"
            },
            "dps_cc": {
                "classe": "Classe II (Proteção contra Surtos Atmosféricos Induzidos)",
                "tensao_max_continua_ucpv_v": ucpv_dps_v,
                "corrente_descarga_nominal_in_ka": 20.0,
                "corrente_descarga_maxima_imax_ka": 40.0,
                "configuracao_circuito": "Y (3 Varistores de Óxido de Zinco com Desconector Térmico)",
                "protecao_modos": ["Polo (+) ao PE", "Polo (-) ao PE", "Polo (+) ao Polo (-)"]
            },
            "cabos_e_conexoes": {
                "cabo_solar_strings": f"{secao_cabo_solar_mm2} mm² 1.8kVcc XLPE Anti-UV Sem Halogênio",
                "cabo_principal_inversor": f"{secao_cabo_principal_mm2} mm² 1.8kVcc",
                "condutor_protecao_pe": "16.0 mm² Cobre Nu / Verde-Amarelo até o BEP",
                "conectores": "MC4 Original IP68 com trava anti-desconexão"
            },
            "caixa_invólucro": {
                "grau_protecao": "IP65 resistente a intempéries e UV",
                "material": "Termoplástico Autoextinguível V0",
                "respiro": "Válvula de Alívio de Pressão e Membrana Anticondensação Gore"
            }
        }
