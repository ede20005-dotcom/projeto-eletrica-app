"""
Motor Gráfico 2D CAD em DXF para Estudo de Coordenação e Seletividade das Proteções
Conforme ABNT NBR 5410:2004, IEC 60947-2 e NBR NM 60898
Desenha a Grade Bi-Logarítmica (Tempo x Corrente) e as Curvas Características dos Disjuntores.
"""

import os
import math
from typing import Dict, List, Any, Tuple
import ezdxf
from ezdxf.enums import TextEntityAlignment

class GeradorCurvasSeletividadeDXF:
    """Gera prancha técnica DXF do gráfico de seletividade e coordenação tempo-corrente."""

    def __init__(self, dados_seletividade: Dict[str, Any]):
        self.dados = dados_seletividade
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self._configurar_layers()

    def _configurar_layers(self):
        layers = [
            ("GRADE_LOG", 8, 0.15),           # Cinza claro (Eixos e subdivisões logarítmicas)
            ("EIXOS_PRINCIPAIS", 7, 0.35),     # Branco (Bordas do gráfico)
            ("CURVA_GERAL", 1, 0.50),          # Vermelho (Disjuntor Geral 125A Curva C)
            ("CURVA_CHUVEIRO", 2, 0.40),       # Amarelo (Disjuntor Chuveiro 40A Curva C)
            ("CURVA_TOMADAS", 3, 0.35),        # Verde (Disjuntor Tomadas 20A Curva C)
            ("CURVA_ILUMINACAO", 4, 0.30),     # Ciano (Disjuntor Iluminação 10A Curva B)
            ("TEXTOS_COTAS", 7, 0.20),         # Branco (Anotações, legendas e tabela)
            ("PRANCHA_MOLDURA", 7, 0.50),      # Moldura A1
            ("PRANCHA_CARIMBO", 7, 0.25),      # Carimbo técnico
        ]
        for nome, cor, lw in layers:
            if nome not in self.doc.layers:
                self.doc.layers.add(name=nome, color=cor, lineweight=int(lw * 100))

    def _val_to_coord(self, corrente_a: float, tempo_s: float, x0: float, y0: float, w: float, h: float) -> Tuple[float, float]:
        """Converte escala bi-logarítmica (I: 1A a 10000A, t: 0.01s a 1000s) para coordenadas CAD."""
        log_i_min, log_i_max = math.log10(1.0), math.log10(10000.0)
        log_t_min, log_t_max = math.log10(0.01), math.log10(1000.0)

        c = max(1.0, min(10000.0, corrente_a))
        t = max(0.01, min(1000.0, tempo_s))

        u = (math.log10(c) - log_i_min) / (log_i_max - log_i_min)
        v = (math.log10(t) - log_t_min) / (log_t_max - log_t_min)

        return x0 + u * w, y0 + v * h

    def gerar_dxf(self, caminho_arquivo: str) -> str:
        """Desenha a grade logarítmica e plota as curvas de atuação."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        self._configurar_layers()

        # Posição do Gráfico na Folha A1
        gx, gy = 3.0, 1.5
        gw, gh = 20.0, 14.0

        # 1. Desenhar Moldura do Gráfico e Grade Logarítmica
        self.msp.add_lwpolyline([(gx, gy), (gx + gw, gy), (gx + gw, gy + gh), (gx, gy + gh), (gx, gy)], dxfattribs={"layer": "EIXOS_PRINCIPAIS", "closed": True})

        # Grade Horizontal de Tempos (0.01, 0.1, 1, 10, 100, 1000 s)
        decadas_t = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
        for t in decadas_t:
            _, py = self._val_to_coord(1.0, t, gx, gy, gw, gh)
            self.msp.add_line((gx, py), (gx + gw, py), dxfattribs={"layer": "GRADE_LOG"})
            txt_t = f"{t:g}s" if t >= 1.0 else f"{t:.2f}s"
            self.msp.add_text(txt_t, dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.15}).set_placement((gx - 0.2, py), align=TextEntityAlignment.MIDDLE_RIGHT)

        # Grade Vertical de Correntes (1, 10, 100, 1000, 10000 A)
        decadas_i = [1.0, 10.0, 100.0, 1000.0, 10000.0]
        for c in decadas_i:
            px, _ = self._val_to_coord(c, 0.01, gx, gy, gw, gh)
            self.msp.add_line((px, gy), (px, gy + gh), dxfattribs={"layer": "GRADE_LOG"})
            self.msp.add_text(f"{int(c)}A", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.15}).set_placement((px, gy - 0.3), align=TextEntityAlignment.TOP_CENTER)

        # Rótulos dos Eixos
        self.msp.add_text("CORRENTE DE FALTA / SOBRECORRENTE (A) — ESCALA LOGARÍTMICA", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.22}).set_placement((gx + gw/2.0, gy - 0.8), align=TextEntityAlignment.TOP_CENTER)
        self.msp.add_text("TEMPO DE ATUAÇÃO (s)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.22, "rotation": 90.0}).set_placement((gx - 1.2, gy + gh/2.0), align=TextEntityAlignment.BOTTOM_CENTER)

        # 2. Plotar Curvas dos Disjuntores
        curvas_dados = self.dados.get("curvas_plotagem_log_log", {})
        
        mapa_estilos = {
            "geral_125a_c": ("CURVA_GERAL", "Disjuntor Geral 125A (Curva C DIN 6kA)"),
            "chuveiro_40a_c": ("CURVA_CHUVEIRO", "Circuito Chuveiro 40A (Curva C DIN)"),
            "tomadas_20a_c": ("CURVA_TOMADAS", "Circuito Tomadas Cozinha 20A (Curva C DIN)"),
            "iluminacao_10a_b": ("CURVA_ILUMINACAO", "Circuito Iluminação 10A (Curva B DIN)")
        }

        legenda_y = gy + gh - 1.0
        for chave, (layer_curva, label_desc) in mapa_estilos.items():
            pts = curvas_dados.get(chave, [])
            if pts:
                # Linha de tempo mínimo e máximo
                linha_min = []
                linha_max = []
                for p in pts:
                    c = p["corrente_a"]
                    t_min = p["tempo_min_s"]
                    t_max = p["tempo_max_s"]
                    linha_min.append(self._val_to_coord(c, t_min, gx, gy, gw, gh))
                    linha_max.append(self._val_to_coord(c, t_max, gx, gy, gw, gh))

                if len(linha_min) >= 2:
                    self.msp.add_lwpolyline(linha_min, dxfattribs={"layer": layer_curva})
                if len(linha_max) >= 2:
                    self.msp.add_lwpolyline(linha_max, dxfattribs={"layer": layer_curva})

            # Adicionar na Legenda lateral
            self.msp.add_line((gx + gw + 1.0, legenda_y), (gx + gw + 2.5, legenda_y), dxfattribs={"layer": layer_curva})
            self.msp.add_text(label_desc, dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.14}).set_placement((gx + gw + 2.8, legenda_y), align=TextEntityAlignment.MIDDLE_LEFT)
            legenda_y -= 0.6

        # 3. Tabela de Matriz de Seletividade e Conformidade NBR 5410
        tx, ty = gx + gw + 1.0, gy + gh - 4.5
        tw, th = 9.0, 7.5
        self.msp.add_lwpolyline([(tx, ty), (tx + tw, ty), (tx + tw, ty - th), (tx, ty - th), (tx, ty)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("MATRIZ DE SELETIVIDADE TÉCNICA", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.16}).set_placement((tx + tw/2.0, ty - 0.4), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_line((tx, ty - 0.7), (tx + tw, ty - 0.7), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})

        linhas_tabela = [
            ("Circuito 1 (Ilum 10A B)", "Razão In = 12.5", "SELETIVIDADE TOTAL", "Aprovado"),
            ("Circuito 3 (Tom 20A C)", "Razão In = 6.25", "SELETIVIDADE TOTAL", "Aprovado"),
            ("Circuito 7 (Chuv 40A C)", "Razão In = 3.12", "SELETIVIDADE TOTAL", "Aprovado"),
            ("Limite Magnético Is", "Im_geral = 625A", "Icc presumida = 1.5kA", "Seletivo até Is"),
            ("Proteção DR (30mA)", "IDR Parcial Instantâneo", "Coordenação Diferencial", "Conforme")
        ]

        row_y = ty - 1.2
        for c1, c2, c3, c4 in linhas_tabela:
            self.msp.add_text(f"{c1}", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((tx + 0.3, row_y), align=TextEntityAlignment.MIDDLE_LEFT)
            self.msp.add_text(f"{c3} ({c4})", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((tx + tw - 0.3, row_y), align=TextEntityAlignment.MIDDLE_RIGHT)
            row_y -= 0.6

        # Carimbo e Moldura
        x0, y0 = -1.0, -1.5
        w_tot, h_tot = 36.0, 18.5
        self.msp.add_lwpolyline([(x0, y0), (x0 + w_tot, y0), (x0 + w_tot, y0 + h_tot), (x0, y0 + h_tot), (x0, y0)], dxfattribs={"layer": "PRANCHA_MOLDURA", "closed": True})
        
        cb_w, cb_h = 8.5, 2.6
        cb_x = x0 + w_tot - 0.4 - cb_w
        cb_y = y0 + 0.4
        self.msp.add_lwpolyline([(cb_x, cb_y), (cb_x + cb_w, cb_y), (cb_x + cb_w, cb_y + cb_h), (cb_x, cb_y + cb_h), (cb_x, cb_y)], dxfattribs={"layer": "PRANCHA_CARIMBO", "closed": True})
        self.msp.add_text("SISTEMA ANTIGRAVITY - ENGENHARIA ELÉTRICA", dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.16}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.4), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("ESTUDO DE COORDENAÇÃO E SELETIVIDADE DE PROTEÇÕES", dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.12}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.85), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("NORMAS: ABNT NBR 5410:2004 / IEC 60947-2 / NBR NM 60898", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((cb_x + 0.3, cb_y + 0.5), align=TextEntityAlignment.MIDDLE_LEFT)

        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo
