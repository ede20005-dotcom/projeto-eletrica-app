"""
Módulo de Cálculo de Demanda Total e Dimensionamento do Padrão de Entrada
Normas das Concessionárias Brasileiras (CEMIG ND-5.1, CPFL GED-13, ENEL) e NBR 5410:2004
"""

import math
from typing import Dict, List, Any, Tuple
from .levantamento_cargas import ComodoResidencial
from .divisao_circuitos import CircuitoTerminal

class CalculadorDemandaInstalacao:
    """Calcula a potência instalada, demanda diversificada provável e dimensiona o ramal de entrada."""

    @staticmethod
    def obter_fator_demanda_ilum_tug(potencia_w: float) -> float:
        """Tabela de fatores de demanda para iluminação e TUG residencial."""
        if potencia_w <= 1000:
            return 0.86
        elif potencia_w <= 2000:
            return 0.75
        elif potencia_w <= 3000:
            return 0.66
        elif potencia_w <= 4000:
            return 0.59
        elif potencia_w <= 5000:
            return 0.52
        elif potencia_w <= 6000:
            return 0.45
        elif potencia_w <= 7000:
            return 0.40
        elif potencia_w <= 8000:
            return 0.35
        elif potencia_w <= 9000:
            return 0.31
        elif potencia_w <= 10000:
            return 0.27
        else:
            return 0.24

    @staticmethod
    def obter_fator_demanda_aquecimento(qtd_aparelhos: int) -> float:
        """Fator de demanda para chuveiros e torneiras elétricas."""
        tabela = {1: 1.00, 2: 0.75, 3: 0.70, 4: 0.66, 5: 0.62, 6: 0.59}
        if qtd_aparelhos <= 0:
            return 0.0
        return tabela.get(qtd_aparelhos, 0.55)

    @staticmethod
    def obter_fator_demanda_ar(qtd_aparelhos: int) -> float:
        """Fator de demanda para aparelhos de ar condicionado."""
        tabela = {1: 1.00, 2: 1.00, 3: 0.86, 4: 0.80, 5: 0.75, 6: 0.70}
        if qtd_aparelhos <= 0:
            return 0.0
        return tabela.get(qtd_aparelhos, 0.65)

    @classmethod
    def calcular_demanda(
        cls,
        comodos: List[ComodoResidencial],
        tensao_fn: int = 127,
        tensao_ff: int = 220
    ) -> Dict[str, Any]:
        """Calcula as potências instaladas e demandas por categoria de carga."""
        # 1. Totalização de cargas nominais
        pot_ilum_va = sum(c.iluminacao_min_va for c in comodos)
        pot_ilum_w = pot_ilum_va * 1.0
        
        pot_tug_va = sum(sum(t["potencia_va"] for t in c.tug_pontos) for c in comodos)
        pot_tug_w = pot_tug_va * 0.8
        
        # Categorizar TUEs
        tues_aquecimento = []
        tues_ar = []
        tues_outros = []
        
        for c in comodos:
            for tue in c.tue_cargas:
                cat = tue.get("categoria", "")
                if cat == "aquecimento":
                    tues_aquecimento.append(tue)
                elif cat == "climatizacao":
                    tues_ar.append(tue)
                else:
                    tues_outros.append(tue)

        pot_aquec_w = sum(t["potencia_w"] for t in tues_aquecimento)
        pot_ar_w = sum(t["potencia_w"] for t in tues_ar)
        pot_outros_w = sum(t["potencia_w"] for t in tues_outros)
        
        pot_total_instalada_w = pot_ilum_w + pot_tug_w + pot_aquec_w + pot_ar_w + pot_outros_w
        pot_total_instalada_va = pot_ilum_va + pot_tug_va + sum(t["potencia_va"] for t in tues_aquecimento + tues_ar + tues_outros)

        # 2. Fatores de Demanda
        fd_ilum_tug = cls.obter_fator_demanda_ilum_tug(pot_ilum_w + pot_tug_w)
        demanda_ilum_tug_w = (pot_ilum_w + pot_tug_w) * fd_ilum_tug
        
        fd_aquec = cls.obter_fator_demanda_aquecimento(len(tues_aquecimento))
        demanda_aquec_w = pot_aquec_w * fd_aquec
        
        fd_ar = cls.obter_fator_demanda_ar(len(tues_ar))
        demanda_ar_w = pot_ar_w * fd_ar
        
        # Outros TUEs com fator 0.75
        fd_outros = 0.75 if tues_outros else 0.0
        demanda_outros_w = pot_outros_w * fd_outros

        # Demanda total calculada (kW e kVA)
        demanda_total_w = demanda_ilum_tug_w + demanda_aquec_w + demanda_ar_w + demanda_outros_w
        fp_medio_geral = 0.92
        demanda_total_va = demanda_total_w / fp_medio_geral

        # 3. Determinação do Tipo de Fornecimento da Concessionária
        pot_inst_kw = pot_total_instalada_w / 1000.0
        demanda_kva = demanda_total_va / 1000.0
        
        if pot_inst_kw <= 12.0 and demanda_kva <= 10.0:
            tipo_fornecimento = "Monofásico a 2 fios (F+N)"
            tipo_rede = "monofasico"
            corrente_entrada = demanda_total_va / tensao_fn
            disjuntor_sugerido = 50 if corrente_entrada <= 40 else 63
            secao_cabo_entrada = 10.0 if disjuntor_sugerido <= 50 else 16.0
        elif pot_inst_kw <= 25.0 and demanda_kva <= 18.0:
            tipo_fornecimento = "Bifásico a 3 fios (2F+N)"
            tipo_rede = "bifasico"
            corrente_entrada = demanda_total_va / tensao_ff
            disjuntor_sugerido = 63 if corrente_entrada <= 50 else 70
            secao_cabo_entrada = 16.0 if disjuntor_sugerido <= 63 else 25.0
        else:
            tipo_fornecimento = "Trifásico a 4 fios (3F+N)"
            tipo_rede = "trifasico"
            corrente_entrada = demanda_total_va / (math.sqrt(3) * tensao_ff)
            if corrente_entrada <= 50:
                disjuntor_sugerido = 63
                secao_cabo_entrada = 16.0
            elif corrente_entrada <= 65:
                disjuntor_sugerido = 80
                secao_cabo_entrada = 25.0
            elif corrente_entrada <= 85:
                disjuntor_sugerido = 100
                secao_cabo_entrada = 35.0
            elif corrente_entrada <= 105:
                disjuntor_sugerido = 125
                secao_cabo_entrada = 50.0
            else:
                disjuntor_sugerido = 150
                secao_cabo_entrada = 70.0

        return {
            "potencia_instalada_total_w": round(pot_total_instalada_w, 1),
            "potencia_instalada_total_kw": round(pot_inst_kw, 2),
            "potencia_instalada_total_va": round(pot_total_instalada_va, 1),
            "potencia_instalada_total_kva": round(pot_total_instalada_va / 1000.0, 2),
            "demanda_total_w": round(demanda_total_w, 1),
            "demanda_total_kw": round(demanda_total_w / 1000.0, 2),
            "demanda_total_va": round(demanda_total_va, 1),
            "demanda_total_kva": round(demanda_kva, 2),
            "fatores_demanda": {
                "iluminacao_tug": fd_ilum_tug,
                "aquecimento": fd_aquec,
                "climatizacao": fd_ar,
                "outros": fd_outros
            },
            "parcelas_demanda_w": {
                "iluminacao_tug": round(demanda_ilum_tug_w, 1),
                "aquecimento": round(demanda_aquec_w, 1),
                "climatizacao": round(demanda_ar_w, 1),
                "outros": round(demanda_outros_w, 1)
            },
            "padrao_entrada": {
                "tipo_fornecimento": tipo_fornecimento,
                "tipo_rede": tipo_rede,
                "corrente_calculada_a": round(corrente_entrada, 1),
                "disjuntor_geral_in_a": disjuntor_sugerido,
                "secao_condutor_fase_mm2": secao_cabo_entrada,
                "secao_condutor_neutro_mm2": secao_cabo_entrada,
                "secao_condutor_pe_mm2": secao_cabo_entrada if secao_cabo_entrada <= 16 else 16.0,
                "eletroduto_ramal_dn_mm": 32 if secao_cabo_entrada <= 16 else (40 if secao_cabo_entrada <= 25 else 50),
                "eletroduto_ramal_pol": '1.1/4"' if secao_cabo_entrada <= 16 else ('1.1/2"' if secao_cabo_entrada <= 25 else '2"'),
                "dps_protecao": "DPS Classe II, 275V, In 20kA, Imax 45kA (1 por fase + 1 para neutro)",
                "idr_geral": "Dispositivo DR Geral Tetrapolar/Bipolar 30mA (ou distribuído nos circuitos terminais)"
            }
        }
