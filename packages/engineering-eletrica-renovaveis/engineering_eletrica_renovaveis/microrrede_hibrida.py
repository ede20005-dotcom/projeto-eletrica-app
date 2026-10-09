"""
Módulo de Integração de Microrredes Híbridas Multivetoriais
Integra Solar Fotovoltaico + Eólica + Biogás/CHP + Micro-Hidrelétrica (PCH) + Armazenamento BESS
Aplicações: Residencial, Predial (EMUC) e Fazendas Agroindustriais Autossuficientes
"""

from typing import Dict, List, Any, Optional
from .solar_fotovoltaico import DimensionadorSolarFotovoltaico
from .eolica_geradores import DimensionadorEolico
from .biodigestor_biogas import DimensionadorBiodigestor
from .motogerador_chp import DimensionadorTermeletricaBiogas
from .hidreletrica_pch import DimensionadorHidreletricoPCH

class MicrorredeHibridaIntegrada:
    """Orquestra a integração de múltiplas fontes renováveis com a rede da concessionária."""

    @classmethod
    def simular_cenario(
        cls,
        perfil: str = "fazenda", # "residencial", "predial", "fazenda"
        consumo_mensal_kwh: float = 8500.0,
        incluir_solar: bool = True,
        incluir_eolica: bool = True,
        incluir_biogas: bool = True,
        incluir_hidraulica: bool = True,
        plantel_animais: int = 1000,
        tipo_criacao: str = "suinos_terminacao",
        tarifa_energia_r_kwh: float = 0.85
    ) -> Dict[str, Any]:
        """Calcula o balanço de geração, autossuficiência e retorno econômico."""
        resultados_fontes = {}
        geracao_total_mensal_kwh = 0.0

        # 1. Solar Fotovoltaico
        if incluir_solar:
            consumo_solar = consumo_mensal_kwh * (0.5 if (incluir_biogas or incluir_hidraulica) else 1.0)
            res_solar = DimensionadorSolarFotovoltaico.dimensionar_por_consumo(
                consumo_mensal_kwh=consumo_solar,
                tipo_aplicacao=perfil
            )
            resultados_fontes["solar"] = res_solar
            geracao_total_mensal_kwh += res_solar["geracao_estimada_kwh_mes"]

        # 2. Eólica
        if incluir_eolica:
            res_eolica = DimensionadorEolico.dimensionar_aerogerador(
                velocidade_media_vento_ms=6.2,
                tipo_aplicacao=perfil
            )
            resultados_fontes["eolica"] = res_eolica
            geracao_total_mensal_kwh += res_eolica["geracao_mensal_kwh"]

        # 3. Biodigestor e Motogerador Biogás (Especialmente para Fazendas)
        if incluir_biogas and perfil == "fazenda":
            res_biodig = DimensionadorBiodigestor.dimensionar_biodigestor_fazenda(
                tipo_criacao=tipo_criacao,
                quantidade_animais=plantel_animais
            )
            producao_gas = res_biodig["potencial_energetico_biogas"]["producao_biogas_dia_m3"]
            res_termo = DimensionadorTermeletricaBiogas.dimensionar_gerador_por_biogas(
                producao_biogas_dia_m3=producao_gas,
                teor_metano_ch4_pct=res_biodig["potencial_energetico_biogas"]["teor_metano_ch4_pct"]
            )
            resultados_fontes["biodigestor"] = res_biodig
            resultados_fontes["termeletrica_biogas"] = res_termo
            geracao_total_mensal_kwh += res_termo["balanco_energetico_eletrico"]["geracao_eletrica_mensal_kwh"]

        # 4. Micro-Hidrelétrica PCH (Para Fazendas / Cursos d'água rurais)
        if incluir_hidraulica and perfil == "fazenda":
            res_pch = DimensionadorHidreletricoPCH.dimensionar_micro_hidreletrica(
                vazao_disponivel_l_s=65.0,
                queda_bruta_m=24.0,
                comprimento_conduto_m=95.0,
                material_conduto="pead_pn10",
                fator_capacidade_pct=85.0
            )
            resultados_fontes["hidreletrica"] = res_pch
            geracao_total_mensal_kwh += res_pch["geracao_mensal_kwh"]

        # 5. Balanço Energético e Autossuficiência
        balanco_liquido_mensal_kwh = round(geracao_total_mensal_kwh - consumo_mensal_kwh, 1)
        taxa_autossuficiencia_pct = round((geracao_total_mensal_kwh / consumo_mensal_kwh) * 100.0, 1)

        # 6. Aspectos Financeiros e Sustentabilidade
        economia_mensal_reais = round(min(consumo_mensal_kwh, geracao_total_mensal_kwh) * tarifa_energia_r_kwh, 2)
        creditos_excedentes_reais = round(max(0.0, balanco_liquido_mensal_kwh) * tarifa_energia_r_kwh * 0.7, 2)
        economia_anual_reais = round((economia_mensal_reais + creditos_excedentes_reais) * 12.0, 2)

        # Fator de emissão médio do SIN ≈ 0.08 kg CO2/kWh
        co2_evitado_ano_ton = round((geracao_total_mensal_kwh * 12.0 * 0.08) / 1000.0, 2)
        if "biodigestor" in resultados_fontes:
            metano_dia_m3 = resultados_fontes["biodigestor"]["potencial_energetico_biogas"]["producao_metano_dia_m3"]
            ch4_evitado_ton = round((metano_dia_m3 * 365.0 * 0.717 * 28.0) / 1000.0, 2)
            co2_evitado_ano_ton += ch4_evitado_ton

        return {
            "perfil_microrrede": perfil.upper(),
            "consumo_mensal_referencia_kwh": consumo_mensal_kwh,
            "geracao_total_mensal_kwh": round(geracao_total_mensal_kwh, 1),
            "geracao_total_anual_kwh": round(geracao_total_mensal_kwh * 12.0, 1),
            "balanco_liquido_mensal_kwh": balanco_liquido_mensal_kwh,
            "taxa_autossuficiencia_pct": taxa_autossuficiencia_pct,
            "status_operacional": "SUPERAVITÁRIO (Exportação de Energia)" if balanco_liquido_mensal_kwh >= 0 else "COMPLEMENTAR COM REDE",
            "economia_financeira": {
                "tarifa_referencia_r_kwh": tarifa_energia_r_kwh,
                "economia_mensal_estimada_r": economia_mensal_reais,
                "creditos_excedentes_mensais_r": creditos_excedentes_reais,
                "economia_anual_projetada_r": economia_anual_reais
            },
            "impacto_ambiental_esg": {
                "co2_equivalente_evitado_ano_ton": co2_evitado_ano_ton,
                "equivalente_arvores_plantadas": int(co2_evitado_ano_ton * 7.2)
            },
            "fontes_integradas": resultados_fontes
        }
