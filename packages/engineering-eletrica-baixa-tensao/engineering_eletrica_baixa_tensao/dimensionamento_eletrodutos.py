"""
Módulo de Dimensionamento de Eletrodutos conforme ABNT NBR 5410:2004
Subitem 6.2.11.1 - Taxa de Ocupação Máxima de Eletrodutos
"""

import math
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "engineering-eletrica-core", "src")))
from tabelas_condutores import PARAMETROS_CABOS_COBRE_PVC, ELETRODUTOS_PVC

class DimensionadorEletrodutosNBR5410:
    """Calcula a taxa de ocupação e dimensiona o diâmetro nominal do eletroduto."""
    
    @staticmethod
    def obter_taxa_maxima_ocupacao(qtd_condutores: int) -> float:
        """
        NBR 5410:2004 - Subitem 6.2.11.1:
        - 1 condutor: 53% (0.53)
        - 2 condutores: 31% (0.31)
        - 3 ou mais condutores: 40% (0.40)
        """
        if qtd_condutores == 1:
            return 0.53
        elif qtd_condutores == 2:
            return 0.31
        else:
            return 0.40

    @classmethod
    def dimensionar_trecho(
        cls,
        condutores: List[Dict[str, Any]], # [{"secao_mm2": 2.5, "qtd": 3, "tipo": "fase+neutro+pe"}]
        dn_minimo_adotado: int = 20 # Prática de engenharia: mínimo DN 20 (3/4") para embutido
    ) -> Dict[str, Any]:
        """
        Dimensiona o eletroduto para um conjunto de condutores no trecho.
        Retorna detalhes de área ocupada, diâmetro selecionado e folga percentual.
        """
        area_total_cabos = 0.0
        total_condutores = 0
        
        for c in condutores:
            secao = c.get("secao_mm2", 2.5)
            qtd = c.get("qtd", 1)
            total_condutores += qtd
            param = PARAMETROS_CABOS_COBRE_PVC.get(secao, {"area_externa_mm2": 10.18})
            area_cabo = param["area_externa_mm2"]
            area_total_cabos += area_cabo * qtd

        taxa_max = cls.obter_taxa_maxima_ocupacao(total_condutores)
        
        # Procura o menor eletroduto comercial que atenda
        eletroduto_escolhido = None
        for eletro in ELETRODUTOS_PVC:
            if eletro["dn_mm"] < dn_minimo_adotado:
                continue
            # Área interna total do eletroduto
            di = eletro["di_interno_mm"]
            area_interna_total = (math.pi * (di ** 2)) / 4.0
            area_maxima_permitida = area_interna_total * taxa_max
            
            if area_total_cabos <= area_maxima_permitida:
                taxa_ocupacao_real = (area_total_cabos / area_interna_total) * 100.0
                eletroduto_escolhido = {
                    "dn_mm": eletro["dn_mm"],
                    "polegadas": eletro["pol"],
                    "di_interno_mm": di,
                    "area_interna_mm2": round(area_interna_total, 1),
                    "area_total_cabos_mm2": round(area_total_cabos, 1),
                    "taxa_maxima_norma_pct": round(taxa_max * 100.0, 1),
                    "taxa_ocupacao_real_pct": round(taxa_ocupacao_real, 1),
                    "total_condutores": total_condutores,
                    "status": "CONFORME (NBR 5410)"
                }
                break

        if eletroduto_escolhido is None:
            # Caso extremo com muitos cabos -> pega o maior diâmetro disponível
            maior = ELETRODUTOS_PVC[-1]
            di = maior["di_interno_mm"]
            area_interna_total = (math.pi * (di ** 2)) / 4.0
            eletroduto_escolhido = {
                "dn_mm": maior["dn_mm"],
                "polegadas": maior["pol"],
                "di_interno_mm": di,
                "area_interna_mm2": round(area_interna_total, 1),
                "area_total_cabos_mm2": round(area_total_cabos, 1),
                "taxa_maxima_norma_pct": round(taxa_max * 100.0, 1),
                "taxa_ocupacao_real_pct": round((area_total_cabos / area_interna_total) * 100.0, 1),
                "total_condutores": total_condutores,
                "status": "ATENÇÃO (Sugerir subdivisão de eletroduto)"
            }

        return eletroduto_escolhido
