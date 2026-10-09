"""
Módulo de Estudo de Coordenação e Seletividade de Proteções Elétricas
Conforme ABNT NBR 5410:2004 (item 5.3.5), ABNT NBR NM 60898 e IEC 60947-2
Gera curvas de atuação Tempo x Corrente (Log-Log) e verifica Seletividade Térmica e Magnética.
"""

import math
from typing import Dict, List, Any, Tuple, Optional

class CurvaDisjuntorTermomagnetico:
    """Modela o comportamento tempo-corrente de disjuntores DIN termomagnéticos."""

    def __init__(self, corrente_nominal_a: float, curva_tipo: str = "C", capacidade_ruptura_ka: float = 4.5):
        self.in_a = float(corrente_nominal_a)
        self.curva = curva_tipo.upper() # "B", "C" ou "D"
        self.icu_ka = capacidade_ruptura_ka
        
        # Parâmetros normalizados de disparo magnético (múltiplos de In)
        if self.curva == "B":
            self.im_min_mult = 3.0
            self.im_max_mult = 5.0
        elif self.curva == "D":
            self.im_min_mult = 10.0
            self.im_max_mult = 20.0
        else: # Padrão Curva C
            self.im_min_mult = 5.0
            self.im_max_mult = 10.0
            
        self.im_min_a = self.in_a * self.im_min_mult
        self.im_max_a = self.in_a * self.im_max_mult

    def calcular_tempo_disparo(self, corrente_a: float) -> Dict[str, float]:
        """
        Retorna o tempo mínimo e máximo de disparo em segundos para uma corrente dada.
        Baseado na equação térmica aproximada t = k / ((I/In)^2 - 1) e limite magnético instantâneo.
        """
        if corrente_a <= self.in_a * 1.05:
            return {"tempo_min_s": 10000.0, "tempo_max_s": 10000.0, "regiao": "sem_disparo"}
            
        mult = corrente_a / self.in_a
        
        # Região Magnética Instantânea
        if mult >= self.im_max_mult:
            return {"tempo_min_s": 0.005, "tempo_max_s": 0.02, "regiao": "magnetica_instantanea"}
        elif mult >= self.im_min_mult:
            # Zona de transição magnética
            t_min = 0.005
            t_max = max(0.04, 30.0 / (mult ** 1.8))
            return {"tempo_min_s": t_min, "tempo_max_s": t_max, "regiao": "transicao_magnetica"}
        else:
            # Região Térmica (Sobrecarga)
            # t = k / ((I/In)^2 - 1)
            t_min = max(0.04, 18.0 / ((mult ** 2.05) - 1.05))
            t_max = max(0.10, 85.0 / ((mult ** 1.95) - 1.0))
            return {"tempo_min_s": round(t_min, 3), "tempo_max_s": round(t_max, 3), "regiao": "sobrecarga_termica"}

    def gerar_pontos_curva(self, num_pontos: int = 50) -> List[Dict[str, float]]:
        """Gera pontos (corrente_a, tempo_min_s, tempo_max_s) para plotagem em gráfico Log-Log."""
        pontos = []
        # Varrer múltiplos de 1.13 até 30x In
        multiplos = [1.13, 1.20, 1.30, 1.45, 1.6, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.5, 9.0, 10.0, 12.0, 15.0, 20.0, 30.0]
        for m in multiplos:
            corr = self.in_a * m
            res = self.calcular_tempo_disparo(corr)
            if res["tempo_max_s"] <= 3600.0:
                pontos.append({
                    "multiplo": round(m, 2),
                    "corrente_a": round(corr, 1),
                    "tempo_min_s": res["tempo_min_s"],
                    "tempo_max_s": res["tempo_max_s"],
                    "regiao": res["regiao"]
                })
        return pontos


class AnalisadorSeletividadeProtecoes:
    """Executa a verificação técnica da seletividade entre proteção a montante e jusante."""

    @classmethod
    def verificar_seletividade(
        cls,
        disjuntor_montante: CurvaDisjuntorTermomagnetico,
        disjuntor_jusante: CurvaDisjuntorTermomagnetico,
        corrente_curto_circuito_presumida_a: float = 1500.0
    ) -> Dict[str, Any]:
        """
        Avalia seletividade amperimétrica, cronométrica e total.
        Critérios NBR 5410 / IEC 60947-2:
        1. Relação de correntes: In_montante / In_jusante >= 1.6 garante seletividade térmica total.
        2. Limite magnético: Seletividade é plena se Im_min(montante) >= Icc_presumida ou Im_min(montante) >= Im_max(jusante).
        """
        razao_in = disjuntor_montante.in_a / disjuntor_jusante.in_a
        seletividade_termica = razao_in >= 1.6
        
        # Limite de seletividade magnética (Is)
        limite_seletividade_a = disjuntor_montante.im_min_a
        seletividade_total = (limite_seletividade_a >= corrente_curto_circuito_presumida_a) and seletividade_termica
        
        if seletividade_total:
            grau = "TOTAL"
            parecer = f"Seletividade TOTAL garantida até {corrente_curto_circuito_presumida_a:.0f}A. O disjuntor a jusante ({disjuntor_jusante.in_a:.0f}A {disjuntor_jusante.curva}) opera sem desarmar o geral ({disjuntor_montante.in_a:.0f}A {disjuntor_montante.curva})."
        elif seletividade_termica:
            grau = "PARCIAL"
            parecer = f"Seletividade PARCIAL até {limite_seletividade_a:.0f}A. Sobrecargas são 100% seletivas. Em faltas severas acima de {limite_seletividade_a:.0f}A, ambos podem desarmar simultaneamente."
        else:
            grau = "NÃO SELETIVO"
            parecer = f"Risco de atuação intempestiva do geral (Razão In = {razao_in:.2f} < 1.60). Recomenda-se aumentar a capacidade do disjuntor geral ou ajustar a curva do parcial."

        return {
            "disjuntor_montante": {
                "in_a": disjuntor_montante.in_a,
                "curva": disjuntor_montante.curva,
                "im_min_a": disjuntor_montante.im_min_a,
                "im_max_a": disjuntor_montante.im_max_a
            },
            "disjuntor_jusante": {
                "in_a": disjuntor_jusante.in_a,
                "curva": disjuntor_jusante.curva,
                "im_min_a": disjuntor_jusante.im_min_a,
                "im_max_a": disjuntor_jusante.im_max_a
            },
            "razao_correntes": round(razao_in, 2),
            "seletividade_termica": seletividade_termica,
            "limite_seletividade_amperimetrica_a": limite_seletividade_a,
            "corrente_curto_circuito_presumida_a": corrente_curto_circuito_presumida_a,
            "grau_seletividade": grau,
            "parecer_tecnico": parecer,
            "conforme_nbr5410": seletividade_termica
        }

    @classmethod
    def gerar_estudo_completo_instalacao(cls, circuitos: List[Dict[str, Any]], disjuntor_geral_a: float = 125.0) -> Dict[str, Any]:
        """Gera a matriz completa de seletividade de todos os circuitos contra o disjuntor geral."""
        geral = CurvaDisjuntorTermomagnetico(disjuntor_geral_a, "C")
        matriz = []
        
        for c in circuitos:
            in_circ = float(c.get("disjuntor_in_a", 16.0))
            # Circuito de iluminação usa Curva B, circuitos de força e chuveiro Curva C
            curva = "B" if "Iluminação" in c.get("descricao", "") else "C"
            dj_circ = CurvaDisjuntorTermomagnetico(in_circ, curva)
            analise = cls.verificar_seletividade(geral, dj_circ)
            matriz.append({
                "circuito_num": c.get("numero", 0),
                "descricao": c.get("descricao", ""),
                "disjuntor_in_a": in_circ,
                "curva": curva,
                "razao_geral": analise["razao_correntes"],
                "grau_seletividade": analise["grau_seletividade"],
                "limite_seletividade_a": analise["limite_seletividade_amperimetrica_a"],
                "parecer": analise["parecer_tecnico"]
            })
            
        curvas_plot = {
            "geral_125a_c": geral.gerar_pontos_curva(),
            "chuveiro_40a_c": CurvaDisjuntorTermomagnetico(40.0, "C").gerar_pontos_curva(),
            "tomadas_20a_c": CurvaDisjuntorTermomagnetico(20.0, "C").gerar_pontos_curva(),
            "iluminacao_10a_b": CurvaDisjuntorTermomagnetico(10.0, "B").gerar_pontos_curva()
        }
        
        return {
            "disjuntor_geral": {"in_a": disjuntor_geral_a, "curva": "C", "icu_ka": 6.0},
            "matriz_seletividade": matriz,
            "curvas_plotagem_log_log": curvas_plot
        }
