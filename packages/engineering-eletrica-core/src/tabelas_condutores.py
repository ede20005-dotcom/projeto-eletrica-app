"""
Tabelas e Parâmetros Normativos ABNT NBR 5410:2004 para Condutores e Eletrodutos
"""

from typing import Dict, List, Tuple, Any

# Seções padronizadas de cabos de cobre (mm²)
SECOES_PADRAO_COBRE: List[float] = [1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0, 70.0, 95.0, 120.0, 150.0, 185.0, 240.0]

# Seções mínimas de condutores de cobre conforme Tabela 47 da NBR 5410
SECOES_MINIMAS_NBR5410: Dict[str, float] = {
    "iluminacao": 1.5,
    "tomadas_forca": 2.5,
    "sinalizacao_controle": 0.5
}

# Tabela 36 - NBR 5410: Capacidade de condução de corrente (A) para condutores de COBRE com isolação PVC (70°C), temp. referência 30°C
# Formato: secao_mm2: {"B1_2c": A, "B1_3c": A, "B2_2c": A, "B2_3c": A, "C_2c": A, "C_3c": A}
# B1: Condutores isolados em eletroduto de seção circular embutido em alvenaria (padrão residencial mais comum)
# B2: Cabos unipolares em eletroduto aparente
# C: Cabos unipolares ou multipolares sobre parede ou perfilado
CAPACIDADE_CORRENTE_PVC_COBRE: Dict[float, Dict[str, float]] = {
    1.5:  {"B1_2c": 17.5, "B1_3c": 15.5, "B2_2c": 16.5, "B2_3c": 15.0, "C_2c": 19.5, "C_3c": 17.5},
    2.5:  {"B1_2c": 24.0, "B1_3c": 21.0, "B2_2c": 23.0, "B2_3c": 20.0, "C_2c": 27.0, "C_3c": 24.0},
    4.0:  {"B1_2c": 32.0, "B1_3c": 28.0, "B2_2c": 30.0, "B2_3c": 27.0, "C_2c": 36.0, "C_3c": 32.0},
    6.0:  {"B1_2c": 41.0, "B1_3c": 36.0, "B2_2c": 38.0, "B2_3c": 34.0, "C_2c": 46.0, "C_3c": 41.0},
    10.0: {"B1_2c": 57.0, "B1_3c": 50.0, "B2_2c": 52.0, "B2_3c": 46.0, "C_2c": 63.0, "C_3c": 57.0},
    16.0: {"B1_2c": 76.0, "B1_3c": 68.0, "B2_2c": 69.0, "B2_3c": 62.0, "C_2c": 85.0, "C_3c": 76.0},
    25.0: {"B1_2c": 101.0, "B1_3c": 89.0, "B2_2c": 90.0, "B2_3c": 80.0, "C_2c": 112.0, "C_3c": 96.0},
    35.0: {"B1_2c": 125.0, "B1_3c": 110.0, "B2_2c": 111.0, "B2_3c": 99.0, "C_2c": 138.0, "C_3c": 119.0},
    50.0: {"B1_2c": 151.0, "B1_3c": 134.0, "B2_2c": 133.0, "B2_3c": 118.0, "C_2c": 168.0, "C_3c": 144.0},
    70.0: {"B1_2c": 192.0, "B1_3c": 171.0, "B2_2c": 168.0, "B2_3c": 149.0, "C_2c": 213.0, "C_3c": 184.0},
    95.0: {"B1_2c": 232.0, "B1_3c": 207.0, "B2_2c": 201.0, "B2_3c": 179.0, "C_2c": 258.0, "C_3c": 223.0},
    120.0: {"B1_2c": 269.0, "B1_3c": 239.0, "B2_2c": 232.0, "B2_3c": 206.0, "C_2c": 299.0, "C_3c": 259.0},
}

# Tabela 40 - Fatores de correção para temperaturas ambientes diferentes de 30°C (ar)
FATOR_CORRECAO_TEMP_PVC: Dict[int, float] = {
    10: 1.22,
    15: 1.17,
    20: 1.12,
    25: 1.06,
    30: 1.00,
    35: 0.94,
    40: 0.87,
    45: 0.79,
    50: 0.71,
    55: 0.61,
    60: 0.50
}

# Tabela 42 - Fatores de correção para agrupamento de circuitos em feixe ou no mesmo eletroduto
# Número de circuitos agrupados -> fator de agrupamento
FATOR_AGRUPAMENTO_NBR5410: Dict[int, float] = {
    1: 1.00,
    2: 0.80,
    3: 0.70,
    4: 0.65,
    5: 0.60,
    6: 0.57,
    7: 0.54,
    8: 0.52,
    9: 0.50,
    10: 0.48,
    12: 0.45,
    14: 0.43,
    16: 0.41,
    18: 0.39,
    20: 0.38
}

# Tabela 58 - Seção mínima do condutor de proteção (PE) em função da seção do condutor de fase S (mm²)
def obter_secao_pe_minima(secao_fase: float) -> float:
    """
    NBR 5410 - Tabela 58:
    S <= 16 mm²       -> S_pe = S
    16 < S <= 35 mm²  -> S_pe = 16 mm²
    S > 35 mm²        -> S_pe = S / 2
    """
    if secao_fase <= 16.0:
        return secao_fase
    elif secao_fase <= 35.0:
        return 16.0
    else:
        # Aredonda para a seção padrão mais próxima superior ou igual a S/2
        metade = secao_fase / 2.0
        for s in SECOES_PADRAO_COBRE:
            if s >= metade:
                return s
        return metade

