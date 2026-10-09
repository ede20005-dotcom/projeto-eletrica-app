"""
Motor Gráfico 2D CAD em DXF para Diagrama Multifilar de Stringbox Solar CC
Conforme ABNT NBR 16690:2019, IEC 60269-6, IEC 61643-31 e IEC 60947-3
Desenha o circuito elétrico interno da Stringbox CC, fusíveis gPV, chave seccionadora, DPS em Y e BEP.
"""

import os
import math
from typing import Dict, List, Any, Tuple
import ezdxf
from ezdxf.enums import TextEntityAlignment

class GeradorDiagramaStringboxDXF:
    """Gera prancha técnica DXF do diagrama multifilar da caixa de junção fotovoltaica (Stringbox CC)."""

    def __init__(self, dados_stringbox: Dict[str, Any]):
        self.dados = dados_stringbox
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self._configurar_layers()

    def _configurar_layers(self):
        layers = [
            ("POLO_POSITIVO", 1, 0.40),        # Vermelho (Condutores CC +)
            ("POLO_NEGATIVO", 8, 0.40),        # Preto / Cinza Escuro (Condutores CC -)
            ("TERRA_PROTECAO", 3, 0.40),       # Verde (Condutor PE e barramento BEP)
            ("INVÓLUCRO_STRINGBOX", 7, 0.40),  # Branco (Caixa termoplástica IP65)
            ("COMPONENTES_DIN", 4, 0.35),      # Ciano (Fusíveis, seccionadora, DPS)
            ("SIMBOLOS_SOLAR", 2, 0.35),       # Amarelo (Módulos solares)
            ("TEXTOS_COTAS", 7, 0.20),         # Branco (Identificação e especificações)
            ("PRANCHA_MOLDURA", 7, 0.50),      # Moldura A1
            ("PRANCHA_CARIMBO", 7, 0.25),      # Carimbo técnico
        ]
        for nome, cor, lw in layers:
            if nome not in self.doc.layers:
                self.doc.layers.add(name=nome, color=cor, lineweight=int(lw * 100))

    def gerar_dxf(self, caminho_arquivo: str) -> str:
        """Desenha o diagrama multifilar da Stringbox CC."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        self._configurar_layers()

        # 1. Desenho dos Arranjos / Strings Fotovoltaicos à Esquerda
        x_mod, y_mod = 2.0, 10.0
        # String 1
        self.msp.add_lwpolyline([(x_mod, y_mod + 3.0), (x_mod + 2.5, y_mod + 3.0), (x_mod + 2.5, y_mod + 1.2), (x_mod, y_mod + 1.2), (x_mod, y_mod + 3.0)], dxfattribs={"layer": "SIMBOLOS_SOLAR", "closed": True})
        self.msp.add_line((x_mod + 0.8, y_mod + 1.2), (x_mod + 0.8, y_mod + 3.0), dxfattribs={"layer": "SIMBOLOS_SOLAR"})
        self.msp.add_line((x_mod + 1.7, y_mod + 1.2), (x_mod + 1.7, y_mod + 3.0), dxfattribs={"layer": "SIMBOLOS_SOLAR"})
        self.msp.add_text("ARRANJO SOLAR STRING 1\n(18 Módulos em Série 550W)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((x_mod + 1.25, y_mod + 3.4), align=TextEntityAlignment.MIDDLE_CENTER)

        # String 2
        self.msp.add_lwpolyline([(x_mod, y_mod - 2.5), (x_mod + 2.5, y_mod - 2.5), (x_mod + 2.5, y_mod - 4.3), (x_mod, y_mod - 4.3), (x_mod, y_mod - 2.5)], dxfattribs={"layer": "SIMBOLOS_SOLAR", "closed": True})
        self.msp.add_line((x_mod + 0.8, y_mod - 4.3), (x_mod + 0.8, y_mod - 2.5), dxfattribs={"layer": "SIMBOLOS_SOLAR"})
        self.msp.add_line((x_mod + 1.7, y_mod - 4.3), (x_mod + 1.7, y_mod - 2.5), dxfattribs={"layer": "SIMBOLOS_SOLAR"})
        self.msp.add_text("ARRANJO SOLAR STRING 2\n(18 Módulos em Série 550W)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((x_mod + 1.25, y_mod - 2.1), align=TextEntityAlignment.MIDDLE_CENTER)

        # 2. Invólucro da Stringbox CC (Caixa IP65)
        bx, by = 6.5, 3.5
        bw, bh = 14.5, 12.0
        self.msp.add_lwpolyline([(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh), (bx, by)], dxfattribs={"layer": "INVÓLUCRO_STRINGBOX", "closed": True})
        self.msp.add_text("STRINGBOX SOLAR CC (GRAU DE PROTEÇÃO IP65 / ANTI-UV)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.16}).set_placement((bx + bw/2.0, by + bh + 0.4), align=TextEntityAlignment.MIDDLE_CENTER)

        # 3. Barramento / Trilho de Entrada e Fusíveis gPV
        # Linha Positiva String 1 (Vermelha)
        y_s1_pos = by + 10.0
        y_s1_neg = by + 8.5
        y_s2_pos = by + 5.5
        y_s2_neg = by + 4.0

        # Condutores de entrada
        self.msp.add_line((x_mod + 2.5, y_mod + 2.6), (bx + 1.5, y_s1_pos), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((x_mod + 2.5, y_mod + 1.6), (bx + 1.5, y_s1_neg), dxfattribs={"layer": "POLO_NEGATIVO"})
        self.msp.add_line((x_mod + 2.5, y_mod - 2.9), (bx + 1.5, y_s2_pos), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((x_mod + 2.5, y_mod - 3.9), (bx + 1.5, y_s2_neg), dxfattribs={"layer": "POLO_NEGATIVO"})

        # Porta-Fusíveis gPV (Retângulos com linha interna)
        fx = bx + 1.8
        for fy, label in [(y_s1_pos, "+ FUSÍVEL gPV 20A 1000Vcc"), (y_s1_neg, "- FUSÍVEL gPV 20A 1000Vcc"),
                          (y_s2_pos, "+ FUSÍVEL gPV 20A 1000Vcc"), (y_s2_neg, "- FUSÍVEL gPV 20A 1000Vcc")]:
            self.msp.add_lwpolyline([(fx, fy + 0.35), (fx + 1.8, fy + 0.35), (fx + 1.8, fy - 0.35), (fx, fy - 0.35), (fx, fy + 0.35)], dxfattribs={"layer": "COMPONENTES_DIN", "closed": True})
            self.msp.add_line((fx + 0.9, fy - 0.35), (fx + 0.9, fy + 0.35), dxfattribs={"layer": "COMPONENTES_DIN"})
            self.msp.add_text(label, dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.08}).set_placement((fx + 0.9, fy + 0.45), align=TextEntityAlignment.MIDDLE_CENTER)

        # Paralelismo dos Barramentos CC
        px = fx + 3.2
        self.msp.add_line((fx + 1.8, y_s1_pos), (px, y_s1_pos), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((fx + 1.8, y_s2_pos), (px, y_s2_pos), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((px, y_s1_pos), (px, y_s2_pos), dxfattribs={"layer": "POLO_POSITIVO"}) # Barramento +

        self.msp.add_line((fx + 1.8, y_s1_neg), (px + 0.8, y_s1_neg), dxfattribs={"layer": "POLO_NEGATIVO"})
        self.msp.add_line((fx + 1.8, y_s2_neg), (px + 0.8, y_s2_neg), dxfattribs={"layer": "POLO_NEGATIVO"})
        self.msp.add_line((px + 0.8, y_s1_neg), (px + 0.8, y_s2_neg), dxfattribs={"layer": "POLO_NEGATIVO"}) # Barramento -

        # Ponto de derivação para DPS CC Classe II em Y
        dps_x = px + 2.2
        dps_y = by + 2.0
        self.msp.add_lwpolyline([(dps_x, dps_y), (dps_x + 3.2, dps_y), (dps_x + 3.2, dps_y + 3.5), (dps_x, dps_y + 3.5), (dps_x, dps_y)], dxfattribs={"layer": "COMPONENTES_DIN", "closed": True})
        self.msp.add_text("DPS CC CLASSE II (1000Vcc / 40kA)\nConfiguração em Y (3 Varistores)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.09}).set_placement((dps_x + 1.6, dps_y + 3.8), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Conexão do DPS aos barramentos e terra
        self.msp.add_line((px, y_s2_pos), (dps_x + 0.8, y_s2_pos), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((dps_x + 0.8, y_s2_pos), (dps_x + 0.8, dps_y + 3.5), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((px + 0.8, y_s2_neg), (dps_x + 2.4, y_s2_neg), dxfattribs={"layer": "POLO_NEGATIVO"})
        self.msp.add_line((dps_x + 2.4, y_s2_neg), (dps_x + 2.4, dps_y + 3.5), dxfattribs={"layer": "POLO_NEGATIVO"})

        # Aterramento do DPS até o Barramento BEP
        self.msp.add_line((dps_x + 1.6, dps_y), (dps_x + 1.6, by + 0.8), dxfattribs={"layer": "TERRA_PROTECAO"})

        # Barramento BEP no fundo da Stringbox
        bep_x1, bep_x2 = bx + 1.0, bx + bw - 1.0
        bep_y = by + 0.8
        self.msp.add_line((bep_x1, bep_y), (bep_x2, bep_y), dxfattribs={"layer": "TERRA_PROTECAO"})
        self.msp.add_text("BARRAMENTO DE EQUIPOTENCIALIZAÇÃO PRINCIPAL (BEP) — CONDUTOR VERDE 16 mm²", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((bx + bw/2.0, bep_y - 0.4), align=TextEntityAlignment.MIDDLE_CENTER)

        # 4. Chave Seccionadora Bipolar sob Carga CC (DC-PV2 1000Vcc)
        sec_x = px + 4.2
        sec_y_center = (y_s1_pos + y_s1_neg) / 2.0
        self.msp.add_lwpolyline([(sec_x, sec_y_center - 1.6), (sec_x + 2.8, sec_y_center - 1.6), (sec_x + 2.8, sec_y_center + 1.6), (sec_x, sec_y_center + 1.6), (sec_x, sec_y_center - 1.6)], dxfattribs={"layer": "COMPONENTES_DIN", "closed": True})
        self.msp.add_text("CHAVE SECCIONADORA CC\n(DC-PV2 63A 1000Vcc)\nManopla Rotativa LOTO", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.09}).set_placement((sec_x + 1.4, sec_y_center + 2.0), align=TextEntityAlignment.MIDDLE_CENTER)

        # Contatos seccionadora
        self.msp.add_line((px, y_s1_pos), (sec_x, y_s1_pos), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((px + 0.8, y_s1_neg), (sec_x, y_s1_neg), dxfattribs={"layer": "POLO_NEGATIVO"})

        # Saída da Seccionadora para o Inversor Solar
        out_x = bx + bw + 3.0
        self.msp.add_line((sec_x + 2.8, y_s1_pos), (out_x, y_s1_pos), dxfattribs={"layer": "POLO_POSITIVO"})
        self.msp.add_line((sec_x + 2.8, y_s1_neg), (out_x, y_s1_neg), dxfattribs={"layer": "POLO_NEGATIVO"})

        # Inversor Solar à Direita
        inv_w, inv_h = 4.5, 7.0
        inv_x = out_x
        inv_y = sec_y_center - inv_h / 2.0
        self.msp.add_lwpolyline([(inv_x, inv_y), (inv_x + inv_w, inv_y), (inv_x + inv_w, inv_y + inv_h), (inv_x, inv_y + inv_h), (inv_x, inv_y)], dxfattribs={"layer": "INVÓLUCRO_STRINGBOX", "closed": True})
        self.msp.add_text("INVERSOR SOLAR GRID-TIE\n(Trifásico 380V / MPPT Duplo)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.13}).set_placement((inv_x + inv_w/2.0, inv_y + inv_h/2.0), align=TextEntityAlignment.MIDDLE_CENTER)

        # Notas Técnicas e Normativas NBR 16690
        nx, ny = 2.0, 1.5
        notas = [
            "NOTAS TÉCNICAS E CRITÉRIOS DE PROJETO (ABNT NBR 16690:2019):",
            "1. Fusíveis gPV 10x38mm 1000Vcc obrigatórios em ambos os polos (+ e -) para isolamento galvânico de faltas.",
            "2. Chave seccionadora sob carga categoria DC-PV2 permite manutenção segura com o arranjo sob plena irradiação.",
            "3. DPS Classe II em circuito 'Y' evita queima da string em caso de surto atmosférico e conduz com segurança ao BEP.",
            "4. Condutores solares 1.8kVcc com isolação em XLPE resistente à radiação UV, ozônio e intempéries.",
            "5. Todas as estruturas metálicas de alumínio e carcaça da stringbox equipotencializadas ao barramento BEP."
        ]
        curr_ny = ny + 1.2
        for n in notas:
            self.msp.add_text(n, dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((nx, curr_ny), align=TextEntityAlignment.MIDDLE_LEFT)
            curr_ny -= 0.35

        # Carimbo e Moldura A1
        x0, y0 = -1.0, -1.5
        w_tot, h_tot = 35.0, 18.5
        self.msp.add_lwpolyline([(x0, y0), (x0 + w_tot, y0), (x0 + w_tot, y0 + h_tot), (x0, y0 + h_tot), (x0, y0)], dxfattribs={"layer": "PRANCHA_MOLDURA", "closed": True})
        
        cb_w, cb_h = 8.5, 2.6
        cb_x = x0 + w_tot - 0.4 - cb_w
        cb_y = y0 + 0.4
        self.msp.add_lwpolyline([(cb_x, cb_y), (cb_x + cb_w, cb_y), (cb_x + cb_w, cb_y + cb_h), (cb_x, cb_y + cb_h), (cb_x, cb_y)], dxfattribs={"layer": "PRANCHA_CARIMBO", "closed": True})
        self.msp.add_text("SISTEMA ANTIGRAVITY - ENERGIA SOLAR", dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.16}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.4), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("DIAGRAMA MULTIFILAR STRINGBOX SOLAR CC E PROTEÇÕES", dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.11}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.85), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("NORMAS: ABNT NBR 16690:2019 / IEC 60269-6 / IEC 61643-31", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((cb_x + 0.3, cb_y + 0.5), align=TextEntityAlignment.MIDDLE_LEFT)

        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo
