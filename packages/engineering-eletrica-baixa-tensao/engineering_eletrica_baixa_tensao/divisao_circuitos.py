"""
Módulo de Divisão de Circuitos e Balanceamento de Fases conforme ABNT NBR 5410:2004
Subitem 9.5.3 - Divisão da instalação em circuitos
"""

from typing import Dict, List, Any, Optional
import math
from .levantamento_cargas import ComodoResidencial

class CircuitoTerminal:
    """Representa um circuito terminal derivado do QDC."""
    def __init__(
        self,
        numero: int,
        descricao: str,
        tipo: str, # "iluminacao", "tug", "tue"
        tensao_v: int,
        esquema: str = "F+N+PE", # "F+N+PE", "2F+PE", "3F+N+PE"
        dr_obrigatorio: bool = True
    ):
        self.numero = numero
        self.descricao = descricao
        self.tipo = tipo
        self.tensao_v = tensao_v
        self.esquema = esquema
        self.dr_obrigatorio = dr_obrigatorio
        
        self.pontos: List[Dict[str, Any]] = []
        self.potencia_va = 0.0
        self.potencia_w = 0.0
        self.fator_potencia = 1.0
        self.comodos_atendidos: List[str] = []
        
        # Atribuição de fase(s) - ex: ["R"], ["R", "S"], ["R", "S", "T"]
        self.fases: List[str] = []
        
        # Resultados de dimensionamento
        self.comprimento_estimado_m = 15.0 # Distância média do QDC aos pontos
        self.corrente_projeto_ib = 0.0
        self.secao_condutor_mm2 = 1.5
        self.secao_neutro_mm2 = 1.5
        self.secao_pe_mm2 = 1.5
        self.disjuntor_in_a = 10
        self.queda_tensao_percentual = 0.0
        self.queda_tensao_v = 0.0
        self.eletroduto_trecho_dn_mm = 20 # 3/4"
        self.detalhes_dimensionamento: Dict[str, Any] = {}

    def adicionar_ponto(self, id_ponto: str, comodo: str, pot_va: float, pot_w: float, fp: float = 1.0):
        self.pontos.append({
            "id": id_ponto,
            "comodo": comodo,
            "potencia_va": pot_va,
            "potencia_w": pot_w,
            "fator_potencia": fp
        })
        self.potencia_va += pot_va
        self.potencia_w += pot_w
        if comodo not in self.comodos_atendidos:
            self.comodos_atendidos.append(comodo)
        if self.potencia_va > 0:
            self.fator_potencia = round(self.potencia_w / self.potencia_va, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "numero": self.numero,
            "descricao": self.descricao,
            "tipo": self.tipo,
            "tensao_v": self.tensao_v,
            "esquema": self.esquema,
            "fases": self.fases,
            "dr_obrigatorio": self.dr_obrigatorio,
            "potencia_va": round(self.potencia_va, 1),
            "potencia_w": round(self.potencia_w, 1),
            "fator_potencia": self.fator_potencia,
            "corrente_projeto_ib": round(self.corrente_projeto_ib, 2),
            "secao_condutor_mm2": self.secao_condutor_mm2,
            "secao_neutro_mm2": self.secao_neutro_mm2,
            "secao_pe_mm2": self.secao_pe_mm2,
            "disjuntor_in_a": self.disjuntor_in_a,
            "queda_tensao_percentual": round(self.queda_tensao_percentual, 2),
            "queda_tensao_v": round(self.queda_tensao_v, 2),
            "eletroduto_trecho_dn_mm": self.eletroduto_trecho_dn_mm,
            "comprimento_estimado_m": self.comprimento_estimado_m,
            "comodos_atendidos": self.comodos_atendidos,
            "detalhes_dimensionamento": self.detalhes_dimensionamento
        }


class DivisorCircuitosResidencial:
    """Gerencia a divisão automática de circuitos e balanceamento de fases conforme NBR 5410."""
    def __init__(self, tipo_fornecimento: str = "trifasico", tensao_fn: int = 127, tensao_ff: int = 220):
        self.tipo_fornecimento = tipo_fornecimento.lower() # "monofasico", "bifasico", "trifasico"
        self.tensao_fn = tensao_fn # 127 ou 220
        self.tensao_ff = tensao_ff # 220 ou 380
        self.fases_disponiveis = ["R"] if self.tipo_fornecimento == "monofasico" else (
            ["R", "S"] if self.tipo_fornecimento == "bifasico" else ["R", "S", "T"]
        )
        self.circuitos: List[CircuitoTerminal] = []

    def gerar_divisao(self, comodos: List[ComodoResidencial]) -> List[CircuitoTerminal]:
        """Aplica as regras normativas de agrupamento e separação de circuitos."""
        self.circuitos = []
        num_circuito = 1
        
        # 1. Agrupamento de Iluminação (Separado de tomadas - NBR 5410 subitem 9.5.3)
        # Dividir em Iluminação Social/Serviço e Iluminação Íntima se ultrapassar ~1200 VA
        pontos_ilum_social = []
        pontos_ilum_intima = []
        
        for c in comodos:
            pot_va = c.iluminacao_min_va
            pot_w = pot_va * 1.0
            ponto = {"id": f"ILUM_{c.id}", "comodo": c.nome, "pot_va": pot_va, "pot_w": pot_w, "fp": 1.0}
            if c.tipo in ["quarto", "suite", "dormitorio", "banheiro", "lavabo"]:
                pontos_ilum_intima.append(ponto)
            else:
                pontos_ilum_social.append(ponto)
                
        # Circuito Iluminação 1 (Social / Serviço / Área Externa)
        circ_ilum_1 = CircuitoTerminal(
            numero=num_circuito,
            descricao="Iluminação Área Social e Serviços",
            tipo="iluminacao",
            tensao_v=self.tensao_fn,
            esquema="F+N+PE",
            dr_obrigatorio=False # NBR 5410 permite dispensar DR em iluminação se não for externa
        )
        for p in pontos_ilum_social:
            circ_ilum_1.adicionar_ponto(p["id"], p["comodo"], p["pot_va"], p["pot_w"], p["fp"])
        self.circuitos.append(circ_ilum_1)
        num_circuito += 1
        
        # Circuito Iluminação 2 (Íntima / Quartos)
        if pontos_ilum_intima:
            circ_ilum_2 = CircuitoTerminal(
                numero=num_circuito,
                descricao="Iluminação Área Íntima e Dormitórios",
                tipo="iluminacao",
                tensao_v=self.tensao_fn,
                esquema="F+N+PE",
                dr_obrigatorio=False
            )
            for p in pontos_ilum_intima:
                circ_ilum_2.adicionar_ponto(p["id"], p["comodo"], p["pot_va"], p["pot_w"], p["fp"])
            self.circuitos.append(circ_ilum_2)
            num_circuito += 1

        # 2. TUGs de Áreas Molhadas (Cozinha, Copa, Área de Serviço)
        # Devem ser circuitos independentes de salas e quartos (item 9.5.3)
        pontos_tug_cozinha = []
        pontos_tug_servico = []
        
        for c in comodos:
            if c.tipo in ["copa_cozinha", "cozinha", "copa"]:
                for t in c.tug_pontos:
                    pontos_tug_cozinha.append((t, c.nome))
            elif c.tipo in ["area_servico", "lavanderia"]:
                for t in c.tug_pontos:
                    pontos_tug_servico.append((t, c.nome))

        if pontos_tug_cozinha:
            # Dividir em 2 circuitos se ultrapassar ~2000 VA
            cargas_c1 = []
            cargas_c2 = []
            va_acum = 0
            for t, nome_comodo in pontos_tug_cozinha:
                if va_acum + t["potencia_va"] <= 2000 or len(cargas_c1) < 2:
                    cargas_c1.append((t, nome_comodo))
                    va_acum += t["potencia_va"]
                else:
                    cargas_c2.append((t, nome_comodo))
                    
            circ_tug_coz1 = CircuitoTerminal(
                numero=num_circuito,
                descricao="Tomadas de Uso Geral (TUG) - Copa e Cozinha 1",
                tipo="tug",
                tensao_v=self.tensao_fn,
                esquema="F+N+PE",
                dr_obrigatorio=True
            )
            for t, nome_comodo in cargas_c1:
                circ_tug_coz1.adicionar_ponto(t["id"], nome_comodo, t["potencia_va"], t["potencia_va"] * 0.8, 0.8)
            self.circuitos.append(circ_tug_coz1)
            num_circuito += 1
            
            if cargas_c2:
                circ_tug_coz2 = CircuitoTerminal(
                    numero=num_circuito,
                    descricao="Tomadas de Uso Geral (TUG) - Copa e Cozinha 2",
                    tipo="tug",
                    tensao_v=self.tensao_fn,
                    esquema="F+N+PE",
                    dr_obrigatorio=True
                )
                for t, nome_comodo in cargas_c2:
                    circ_tug_coz2.adicionar_ponto(t["id"], nome_comodo, t["potencia_va"], t["potencia_va"] * 0.8, 0.8)
                self.circuitos.append(circ_tug_coz2)
                num_circuito += 1

        if pontos_tug_servico:
            circ_tug_serv = CircuitoTerminal(
                numero=num_circuito,
                descricao="Tomadas de Uso Geral (TUG) - Área de Serviço",
                tipo="tug",
                tensao_v=self.tensao_fn,
                esquema="F+N+PE",
                dr_obrigatorio=True
            )
            for t, nome_comodo in pontos_tug_servico:
                circ_tug_serv.adicionar_ponto(t["id"], nome_comodo, t["potencia_va"], t["potencia_va"] * 0.8, 0.8)
            self.circuitos.append(circ_tug_serv)
            num_circuito += 1

        # 3. TUGs de Áreas Sociais e Íntimas (Salas, Quartos, Banheiros, Circulação, Varanda)
        pontos_tug_social_intima = []
        for c in comodos:
            if c.tipo not in ["copa_cozinha", "cozinha", "copa", "area_servico", "lavanderia"]:
                for t in c.tug_pontos:
                    pontos_tug_social_intima.append((t, c.nome, c.tipo))

        # Agrupar TUGs em blocos de até ~1500-2000 VA
        bloco_atual = []
        va_bloco = 0
        bloco_idx = 1
        for t, nome_comodo, tipo_comodo in pontos_tug_social_intima:
            if va_bloco + t["potencia_va"] > 1800 and len(bloco_atual) >= 3:
                # Fecha circuito
                circ_tug = CircuitoTerminal(
                    numero=num_circuito,
                    descricao=f"Tomadas de Uso Geral (TUG) - Setor Social/Íntimo {bloco_idx}",
                    tipo="tug",
                    tensao_v=self.tensao_fn,
                    esquema="F+N+PE",
                    dr_obrigatorio=True
                )
                for item_t, item_nome in bloco_atual:
                    circ_tug.adicionar_ponto(item_t["id"], item_nome, item_t["potencia_va"], item_t["potencia_va"] * 0.8, 0.8)
                self.circuitos.append(circ_tug)
                num_circuito += 1
                bloco_idx += 1
                bloco_atual = [(t, nome_comodo)]
                va_bloco = t["potencia_va"]
            else:
                bloco_atual.append((t, nome_comodo))
                va_bloco += t["potencia_va"]

        if bloco_atual:
            circ_tug = CircuitoTerminal(
                numero=num_circuito,
                descricao=f"Tomadas de Uso Geral (TUG) - Setor Social/Íntimo {bloco_idx}",
                tipo="tug",
                tensao_v=self.tensao_fn,
                esquema="F+N+PE",
                dr_obrigatorio=True
            )
            for item_t, item_nome in bloco_atual:
                circ_tug.adicionar_ponto(item_t["id"], item_nome, item_t["potencia_va"], item_t["potencia_va"] * 0.8, 0.8)
            self.circuitos.append(circ_tug)
            num_circuito += 1

        # 4. TUEs (Tomadas de Uso Específico) - Circuitos dedicados individuais
        for c in comodos:
            for tue in c.tue_cargas:
                tensao_tue = tue["tensao_v"]
                if self.tipo_fornecimento == "monofasico":
                    tensao_tue = self.tensao_fn
                    esquema = "F+N+PE"
                elif tensao_tue == self.tensao_fn:
                    esquema = "F+N+PE"
                else:
                    esquema = "2F+PE" if self.tensao_ff == 220 and self.tensao_fn == 127 else "F+N+PE"

                circ_tue = CircuitoTerminal(
                    numero=num_circuito,
                    descricao=f"{tue['nome']} ({c.nome})",
                    tipo="tue",
                    tensao_v=tensao_tue,
                    esquema=esquema,
                    dr_obrigatorio=True
                )
                circ_tue.adicionar_ponto(tue["id"], c.nome, tue["potencia_va"], tue["potencia_w"], tue["fp"])
                self.circuitos.append(circ_tue)
                num_circuito += 1

        # Balancear fases dos circuitos criados
        self.balancear_fases()
        return self.circuitos

    def balancear_fases(self):
        """Distribui os circuitos pelas fases disponíveis visando o menor desequilíbrio percentual."""
        if len(self.fases_disponiveis) == 1:
            for c in self.circuitos:
                c.fases = ["R"]
            return

        # Para bifásico ou trifásico, ordenar os circuitos por maior potência VA decrescente
        # e alocar de forma gulosa na(s) fase(s) com menor carga acumulada
        potencias_fase = {fase: 0.0 for fase in self.fases_disponiveis}
        
        # Ordena circuitos pela maior potência VA
        circuitos_ordenados = sorted(self.circuitos, key=lambda c: c.potencia_va, reverse=True)
        
        for circ in circuitos_ordenados:
            if circ.esquema == "2F+PE" and len(self.fases_disponiveis) >= 2:
                # Pega as duas fases menos carregadas
                fases_sort = sorted(self.fases_disponiveis, key=lambda f: potencias_fase[f])
                fase_a, fase_b = fases_sort[0], fases_sort[1]
                circ.fases = [fase_a, fase_b]
                # Metade da potência em cada fase
                potencias_fase[fase_a] += circ.potencia_va / 2.0
                potencias_fase[fase_b] += circ.potencia_va / 2.0
            elif circ.esquema == "3F+N+PE" and len(self.fases_disponiveis) == 3:
                circ.fases = ["R", "S", "T"]
                for f in ["R", "S", "T"]:
                    potencias_fase[f] += circ.potencia_va / 3.0
            else: # Monofásico F+N+PE
                # Pega a fase com menor potência acumulada
                fase_menor = min(self.fases_disponiveis, key=lambda f: potencias_fase[f])
                circ.fases = [fase_menor]
                potencias_fase[fase_menor] += circ.potencia_va

    def obter_resumo_fases(self) -> Dict[str, Any]:
        totais = {f: 0.0 for f in self.fases_disponiveis}
        for c in self.circuitos:
            if len(c.fases) == 1:
                totais[c.fases[0]] += c.potencia_va
            elif len(c.fases) == 2:
                for f in c.fases:
                    totais[f] += c.potencia_va / 2.0
            elif len(c.fases) == 3:
                for f in c.fases:
                    totais[f] += c.potencia_va / 3.0
                    
        valores = list(totais.values())
        max_val = max(valores) if valores else 1.0
        min_val = min(valores) if valores else 0.0
        desequilibrio_pct = round(((max_val - min_val) / max_val * 100) if max_val > 0 else 0.0, 2)
        
        return {
            "potencias_por_fase_va": {k: round(v, 1) for k, v in totais.items()},
            "desequilibrio_percentual": desequilibrio_pct,
            "status_equilibrio": "CONFORME (Excelente < 10%)" if desequilibrio_pct <= 10.0 else "ATENÇÃO (> 10%)"
        }
