"""
Motor Gráfico 2D CAD em DXF para Diagrama Unifilar do QDC e Quadro de Cargas
Conforme ABNT NBR 5410:2004 e NR-10
"""

import os
from typing import Dict, List, Any, Tuple
import ezdxf
from ezdxf.enums import TextEntityAlignment

class GeradorDiagramaUnifilarQDCDXF:
    """Gera arquivos DXF técnicos do Diagrama Unifilar do Quadro de Distribuição de Circuitos (QDC)."""
    
    def __init__(self, projeto_dados: Dict[str, Any]):
        self.projeto = projeto_dados
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self._configurar_layers()

    def _configurar_layers(self):
        layers = [
            ("UNIFILAR_ALIMENTADOR", 1, 0.60),  # Vermelho forte (Ramal Geral)
            ("UNIFILAR_BARRAMENTOS", 4, 0.50),  # Ciano (Barramentos R, S, T, N, PE)
            ("UNIFILAR_DISJUNTORES", 2, 0.40),  # Amarelo
            ("UNIFILAR_CIRCUITOS", 7, 0.30),    # Branco
            ("UNIFILAR_TEXTOS", 7, 0.20),       # Branco
            ("UNIFILAR_TABELAS", 8, 0.25),      # Cinza
            ("PRANCHA_MOLDURA", 7, 0.50),       # Branco
            ("PRANCHA_CARIMBO", 7, 0.25),       # Branco
        ]
        for nome, cor, lineweight in layers:
            if nome not in self.doc.layers:
                self.doc.layers.add(name=nome, color=cor, lineweight=int(lineweight * 100))

    def gerar_dxf(self, caminho_arquivo: str):
        """Desenha o diagrama unifilar completo com barramentos, proteções e tabela de cargas."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        
        circuitos = self.projeto.get("circuitos", [])
        padrao = self.projeto.get("demanda_instalacao", {}).get("padrao_entrada", {})
        
        # Ponto inicial do Diagrama Unifilar (x: 0.0, y: 15.0)
        x_base = 0.0
        y_base = 14.0
        
        # 1. Alimentador Geral e Disjuntor Geral
        self._desenhar_entrada_geral(x_base, y_base, padrao)

        # 2. Barramento Principal e Distribuição dos Circuitos Terminais
        # Cada circuito terminal será desenhado como uma coluna vertical descendo do barramento
        largura_coluna = 1.6 # 1.6m por circuito no desenho
        total_circuitos = len(circuitos)
        
        x_inicio_circ = x_base + 6.0
        y_barramento = y_base - 3.5
        
        # Barramento Geral de Fases (Linha Horizontal grossa)
        comp_barramento = max(18.0, total_circuitos * largura_coluna + 2.0)
        self.msp.add_line((x_inicio_circ - 1.0, y_barramento), (x_inicio_circ + comp_barramento, y_barramento), dxfattribs={"layer": "UNIFILAR_BARRAMENTOS"})
        self.msp.add_text("BARRAMENTO DE FASES (R, S, T) - COBRE ELETROLÍTICO 200A", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.18}).set_placement((x_inicio_circ, y_barramento + 0.3), align=TextEntityAlignment.MIDDLE_LEFT)

        # Barramento de Neutro (N) e Terra (PE)
        y_barr_n = y_barramento - 0.4
        y_barr_pe = y_barramento - 0.8
        self.msp.add_line((x_inicio_circ - 1.0, y_barr_n), (x_inicio_circ + comp_barramento, y_barr_n), dxfattribs={"layer": "UNIFILAR_BARRAMENTOS"})
        self.msp.add_text("BARRAMENTO DE NEUTRO (N) ISOLADO", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.14}).set_placement((x_inicio_circ + comp_barramento + 0.2, y_barr_n), align=TextEntityAlignment.MIDDLE_LEFT)
        
        self.msp.add_line((x_inicio_circ - 1.0, y_barr_pe), (x_inicio_circ + comp_barramento, y_barr_pe), dxfattribs={"layer": "UNIFILAR_BARRAMENTOS"})
        self.msp.add_text("BARRAMENTO DE PROTEÇÃO (PE - TERRA)", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.14}).set_placement((x_inicio_circ + comp_barramento + 0.2, y_barr_pe), align=TextEntityAlignment.MIDDLE_LEFT)

        # 3. Desenhar DPSs (Dispositivos de Proteção contra Surtos) interligando Fases/Neutro ao PE
        self._desenhar_modulo_dps(x_inicio_circ - 0.5, y_barramento, y_barr_pe)

        # 4. Desenhar os Ramos de Cada Circuito Terminal
        for i, circ in enumerate(circuitos):
            x_circ = x_inicio_circ + i * largura_coluna + 0.8
            self._desenhar_ramo_circuito(x_circ, y_barr_pe - 0.5, circ)

        # 5. Desenhar Tabela Resumo do Quadro de Cargas abaixo
        self._desenhar_tabela_quadro_cargas(x_base, y_base - 14.0, circuitos)

        # 6. Moldura e Carimbo Técnico da Prancha A1
        self._desenhar_moldura_e_carimbo(comp_barramento)

        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo

    def _desenhar_entrada_geral(self, x: float, y: float, padrao: Dict[str, Any]):
        """Desenha a chegada da rede, medidor, disjuntor geral e DR tetrapolar."""
        # Linha de entrada da concessionária
        self.msp.add_line((x, y), (x + 3.0, y), dxfattribs={"layer": "UNIFILAR_ALIMENTADOR"})
        self.msp.add_text("ENTRADA DA CONCESSIONÁRIA (3F+N+PE)", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.16}).set_placement((x, y + 0.3), align=TextEntityAlignment.MIDDLE_LEFT)
        
        # Dados do ramal
        s_cabo = padrao.get("secao_condutor_fase_mm2", 25.0)
        disj_geral = padrao.get("disjuntor_geral_in_a", 125)
        self.msp.add_text(f"Ramal: # {s_cabo} mm² Cobre", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.13}).set_placement((x, y - 0.3), align=TextEntityAlignment.MIDDLE_LEFT)
        
        # Disjuntor Geral (Símbolo DIN)
        cx_disj = x + 3.5
        self.msp.add_lwpolyline([(cx_disj - 0.3, y - 0.3), (cx_disj + 0.3, y - 0.3), (cx_disj + 0.3, y + 0.3), (cx_disj - 0.3, y + 0.3), (cx_disj - 0.3, y - 0.3)], dxfattribs={"layer": "UNIFILAR_DISJUNTORES", "closed": True})
        self.msp.add_line((cx_disj - 0.3, y - 0.3), (cx_disj + 0.3, y + 0.3), dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        self.msp.add_text(f"DJ GERAL\n{disj_geral}A 3P", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.13}).set_placement((cx_disj, y + 0.5), align=TextEntityAlignment.MIDDLE_CENTER)

        # IDR Geral / Seccionador Tetrapolar
        cx_idr = x + 4.8
        self.msp.add_circle((cx_idr, y), 0.35, dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        self.msp.add_text("IDR 30mA\n63A 4P", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.11}).set_placement((cx_idr, y - 0.55), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Conexão até o barramento
        self.msp.add_line((cx_disj + 0.3, y), (cx_idr - 0.35, y), dxfattribs={"layer": "UNIFILAR_ALIMENTADOR"})
        self.msp.add_line((cx_idr + 0.35, y), (x + 5.5, y), dxfattribs={"layer": "UNIFILAR_ALIMENTADOR"})
        self.msp.add_line((x + 5.5, y), (x + 5.5, y - 3.5), dxfattribs={"layer": "UNIFILAR_ALIMENTADOR"})

    def _desenhar_modulo_dps(self, x: float, y_fase: float, y_pe: float):
        """Desenha o banco de DPS Classe II para as 3 fases e neutro."""
        self.msp.add_line((x, y_fase), (x, y_pe - 1.2), dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        # Caixa do DPS
        self.msp.add_lwpolyline([(x - 0.25, y_pe - 0.3), (x + 0.25, y_pe - 0.3), (x + 0.25, y_pe - 0.9), (x - 0.25, y_pe - 0.9), (x - 0.25, y_pe - 0.3)], dxfattribs={"layer": "UNIFILAR_DISJUNTORES", "closed": True})
        self.msp.add_text("DPS 4x\n20kA/45kA\n275V Cl.II", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.09}).set_placement((x, y_pe - 0.6), align=TextEntityAlignment.MIDDLE_CENTER)
        # Símbolo de aterramento / BEP
        self.msp.add_line((x, y_pe - 1.2), (x, y_pe - 1.5), dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        self.msp.add_line((x - 0.2, y_pe - 1.5), (x + 0.2, y_pe - 1.5), dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        self.msp.add_line((x - 0.12, y_pe - 1.6), (x + 0.12, y_pe - 1.6), dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        self.msp.add_line((x - 0.05, y_pe - 1.7), (x + 0.05, y_pe - 1.7), dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        self.msp.add_text("BEP / Malha", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.09}).set_placement((x, y_pe - 1.85), align=TextEntityAlignment.MIDDLE_CENTER)

    def _desenhar_ramo_circuito(self, x: float, y_topo: float, circ: Dict[str, Any]):
        """Desenha um circuito terminal com seu disjuntor, condutores e etiqueta da carga."""
        # Linha vertical descendo
        y_fim = y_topo - 5.5
        self.msp.add_line((x, y_topo), (x, y_fim), dxfattribs={"layer": "UNIFILAR_CIRCUITOS"})
        
        # Disjuntor DIN do circuito
        y_disj = y_topo - 1.0
        self.msp.add_lwpolyline([(x - 0.18, y_disj - 0.25), (x + 0.18, y_disj - 0.25), (x + 0.18, y_disj + 0.25), (x - 0.18, y_disj + 0.25), (x - 0.18, y_disj - 0.25)], dxfattribs={"layer": "UNIFILAR_DISJUNTORES", "closed": True})
        self.msp.add_line((x - 0.18, y_disj - 0.25), (x + 0.18, y_disj + 0.25), dxfattribs={"layer": "UNIFILAR_DISJUNTORES"})
        
        # Número do Circuito e Fase
        fases_str = "/".join(circ.get("fases", ["R"]))
        self.msp.add_text(f"CIRC {circ['numero']}", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.12}).set_placement((x, y_topo + 0.25), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text(f"Fase {fases_str}", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.09}).set_placement((x, y_topo + 0.05), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Dados do Disjuntor
        polos = f"{len(circ.get('fases', ['R']))}P"
        self.msp.add_text(f"{circ['disjuntor_in_a']}A {polos}", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.10}).set_placement((x + 0.25, y_disj), align=TextEntityAlignment.MIDDLE_LEFT)

        # Dados dos Condutores
        s_fase = circ.get("secao_condutor_mm2", 2.5)
        s_pe = circ.get("secao_pe_mm2", 2.5)
        y_info = y_disj - 0.8
        self.msp.add_text(f"# {s_fase} mm²", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.10}).set_placement((x + 0.15, y_info), align=TextEntityAlignment.MIDDLE_LEFT)
        self.msp.add_text(f"PE: {s_pe} mm²", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.09}).set_placement((x + 0.15, y_info - 0.25), align=TextEntityAlignment.MIDDLE_LEFT)
        self.msp.add_text(f"ΔU: {circ.get('queda_tensao_percentual', 0)}%", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.09}).set_placement((x + 0.15, y_info - 0.50), align=TextEntityAlignment.MIDDLE_LEFT)

        # Círculo/Seta de Carga no final
        self.msp.add_circle((x, y_fim), 0.20, dxfattribs={"layer": "UNIFILAR_CIRCUITOS"})
        
        # Descrição da Carga e Potência (Rotacionado a 90 graus para caber limpo)
        desc = circ.get("descricao", "")
        if len(desc) > 28:
            desc = desc[:26] + ".."
        pot_info = f"{circ.get('potencia_va', 0)} VA ({circ.get('potencia_w', 0)}W)"
        
        txt_desc = self.msp.add_text(desc, dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.09, "rotation": 270})
        txt_desc.set_placement((x - 0.05, y_fim - 0.4), align=TextEntityAlignment.TOP_LEFT)
        
        txt_pot = self.msp.add_text(pot_info, dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.08, "rotation": 270})
        txt_pot.set_placement((x + 0.15, y_fim - 0.4), align=TextEntityAlignment.TOP_LEFT)

    def _desenhar_tabela_quadro_cargas(self, x0: float, y0: float, circuitos: List[Dict[str, Any]]):
        """Desenha a planilha técnica do Quadro de Cargas da NBR 5410 em DXF."""
        larguras = [1.2, 5.0, 1.4, 1.4, 1.4, 1.4, 1.6, 1.6, 1.6, 1.8]
        colunas = ["CIRC", "DESCRIÇÃO DA CARGA", "TENSÃO", "FASE", "POT (VA)", "POT (W)", "CORR (A)", "COND (mm²)", "DISJ (A)", "ELETRODUTO"]
        w_tot = sum(larguras)
        h_linha = 0.45
        
        # Título da Tabela
        top_y = y0 + 1.0
        self.msp.add_text("QUADRO DE DISTRIBUIÇÃO DE CARGAS RESIDENCIAL - ABNT NBR 5410:2004", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.18}).set_placement((x0 + w_tot/2.0, top_y), align=TextEntityAlignment.MIDDLE_CENTER)

        # Cabeçalho
        y_curr = y0
        self.msp.add_lwpolyline([(x0, y_curr), (x0 + w_tot, y_curr), (x0 + w_tot, y_curr - h_linha), (x0, y_curr - h_linha), (x0, y_curr)], dxfattribs={"layer": "UNIFILAR_TABELAS", "closed": True})
        
        cx = x0
        for i, col in enumerate(colunas):
            self.msp.add_text(col, dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.10}).set_placement((cx + larguras[i]/2.0, y_curr - h_linha/2.0), align=TextEntityAlignment.MIDDLE_CENTER)
            cx += larguras[i]
            if i < len(colunas) - 1:
                self.msp.add_line((cx, y_curr), (cx, y_curr - (len(circuitos) + 1) * h_linha), dxfattribs={"layer": "UNIFILAR_TABELAS"})

        # Linhas de cada circuito
        for circ in circuitos:
            y_curr -= h_linha
            self.msp.add_line((x0, y_curr), (x0 + w_tot, y_curr), dxfattribs={"layer": "UNIFILAR_TABELAS"})
            
            valores = [
                f"C{circ['numero']}",
                circ.get("descricao", "")[:28],
                f"{circ.get('tensao_v', 127)}V",
                "/".join(circ.get("fases", ["R"])),
                f"{circ.get('potencia_va', 0)}",
                f"{circ.get('potencia_w', 0)}",
                f"{circ.get('corrente_projeto_ib', 0)}",
                f"{circ.get('secao_condutor_mm2', 2.5)}",
                f"{circ.get('disjuntor_in_a', 16)}A",
                f"DN {circ.get('eletroduto_trecho_dn_mm', 20)}mm"
            ]
            cx = x0
            for i, val in enumerate(valores):
                alinh = TextEntityAlignment.MIDDLE_LEFT if i == 1 else TextEntityAlignment.MIDDLE_CENTER
                px = cx + 0.15 if i == 1 else cx + larguras[i]/2.0
                self.msp.add_text(val, dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.09}).set_placement((px, y_curr - h_linha/2.0), align=alinh)
                cx += larguras[i]

        # Fechamento inferior da tabela
        self.msp.add_line((x0, y_curr - h_linha), (x0 + w_tot, y_curr - h_linha), dxfattribs={"layer": "UNIFILAR_TABELAS"})

    def _desenhar_moldura_e_carimbo(self, largura_util: float):
        """Moldura e Carimbo A1."""
        x0, y0 = -2.0, -18.5
        w_total = max(34.0, largura_util + 10.0)
        h_total = 34.0
        
        self.msp.add_lwpolyline([(x0, y0), (x0 + w_total, y0), (x0 + w_total, y0 + h_total), (x0, y0 + h_total), (x0, y0)], dxfattribs={"layer": "PRANCHA_MOLDURA", "closed": True})
        
        cb_w, cb_h = 7.5, 2.5
        cb_x = x0 + w_total - 0.4 - cb_w
        cb_y = y0 + 0.4
        
        self.msp.add_lwpolyline([(cb_x, cb_y), (cb_x + cb_w, cb_y), (cb_x + cb_w, cb_y + cb_h), (cb_x, cb_y + cb_h), (cb_x, cb_y)], dxfattribs={"layer": "PRANCHA_CARIMBO", "closed": True})
        self.msp.add_text("SISTEMA ANTIGRAVITY - ENGENHARIA ELÉTRICA", dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.16}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.35), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("DIAGRAMA UNIFILAR QDC E QUADRO DE CARGAS", dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.14}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.75), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("PRANCHA: ELE-02/02 | ESCALA: INDICADA | NBR 5410:2004", dxfattribs={"layer": "UNIFILAR_TEXTOS", "height": 0.10}).set_placement((cb_x + 0.3, cb_y + 0.45), align=TextEntityAlignment.MIDDLE_LEFT)