# Tabela 48 - Seção do condutor neutro
def obter_secao_neutro_minima(secao_fase: float, trifasico_equilibrado: bool = True, harmonicas_significativas: bool = False) -> float:
    """
    NBR 5410 - Tabela 48:
    Em circuitos monofásicos e bifásicos sem neutro, o neutro é igual à fase.
    Em circuitos trifásicos equilibrados:
    S <= 25 mm²       -> S_neutro = S
    S = 35 mm²        -> S_neutro = 25 mm²
    S = 50 mm²        -> S_neutro = 25 mm²
    S = 70 mm²        -> S_neutro = 35 mm²
    S = 95 mm²        -> S_neutro = 50 mm²
    S = 120 mm²       -> S_neutro = 70 mm²
    Se houver alta taxa de 3ª harmônica (cargas eletrônicas / TI): neutro >= fase ou até 1.45*fase.
    """
    if harmonicas_significativas:
        return secao_fase
    if not trifasico_equilibrado or secao_fase <= 25.0:
        return secao_fase
    elif secao_fase == 35.0:
        return 25.0
    elif secao_fase == 50.0:
        return 25.0
    elif secao_fase == 70.0:
        return 35.0
    elif secao_fase == 95.0:
        return 50.0
    elif secao_fase >= 120.0:
        return 70.0
    return secao_fase

# Parâmetros elétricos dos condutores de cobre isolados em PVC 70°C a 75°C (Resistência R em ohm/km e Reatância X em ohm/km)
PARAMETROS_CABOS_COBRE_PVC: Dict[float, Dict[str, float]] = {
    1.5:  {"R_ohm_km": 14.80, "X_ohm_km": 0.118, "diam_externo_medio_mm": 3.0,  "area_externa_mm2": 7.07},
    2.5:  {"R_ohm_km": 8.91,  "X_ohm_km": 0.112, "diam_externo_medio_mm": 3.6,  "area_externa_mm2": 10.18},
    4.0:  {"R_ohm_km": 5.54,  "X_ohm_km": 0.107, "diam_externo_medio_mm": 4.2,  "area_externa_mm2": 13.85},
    6.0:  {"R_ohm_km": 3.69,  "X_ohm_km": 0.101, "diam_externo_medio_mm": 4.8,  "area_externa_mm2": 18.10},
    10.0: {"R_ohm_km": 2.21,  "X_ohm_km": 0.095, "diam_externo_medio_mm": 6.1,  "area_externa_mm2": 29.22},
    16.0: {"R_ohm_km": 1.40,  "X_ohm_km": 0.090, "diam_externo_medio_mm": 7.2,  "area_externa_mm2": 40.72},
    25.0: {"R_ohm_km": 0.89,  "X_ohm_km": 0.086, "diam_externo_medio_mm": 9.0,  "area_externa_mm2": 63.62},
    35.0: {"R_ohm_km": 0.63,  "X_ohm_km": 0.084, "diam_externo_medio_mm": 10.4, "area_externa_mm2": 84.95},
    50.0: {"R_ohm_km": 0.46,  "X_ohm_km": 0.082, "diam_externo_medio_mm": 12.3, "area_externa_mm2": 118.82},
    70.0: {"R_ohm_km": 0.32,  "X_ohm_km": 0.080, "diam_externo_medio_mm": 14.3, "area_externa_mm2": 160.61},
    95.0: {"R_ohm_km": 0.23,  "X_ohm_km": 0.078, "diam_externo_medio_mm": 16.7, "area_externa_mm2": 219.04},
    120.0:{"R_ohm_km": 0.18,  "X_ohm_km": 0.076, "diam_externo_medio_mm": 18.6, "area_externa_mm2": 271.72}
}

# Diâmetros comerciais de eletrodutos de PVC rígido / corrugado (DN nominal em mm e polegadas, e diâmetro interno útil)
ELETRODUTOS_PVC: List[Dict[str, Any]] = [
    {"dn_mm": 16, "pol": '1/2"',  "di_interno_mm": 13.0, "area_util_40_mm2": 53.09},
    {"dn_mm": 20, "pol": '3/4"',  "di_interno_mm": 16.6, "area_util_40_mm2": 86.59},
    {"dn_mm": 25, "pol": '1"',    "di_interno_mm": 21.4, "area_util_40_mm2": 143.87},
    {"dn_mm": 32, "pol": '1.1/4"',"di_interno_mm": 27.8, "area_util_40_mm2": 242.79},
    {"dn_mm": 40, "pol": '1.1/2"',"di_interno_mm": 35.2, "area_util_40_mm2": 389.28},
    {"dn_mm": 50, "pol": '2"',    "di_interno_mm": 44.4, "area_util_40_mm2": 619.32},
    {"dn_mm": 60, "pol": '2.1/2"',"di_interno_mm": 54.0, "area_util_40_mm2": 916.09},
    {"dn_mm": 75, "pol": '3"',    "di_interno_mm": 67.8, "area_util_40_mm2": 1444.18},
    {"dn_mm": 85, "pol": '3.1/2"',"di_interno_mm": 78.0, "area_util_40_mm2": 1911.35},
    {"dn_mm": 110,"pol": '4"',    "di_interno_mm": 100.2,"area_util_40_mm2": 3154.16}
]

# Disjuntores termomagnéticos padrão DIN (Correntes nominais padronizadas In em Amperes)
DISJUNTORES_DIN_PADRAO: List[int] = [6, 10, 16, 20, 25, 32, 40, 50, 63, 70, 80, 100, 125]
