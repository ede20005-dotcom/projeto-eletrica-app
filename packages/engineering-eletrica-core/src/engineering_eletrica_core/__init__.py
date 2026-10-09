"""Pacote Core de Engenharia Elétrica"""
from .normas_referencia import NORMAS_ELETRICA_BRASIL
from .tabelas_condutores import (
    SECOES_PADRAO_COBRE,
    SECOES_MINIMAS_NBR5410,
    CAPACIDADE_CORRENTE_PVC_COBRE,
    FATOR_CORRECAO_TEMP_PVC,
    FATOR_AGRUPAMENTO_NBR5410,
    PARAMETROS_CABOS_COBRE_PVC,
    ELETRODUTOS_PVC,
    DISJUNTORES_DIN_PADRAO,
    obter_secao_pe_minima,
    obter_secao_neutro_minima
)
