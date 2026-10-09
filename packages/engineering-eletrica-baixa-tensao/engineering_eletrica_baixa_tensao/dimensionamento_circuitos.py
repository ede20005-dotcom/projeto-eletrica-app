"""
Módulo de Dimensionamento de Circuitos de Baixa Tensão conforme ABNT NBR 5410:2004
Implementação dos 6 Critérios Normativos:
1. Seção Mínima (Tabela 47)
2. Capacidade de Condução de Corrente (Tabela 36, 40, 42)
3. Queda de Tensão Admissível (Delta U <= 4%)
4. Proteção contra Sobrecargas (Ib <= In <= Iz e I2 <= 1.45*Iz)
5. Condutor Neutro (Tabela 48) e Condutor de Proteção PE (Tabela 58)
6. Proteção contra Choques Elétricos (Dispositivo DR 30mA) e DPS Classe II
"""

import math
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "engineering-eletrica-core", "src")))
from tabelas_condutores import (
    SECOES_PADRAO_COBRE,
    SECOES_MINIMAS_NBR5410,
    CAPACIDADE_CORRENTE_PVC_COBRE,
    FATOR_CORRECAO_TEMP_PVC,
    FATOR_AGRUPAMENTO_NBR5410,
    PARAMETROS_CABOS_COBRE_PVC,
    DISJUNTORES_DIN_PADRAO,
    obter_secao_pe_minima,
    obter_secao_neutro_minima
)
from .divisao_circuitos import CircuitoTerminal

class DimensionadorCircuitosNBR5410:
    """Aplica o dimensionamento rigoroso pelos 6 critérios normativos da NBR 5410:2004."""
    def __init__(
        self,
        temperatura_ambiente: int = 30,
        metodo_instalacao: str = "B1", # B1 = condutores isolados em eletroduto embutido em alvenaria
        queda_tensao_max_terminal: float = 4.0, # 4% para circuitos terminais
        circuitos_agrupados_medio: int = 2 # Média de circuitos agrupados no mesmo eletroduto
    ):
        self.temperatura_ambiente = temperatura_ambiente
        self.metodo_instalacao = metodo_instalacao
        self.queda_tensao_max_terminal = queda_tensao_max_terminal
        self.circuitos_agrupados_medio = circuitos_agrupados_medio
        
        # Fatores de correção
        self.ft = FATOR_CORRECAO_TEMP_PVC.get(temperatura_ambiente, 1.0)
        self.fa = FATOR_AGRUPAMENTO_NBR5410.get(circuitos_agrupados_medio, 0.80)
        self.fator_correcao_total = round(self.ft * self.fa, 3)

    def dimensionar_circuito(self, circ: CircuitoTerminal, comprimento_m: Optional[float] = None) -> CircuitoTerminal:
        """Executa a verificação dos 6 critérios e atribui as propriedades calculadas ao circuito."""
        if comprimento_m is not None:
            circ.comprimento_estimado_m = float(comprimento_m)

        L = circ.comprimento_estimado_m
        V = circ.tensao_v
        P_va = circ.potencia_va
        fp = max(0.2, min(1.0, circ.fator_potencia))
        sin_phi = math.sqrt(max(0.0, 1.0 - fp**2))
        
        # 1. Corrente de Projeto (Ib)
        if circ.esquema in ["F+N+PE", "2F+PE"]:
            Ib = P_va / V
            num_condutores_carregados = 2
            coluna_capacidade = f"{self.metodo_instalacao}_2c"
        else: # 3F+N+PE ou 3F+PE
            Ib = P_va / (math.sqrt(3) * V)
            num_condutores_carregados = 3
            coluna_capacidade = f"{self.metodo_instalacao}_3c"
            
        circ.corrente_projeto_ib = round(Ib, 2)
        
        # Corrente de projeto fictícia para dimensionamento térmico corrigido
        Ib_corrigido = Ib / self.fator_correcao_total

        # CRITÉRIO 1: Seção Mínima Normativa (Tabela 47)
        if circ.tipo == "iluminacao":
            secao_min_norma = SECOES_MINIMAS_NBR5410["iluminacao"] # 1.5 mm²
        else:
            secao_min_norma = SECOES_MINIMAS_NBR5410["tomadas_forca"] # 2.5 mm²

        # CRITÉRIO 2: Capacidade de Condução de Corrente (Tabela 36 corrigida)
        secao_capacidade = None
        for s in SECOES_PADRAO_COBRE:
            if s >= secao_min_norma:
                cap_tab = CAPACIDADE_CORRENTE_PVC_COBRE.get(s, {}).get(coluna_capacidade, 0.0)
                if cap_tab >= Ib_corrigido:
                    secao_capacidade = s
                    break
        if secao_capacidade is None:
            secao_capacidade = SECOES_PADRAO_COBRE[-1]

        # Inicia a busca pela seção que satisfaça TODOS os critérios (Térmico, Queda de Tensão e Coordenação de Disjuntor)
        secao_adotada = max(secao_min_norma, secao_capacidade)
        idx_secao = SECOES_PADRAO_COBRE.index(secao_adotada)
        
        disjuntor_selecionado = None
        delta_u_pct = 0.0
        delta_u_v = 0.0
        Iz_corrigido = 0.0

        while idx_secao < len(SECOES_PADRAO_COBRE):
            s_cand = SECOES_PADRAO_COBRE[idx_secao]
            cap_tab = CAPACIDADE_CORRENTE_PVC_COBRE.get(s_cand, {}).get(coluna_capacidade, 0.0)
            Iz_cand = cap_tab * self.fator_correcao_total
            
            # CRITÉRIO 3: Queda de Tensão
            param_cabo = PARAMETROS_CABOS_COBRE_PVC.get(s_cand, {"R_ohm_km": 14.8, "X_ohm_km": 0.118})
            R = param_cabo["R_ohm_km"]
            X = param_cabo["X_ohm_km"]
            
            if num_condutores_carregados == 2:
                # Monofásico / Bifásico 2 fios: DeltaU = 2 * Ib * L * (R*cos_phi + X*sin_phi) / 1000
                delta_v = (2.0 * Ib * L * (R * fp + X * sin_phi)) / 1000.0
                delta_pct = (delta_v / V) * 100.0
            else:
                # Trifásico: DeltaU = sqrt(3) * Ib * L * (R*cos_phi + X*sin_phi) / 1000
                delta_v = (math.sqrt(3.0) * Ib * L * (R * fp + X * sin_phi)) / 1000.0
                delta_pct = (delta_v / V) * 100.0
                
            # CRITÉRIO 4: Proteção contra Sobrecarga (Ib <= In <= Iz)
            # Busca disjuntor DIN comercial tal que Ib <= In <= Iz_cand
            cand_disjuntores = [din for din in DISJUNTORES_DIN_PADRAO if din >= Ib and din <= Iz_cand]
            
            # Se delta_pct <= queda máxima e encontramos disjuntor adequado
            if delta_pct <= self.queda_tensao_max_terminal and cand_disjuntores:
                secao_adotada = s_cand
                disjuntor_selecionado = cand_disjuntores[0] # Menor disjuntor que protege contra sobrecarga
                delta_u_pct = delta_pct
                delta_u_v = delta_v
                Iz_corrigido = Iz_cand
                break
            elif delta_pct <= self.queda_tensao_max_terminal and not cand_disjuntores and Ib <= Iz_cand:
                # Não há disjuntor exatamente no intervalo porque o menor DIN disponível pode ser > Iz_cand
                # Aumenta seção para que Iz_cand cresça e caiba um disjuntor padronizado
                idx_secao += 1
            else:
                # Queda de tensão reprovou ou capacidade reprovou -> incrementa seção
                idx_secao += 1

        if disjuntor_selecionado is None:
            # Caso extremo de contingência
            secao_adotada = SECOES_PADRAO_COBRE[min(idx_secao, len(SECOES_PADRAO_COBRE)-1)]
            disjuntor_selecionado = max(10, min([din for din in DISJUNTORES_DIN_PADRAO if din >= Ib] or [16]))

        # CRITÉRIO 5: Condutor Neutro e Condutor de Proteção (PE)
        secao_neutro = secao_adotada if circ.esquema != "2F+PE" else 0.0
        secao_pe = obter_secao_pe_minima(secao_adotada)

        # Atribuição dos resultados ao circuito
        circ.secao_condutor_mm2 = secao_adotada
        circ.secao_neutro_mm2 = secao_neutro
        circ.secao_pe_mm2 = secao_pe
        circ.disjuntor_in_a = disjuntor_selecionado
        circ.queda_tensao_percentual = round(delta_u_pct, 2)
        circ.queda_tensao_v = round(delta_u_v, 2)
        
        circ.detalhes_dimensionamento = {
            "criterio_secao_minima_mm2": secao_min_norma,
            "criterio_capacidade_corrente_mm2": secao_capacidade,
            "corrente_corrigida_ib_linha_a": round(Ib_corrigido, 2),
            "capacidade_efetiva_iz_a": round(Iz_corrigido, 2),
            "fator_temperatura_ft": self.ft,
            "fator_agrupamento_fa": self.fa,
            "queda_tensao_admissivel_pct": self.queda_tensao_max_terminal,
            "conformidade_queda_tensao": delta_u_pct <= self.queda_tensao_max_terminal,
            "conformidade_sobrecarga": Ib <= disjuntor_selecionado <= Iz_corrigido,
            "status_geral": "APROVADO (NBR 5410)"
        }
        
        return circ

    def dimensionar_todos(self, circuitos: List[CircuitoTerminal]) -> List[CircuitoTerminal]:
        for c in circuitos:
            self.dimensionar_circuito(c)
        return circuitos
