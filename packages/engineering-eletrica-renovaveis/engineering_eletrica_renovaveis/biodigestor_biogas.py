"""
Módulo de Dimensionamento de Biodigestores Rurais e Produção de Biogás / Biometano
Dimensionamento Biomecânico para Fazendas de Suinocultura, Bovinocultura e Avicultura
Modelo Canadense / Tubular com Lona PEAD e Gasômetro Integrado
"""

import math
from typing import Dict, List, Any, Optional

# Parâmetros de Dejetos e Rendimento de Biogás por Espécie Animal
PARAMETROS_BIOMASSA_ANIMAL: Dict[str, Dict[str, Any]] = {
    "suinos_terminacao": {
        "nome": "Suínos (Fase de Terminação / Engorda)",
        "dejeto_fresco_kg_dia": 2.3,
        "proporcao_agua_lavagem": 1.5, # 1.5 L água por kg de dejeto
        "solidos_totais_st_pct": 8.0,
        "solidos_volateis_sv_pct": 80.0, # 80% do ST
        "biogas_por_animal_m3_dia": 0.075, # m³/animal.dia
        "teor_metano_ch4_pct": 65.0,
        "trh_recomendado_dias": 30
    },
    "bovinos_leite_confinados": {
        "nome": "Bovinos de Leite (Vacas em Lactação Confinadas)",
        "dejeto_fresco_kg_dia": 40.0,
        "proporcao_agua_lavagem": 1.0,
        "solidos_totais_st_pct": 12.0,
        "solidos_volateis_sv_pct": 82.0,
        "biogas_por_animal_m3_dia": 1.80, # m³/animal.dia
        "teor_metano_ch4_pct": 62.0,
        "trh_recomendado_dias": 35
    },
    "bovinos_corte_confinamento": {
        "nome": "Bovinos de Corte (Confinamento Intensivo)",
        "dejeto_fresco_kg_dia": 22.0,
        "proporcao_agua_lavagem": 0.8,
        "solidos_totais_st_pct": 14.0,
        "solidos_volateis_sv_pct": 85.0,
        "biogas_por_animal_m3_dia": 0.95,
        "teor_metano_ch4_pct": 60.0,
        "trh_recomendado_dias": 40
    },
    "aves_postura": {
        "nome": "Aves de Postura (Galinhas Poedeiras)",
        "dejeto_fresco_kg_dia": 0.12,
        "proporcao_agua_lavagem": 1.2,
        "solidos_totais_st_pct": 25.0,
        "solidos_volateis_sv_pct": 75.0,
        "biogas_por_animal_m3_dia": 0.015,
        "teor_metano_ch4_pct": 60.0,
        "trh_recomendado_dias": 45
    }
}


class DimensionadorBiodigestor:
    """Calcula o volume, dimensões e produção de gás do biodigestor rural."""

    @classmethod
    def dimensionar_biodigestor_fazenda(
        cls,
        tipo_criacao: str = "suinos_terminacao",
        quantidade_animais: int = 1000,
        modelo_biodigestor: str = "canadense_tubular_pead" # "canadense_tubular_pead" ou "indiano"
    ) -> Dict[str, Any]:
        """Dimensiona o biodigestor anaeróbio completo a partir do plantel de animais."""
        param = PARAMETROS_BIOMASSA_ANIMAL.get(tipo_criacao, PARAMETROS_BIOMASSA_ANIMAL["suinos_terminacao"])
        
        # 1. Vazão Diária de Dejetos e Afluente
        dejetos_dia_kg = quantidade_animais * param["dejeto_fresco_kg_dia"]
        agua_lavagem_l_dia = dejetos_dia_kg * param["proporcao_agua_lavagem"]
        vazao_afluente_m3_dia = round((dejetos_dia_kg + agua_lavagem_l_dia) / 1000.0, 2)
        
        # 2. Volume Útil da Câmara de Digestão Anaeróbia
        trh = param["trh_recomendado_dias"]
        volume_util_m3 = round(vazao_afluente_m3_dia * trh, 1)
        
        # 3. Produção Diária de Biogás e Metano
        producao_biogas_dia_m3 = round(quantidade_animais * param["biogas_por_animal_m3_dia"], 1)
        teor_ch4 = param["teor_metano_ch4_pct"]
        producao_metano_dia_m3 = round(producao_biogas_dia_m3 * (teor_ch4 / 100.0), 1)
        
        # Poder Calorífico Inferior (PCI): ~35.8 MJ/m³ para CH4 puro; Biogás proporcional
        pci_biogas_mj_m3 = round(35.8 * (teor_ch4 / 100.0), 2) # ~22 a 23 MJ/m³
        pci_biogas_kwh_m3 = round(pci_biogas_mj_m3 / 3.6, 2) # ~6.2 kWh/m³
        
        energia_termica_bruta_kwh_dia = round(producao_biogas_dia_m3 * pci_biogas_kwh_m3, 1)

        # 4. Dimensionamento Físico da Vala Trapezoidal (Modelo Canadense)
        # Profundidade útil típica h = 2.5 a 3.5m; Talude lateral 1:1
        h_util = 3.0
        # Relação comprimento/largura recomendada = 4:1 a 5:1 (Plug-flow)
        # V ≈ L * W * h_util (aproximação geométrica)
        largura_boca_m = round(math.sqrt(volume_util_m3 / (4.0 * h_util)), 1)
        largura_boca_m = max(5.0, largura_boca_m)
        comprimento_m = round(volume_util_m3 / (largura_boca_m * h_util), 1)
        
        # Volume do gasômetro flexível (capacidade de armazenamento para 12 a 16 horas de biogás)
        volume_gasometro_m3 = round(producao_biogas_dia_m3 * 0.65, 1)

        # 5. Produção de Biofertilizante Efluente
        biofertilizante_dia_m3 = round(vazao_afluente_m3_dia * 0.95, 2)
        biofertilizante_ano_m3 = round(biofertilizante_dia_m3 * 365.0, 1)

        # 6. Equipamentos de Tratamento e Segurança
        especificacoes_tratamento = {
            "geomembrana": "Geomembrana de PEAD 1,5 mm virgem com proteção UV e solda térmica de dupla pista com canal de teste",
            "gasometro_lona": f"Lona superior flexível para cúpula inflável de biogás ({volume_gasometro_m3} m³ de reserva sob pressão 15 mbar)",
            "filtro_dessulfurizador": f"Torre cilíndrica de ferro esponjoso/carvão ativado para remoção de H2S (vazão de pico {round(producao_biogas_dia_m3/8, 1)} m³/h)",
            "dreno_condensado": "Separador mecânico de condensado e purgador automático em PEAD instalado no ponto mais baixo da tubulação",
            "valvula_seguranca": "Válvula hidráulica de alívio e contrapressão tipo selo d'água regulada para 20 mbar",
            "queimador_flare": f"Queimador de segurança (Flare) com acendimento piezoelétrico automático para queima de excedentes ({round(producao_biogas_dia_m3/4, 1)} m³/h)"
        }

        return {
            "tipo_criacao": param["nome"],
            "plantel_animais": quantidade_animais,
            "modelo_construtivo": "Biodigestor Tubular Contínuo (Modelo Canadense em Geomembrana PEAD)",
            "balanco_hidraulico": {
                "dejetos_frescos_kg_dia": dejetos_dia_kg,
                "vazao_afluente_total_m3_dia": vazao_afluente_m3_dia,
                "tempo_retencao_trh_dias": trh,
                "volume_util_digestor_m3": volume_util_m3,
                "volume_gasometro_reserva_m3": volume_gasometro_m3
            },
            "dimensoes_cava_trapezoidal": {
                "largura_m": largura_boca_m,
                "comprimento_m": comprimento_m,
                "profundidade_util_m": h_util,
                "inclinacao_talude": "1:1 (45°)"
            },
            "potencial_energetico_biogas": {
                "producao_biogas_dia_m3": producao_biogas_dia_m3,
                "producao_biogas_mes_m3": round(producao_biogas_dia_m3 * 30.0, 1),
                "teor_metano_ch4_pct": teor_ch4,
                "producao_metano_dia_m3": producao_metano_dia_m3,
                "pci_biogas_kwh_m3": pci_biogas_kwh_m3,
                "energia_termica_bruta_kwh_dia": energia_termica_bruta_kwh_dia
            },
            "subprodutos": {
                "biofertilizante_m3_dia": biofertilizante_dia_m3,
                "biofertilizante_m3_ano": biofertilizante_ano_m3,
                "beneficio_agronomico": "Substituição de adubos químicos NPK para pastagens, milho e lavouras"
            },
            "equipamentos_tratamento": especificacoes_tratamento
        }
