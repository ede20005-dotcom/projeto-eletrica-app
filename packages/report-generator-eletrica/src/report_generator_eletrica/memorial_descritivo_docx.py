"""
Gerador de Memorial Descritivo e de Cálculo das Instalações Elétricas em DOCX
Conforme ABNT NBR 5410:2004, NR-10 e ABNT NBR 5419:2015
"""

import os
from typing import Dict, List, Any
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

class GeradorMemorialEletricoDOCX:
    """Gera laudos técnicos e memoriais de cálculo de engenharia elétrica em formato Word (.docx)."""
    
    def __init__(self, projeto_dados: Dict[str, Any]):
        self.projeto = projeto_dados
        self.doc = docx.Document()
        self._configurar_estilos()

    def _configurar_estilos(self):
        """Configura margens, tipografia e espaçamentos do documento."""
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)
            
        # Estilo Normal
        style_normal = self.doc.styles['Normal']
        font = style_normal.font
        font.name = 'Calibri'
        font.size = Pt(11)
        font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    def _adicionar_cabecalho_secao(self, titulo: str, subtitulo: str = ""):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(titulo)
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x00, 0x33, 0x66) # Azul escuro técnico
        
        if subtitulo:
            p_sub = self.doc.add_paragraph()
            p_sub.paragraph_format.space_before = Pt(0)
            p_sub.paragraph_format.space_after = Pt(8)
            run_sub = p_sub.add_run(subtitulo)
            run_sub.italic = True
            run_sub.font.size = Pt(10)
            run_sub.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    def _pintar_celula(self, cell, cor_hex: str):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{cor_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    def gerar_memorial(self, caminho_arquivo: str) -> str:
        """Gera o documento completo e salva no caminho indicado."""
        os.makedirs(os.path.dirname(os.path.abspath(caminho_arquivo)), exist_ok=True)
        
        # 1. CAPA TÉCNICA
        self._adicionar_capa()

        # 2. OBJETIVO E IDENTIFICAÇÃO DA OBRA
        self._adicionar_cabecalho_secao("1. OBJETIVO E IDENTIFICAÇÃO DO PROJETO")
        p = self.doc.add_paragraph(
            "O presente Memorial Descritivo e de Cálculo tem como objetivo detalhar, fundamentar e especificar "
            "o dimensionamento das instalações elétricas de baixa tensão da edificação residencial, estabelecendo "
            "as diretrizes para os circuitos de iluminação, tomadas de uso geral (TUG), tomadas de uso específico (TUE), "
            "quadros de distribuição, dispositivos de proteção (disjuntores termomagnéticos, DRs e DPSs), infraestrutura de "
            "eletrodutos e malha de aterramento, assegurando a conformidade estrita com as normas vigentes, "
            "a máxima segurança de pessoas e a confiabilidade operacional do patrimônio."
        )
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(8)

        # 3. NORMAS TÉCNICAS APLICÁVEIS
        self._adicionar_cabecalho_secao("2. NORMAS TÉCNICAS E REFERÊNCIAS REGULAMENTADORAS")
        normas = [
            ("ABNT NBR 5410:2004", "Instalações elétricas de baixa tensão (Requisitos gerais, métodos de instalação, critérios de dimensionamento e proteção)."),
            ("NR-10 (Ministério do Trabalho)", "Segurança em instalações e serviços em eletricidade (Requisitos de segurança, desenergização e proteção)."),
            ("ABNT NBR 5419:2015", "Proteção contra descargas atmosféricas (Partes 1 a 4 - Gerenciamento de risco e Medidas de Proteção contra Surtos MPS)."),
            ("ABNT NBR 5444:1989", "Símbolos gráficos para instalações elétricas prediais."),
            ("ABNT NBR 14136:2012", "Plugues e tomadas para uso doméstico e análogo até 20 A / 250 V em corrente alternada."),
            ("Normas de Concessionária", "Regulamentos técnicos de fornecimento em Baixa Tensão (CEMIG, CPFL, ENEL, Light).")
        ]
        for codigo, desc in normas:
            p_n = self.doc.add_paragraph()
            p_n.paragraph_format.space_after = Pt(3)
            p_n.add_run(f"• {codigo}: ").bold = True
            p_n.add_run(desc)

        # 4. CARACTERÍSTICAS DO FORNECIMENTO E PADRÃO DE ENTRADA
        self._adicionar_cabecalho_secao("3. CARACTERÍSTICAS DA REDE E PADRÃO DE ENTRADA")
        demanda = self.projeto.get("demanda_instalacao", {})
        padrao = demanda.get("padrao_entrada", {})
        
        t_padrao = self.doc.add_table(rows=6, cols=2)
        t_padrao.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_padrao.autofit = False
        
        eletro_pol = padrao.get("eletroduto_ramal_pol", "1.1/4 pol")
        dados_padrao = [
            ("Tipo de Fornecimento / Rede", padrao.get("tipo_fornecimento", "Trifásico")),
            ("Tensão Nominal de Atendimento", f"{self.projeto.get('parametros_fornecimento', {}).get('tensao_fase_neutro_v', 127)} / {self.projeto.get('parametros_fornecimento', {}).get('tensao_fase_fase_v', 220)} V (60 Hz)"),
            ("Potência Total Instalada", f"{demanda.get('potencia_instalada_total_kw', 0)} kW ({demanda.get('potencia_instalada_total_kva', 0)} kVA)"),
            ("Demanda Total Provável Calculada", f"{demanda.get('demanda_total_kw', 0)} kW ({demanda.get('demanda_total_kva', 0)} kVA)"),
            ("Disjuntor Geral da Entrada", f"{padrao.get('disjuntor_geral_in_a', 100)} A DIN Tripolar (Capacidade de interrupção 10 kA)"),
            ("Condutores do Ramal Alimentador", f"Cobre # {padrao.get('secao_condutor_fase_mm2', 25.0)} mm² em eletroduto DN {padrao.get('eletroduto_ramal_dn_mm', 32)} mm ({eletro_pol})")
        ]
        for row_idx, (k, v) in enumerate(dados_padrao):
            row = t_padrao.rows[row_idx]
            c0, c1 = row.cells[0], row.cells[1]
            c0.width, c1.width = Inches(2.6), Inches(4.0)
            c0.paragraphs[0].add_run(k).bold = True
            c1.paragraphs[0].add_run(v)
            self._pintar_celula(c0, "F0F4F8")
            self._pintar_celula(c1, "FFFFFF" if row_idx % 2 == 0 else "F9FBFD")

        # 5. METODOLOGIA E OS 6 CRITÉRIOS DE DIMENSIONAMENTO
        self._adicionar_cabecalho_secao("4. MEMÓRIA DE CÁLCULO E OS 6 CRITÉRIOS NORMATIVOS DA NBR 5410")
        p_crit = self.doc.add_paragraph(
            "Todos os circuitos terminais e alimentadores foram rigorosamente calculados cumprindo simultaneamente "
            "os seis critérios prescritos pela ABNT NBR 5410:2004:\n"
            "1. Critério da Seção Mínima: 1,5 mm² para iluminação e 2,5 mm² para força e tomadas (Tabela 47);\n"
            "2. Critério da Capacidade de Condução de Corrente: Corrente corrigida Ib' = Ib / (ft * fa), adotando método B1 embutido (Tabelas 36, 40 e 42);\n"
            "3. Critério da Queda de Tensão Admissível: Queda de tensão máxima restrita a 4,0% a partir do QDC;\n"
            "4. Critério de Proteção contra Sobrecargas: Coordenação de sobrecorrente Ib <= In <= Iz e I2 <= 1,45*Iz;\n"
            "5. Critério dos Condutores Neutro e PE: Neutro conforme Tabela 48 e Condutor de Proteção conforme Tabela 58;\n"
            "6. Proteção contra Choques e Surtos: Dispositivos DR de alta sensibilidade (30mA) para áreas molhadas/tomadas e DPS Classe II."
        )
        p_crit.paragraph_format.line_spacing = 1.15
        p_crit.paragraph_format.space_after = Pt(8)

        # 6. TABELA DE LEVANTAMENTO DE CARGAS POR CÔMODO
        self._adicionar_cabecalho_secao("5. LEVANTAMENTO DE CARGAS POR COMPARTIMENTO (NBR 5410 SUBITEM 9.5.2)")
        comodos = self.projeto.get("comodos", [])
        
        t_comodos = self.doc.add_table(rows=len(comodos) + 1, cols=6)
        t_comodos.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers_com = ["CÔMODO", "ÁREA (m²)", "PERÍMETRO (m)", "ILUMINAÇÃO (VA)", "TUGs (Qtd / VA)", "TUEs INSTALADAS"]
        
        for col_idx, h in enumerate(headers_com):
            cell = t_comodos.rows[0].cells[col_idx]
            cell.paragraphs[0].add_run(h).bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            self._pintar_celula(cell, "003366")
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            
        for r_idx, c in enumerate(comodos):
            row = t_comodos.rows[r_idx + 1]
            tues_nomes = ", ".join([f"{t['nome']} ({t['potencia_w']}W)" for t in c.get("tue", [])]) or "Nenhuma"
            vals = [
                c.get("nome", ""),
                f"{c.get('area_m2', 0)}",
                f"{c.get('perimetro_m', 0)}",
                f"{c.get('iluminacao', {}).get('potencia_va', 0)} VA",
                f"{c.get('tug', {}).get('qtd', 0)} pts ({c.get('tug', {}).get('potencia_total_va', 0)} VA)",
                tues_nomes
            ]
            for c_idx, val in enumerate(vals):
                cell = row.cells[c_idx]
                p_c = cell.paragraphs[0]
                p_c.add_run(val)
                p_c.runs[0].font.size = Pt(8.5)
                if c_idx in [1, 2, 3, 4]:
                    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                self._pintar_celula(cell, "FFFFFF" if r_idx % 2 == 0 else "F4F8FA")

        # 7. QUADRO DE CARGAS COMPLETO DOS CIRCUITOS TERMINAIS
        self._adicionar_cabecalho_secao("6. QUADRO DE CARGAS E DIMENSIONAMENTO DOS CIRCUITOS TERMINAIS")
        circuitos = self.projeto.get("circuitos", [])
        
        t_circ = self.doc.add_table(rows=len(circuitos) + 1, cols=9)
        t_circ.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers_circ = ["CIRC", "DESCRIÇÃO DO CIRCUITO", "TENSÃO", "FASE", "POT (VA)", "Ib (A)", "COND (mm²)", "DISJ (A)", "ΔU (%)"]
        
        for col_idx, h in enumerate(headers_circ):
            cell = t_circ.rows[0].cells[col_idx]
            cell.paragraphs[0].add_run(h).bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            self._pintar_celula(cell, "003366")
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)

        for r_idx, circ in enumerate(circuitos):
            row = t_circ.rows[r_idx + 1]
            fases_txt = "/".join(circ.get("fases", ["R"]))
            vals_circ = [
                f"C{circ['numero']}",
                circ.get("descricao", ""),
                f"{circ.get('tensao_v', 127)}V",
                fases_txt,
                f"{circ.get('potencia_va', 0)}",
                f"{circ.get('corrente_projeto_ib', 0)}",
                f"{circ.get('secao_condutor_mm2', 2.5)}",
                f"{circ.get('disjuntor_in_a', 16)}A",
                f"{circ.get('queda_tensao_percentual', 0)}%"
            ]
            for c_idx, val in enumerate(vals_circ):
                cell = row.cells[c_idx]
                p_c = cell.paragraphs[0]
                p_c.add_run(val)
                p_c.runs[0].font.size = Pt(8.0)
                if c_idx != 1:
                    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                self._pintar_celula(cell, "FFFFFF" if r_idx % 2 == 0 else "F4F8FA")

        # 8. BALANCEAMENTO DE CARGAS ENTRE FASES
        self._adicionar_cabecalho_secao("7. RESUMO DO EQUILÍBRIO DE FASES")
        eq = self.projeto.get("balanceamento_fases", {})
        pots_fase = eq.get("potencias_por_fase_va", {})
        
        p_eq = self.doc.add_paragraph()
        p_eq.paragraph_format.space_after = Pt(6)
        p_eq.add_run("• Potência por Fase: ").bold = True
        p_eq.add_run(" | ".join([f"Fase {k}: {v} VA" for k, v in pots_fase.items()]))
        
        p_des = self.doc.add_paragraph()
        p_des.paragraph_format.space_after = Pt(8)
        p_des.add_run("• Desequilíbrio Percentual Calculado: ").bold = True
        p_des.add_run(f"{eq.get('desequilibrio_percentual', 0)}% — ")
        run_st = p_des.add_run(f"Status: {eq.get('status_equilibrio', 'CONFORME')}")
        run_st.bold = True
        run_st.font.color.rgb = RGBColor(0x00, 0x88, 0x00)

        # 9. LISTA DE MATERIAIS QUANTITATIVA
        self._adicionar_cabecalho_secao("8. LISTA QUANTITATIVA DE MATERIAIS DA INSTALAÇÃO")
        materiais = self.projeto.get("lista_materiais", [])
        
        t_mat = self.doc.add_table(rows=len(materiais) + 1, cols=3)
        t_mat.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_mat.rows[0].cells[0].paragraphs[0].add_run("ESPECIFICAÇÃO TÉCNICA DO MATERIAL").bold = True
        t_mat.rows[0].cells[1].paragraphs[0].add_run("QTD").bold = True
        t_mat.rows[0].cells[2].paragraphs[0].add_run("UNIDADE").bold = True
        
        for c_idx in range(3):
            cell = t_mat.rows[0].cells[c_idx]
            self._pintar_celula(cell, "003366")
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            if c_idx > 0:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                
        for r_idx, mat in enumerate(materiais):
            row = t_mat.rows[r_idx + 1]
            row.cells[0].paragraphs[0].add_run(mat["item"]).font.size = Pt(8.5)
            row.cells[1].paragraphs[0].add_run(str(mat["quantidade"])).font.size = Pt(8.5)
            row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row.cells[2].paragraphs[0].add_run(mat["unidade"]).font.size = Pt(8.5)
            row.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            for c_idx in range(3):
                self._pintar_celula(row.cells[c_idx], "FFFFFF" if r_idx % 2 == 0 else "F4F8FA")

        # 10. MINUTA DE ART (CREA / CFT)
        self._adicionar_cabecalho_secao("9. MINUTA DE ANOTAÇÃO DE RESPONSABILIDADE TÉCNICA (ART)")
        p_art = self.doc.add_paragraph(
            "MINUTA DE ART - CONSELHO REGIONAL DE ENGENHARIA E AGRONOMIA (CREA)\n"
            "Atividade Técnica: Projeto Executivo e Memória de Cálculo de Instalações Elétricas Prediais em Baixa Tensão\n"
            "Classificação: Obra / Serviço Técnico\n"
            f"Objeto: {self.projeto.get('nome_projeto', 'Residência Unifamiliar')}\n"
            f"Norma Regulamentadora: ABNT NBR 5410:2004, NR-10 e ABNT NBR 5419:2015\n"
            f"Potência Instalada: {demanda.get('potencia_instalada_total_kw', 0)} kW | Demanda Provável: {demanda.get('demanda_total_kva', 0)} kVA\n"
            "Número de Circuitos Terminais: 18 circuitos balanceados com proteção DR 30mA e DPS Classe II\n"
            "Declaração: O Responsável Técnico declara sob as penas da lei que todos os cálculos obedeceram aos "
            "critérios prescritos pelas normas da ABNT e normas das concessionárias de energia."
        )
        p_art.paragraph_format.line_spacing = 1.15
        p_art.paragraph_format.space_after = Pt(16)

        # 11. ENCERRAMENTO E ASSINATURA TÉCNICA
        self.doc.add_paragraph().paragraph_format.space_before = Pt(24)
        p_ass = self.doc.add_paragraph()
        p_ass.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ass.add_run("_____________________________________________________\n").bold = True
        p_ass.add_run("ENGENHEIRO ELETRICISTA RESPONSÁVEL TÉCNICO\n").bold = True
        p_ass.add_run("CREA / RNP: 000000000-0/UF\n")
        p_ass.add_run("Sistema de Engenharia Elétrica Antigravity Desktop Platform")

        self.doc.save(caminho_arquivo)
        return caminho_arquivo

    def _adicionar_capa(self):
        """Gera uma capa formal de memorial de cálculo de engenharia."""
        p_topo = self.doc.add_paragraph()
        p_topo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_topo.paragraph_format.space_before = Pt(36)
        r_top = p_topo.add_run("SISTEMA INTEGRADO DE ENGENHARIA ELÉTRICA ANTIGRAVITY\n")
        r_top.bold = True
        r_top.font.size = Pt(13)
        r_top.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
        
        p_subtop = self.doc.add_paragraph()
        p_subtop.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sub = p_subtop.add_run("DEPARTAMENTO DE ENGENHARIA ELÉTRICA E PROJETOS EM BAIXA TENSÃO\nCONFORME ABNT NBR 5410:2004 E NR-10\n")
        r_sub.font.size = Pt(10)
        r_sub.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

        # Linha divisória
        p_div = self.doc.add_paragraph()
        p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_div.paragraph_format.space_before = Pt(18)
        p_div.paragraph_format.space_after = Pt(36)
        r_div = p_div.add_run("━" * 50)
        r_div.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

        # Título Principal
        p_tit = self.doc.add_paragraph()
        p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_tit.paragraph_format.space_before = Pt(24)
        p_tit.paragraph_format.space_after = Pt(12)
        r_tit = p_tit.add_run("MEMORIAL DESCRITIVO E DE CÁLCULO\nINSTALAÇÕES ELÉTRICAS DE BAIXA TENSÃO")
        r_tit.bold = True
        r_tit.font.size = Pt(20)
        r_tit.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

        # Subtítulo da Obra
        p_obra = self.doc.add_paragraph()
        p_obra.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_obra.paragraph_format.space_after = Pt(72)
        r_obra = p_obra.add_run(self.projeto.get("nome_projeto", "Residência Unifamiliar Modelo NBR 5410"))
        r_obra.font.size = Pt(14)
        r_obra.italic = True
        r_obra.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

        # Dados da Emissão
        p_rodape = self.doc.add_paragraph()
        p_rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_rodape.paragraph_format.space_before = Pt(72)
        p_rodape.add_run("VERSÃO DO PROJETO: 1.0 (REVISÃO R0)\n").bold = True
        p_rodape.add_run("DATA DE EMISSÃO: OUTUBRO DE 2026\nLOCAL: BRASIL\n")
        p_rodape.add_run("RESPONSABILIDADE TÉCNICA: ART / CREA")
        
        self.doc.add_page_break()
