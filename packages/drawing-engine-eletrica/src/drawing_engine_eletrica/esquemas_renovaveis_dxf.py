"""
Motor Gráfico 2D CAD em DXF para Montagem e Esquemas de Energias Renováveis
Gera pranchas técnicas em DXF para:
1. Usina Solar Fotovoltaica (Estrutura de fixação, strings e diagrama unifilar)
2. Aerogerador Eólico (Fundação, torre, nacele, pás e painel com dump load)
3. Biodigestor Rural e Casa de Força de Biogás CHP (Corte da vala PEAD, linha de gás, filtro e motogerador)
"""

import os
import math
from typing import Dict, List, Any, Tuple
import ezdxf
from ezdxf.enums import TextEntityAlignment

class GeradorEsquemasRenovaveisDXF:
    """Gera arquivos DXF técnicos de alta fidelidade para sistemas de energias renováveis e biogás."""

    def __init__(self, dados_cenario: Dict[str, Any]):
        self.dados = dados_cenario
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self._configurar_layers()

    def _configurar_layers(self):
        layers = [
            ("ESTRUTURA_MONTAGEM", 7, 0.40),   # Branco (Perfis, vigas, fundação)
            ("SOLAR_PAINEIS", 2, 0.35),        # Amarelo (Módulos fotovoltaicos)
            ("EOLICA_ROTOR", 4, 0.35),         # Ciano (Pás e torre eólica)
            ("BIODIGESTOR_PEAD", 1, 0.40),     # Vermelho (Geomembrana e vala)
            ("TUBULACOES_GAS", 6, 0.35),       # Magenta (Linha de biogás e drenos)
            ("ELETRICA_CABOS", 3, 0.30),       # Verde (Condutores e barramentos)
            ("TEXTOS_COTAS", 7, 0.20),         # Branco (Textos e cotas de projeto)
            ("PRANCHA_MOLDURA", 7, 0.50),      # Moldura A1
            ("PRANCHA_CARIMBO", 7, 0.25),      # Carimbo técnico
        ]
        for nome, cor, lw in layers:
            if nome not in self.doc.layers:
                self.doc.layers.add(name=nome, color=cor, lineweight=int(lw * 100))

    def gerar_dxf_solar(self, caminho_arquivo: str) -> str:
        """Prancha técnica com Detalhe de Montagem dos Módulos e Diagrama Unifilar Solar."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        self._configurar_layers()
        
        # 1. Desenho de Montagem Estrutural dos Módulos Fotovoltaicos (Escala métrica)
        x0, y0 = 0.0, 10.0
        # Inclinação de 18° norte
        # Desenhar perfis de alumínio e suporte triangular
        ang_rad = math.radians(18.0)
        comp_mesa = 4.8
        dx = comp_mesa * math.cos(ang_rad)
        dy = comp_mesa * math.sin(ang_rad)

        # Suporte estrutural (Triângulo em alumínio)
        self.msp.add_line((x0, y0), (x0 + dx, y0 + dy), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_line((x0, y0), (x0 + dx, y0), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_line((x0 + dx, y0), (x0 + dx, y0 + dy), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_text("Estrutura Triangular em Alumínio 6063-T6 (Inclinação 18° Norte)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.16}).set_placement((x0, y0 - 0.4), align=TextEntityAlignment.MIDDLE_LEFT)

        # Módulos fotovoltaicos sobre os trilhos (2 módulos em retrato de 2,28m)
        num_mods = 4
        for i in range(num_mods):
            mx = x0 + (i * 1.15) * math.cos(ang_rad)
            my = y0 + (i * 1.15) * math.sin(ang_rad)
            # Retângulo inclinado do módulo
            self.msp.add_lwpolyline([
                (mx, my), (mx + 1.13 * math.cos(ang_rad), my + 1.13 * math.sin(ang_rad)),
                (mx + 1.13 * math.cos(ang_rad) - 0.05 * math.sin(ang_rad), my + 1.13 * math.sin(ang_rad) + 0.05 * math.cos(ang_rad)),
                (mx - 0.05 * math.sin(ang_rad), my + 0.05 * math.cos(ang_rad)), (mx, my)
            ], dxfattribs={"layer": "SOLAR_PAINEIS", "closed": True})
            # Grampo de fixação intermediário
            self.msp.add_circle((mx, my + 0.05), 0.04, dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})

        self.msp.add_text("Módulos Fotovoltaicos 550W Half-Cell Monocristalino com Grampos Mid/End Clamp", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.14}).set_placement((x0 + 0.5, y0 + dy + 0.5), align=TextEntityAlignment.MIDDLE_LEFT)

        # 2. Diagrama Unifilar Elétrico da Usina Solar Fotovoltaica
        ux, uy = 8.0, 12.0
        # Módulos em String
        self.msp.add_lwpolyline([(ux, uy), (ux + 3.0, uy), (ux + 3.0, uy - 1.5), (ux, uy - 1.5), (ux, uy)], dxfattribs={"layer": "SOLAR_PAINEIS", "closed": True})
        self.msp.add_text("ARRANJO DE STRINGS CC\n(Vmp=420V / Isc=14A)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.13}).set_placement((ux + 1.5, uy - 0.75), align=TextEntityAlignment.MIDDLE_CENTER)

        # Linha CC até a String Box
        self.msp.add_line((ux + 3.0, uy - 0.75), (ux + 4.5, uy - 0.75), dxfattribs={"layer": "ELETRICA_CABOS"})
        self.msp.add_text("Cabo Solar #6mm² 1.8kV (Preto/Verm)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.09}).set_placement((ux + 3.1, uy - 0.55), align=TextEntityAlignment.MIDDLE_LEFT)

        # String Box CC
        sb_x, sb_y = ux + 4.5, uy
        self.msp.add_lwpolyline([(sb_x, sb_y), (sb_x + 2.5, sb_y), (sb_x + 2.5, sb_y - 2.5), (sb_x, sb_y - 2.5), (sb_x, sb_y)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("STRING BOX CC\n• Fusíveis gPV 20A\n• Chave Seccionadora 32A\n• DPS CC Cl.II 1000V", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((sb_x + 1.25, sb_y - 1.25), align=TextEntityAlignment.MIDDLE_CENTER)

        # Linha até o Inversor
        self.msp.add_line((sb_x + 2.5, uy - 0.75), (sb_x + 4.0, uy - 0.75), dxfattribs={"layer": "ELETRICA_CABOS"})

        # Inversor Grid-Tie
        inv_x, inv_y = sb_x + 4.0, uy + 0.3
        self.msp.add_lwpolyline([(inv_x, inv_y), (inv_x + 3.0, inv_y), (inv_x + 3.0, inv_y - 3.0), (inv_x, inv_y - 3.0), (inv_x, inv_y)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_line((inv_x, inv_y), (inv_x + 3.0, inv_y - 3.0), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_text("INVERSOR GRID-TIE MPPT\nCC / CA\n(NBR 16149 / Anti-ilhamento)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((inv_x + 1.5, inv_y - 1.5), align=TextEntityAlignment.MIDDLE_CENTER)

        # Saída CA até o QDC
        self.msp.add_line((inv_x + 3.0, uy - 0.75), (inv_x + 5.5, uy - 0.75), dxfattribs={"layer": "ELETRICA_CABOS"})
        self.msp.add_text("INTERLIGAÇÃO AO QDC GERAL\nDisjuntor Bipolar/Tripolar DIN + DPS CA", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.12}).set_placement((inv_x + 5.7, uy - 0.75), align=TextEntityAlignment.MIDDLE_LEFT)

        # Moldura e Carimbo
        self._desenhar_moldura_e_carimbo("PROJETO EXECUTIVO SOLAR FOTOVOLTAICO - NBR 16690 / LEI 14.300")
        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo

    def gerar_dxf_eolica(self, caminho_arquivo: str) -> str:
        """Prancha técnica com Detalhe de Montagem da Turbina Eólica e Fundação."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        self._configurar_layers()

        # Desenho da Torre e Turbina (Escala proporcional)
        bx, by = 6.0, 2.0
        # Fundação de concreto
        self.msp.add_lwpolyline([(bx - 2.0, by), (bx + 2.0, by), (bx + 2.0, by - 1.2), (bx - 2.0, by - 1.2), (bx - 2.0, by)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("BLOCO DE CONCRETO ARMADO FCK 30 MPa\n(Chumbadores de Aço ASTM A36)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.12}).set_placement((bx, by - 0.6), align=TextEntityAlignment.MIDDLE_CENTER)

        # Torre Tubular de Aço (h=14m no desenho)
        h_torre = 14.0
        self.msp.add_line((bx - 0.4, by), (bx - 0.15, by + h_torre), dxfattribs={"layer": "EOLICA_ROTOR"})
        self.msp.add_line((bx + 0.4, by), (bx + 0.15, by + h_torre), dxfattribs={"layer": "EOLICA_ROTOR"})

        # Estais de aço
        self.msp.add_line((bx - 0.25, by + h_torre * 0.7), (bx - 4.5, by), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_line((bx + 0.25, by + h_torre * 0.7), (bx + 4.5, by), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_text("Cabo de Aço Galvanizado 3/8\" com Esticadores", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((bx + 2.5, by + 4.0), align=TextEntityAlignment.MIDDLE_LEFT)

        # Nacele e Gerador PMSG
        ny = by + h_torre
        self.msp.add_lwpolyline([(bx - 0.5, ny), (bx + 0.9, ny), (bx + 0.9, ny + 0.8), (bx - 0.5, ny + 0.8), (bx - 0.5, ny)], dxfattribs={"layer": "EOLICA_ROTOR", "closed": True})
        self.msp.add_text("NACELE / GERADOR PMSG DIRECT DRIVE", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((bx + 0.2, ny + 1.1), align=TextEntityAlignment.MIDDLE_CENTER)

        # Rotor com 3 pás
        raio_pa = 4.2
        # Cubo central
        self.msp.add_circle((bx - 0.5, ny + 0.4), 0.35, dxfattribs={"layer": "EOLICA_ROTOR"})
        # Pá 1 (para cima)
        self.msp.add_line((bx - 0.5, ny + 0.75), (bx - 0.5, ny + 0.75 + raio_pa), dxfattribs={"layer": "EOLICA_ROTOR"})
        # Pá 2 (120°)
        ang2 = math.radians(210)
        self.msp.add_line((bx - 0.5, ny + 0.4), (bx - 0.5 + raio_pa * math.cos(ang2), ny + 0.4 + raio_pa * math.sin(ang2)), dxfattribs={"layer": "EOLICA_ROTOR"})
        # Pá 3 (240°)
        ang3 = math.radians(330)
        self.msp.add_line((bx - 0.5, ny + 0.4), (bx - 0.5 + raio_pa * math.cos(ang3), ny + 0.4 + raio_pa * math.sin(ang3)), dxfattribs={"layer": "EOLICA_ROTOR"})

        # Leme de Cauda
        self.msp.add_line((bx + 0.9, ny + 0.4), (bx + 2.5, ny + 0.4), dxfattribs={"layer": "EOLICA_ROTOR"})
        self.msp.add_lwpolyline([(bx + 2.5, ny + 0.1), (bx + 3.2, ny + 0.1), (bx + 3.2, ny + 0.8), (bx + 2.5, ny + 0.6), (bx + 2.5, ny + 0.1)], dxfattribs={"layer": "EOLICA_ROTOR", "closed": True})

        # Painel Elétrico de Controle e Dump Load
        px, py = 14.0, 8.0
        self.msp.add_lwpolyline([(px, py), (px + 4.5, py), (px + 4.5, py - 4.5), (px, py - 4.5), (px, py)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("PAINEL DE CONTROLE EÓLICO\n• Retificador Trifásico CA/CC\n• Controlador MPPT de Vento\n• Resistência de Frenagem (Dump Load)\n• Chave de Parada de Emergência", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.13}).set_placement((px + 2.25, py - 2.25), align=TextEntityAlignment.MIDDLE_CENTER)

        self._desenhar_moldura_e_carimbo("PROJETO EXECUTIVO DE AEROGERADOR - NBR IEC 61400-2")
        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo

    def gerar_dxf_biodigestor(self, caminho_arquivo: str) -> str:
        """Prancha técnica com Corte Esquemático do Biodigestor Tubular PEAD e Usina a Biogás."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        self._configurar_layers()

        # 1. Corte Esquemático do Biodigestor Canadense em Vala Trapezoidal
        vx, vy = 1.0, 6.0
        # Caixa de Entrada / Carga (Alvenaria)
        self.msp.add_lwpolyline([(vx, vy + 1.2), (vx + 1.4, vy + 1.2), (vx + 1.4, vy - 0.8), (vx, vy - 0.8), (vx, vy + 1.2)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("CAIXA DE CARGA\n(Dejetos + Água)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((vx + 0.7, vy + 0.2), align=TextEntityAlignment.MIDDLE_CENTER)

        # Tubo de entrada PEAD inclinado
        self.msp.add_line((vx + 1.4, vy - 0.2), (vx + 3.2, vy - 2.2), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})

        # Vala Trapezoidal do Biodigestor (Lona PEAD 1,5mm)
        # Talude 1:1, fundo plano
        v_fundo = vy - 3.0
        v_topo = vy + 0.5
        v_larg = 14.0
        pts_vala = [
            (vx + 2.5, v_topo),
            (vx + 5.5, v_fundo),
            (vx + 5.5 + v_larg, v_fundo),
            (vx + 8.5 + v_larg, v_topo)
        ]
        self.msp.add_lwpolyline(pts_vala, dxfattribs={"layer": "BIODIGESTOR_PEAD"})
        self.msp.add_text("GEOMEMBRANA PEAD 1,5mm (Impermeabilização Inferior)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.12}).set_placement((vx + 5.5 + v_larg/2, v_fundo - 0.4), align=TextEntityAlignment.MIDDLE_CENTER)

        # Nível de Lodo / Líquido em Digestão
        self.msp.add_line((vx + 3.0, vy), (vx + 8.0 + v_larg, vy), dxfattribs={"layer": "BIODIGESTOR_PEAD", "linetype": "DASHED"})
        self.msp.add_text("NÍVEL DE LÍQUIDO EM DIGESTÃO ANAERÓBIA (TRH = 30 DIAS)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((vx + 5.5 + v_larg/2, vy - 0.5), align=TextEntityAlignment.MIDDLE_CENTER)

        # Cúpula Inflável do Gasômetro (Arco de Lona Superior)
        # Arco representando a lona inflada com biogás acumulado
        cx_centro = vx + 5.5 + v_larg/2
        self.msp.add_arc(
            (cx_centro, vy),
            v_larg/2 + 1.5,
            start_angle=10,
            end_angle=170,
            dxfattribs={"layer": "BIODIGESTOR_PEAD"}
        )
        self.msp.add_text("GASÔMETRO FLEXÍVEL (BIOGÁS 65% CH4 SOB PRESSÃO 15 mbar)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.13}).set_placement((cx_centro, vy + 4.2), align=TextEntityAlignment.MIDDLE_CENTER)

        # Caixa de Saída / Descarga de Biofertilizante
        sx = vx + 8.5 + v_larg
        self.msp.add_lwpolyline([(sx, vy + 1.0), (sx + 1.4, vy + 1.0), (sx + 1.4, vy - 0.8), (sx, vy - 0.8), (sx, vy + 1.0)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("SAÍDA DE BIOFERTILIZANTE\n(Rico em N, P, K)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((sx + 0.7, vy + 0.1), align=TextEntityAlignment.MIDDLE_CENTER)

        # 2. Linha de Gás, Tratamento e Motogerador CHP
        # Tubo saindo do topo da cúpula
        gy = vy + 6.0
        self.msp.add_line((cx_centro, vy + 5.5), (cx_centro, gy), dxfattribs={"layer": "TUBULACOES_GAS"})
        self.msp.add_line((cx_centro, gy), (cx_centro + 6.0, gy), dxfattribs={"layer": "TUBULACOES_GAS"})

        # Válvula de Alívio / Selo d'Água e Queimador Flare
        self.msp.add_line((cx_centro + 2.0, gy), (cx_centro + 2.0, gy + 1.5), dxfattribs={"layer": "TUBULACOES_GAS"})
        self.msp.add_text("FLARE DE SEGURANÇA\n(Queimador Automático)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.09}).set_placement((cx_centro + 2.0, gy + 1.8), align=TextEntityAlignment.MIDDLE_CENTER)

        # Filtro Dessulfurizador de H2S
        fx = cx_centro + 6.0
        self.msp.add_lwpolyline([(fx, gy + 1.0), (fx + 1.2, gy + 1.0), (fx + 1.2, gy - 1.0), (fx, gy - 1.0), (fx, gy + 1.0)], dxfattribs={"layer": "TUBULACOES_GAS", "closed": True})
        self.msp.add_text("FILTRO DESSULFURIZADOR\n(Remoção de H2S com Óxido de Ferro)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((fx + 0.6, gy - 1.3), align=TextEntityAlignment.MIDDLE_CENTER)

        # Dreno de Condensado
        self.msp.add_line((fx + 1.2, gy), (fx + 2.5, gy), dxfattribs={"layer": "TUBULACOES_GAS"})
        self.msp.add_circle((fx + 2.0, gy - 0.4), 0.2, dxfattribs={"layer": "TUBULACOES_GAS"})
        self.msp.add_text("Purgador de Água", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.08}).set_placement((fx + 2.0, gy - 0.75), align=TextEntityAlignment.MIDDLE_CENTER)

        # Casa de Força / Motogerador a Biogás (Ciclo Otto) com Cogeração CHP
        gx, gy_casa = fx + 3.0, gy - 2.5
        self.msp.add_lwpolyline([(gx, gy_casa + 3.5), (gx + 5.0, gy_casa + 3.5), (gx + 5.0, gy_casa - 1.0), (gx, gy_casa - 1.0), (gx, gy_casa + 3.5)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        
        # Símbolo do Motor e Alternador
        self.msp.add_circle((gx + 1.5, gy_casa + 1.2), 0.7, dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_circle((gx + 3.2, gy_casa + 1.2), 0.6, dxfattribs={"layer": "ELETRICA_CABOS"})
        self.msp.add_text("M", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.25}).set_placement((gx + 1.5, gy_casa + 1.2), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("G", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.22}).set_placement((gx + 3.2, gy_casa + 1.2), align=TextEntityAlignment.MIDDLE_CENTER)

        self.msp.add_text("GRUPO MOTOGERADOR A BIOGÁS\n• Alternador Síncrono 380V/220V\n• Painel de Paralelismo com a Rede\n• Trocador de Calor CHP (Água 88°C)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((gx + 2.5, gy_casa + 2.6), align=TextEntityAlignment.MIDDLE_CENTER)

        self._desenhar_moldura_e_carimbo("PROJETO EXECUTIVO BIODIGESTOR RURAL E USINA BIOGÁS CHP")
        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo

    def gerar_dxf_hidreletrica(self, caminho_arquivo: str) -> str:
        """Prancha técnica com Arranjo Geral de Micro-Hidrelétrica PCH Rural (Captação, Conduto e Casa de Força)."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        self._configurar_layers()

        # 1. Barramento de Captação e Desarenador (Nível Alto Y = 14m)
        x_cap, y_cap = 1.0, 14.0
        # Vertedouro e barramento
        self.msp.add_lwpolyline([(x_cap, y_cap), (x_cap + 3.0, y_cap), (x_cap + 2.5, y_cap - 2.5), (x_cap, y_cap - 2.5), (x_cap, y_cap)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("TOMADA D'ÁGUA & BARRAMENTO\n(Vertedouro com Grade e Comporta)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.12}).set_placement((x_cap + 1.5, y_cap + 0.6), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Desarenador e Caixa de Carga
        x_des = x_cap + 4.0
        self.msp.add_lwpolyline([(x_des, y_cap), (x_des + 4.0, y_cap), (x_des + 4.0, y_cap - 2.0), (x_des, y_cap - 2.0), (x_des, y_cap)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("DESARENADOR / CAIXA DE CARGA\n• Retenção de areia e sedimentos\n• Vertedouro de excesso", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((x_des + 2.0, y_cap - 1.0), align=TextEntityAlignment.MIDDLE_CENTER)

        # 2. Conduto Forçado (Tubulação de Pressão inclinada em PEAD PN10)
        x_tub_ini, y_tub_ini = x_des + 4.0, y_cap - 1.2
        x_casa, y_casa = 22.0, 2.0
        
        # Traçado da tubulação
        self.msp.add_line((x_tub_ini, y_tub_ini), (x_casa, y_casa + 1.5), dxfattribs={"layer": "TUBULACOES_GAS"})
        self.msp.add_line((x_tub_ini, y_tub_ini - 0.3), (x_casa, y_casa + 1.2), dxfattribs={"layer": "TUBULACOES_GAS"})
        
        # Blocos de Ancoragem de Concreto ao longo do declive
        for t in [0.25, 0.50, 0.75]:
            bx = x_tub_ini + (x_casa - x_tub_ini) * t
            by = y_tub_ini + (y_casa + 1.35 - y_tub_ini) * t
            self.msp.add_lwpolyline([(bx - 0.4, by - 0.4), (bx + 0.4, by - 0.4), (bx + 0.4, by + 0.4), (bx - 0.4, by + 0.4), (bx - 0.4, by - 0.4)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
            self.msp.add_text("Bloco Ancoragem", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.08}).set_placement((bx, by - 0.65), align=TextEntityAlignment.MIDDLE_CENTER)

        # Texto do conduto
        x_med = (x_tub_ini + x_casa) / 2.0
        y_med = (y_tub_ini + y_casa) / 2.0
        self.msp.add_text("CONDUTO FORÇADO PEAD PN10 DN 200 mm (Declive Topográfico)\nComprimento: 95m | Velocidade: 2,1 m/s", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.11}).set_placement((x_med, y_med + 1.2), align=TextEntityAlignment.MIDDLE_CENTER)

        # 3. Casa de Força Técnica e Turbina Hidráulica
        cx, cy = x_casa, y_casa - 1.0
        self.msp.add_lwpolyline([(cx, cy), (cx + 8.5, cy), (cx + 8.5, cy + 4.5), (cx, cy + 4.5), (cx, cy)], dxfattribs={"layer": "ESTRUTURA_MONTAGEM", "closed": True})
        self.msp.add_text("CASA DE FORÇA TÉCNICA (PCH RURAL)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.13}).set_placement((cx + 4.25, cy + 4.1), align=TextEntityAlignment.MIDDLE_CENTER)

        # Válvula Borboleta de Segurança
        self.msp.add_circle((cx + 1.2, cy + 2.2), 0.35, dxfattribs={"layer": "TUBULACOES_GAS"})
        self.msp.add_text("Válvula\nBorboleta", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.08}).set_placement((cx + 1.2, cy + 1.5), align=TextEntityAlignment.MIDDLE_CENTER)

        # Turbina Pelton (Roda com pás/conchas)
        self.msp.add_circle((cx + 3.2, cy + 2.2), 0.75, dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            px1 = cx + 3.2 + 0.5 * math.cos(rad)
            py1 = cy + 2.2 + 0.5 * math.sin(rad)
            px2 = cx + 3.2 + 0.75 * math.cos(rad)
            py2 = cy + 2.2 + 0.75 * math.sin(rad)
            self.msp.add_line((px1, py1), (px2, py2), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"})
        self.msp.add_text("TURBINA PELTON\n(Injetor Agulha)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.09}).set_placement((cx + 3.2, cy + 0.9), align=TextEntityAlignment.MIDDLE_CENTER)

        # Eixo e Gerador Síncrono Trifásico
        self.msp.add_line((cx + 3.95, cy + 2.2), (cx + 4.8, cy + 2.2), dxfattribs={"layer": "ESTRUTURA_MONTAGEM"}) # Acoplamento
        self.msp.add_circle((cx + 5.5, cy + 2.2), 0.70, dxfattribs={"layer": "ELETRICA_CABOS"})
        self.msp.add_text("G", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.30}).set_placement((cx + 5.5, cy + 2.2), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("GERADOR SÍNCRONO\n380V/220V 60Hz 1800 RPM", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.09}).set_placement((cx + 5.5, cy + 0.9), align=TextEntityAlignment.MIDDLE_CENTER)

        # Painel Regulador ELC (Electronic Load Controller)
        self.msp.add_lwpolyline([(cx + 6.8, cy + 1.2), (cx + 7.8, cy + 1.2), (cx + 7.8, cy + 3.2), (cx + 6.8, cy + 3.2), (cx + 6.8, cy + 1.2)], dxfattribs={"layer": "ELETRICA_CABOS", "closed": True})
        self.msp.add_text("PAINEL ELC\nRegulador\nde Carga", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.08}).set_placement((cx + 7.3, cy + 2.2), align=TextEntityAlignment.MIDDLE_CENTER)

        # Canal de Fuga / Restituição ao Curso d'Água
        self.msp.add_lwpolyline([(cx + 3.2, cy), (cx + 3.2, cy - 1.5), (cx + 7.0, cy - 1.5), (cx + 7.0, cy)], dxfattribs={"layer": "TUBULACOES_GAS"})
        self.msp.add_text("CANAL DE FUGA (Restituição ao Rio sem consumo d'água)", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.09}).set_placement((cx + 5.0, cy - 1.8), align=TextEntityAlignment.MIDDLE_CENTER)

        self._desenhar_moldura_e_carimbo("PROJETO EXECUTIVO MICRO-HIDRELÉTRICA PCH RURAL (LEI 14.300)")
        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo

    def _desenhar_moldura_e_carimbo(self, titulo_prancha: str):
        """Moldura e Carimbo A1."""
        x0, y0 = -1.0, -5.0
        w_tot, h_tot = 34.0, 20.0
        self.msp.add_lwpolyline([(x0, y0), (x0 + w_tot, y0), (x0 + w_tot, y0 + h_tot), (x0, y0 + h_tot), (x0, y0)], dxfattribs={"layer": "PRANCHA_MOLDURA", "closed": True})
        
        cb_w, cb_h = 8.0, 2.8
        cb_x = x0 + w_tot - 0.4 - cb_w
        cb_y = y0 + 0.4
        self.msp.add_lwpolyline([(cb_x, cb_y), (cb_x + cb_w, cb_y), (cb_x + cb_w, cb_y + cb_h), (cb_x, cb_y + cb_h), (cb_x, cb_y)], dxfattribs={"layer": "PRANCHA_CARIMBO", "closed": True})
        self.msp.add_text("SISTEMA ANTIGRAVITY - ENERGIAS RENOVÁVEIS", dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.16}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.4), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text(titulo_prancha, dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.13}).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.85), align=TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text("ESCALA: INDICADA | MARCO LEGAL GD (LEI 14.300) | ABNT", dxfattribs={"layer": "TEXTOS_COTAS", "height": 0.10}).set_placement((cb_x + 0.3, cb_y + 0.5), align=TextEntityAlignment.MIDDLE_LEFT)
