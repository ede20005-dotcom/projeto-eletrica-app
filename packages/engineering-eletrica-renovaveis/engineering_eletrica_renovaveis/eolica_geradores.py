"""
Módulo de Dimensionamento de Aerogeradores de Pequeno e Médio Porte (Micro e Minieólica)
Conforme ABNT NBR IEC 61400-2 e Marco Legal da GD (Lei 14.300/2022)
Suporta Modelos: Residencial Urbano (VAWT - Eixo Vertical) e Fazenda / Agro (HAWT - Eixo Horizontal)
"""

import math
from typing import Dict, List, Any, Optional

CATALOGO_AEROGERADORES: Dict[str, Dict[str, Any]] = {
    "vawt_urbano_2kw": {
        "modelo": "Aerogerador Vertical Helicoidal VAWT 2.0 kW",
        "tipo": "vertical_darrieus",
        "potencia_nominal_w": 2000,
        "tensao_saida_ca_v": 220,
        "altura_rotor_m": 2.4,
        "diametro_rotor_m": 1.6,
        "area_varredura_m2": 3.84, # H * D
        "velocidade_partida_ms": 1.8, # Cut-in
        "velocidade_nominal_ms": 10.5,
        "velocidade_corte_ms": 20.0, # Cut-out
        "velocidade_sobrevivencia_ms": 50.0,
        "coef_potencia_cp": 0.32,
        "ruido_db": 34, # Ultra silencioso para uso residencial
        "tipo_gerador": "PMSG Ímãs Permanentes Trifásico",
        "torre_recomendada_m": 8.0,
        "peso_turbina_kg": 95.0
    },
    "hawt_rural_20kw": {
        "modelo": "Aerogerador Horizontal Tripá HAWT 20.0 kW",
        "tipo": "horizontal_hawt",
        "potencia_nominal_w": 20000,
        "tensao_saida_ca_v": 380,
        "diametro_rotor_m": 10.2,
        "area_varredura_m2": 81.71, # pi * R^2
        "velocidade_partida_ms": 2.5,
        "velocidade_nominal_ms": 11.0,
        "velocidade_corte_ms": 25.0,
        "velocidade_sobrevivencia_ms": 60.0,
        "coef_potencia_cp": 0.42,
        "ruido_db": 48,
        "tipo_gerador": "PMSG Direct-Drive sem engrenagens",
        "torre_recomendada_m": 24.0, # Torre de aço estaiada
        "peso_turbina_kg": 850.0
    }
}


class DimensionadorEolico:
    """Calcula a energia gerada e especifica aerogeradores para residências, prédios e fazendas."""

    @classmethod
    def dimensionar_aerogerador(
        cls,
        velocidade_media_vento_ms: float = 6.0, # m/s na altura do cubo
        tipo_aplicacao: str = "fazenda", # "residencial", "predial", "fazenda"
        densidade_ar_kg_m3: float = 1.225
    ) -> Dict[str, Any]:
        """Calcula o aproveitamento da energia do vento e detalhes de montagem."""
        if tipo_aplicacao in ["residencial", "predial"]:
            dados = CATALOGO_AEROGERADORES["vawt_urbano_2kw"]
            altura_torre = dados["torre_recomendada_m"]
        else:
            dados = CATALOGO_AEROGERADORES["hawt_rural_20kw"]
            altura_torre = dados["torre_recomendada_m"]

        pot_nom_w = dados["potencia_nominal_w"]
        area_varredura = dados["area_varredura_m2"]
        cp = dados["coef_potencia_cp"]
        v_in = dados["velocidade_partida_ms"]
        v_nom = dados["velocidade_nominal_ms"]
        v_out = dados["velocidade_corte_ms"]

        # Fator de capacidade (CF) baseado na distribuição de Rayleigh para a velocidade média
        # Relação típica para v_media / v_nominal
        razao_v = velocidade_media_vento_ms / v_nom
        if razao_v < 0.2:
            cf = 0.05
        elif razao_v <= 0.6:
            cf = 0.08 + 0.35 * (razao_v - 0.2)
        else:
            cf = min(0.48, 0.22 + 0.30 * (razao_v - 0.6))

        potencia_media_gerada_w = pot_nom_w * cf
        geracao_diaria_kwh = (potencia_media_gerada_w * 24.0) / 1000.0
        geracao_mensal_kwh = round(geracao_diaria_kwh * 30.0, 1)
        geracao_anual_kwh = round(geracao_mensal_kwh * 12.0, 1)

        # Especificação da fundação e ancoragem mecânica
        if dados["tipo"] == "vertical_darrieus":
            fundacao_info = "Base em laje técnica com chumbadores químicos M16 ou sapata isolada de concreto 1,20x1,20x0,60m"
            sistema_frenagem = "Freio eletromagnético por curto-circuito nos enrolamentos e dump load"
        else:
            fundacao_info = "Bloco central de concreto armado 2,50x2,50x1,20m com 4 âncoras estaiadas a 120° com raio de 14m"
            sistema_frenagem = "Freio a disco hidráulico de segurança + controle aerodinâmico por bandeiramento passivo + dump load 25kW"

        return {
            "tipo_aplicacao": tipo_aplicacao,
            "modelo_aerogerador": dados["modelo"],
            "tipo_rotor": dados["tipo"],
            "potencia_nominal_kw": pot_nom_w / 1000.0,
            "velocidade_vento_considerada_ms": velocidade_media_vento_ms,
            "fator_capacidade_estimado_pct": round(cf * 100.0, 1),
            "geracao_mensal_kwh": geracao_mensal_kwh,
            "geracao_anual_kwh": geracao_anual_kwh,
            "especificacoes_mecanicas": {
                "altura_torre_m": altura_torre,
                "area_varredura_m2": area_varredura,
                "peso_conjunto_kg": dados["peso_turbina_kg"],
                "nivel_ruido_db": dados["ruido_db"],
                "fundacao": fundacao_info,
                "sistema_frenagem": sistema_frenagem
            },
            "interface_eletrica": {
                "gerador": dados["tipo_gerador"],
                "tensao_saida_v": dados["tensao_saida_ca_v"],
                "quadro_comando": "Controlador de Carga Híbrido MPPT com retificador CA/CC e Resistência de Dissipação (Dump Load)",
                "inversor_interligacao": "Inversor de Injeção na Rede homologado ANEEL com proteção anti-ilhamento (NBR 16149)"
            }
        }
