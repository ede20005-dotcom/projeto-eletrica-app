"""
Motor Gráfico 2D CAD em DXF para Instalações Elétricas Residenciais e Prediais
Gera prancha técnica com Planta Baixa, Eletrodutos, Pontos de Luz, Tomadas,
Interruptores e Simbologia NBR 5444 / NBR 5410.
"""

import math
import os
from typing import Dict, List, Any, Tuple, Optional
import ezdxf
from ezdxf.enums import TextEntityAlignment

class GeradorPlantaBaixaEletricaDXF:
    """Gera arquivos DXF técnicos de alta fidelidade para plantas elétricas residenciais."""
    
    def __init__(self, projeto_dados: Dict[str, Any]):
        self.projeto = projeto_dados
        self.doc = ezdxf.new(dxfversion="R2010")
        self.msp = self.doc.modelspace()
        self._configurar_layers()

    def _configurar_layers(self):
        """Configura as camadas com cores e espessuras padronizadas de desenho elétrico."""
        layers = [
            ("ARQ_PAREDES", 7, 0.35),          # Branco/Preto
            ("ARQ_PORTAS_JANELAS", 4, 0.18),   # Ciano
            ("ARQ_TEXTOS", 8, 0.18),           # Cinza
            ("ARQ_COTAS", 9, 0.15),            # Cinza Claro
            ("ELET_QDC", 6, 0.50),             # Magenta
            ("ELET_PONTOS_LUZ", 2, 0.35),      # Amarelo
            ("ELET_TOMADAS", 1, 0.30),         # Vermelho
            ("ELET_INTERRUPTORES", 3, 0.25),   # Verde
            ("ELET_ELETRODUTOS", 5, 0.35),     # Azul
            ("ELET_FIACAO_NBR5444", 7, 0.20),  # Branco
            ("ELET_TEXTOS", 2, 0.20),          # Amarelo
            ("PRANCHA_MOLDURA", 7, 0.50),      # Branco
            ("PRANCHA_CARIMBO", 7, 0.25),      # Branco
        ]
        for nome, cor, lineweight in layers:
            if nome not in self.doc.layers:
                self.doc.layers.add(name=nome, color=cor, lineweight=int(lineweight * 100))

    def gerar_dxf(self, caminho_arquivo: str):
        """Gera a prancha completa contendo arquitetura, elétrica, legenda e carimbo."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        
        # 1. Definir Geometria dos Cômodos da Planta Baixa (Escala 1:1 em metros)
        # Layout arquitetônico harmônico da residência:
        # Sala (0,0 a 5,4) | Varanda (0,-2.5 a 4,0) | Garagem (-4,0 a 0,5.5)
        # Cozinha (5,0 a 9,3.2) | Área Serviço (5,3.2 a 8,5.4)
        # Circulação (0,4 a 3,5.2) | Banheiro Social (3,4 a 5.6,5.6)
        # Dormitório 1 (0,5.2 a 3.5,8.4) | Dormitório 2 (3.5,5.6 a 7.0,8.6)
        # Suíte (7.0,5.4 a 11.0,8.9) | Banheiro Suíte (8.4,3.2 a 11.0,4.8)
        
        layout_comodos = {
            "c_garagem": {"x": -4.2, "y": 0.0, "w": 4.0, "h": 5.5, "nome": "GARAGEM COBERTA"},
            "c_varanda": {"x": 0.0, "y": -2.6, "w": 4.5, "h": 2.4, "nome": "VARANDA GOURMET"},
            "c_sala": {"x": 0.0, "y": 0.0, "w": 5.0, "h": 4.0, "nome": "SALA DE ESTAR / JANTAR"},
            "c_cozinha": {"x": 5.2, "y": 0.0, "w": 4.2, "h": 3.4, "nome": "COZINHA / COPA"},
            "c_servico": {"x": 5.2, "y": 3.6, "w": 3.0, "h": 2.2, "nome": "ÁREA DE SERVIÇO"},
            "c_hall": {"x": 0.0, "y": 4.2, "w": 3.2, "h": 1.4, "nome": "CIRCULAÇÃO"},
            "c_bwc_social": {"x": 3.4, "y": 4.2, "w": 1.6, "h": 2.6, "nome": "BWC SOCIAL"},
            "c_dorm1": {"x": 0.0, "y": 5.8, "w": 3.5, "h": 3.4, "nome": "DORMITÓRIO 1"},
            "c_dorm2": {"x": 3.7, "y": 6.0, "w": 3.5, "h": 3.2, "nome": "DORMITÓRIO 2"},
            "c_suite": {"x": 7.4, "y": 5.0, "w": 4.2, "h": 4.2, "nome": "DORMITÓRIO SUÍTE"},
            "c_bwc_suite": {"x": 8.4, "y": 2.6, "w": 2.6, "h": 2.2, "nome": "BWC SUÍTE"}
        }

        # Desenhar Paredes dos cômodos
        esp_parede = 0.15 # 15cm
        for cid, dados in layout_comodos.items():
            x, y, w, h = dados["x"], dados["y"], dados["w"], dados["h"]
            # Retângulo externo
            self.msp.add_lwpolyline(
                [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
                dxfattribs={"layer": "ARQ_PAREDES", "closed": True}
            )
            # Texto identificador do cômodo
            cx, cy = x + w / 2.0, y + h / 2.0
            self.msp.add_text(
                dados["nome"],
                dxfattribs={"layer": "ARQ_TEXTOS", "height": 0.16}
            ).set_placement((cx, cy - 0.4), align=TextEntityAlignment.MIDDLE_CENTER)
            
            # Área em m²
            area_m2 = round(w * h, 1)
            self.msp.add_text(
                f"A = {area_m2} m²",
                dxfattribs={"layer": "ARQ_TEXTOS", "height": 0.12}
            ).set_placement((cx, cy - 0.65), align=TextEntityAlignment.MIDDLE_CENTER)

        # 2. Desenhar o QDC (Quadro de Distribuição de Circuitos)
        # Posicionado estrategicamente na parede da Circulação / Cozinha (centro de carga)
        qdc_x, qdc_y = 3.2, 3.8
        self._desenhar_simbolo_qdc(qdc_x, qdc_y, "QDC GERAL")

        # 3. Desenhar Pontos de Luz no Teto e Conexões com Eletrodutos
        pontos_luz_coords = {}
        for cid, dados in layout_comodos.items():
            cx, cy = dados["x"] + dados["w"] / 2.0, dados["y"] + dados["h"] / 2.0
            # Achar dados de iluminação do projeto
            comodo_proj = next((c for c in self.projeto.get("comodos", []) if c["id"] == cid), None)
            pot_va = comodo_proj["iluminacao"]["potencia_va"] if comodo_proj else 100
            circ_num = 1 if cid in ["c_sala", "c_cozinha", "c_servico", "c_garagem", "c_varanda"] else 2
            
            self._desenhar_ponto_iluminacao(cx, cy, circ_num, pot_va, comando="a")
            pontos_luz_coords[cid] = (cx, cy)
            
            # Eletroduto do QDC para o ponto de luz ou interligando pontos
            if cid in ["c_sala", "c_cozinha", "c_hall"]:
                self._desenhar_eletroduto_teto((qdc_x, qdc_y), (cx, cy), f"C{circ_num}")

        # Interligar pontos de luz secundários entre cômodos adjacentes
        conexoes_eletrodutos = [
            ("c_sala", "c_varanda", "C1"),
            ("c_sala", "c_garagem", "C1"),
            ("c_cozinha", "c_servico", "C1"),
            ("c_hall", "c_dorm1", "C2"),
            ("c_hall", "c_dorm2", "C2"),
            ("c_hall", "c_bwc_social", "C2"),
            ("c_dorm2", "c_suite", "C2"),
            ("c_suite", "c_bwc_suite", "C2")
        ]
        for c_orig, c_dest, etiqueta in conexoes_eletrodutos:
            if c_orig in pontos_luz_coords and c_dest in pontos_luz_coords:
                self._desenhar_eletroduto_teto(pontos_luz_coords[c_orig], pontos_luz_coords[c_dest], etiqueta)

        # 4. Desenhar Tomadas e Interruptores nas paredes com descidas de eletroduto
        self._desenhar_tomadas_e_interruptores(layout_comodos, pontos_luz_coords)

        # 5. Desenhar Prancha A1, Moldura e Carimbo Técnico
        self._desenhar_moldura_e_carimbo()

        # 6. Desenhar Tabela de Legenda NBR 5444 / NBR 5410
        self._desenhar_legenda_simbologia(13.5, 0.0)

        # Salvar arquivo
        self.doc.saveas(caminho_arquivo)
        return caminho_arquivo

    def _desenhar_simbolo_qdc(self, x: float, y: float, tag: str):
        """Símbolo de Quadro de Distribuição Embutido conforme NBR 5444."""
        w, h = 0.50, 0.25
        # Retângulo do quadro
        self.msp.add_lwpolyline(
            [(x - w/2, y - h/2), (x + w/2, y - h/2), (x + w/2, y + h/2), (x - w/2, y + h/2), (x - w/2, y - h/2)],
            dxfattribs={"layer": "ELET_QDC", "closed": True}
        )
        # Metade hachurada/preenchida (triângulo superior)
        self.msp.add_solid(
            [(x - w/2, y - h/2), (x + w/2, y + h/2), (x - w/2, y + h/2)],
            dxfattribs={"layer": "ELET_QDC"}
        )
        # Identificação textual
        self.msp.add_text(
            tag,
            dxfattribs={"layer": "ELET_TEXTOS", "height": 0.14}
        ).set_placement((x, y + 0.22), align=TextEntityAlignment.MIDDLE_CENTER)

    def _desenhar_ponto_iluminacao(self, x: float, y: float, circuito: int, potencia_va: int, comando: str = "a"):
        """Símbolo de Ponto de Luz no Teto (Caixa Octogonal 4x4) conforme NBR 5444."""
        raio = 0.22
        # Círculo externo
        self.msp.add_circle((x, y), raio, dxfattribs={"layer": "ELET_PONTOS_LUZ"})
        # Linha horizontal divisória no centro
        self.msp.add_line((x - raio, y), (x + raio, y), dxfattribs={"layer": "ELET_PONTOS_LUZ"})
        
        # Número do circuito na metade superior
        self.msp.add_text(
            f"{circuito}",
            dxfattribs={"layer": "ELET_TEXTOS", "height": 0.11}
        ).set_placement((x, y + 0.08), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Potência em VA na metade inferior
        self.msp.add_text(
            f"{potencia_va}",
            dxfattribs={"layer": "ELET_TEXTOS", "height": 0.09}
        ).set_placement((x, y - 0.08), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Letra do comando do interruptor (fora do círculo à direita)
        self.msp.add_text(
            comando,
            dxfattribs={"layer": "ELET_TEXTOS", "height": 0.11}
        ).set_placement((x + raio + 0.08, y), align=TextEntityAlignment.MIDDLE_LEFT)

    def _desenhar_eletroduto_teto(self, p1: Tuple[float, float], p2: Tuple[float, float], info_circ: str):
        """Desenha trecho de eletroduto no teto (arco ou linha com fiação NBR 5444)."""
        x1, y1 = p1
        x2, y2 = p2
        # Linha do eletroduto
        self.msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "ELET_ELETRODUTOS"})
        
        # Desenhar os traços de fiação NBR 5444 no ponto médio do trecho
        mx = (x1 + x2) / 2.0
        my = (y1 + y2) / 2.0
        
        # Ângulo normal à linha
        dx = x2 - x1
        dy = y2 - y1
        ang = math.atan2(dy, dx)
        ang_normal = ang + math.pi / 2.0
        
        comp_traco = 0.15
        
        # Traço 1: Fase (traço transversal perpendicular cheio)
        fx1 = mx + comp_traco * math.cos(ang_normal)
        fy1 = my + comp_traco * math.sin(ang_normal)
        fx2 = mx - comp_traco * math.cos(ang_normal)
        fy2 = my - comp_traco * math.sin(ang_normal)
        self.msp.add_line((fx1, fy1), (fx2, fy2), dxfattribs={"layer": "ELET_FIACAO_NBR5444"})
        
        # Traço 2: Neutro (traço transversal com gancho em L invertido)
        nx = mx + 0.12 * math.cos(ang)
        ny = my + 0.12 * math.sin(ang)
        nx1 = nx + comp_traco * math.cos(ang_normal)
        ny1 = ny + comp_traco * math.sin(ang_normal)
        self.msp.add_line((nx, ny), (nx1, ny1), dxfattribs={"layer": "ELET_FIACAO_NBR5444"})
        # Gancho do neutro
        gx = nx1 - 0.06 * math.cos(ang)
        gy = ny1 - 0.06 * math.sin(ang)
        self.msp.add_line((nx1, ny1), (gx, gy), dxfattribs={"layer": "ELET_FIACAO_NBR5444"})
        
        # Traço 3: Terra PE (traço em T invertido)
        px = mx - 0.12 * math.cos(ang)
        py = my - 0.12 * math.sin(ang)
        px1 = px + comp_traco * math.cos(ang_normal)
        py1 = py + comp_traco * math.sin(ang_normal)
        self.msp.add_line((px, py), (px1, py1), dxfattribs={"layer": "ELET_FIACAO_NBR5444"})
        # Barra horizontal do T
        tx1 = px1 - 0.05 * math.cos(ang)
        ty1 = py1 - 0.05 * math.sin(ang)
        tx2 = px1 + 0.05 * math.cos(ang)
        ty2 = py1 + 0.05 * math.sin(ang)
        self.msp.add_line((tx1, ty1), (tx2, ty2), dxfattribs={"layer": "ELET_FIACAO_NBR5444"})
        
        # Etiqueta do circuito
        self.msp.add_text(
            info_circ,
            dxfattribs={"layer": "ELET_TEXTOS", "height": 0.09}
        ).set_placement((mx + 0.18 * math.cos(ang_normal), my + 0.18 * math.sin(ang_normal)), align=TextEntityAlignment.MIDDLE_CENTER)

    def _desenhar_tomadas_e_interruptores(self, layout_comodos: Dict[str, Any], pontos_luz: Dict[str, Tuple[float, float]]):
        """Distribui tomadas baixas, médias, altas e interruptores com conexões às caixas de teto."""
        for cid, dados in layout_comodos.items():
            x, y, w, h = dados["x"], dados["y"], dados["w"], dados["h"]
            luz_pt = pontos_luz.get(cid, (x + w/2, y + h/2))
            
            # Interruptor junto à porta (canto do cômodo)
            sw_x, sw_y = x + 0.4, y + 0.15
            self._desenhar_simbolo_interruptor(sw_x, sw_y, "a")
            # Eletroduto embutido na parede até o ponto de luz
            self.msp.add_line((sw_x, sw_y), luz_pt, dxfattribs={"layer": "ELET_ELETRODUTOS", "linetype": "DASHED"})
            
            # Tomadas normativas nas paredes
            if cid in ["c_cozinha", "c_servico"]:
                # Tomadas de Bancada (Médias - 1.20m) e TUEs
                t1_x, t1_y = x + w - 0.15, y + 1.2
                self._desenhar_simbolo_tomada(t1_x, t1_y, tipo="media", pot_va=600, circ=3)
                self.msp.add_line((t1_x, t1_y), luz_pt, dxfattribs={"layer": "ELET_ELETRODUTOS", "linetype": "DASHED"})
                
                t2_x, t2_y = x + w - 0.15, y + 2.4
                self._desenhar_simbolo_tomada(t2_x, t2_y, tipo="media", pot_va=600, circ=3)
                
                # Ponto alto para TUE (Cooktop ou Chuveiro)
                tue_x, tue_y = x + 1.5, y + h - 0.15
                self._desenhar_simbolo_tomada(tue_x, tue_y, tipo="alta", pot_va=7000, circ=6)
                self.msp.add_line((tue_x, tue_y), luz_pt, dxfattribs={"layer": "ELET_ELETRODUTOS", "linetype": "DASHED"})
                
            elif "bwc" in cid:
                # Tomada média junto ao lavatório (600 VA)
                t_lav_x, t_lav_y = x + 0.15, y + 1.0
                self._desenhar_simbolo_tomada(t_lav_x, t_lav_y, tipo="media", pot_va=600, circ=4)
                
                # Tomada alta para Chuveiro Elétrico (TUE 7500W)
                t_chuv_x, t_chuv_y = x + w - 0.15, y + h - 0.4
                circ_chuv = 8 if "suite" in cid else 9
                self._desenhar_simbolo_tomada(t_chuv_x, t_chuv_y, tipo="alta", pot_va=7500, circ=circ_chuv)
                self.msp.add_line((t_chuv_x, t_chuv_y), luz_pt, dxfattribs={"layer": "ELET_ELETRODUTOS", "linetype": "DASHED"})
                
            else: # Quartos e Sala
                # Tomadas baixas (0.30m)
                tb1_x, tb1_y = x + 0.15, y + h/2
                self._desenhar_simbolo_tomada(tb1_x, tb1_y, tipo="baixa", pot_va=100, circ=4)
                self.msp.add_line((tb1_x, tb1_y), luz_pt, dxfattribs={"layer": "ELET_ELETRODUTOS", "linetype": "DASHED"})
                
                tb2_x, tb2_y = x + w - 0.15, y + h/2
                self._desenhar_simbolo_tomada(tb2_x, tb2_y, tipo="baixa", pot_va=100, circ=4)
                
                # Tomada alta para Ar Condicionado (TUE)
                tar_x, tar_y = x + w/2, y + h - 0.15
                self._desenhar_simbolo_tomada(tar_x, tar_y, tipo="alta", pot_va=1700, circ=7)
                self.msp.add_line((tar_x, tar_y), luz_pt, dxfattribs={"layer": "ELET_ELETRODUTOS", "linetype": "DASHED"})

    def _desenhar_simbolo_tomada(self, x: float, y: float, tipo: str = "baixa", pot_va: int = 100, circ: int = 1):
        """Símbolo de tomada NBR 5444: baixa (vazada), média (semi-preenchida), alta (preenchida)."""
        tam = 0.16
        # Triângulo apontando para a alvenaria
        pts = [(x, y - tam/2), (x + tam, y), (x, y + tam/2), (x, y - tam/2)]
        self.msp.add_lwpolyline(pts, dxfattribs={"layer": "ELET_TOMADAS", "closed": True})
        
        if tipo == "media":
            # Preenche metade inferior
            self.msp.add_solid([(x, y - tam/2), (x + tam, y), (x, y)], dxfattribs={"layer": "ELET_TOMADAS"})
        elif tipo == "alta":
            # Preenche triângulo inteiro
            self.msp.add_solid([(x, y - tam/2), (x + tam, y), (x, y + tam/2)], dxfattribs={"layer": "ELET_TOMADAS"})
            
        # Potência e circuito
        txt = f"C{circ} - {pot_va}VA"
        self.msp.add_text(
            txt,
            dxfattribs={"layer": "ELET_TEXTOS", "height": 0.08}
        ).set_placement((x + tam + 0.05, y), align=TextEntityAlignment.MIDDLE_LEFT)

    def _desenhar_simbolo_interruptor(self, x: float, y: float, comando: str = "a"):
        """Símbolo de interruptor simples (círculo com haste / letra)."""
        raio = 0.08
        self.msp.add_circle((x, y), raio, dxfattribs={"layer": "ELET_INTERRUPTORES"})
        self.msp.add_line((x, y + raio), (x, y + raio + 0.12), dxfattribs={"layer": "ELET_INTERRUPTORES"})
        self.msp.add_text(
            f"S{comando}",
            dxfattribs={"layer": "ELET_TEXTOS", "height": 0.09}
        ).set_placement((x + 0.10, y + 0.05), align=TextEntityAlignment.MIDDLE_LEFT)

    def _desenhar_legenda_simbologia(self, x_origem: float, y_origem: float):
        """Desenha a tabela de convenções e legenda gráfica NBR 5444."""
        largura_tabela = 6.8
        altura_linha = 0.55
        
        itens = [
            ("Ponto de Luz no Teto (Caixa 4x4\")", "Círculo com pot. VA e circuito"),
            ("Tomada Baixa h=0.30m (2P+T 10A)", "Triângulo vazado"),
            ("Tomada Média h=1.20m (2P+T 10A/20A)", "Triângulo semi-preenchido"),
            ("Tomada Alta h=2.20m (Chuveiro/Ar)", "Triângulo totalmente preenchido"),
            ("Interruptor Simples h=1.20m (10A)", "Círculo com haste e letra"),
            ("Quadro Distribuição de Circuitos (QDC)", "Retângulo com metade preenchida"),
            ("Eletroduto embutido no teto / laje", "Linha contínua"),
            ("Eletroduto embutido na parede", "Linha tracejada"),
            ("Condutor de Fase (F)", "Traço transversal cheio (|)"),
            ("Condutor de Neutro (N)", "Traço com gancho em L (⌈)"),
            ("Condutor de Proteção (PE - Terra)", "Traço em T invertido (⊥)"),
            ("Condutor de Retorno de Luz (R)", "Meio traço transversal (/)")
        ]
        
        # Cabeçalho da Legenda
        self.msp.add_lwpolyline(
            [(x_origem, y_origem), (x_origem + largura_tabela, y_origem),
             (x_origem + largura_tabela, y_origem + (len(itens) + 1) * altura_linha),
             (x_origem, y_origem + (len(itens) + 1) * altura_linha), (x_origem, y_origem)],
            dxfattribs={"layer": "PRANCHA_CARIMBO", "closed": True}
        )
        
        # Título
        top_y = y_origem + (len(itens) + 1) * altura_linha
        self.msp.add_text(
            "LEGENDA DE CONVENÇÕES E SÍMBOLOS (NBR 5444 / NBR 5410)",
            dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.16}
        ).set_placement((x_origem + largura_tabela/2.0, top_y - 0.35), align=TextEntityAlignment.MIDDLE_CENTER)
        
        # Linhas
        cur_y = top_y - altura_linha
        for nome, desc in itens:
            self.msp.add_line((x_origem, cur_y), (x_origem + largura_tabela, cur_y), dxfattribs={"layer": "PRANCHA_CARIMBO"})
            self.msp.add_text(
                nome,
                dxfattribs={"layer": "ARQ_TEXTOS", "height": 0.11}
            ).set_placement((x_origem + 0.2, cur_y - 0.35), align=TextEntityAlignment.MIDDLE_LEFT)
            self.msp.add_text(
                desc,
                dxfattribs={"layer": "ELET_TEXTOS", "height": 0.10}
            ).set_placement((x_origem + 3.4, cur_y - 0.35), align=TextEntityAlignment.MIDDLE_LEFT)
            cur_y -= altura_linha

    def _desenhar_moldura_e_carimbo(self):
        """Desenha a moldura de prancha A1 e o carimbo técnico de engenharia."""
        # Margens da prancha (x: -5.0 a 21.0, y: -3.5 a 10.5)
        x0, y0 = -5.0, -3.5
        w_total, h_total = 26.0, 14.0
        
        # Moldura externa
        self.msp.add_lwpolyline(
            [(x0, y0), (x0 + w_total, y0), (x0 + w_total, y0 + h_total), (x0, y0 + h_total), (x0, y0)],
            dxfattribs={"layer": "PRANCHA_MOLDURA", "closed": True}
        )
        # Margem interna (20mm)
        m = 0.3
        self.msp.add_lwpolyline(
            [(x0 + m, y0 + m), (x0 + w_total - m, y0 + m), (x0 + w_total - m, y0 + h_total - m), (x0 + m, y0 + h_total - m), (x0 + m, y0 + m)],
            dxfattribs={"layer": "PRANCHA_MOLDURA", "closed": True}
        )
        
        # Carimbo no canto inferior direito
        cb_w, cb_h = 7.5, 2.5
        cb_x = x0 + w_total - m - cb_w
        cb_y = y0 + m
        
        self.msp.add_lwpolyline(
            [(cb_x, cb_y), (cb_x + cb_w, cb_y), (cb_x + cb_w, cb_y + cb_h), (cb_x, cb_y + cb_h), (cb_x, cb_y)],
            dxfattribs={"layer": "PRANCHA_CARIMBO", "closed": True}
        )
        
        # Textos do Carimbo
        self.msp.add_text(
            "SISTEMA ANTIGRAVITY - ENGENHARIA ELÉTRICA",
            dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.16}
        ).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.35), align=TextEntityAlignment.MIDDLE_CENTER)
        
        self.msp.add_text(
            self.projeto.get("nome_projeto", "Projeto Elétrico Residencial"),
            dxfattribs={"layer": "PRANCHA_CARIMBO", "height": 0.14}
        ).set_placement((cb_x + cb_w/2.0, cb_y + cb_h - 0.75), align=TextEntityAlignment.MIDDLE_CENTER)
        
        self.msp.add_text(
            "CONTEÚDO: PLANTA BAIXA ELÉTRICA UNIFILAR (ILUM / TUG / TUE)",
            dxfattribs={"layer": "ARQ_TEXTOS", "height": 0.11}
        ).set_placement((cb_x + 0.3, cb_y + 1.2), align=TextEntityAlignment.MIDDLE_LEFT)
        
        self.msp.add_text(
            "NORMAS: ABNT NBR 5410:2004 / NBR 5444 / NR-10",
            dxfattribs={"layer": "ARQ_TEXTOS", "height": 0.11}
        ).set_placement((cb_x + 0.3, cb_y + 0.85), align=TextEntityAlignment.MIDDLE_LEFT)
        
        self.msp.add_text(
            "ESCALA: 1:50 | PRANCHA: ELE-01/02 | RESP. TÉCNICO: ENGENHEIRO ELETRICISTA",
            dxfattribs={"layer": "ARQ_TEXTOS", "height": 0.10}
        ).set_placement((cb_x + 0.3, cb_y + 0.45), align=TextEntityAlignment.MIDDLE_LEFT)
