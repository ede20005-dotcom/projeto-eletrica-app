"""
Módulo Integrador: Projeto Elétrico Residencial Completo conforme ABNT NBR 5410:2004
"""

from typing import Dict, List, Any, Optional
from .levantamento_cargas import ComodoResidencial, CATALOGO_TUE_RESIDENCIAL
from .divisao_circuitos import CircuitoTerminal, DivisorCircuitosResidencial
from .dimensionamento_circuitos import DimensionadorCircuitosNBR5410
from .dimensionamento_eletrodutos import DimensionadorEletrodutosNBR5410
from .demanda_instalacao import CalculadorDemandaInstalacao

class ProjetoEletricoResidencial:
    """Orquestra o projeto elétrico completo de uma residência ou edificação."""
    def __init__(
        self,
        nome_projeto: str = "Residência Unifamiliar Modelo NBR 5410",
        tipo_fornecimento: str = "trifasico", # "monofasico", "bifasico", "trifasico"
        tensao_fn: int = 127,
        tensao_ff: int = 220,
        temperatura_ambiente: int = 30,
        metodo_instalacao: str = "B1"
    ):
        self.nome_projeto = nome_projeto
        self.tipo_fornecimento = tipo_fornecimento.lower()
        self.tensao_fn = tensao_fn
        self.tensao_ff = tensao_ff
        self.temperatura_ambiente = temperatura_ambiente
        self.metodo_instalacao = metodo_instalacao
        
        self.comodos: List[ComodoResidencial] = []
        self.circuitos: List[CircuitoTerminal] = []
        self.resultado_demanda: Dict[str, Any] = {}
        self.resumo_fases: Dict[str, Any] = {}
        self.lista_materiais: List[Dict[str, Any]] = []

    def carregar_residencia_padrao(self):
        """Carrega uma planta residencial completa com 3 quartos (1 suíte), sala, cozinha, etc."""
        self.comodos = []
        
        # 1. Sala de Estar e Jantar (5.0m x 4.0m = 20.0 m², Perímetro = 18.0m)
        sala = ComodoResidencial("c_sala", "Sala de Estar e Jantar", "sala", 5.0, 4.0)
        sala.adicionar_tue("ar_condicionado_18000_btu", tensao_v=self.tensao_ff)
        self.comodos.append(sala)
        
        # 2. Cozinha e Copa (4.0m x 3.2m = 12.8 m², Perímetro = 14.4m)
        cozinha = ComodoResidencial("c_cozinha", "Copa e Cozinha", "copa_cozinha", 4.0, 3.2)
        cozinha.adicionar_tue("cooktop_inducao_7000", tensao_v=self.tensao_ff)
        cozinha.adicionar_tue("forno_eletrico_2500", tensao_v=self.tensao_ff)
        cozinha.adicionar_tue("microondas_1500", tensao_v=self.tensao_fn)
        cozinha.adicionar_tue("torneira_eletrica_4500", tensao_v=self.tensao_ff)
        cozinha.adicionar_tue("lava_loucas_1800", tensao_v=self.tensao_ff)
        self.comodos.append(cozinha)
        
        # 3. Área de Serviço / Lavanderia (3.0m x 2.2m = 6.6 m², Perímetro = 10.4m)
        servico = ComodoResidencial("c_servico", "Área de Serviço", "area_servico", 3.0, 2.2)
        servico.adicionar_tue("lava_e_seca_2000", tensao_v=self.tensao_fn)
        self.comodos.append(servico)
        
        # 4. Dormitório Suíte (4.0m x 3.5m = 14.0 m², Perímetro = 15.0m)
        suite = ComodoResidencial("c_suite", "Dormitório Suíte", "suite", 4.0, 3.5)
        suite.adicionar_tue("ar_condicionado_12000_btu", tensao_v=self.tensao_ff)
        self.comodos.append(suite)
        
        # 5. Banheiro Suíte (2.6m x 1.6m = 4.16 m², Perímetro = 8.4m)
        banheiro_suite = ComodoResidencial("c_bwc_suite", "Banheiro da Suíte", "banheiro", 2.6, 1.6)
        banheiro_suite.adicionar_tue("chuveiro_eletrico_7500", tensao_v=self.tensao_ff)
        self.comodos.append(banheiro_suite)
        
        # 6. Dormitório 1 (3.5m x 3.2m = 11.2 m², Perímetro = 13.4m)
        dorm1 = ComodoResidencial("c_dorm1", "Dormitório 1", "quarto", 3.5, 3.2)
        dorm1.adicionar_tue("ar_condicionado_9000_btu", tensao_v=self.tensao_ff)
        self.comodos.append(dorm1)
        
        # 7. Dormitório 2 (3.5m x 3.0m = 10.5 m², Perímetro = 13.0m)
        dorm2 = ComodoResidencial("c_dorm2", "Dormitório 2", "quarto", 3.5, 3.0)
        dorm2.adicionar_tue("ar_condicionado_9000_btu", tensao_v=self.tensao_ff)
        self.comodos.append(dorm2)
        
        # 8. Banheiro Social (2.6m x 1.6m = 4.16 m², Perímetro = 8.4m)
        banheiro_social = ComodoResidencial("c_bwc_social", "Banheiro Social", "banheiro", 2.6, 1.6)
        banheiro_social.adicionar_tue("chuveiro_eletrico_7500", tensao_v=self.tensao_ff)
        self.comodos.append(banheiro_social)
        
        # 9. Circulação / Hall Íntimo (3.0m x 1.2m = 3.6 m², Perímetro = 8.4m)
        hall = ComodoResidencial("c_hall", "Circulação / Hall", "circulacao", 3.0, 1.2)
        self.comodos.append(hall)
        
        # 10. Varanda Gourmet (4.0m x 2.5m = 10.0 m², Perímetro = 13.0m)
        varanda = ComodoResidencial("c_varanda", "Varanda Gourmet", "varanda", 4.0, 2.5)
        self.comodos.append(varanda)
        
        # 11. Garagem Coberta (5.5m x 4.0m = 22.0 m², Perímetro = 19.0m)
        garagem = ComodoResidencial("c_garagem", "Garagem Coberta", "garagem", 5.5, 4.0)
        self.comodos.append(garagem)

    def executar_calculos_completos(self) -> Dict[str, Any]:
        """Processa todas as etapas do projeto em conformidade com a NBR 5410."""
        # 1. Divisão dos circuitos e balanceamento de fases
        divisor = DivisorCircuitosResidencial(
            tipo_fornecimento=self.tipo_fornecimento,
            tensao_fn=self.tensao_fn,
            tensao_ff=self.tensao_ff
        )
        self.circuitos = divisor.gerar_divisao(self.comodos)
        self.resumo_fases = divisor.obter_resumo_fases()

        # 2. Dimensionamento de condutores e proteções pelos 6 critérios
        dimensionador = DimensionadorCircuitosNBR5410(
            temperatura_ambiente=self.temperatura_ambiente,
            metodo_instalacao=self.metodo_instalacao,
            queda_tensao_max_terminal=4.0
        )
        # Atribuir comprimentos médios realistas com base no tipo de carga
        for c in self.circuitos:
            if "chuveiro" in c.descricao.lower():
                c.comprimento_estimado_m = 18.0
            elif "ar condicionado" in c.descricao.lower():
                c.comprimento_estimado_m = 20.0
            elif "cozinha" in c.descricao.lower() or "cooktop" in c.descricao.lower():
                c.comprimento_estimado_m = 12.0
            elif c.tipo == "iluminacao":
                c.comprimento_estimado_m = 16.0
            else:
                c.comprimento_estimado_m = 14.0

        self.circuitos = dimensionador.dimensionar_todos(self.circuitos)

        # 3. Dimensionamento de eletrodutos para cada circuito terminal
        for c in self.circuitos:
            conds = [{"secao_mm2": c.secao_condutor_mm2, "qtd": len(c.fases)}]
            if c.secao_neutro_mm2 > 0:
                conds.append({"secao_mm2": c.secao_neutro_mm2, "qtd": 1})
            if c.secao_pe_mm2 > 0:
                conds.append({"secao_mm2": c.secao_pe_mm2, "qtd": 1})
            
            res_eletro = DimensionadorEletrodutosNBR5410.dimensionar_trecho(conds, dn_minimo_adotado=20)
            c.eletroduto_trecho_dn_mm = res_eletro["dn_mm"]

        # 4. Cálculo de Demanda e Dimensionamento do Padrão de Entrada
        self.resultado_demanda = CalculadorDemandaInstalacao.calcular_demanda(
            self.comodos,
            tensao_fn=self.tensao_fn,
            tensao_ff=self.tensao_ff
        )

        # 5. Levantamento da Lista Quantitativa de Materiais
        self._gerar_lista_materiais()

        return self.to_dict()

    def _gerar_lista_materiais(self):
        """Calcula as quantidades estimadas de cabos, tubos, disjuntores e componentes."""
        self.lista_materiais = []
        
        # 1. Cabos de Cobre Isolados PVC 70°C 750V por bitola e cor (NBR 5410: Azul=Neutro, Verde=PE, Preto/Vermelho=Fase)
        metragem_cabos = {} # secao: {fase: m, neutro: m, pe: m}
        for c in self.circuitos:
            s_fase = c.secao_condutor_mm2
            s_n = c.secao_neutro_mm2
            s_pe = c.secao_pe_mm2
            L = c.comprimento_estimado_m * 1.25 # Margem de curvas e sobras de 25%
            
            # Fases
            metragem_cabos.setdefault(s_fase, {"fase": 0.0, "neutro": 0.0, "pe": 0.0, "retorno": 0.0})
            metragem_cabos[s_fase]["fase"] += L * len(c.fases)
            
            # Neutro
            if s_n > 0:
                metragem_cabos.setdefault(s_n, {"fase": 0.0, "neutro": 0.0, "pe": 0.0, "retorno": 0.0})
                metragem_cabos[s_n]["neutro"] += L
                
            # PE
            if s_pe > 0:
                metragem_cabos.setdefault(s_pe, {"fase": 0.0, "neutro": 0.0, "pe": 0.0, "retorno": 0.0})
                metragem_cabos[s_pe]["pe"] += L

            # Retornos para iluminação
            if c.tipo == "iluminacao":
                metragem_cabos[s_fase]["retorno"] += L * 0.8

        for secao, metros in sorted(metragem_cabos.items()):
            tot_fase = round(metros["fase"])
            tot_n = round(metros["neutro"])
            tot_pe = round(metros["pe"])
            tot_ret = round(metros["retorno"])
            if tot_fase > 0:
                self.lista_materiais.append({"item": f"Cabo Cobre Flexível 750V {secao} mm² - Preto/Vermelho (Fase)", "quantidade": tot_fase, "unidade": "m"})
            if tot_n > 0:
                self.lista_materiais.append({"item": f"Cabo Cobre Flexível 750V {secao} mm² - Azul Claro (Neutro)", "quantidade": tot_n, "unidade": "m"})
            if tot_pe > 0:
                self.lista_materiais.append({"item": f"Cabo Cobre Flexível 750V {secao} mm² - Verde / Verde-Amarelo (Terra PE)", "quantidade": tot_pe, "unidade": "m"})
            if tot_ret > 0:
                self.lista_materiais.append({"item": f"Cabo Cobre Flexível 750V {secao} mm² - Amarelo (Retorno Iluminação)", "quantidade": tot_ret, "unidade": "m"})

        # Cabos do Ramal de Entrada
        pe = self.resultado_demanda.get("padrao_entrada", {})
        s_ramal = pe.get("secao_condutor_fase_mm2", 25.0)
        self.lista_materiais.append({"item": f"Cabo Cobre 1kV {s_ramal} mm² (Alimentador Geral Entrada)", "quantidade": 40, "unidade": "m"})

        # 2. Eletrodutos Corrugados Flexíveis em PVC
        eletro_20 = sum(c.comprimento_estimado_m for c in self.circuitos if c.eletroduto_trecho_dn_mm == 20)
        eletro_25 = sum(c.comprimento_estimado_m for c in self.circuitos if c.eletroduto_trecho_dn_mm == 25)
        self.lista_materiais.append({"item": "Eletroduto Corrugado Flexível PVC Amarelo DN 20mm (3/4\")", "quantidade": max(50, round(eletro_20 * 1.2)), "unidade": "m"})
        self.lista_materiais.append({"item": "Eletroduto Corrugado Flexível PVC Amarelo DN 25mm (1\")", "quantidade": max(30, round(eletro_25 * 1.2)), "unidade": "m"})

        # 3. Disjuntores e Proteções no QDC
        disj_counts = {}
        for c in self.circuitos:
            polo = f"{len(c.fases)}P"
            key = f"Disjuntor Termomagnético DIN Curva C {c.disjuntor_in_a}A ({polo})"
            disj_counts[key] = disj_counts.get(key, 0) + 1
        for k, v in disj_counts.items():
            self.lista_materiais.append({"item": k, "quantidade": v, "unidade": "pç"})

        # Disjuntor Geral, IDR e DPS
        disj_geral_in = pe.get("disjuntor_geral_in_a", 80)
        polo_geral = "Tripolar" if self.tipo_fornecimento == "trifasico" else ("Bipolar" if self.tipo_fornecimento == "bifasico" else "Monopolar")
        self.lista_materiais.append({"item": f"Disjuntor Geral DIN {polo_geral} {disj_geral_in}A 5kA/10kA", "quantidade": 1, "unidade": "pç"})
        self.lista_materiais.append({"item": "Interruptor Diferencial Residual (IDR) Tetrapolar/Bipolar 63A/30mA", "quantidade": 2, "unidade": "pç"})
        self.lista_materiais.append({"item": "Dispositivo de Proteção contra Surtos (DPS) Classe II 275V 20kA/45kA", "quantidade": 4 if self.tipo_fornecimento == "trifasico" else 3, "unidade": "pç"})
        self.lista_materiais.append({"item": f"Quadro de Distribuição de Circuitos (QDC) Embutir para {len(self.circuitos) + 12} Módulos DIN com Barramentos Neutro/Terra", "quantidade": 1, "unidade": "pç"})

        # 4. Caixas, Tomadas e Interruptores
        tot_tug = sum(len(c.tug_pontos) for c in self.comodos)
        tot_tue = sum(len(c.tue_cargas) for c in self.comodos)
        tot_pontos_luz = sum(c.qtd_pontos_iluminacao for c in self.comodos)
        self.lista_materiais.append({"item": "Caixa de Embutir 4x2\" PVC Amarela para Tomadas e Interruptores", "quantidade": tot_tug + tot_tue + 14, "unidade": "pç"})
        self.lista_materiais.append({"item": "Caixa Octogonal 4x4\" Fundo Móvel PVC para Laje/Teto", "quantidade": tot_pontos_luz + 4, "unidade": "pç"})
        self.lista_materiais.append({"item": "Módulo Tomada 2P+T 10A 250V (NBR 14136) com Placa 4x2", "quantidade": tot_tug, "unidade": "pç"})
        self.lista_materiais.append({"item": "Módulo Tomada 2P+T 20A 250V (NBR 14136) para Eletrodomésticos de Alta Potência", "quantidade": 6, "unidade": "pç"})
        self.lista_materiais.append({"item": "Conjunto Interruptor Simples 10A com Placa 4x2", "quantidade": 8, "unidade": "pç"})
        self.lista_materiais.append({"item": "Conjunto Interruptor Paralelo (Three-Way) 10A com Placa 4x2", "quantidade": 6, "unidade": "pç"})
        self.lista_materiais.append({"item": "Haste de Aterramento Aço Cobreado 5/8\" x 2.40m com Conector Cabo-Haste", "quantidade": 3, "unidade": "pç"})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nome_projeto": self.nome_projeto,
            "normas_aplicadas": ["ABNT NBR 5410:2004", "NR-10", "ABNT NBR 5419:2015", "ABNT NBR 5444:1989"],
            "parametros_fornecimento": {
                "tipo_fornecimento": self.tipo_fornecimento,
                "tensao_fase_neutro_v": self.tensao_fn,
                "tensao_fase_fase_v": self.tensao_ff,
                "temperatura_ambiente_c": self.temperatura_ambiente,
                "metodo_instalacao": self.metodo_instalacao
            },
            "resumo_edificacao": {
                "qtd_comodos": len(self.comodos),
                "area_total_construida_m2": round(sum(c.area for c in self.comodos), 2),
                "perimetro_total_m": round(sum(c.perimetro for c in self.comodos), 2)
            },
            "comodos": [c.to_dict() for c in self.comodos],
            "circuitos": [c.to_dict() for c in self.circuitos],
            "balanceamento_fases": self.resumo_fases,
            "demanda_instalacao": self.resultado_demanda,
            "lista_materiais": self.lista_materiais
        }
