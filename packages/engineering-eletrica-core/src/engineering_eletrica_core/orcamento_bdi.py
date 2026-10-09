"""
Módulo de Orçamento Paramétrico, SINAPI, BDI e Análise de Viabilidade Econômico-Financeira
Conforme Acórdão TCU 2622/2013 (Fórmula de BDI), referências SINAPI e Métricas de Engenharia Econômica
Calcula Custos Diretos, BDI, Preço Global de Venda, Payback Simples/Descontado, VPL, TIR e LCOE.
"""

import math
from typing import Dict, List, Any, Optional

# Tabela de Preços de Referência Média de Mercado e SINAPI (Desonerado)
PRECOS_REFERENCIA_INSUMOS: Dict[str, Dict[str, Any]] = {
    "cabo_1_5": {"descricao": "Cabo Cobre Flexível 750V 1,5 mm² Antichama", "unidade": "metro", "preco_unit_r": 2.45},
    "cabo_2_5": {"descricao": "Cabo Cobre Flexível 750V 2,5 mm² Antichama", "unidade": "metro", "preco_unit_r": 3.85},
    "cabo_4_0": {"descricao": "Cabo Cobre Flexível 750V 4,0 mm² Antichama", "unidade": "metro", "preco_unit_r": 6.20},
    "cabo_6_0": {"descricao": "Cabo Cobre Flexível 750V 6,0 mm² Antichama", "unidade": "metro", "preco_unit_r": 9.40},
    "cabo_10_0": {"descricao": "Cabo Cobre Flexível 750V 10,0 mm² Antichama", "unidade": "metro", "preco_unit_r": 15.80},
    "cabo_25_0": {"descricao": "Cabo Cobre Flexível 1kV 25,0 mm² Alimentador", "unidade": "metro", "preco_unit_r": 38.50},
    "cabo_solar_6": {"descricao": "Cabo Solar 1.8kVcc XLPE 6 mm² Vermelho/Preto", "unidade": "metro", "preco_unit_r": 5.90},
    "eletroduto_20": {"descricao": "Eletroduto Corrugado Flexível DN 20 mm (3/4 pol.)", "unidade": "metro", "preco_unit_r": 2.80},
    "eletroduto_25": {"descricao": "Eletroduto Corrugado Flexível DN 25 mm (1 pol.)", "unidade": "metro", "preco_unit_r": 3.60},
    "eletroduto_32": {"descricao": "Eletroduto Corrugado Flexível DN 32 mm (1.1/4 pol.)", "unidade": "metro", "preco_unit_r": 5.50},
    "tubo_pead_200": {"descricao": "Tubo PEAD PN10 DN 200 mm Conduto Forçado PCH", "unidade": "metro", "preco_unit_r": 145.00},
    "disjuntor_mono_10_20": {"descricao": "Disjuntor Termomagnético DIN Monopolar 10A-20A", "unidade": "peça", "preco_unit_r": 16.50},
    "disjuntor_mono_25_40": {"descricao": "Disjuntor Termomagnético DIN Monopolar 25A-40A", "unidade": "peça", "preco_unit_r": 22.00},
    "disjuntor_tri_geral": {"descricao": "Disjuntor Geral DIN Tripolar 125A 6kA", "unidade": "peça", "preco_unit_r": 210.00},
    "idr_tetrapolar_40": {"descricao": "Interruptor Diferencial Residual IDR 40A 30mA Tetrapolar", "unidade": "peça", "preco_unit_r": 185.00},
    "dps_classe_ii": {"descricao": "DPS Classe II 45kA / 275Vca Protetor de Surto", "unidade": "peça", "preco_unit_r": 88.00},
    "qdc_36": {"descricao": "Quadro de Distribuição Embutir 36 Módulos DIN c/ Barramentos", "unidade": "peça", "preco_unit_r": 320.00},
    "haste_aterramento": {"descricao": "Haste Aço Cobreado 5/8 pol. x 2,40m c/ Conector e Caixa", "unidade": "peça", "preco_unit_r": 78.00},
    "modulo_solar_550w": {"descricao": "Módulo Fotovoltaico Monocristalino 550W Tier 1", "unidade": "peça", "preco_unit_r": 440.00},
    "modulo_solar_650w": {"descricao": "Módulo Fotovoltaico Bifacial N-Type 650W", "unidade": "peça", "preco_unit_r": 560.00},
    "inversor_solar_kw": {"descricao": "Inversor String On-Grid Trifásico (Custo por kW)", "unidade": "kW", "preco_unit_r": 480.00},
    "aerogerador_completo_kw": {"descricao": "Sistema Eólico (Turbina + Torre Estaiada + Inversor por kW)", "unidade": "kW", "preco_unit_r": 3800.00},
    "biodigestor_cava_m3": {"descricao": "Implantação Biodigestor PEAD (Cava + Lonas + Filtro por m³ útil)", "unidade": "m³", "preco_unit_r": 95.00},
    "motogerador_biogas_kw": {"descricao": "Grupo Motogerador Ciclo Otto a Biogás CHP (por kW)", "unidade": "kW", "preco_unit_r": 2600.00},
    "pch_hidreletrica_kw": {"descricao": "Sistema PCH (Turbina + Gerador + Painel ELC + Válvula por kW)", "unidade": "kW", "preco_unit_r": 4200.00}
}


class CalculadoraOrcamentoEletrico:
    """Calcula orçamento de engenharia com BDI auditável e viabilidade econômica."""

    @classmethod
    def calcular_bdi_tcu(
        cls,
        administracao_central_pct: float = 4.0,
        seguro_garantia_pct: float = 0.8,
        risco_pct: float = 1.2,
        despesas_financeiras_pct: float = 1.0,
        lucro_operacional_pct: float = 7.4,
        tributos_totais_pct: float = 8.65 # PIS, COFINS, ISS
    ) -> Dict[str, Any]:
        """
        Calcula a taxa de BDI conforme fórmula do Acórdão TCU 2622/2013:
        BDI = [ (1 + AC + S + R + G) * (1 + DF) * (1 + L) / (1 - T) ] - 1
        """
        ac = administracao_central_pct / 100.0
        sg = seguro_garantia_pct / 100.0
        r = risco_pct / 100.0
        df = despesas_financeiras_pct / 100.0
        l = lucro_operacional_pct / 100.0
        t = tributos_totais_pct / 100.0

        numerador = (1.0 + ac + sg + r) * (1.0 + df) * (1.0 + l)
        denominador = 1.0 - t
        bdi_fator = (numerador / denominador) - 1.0
        bdi_pct = round(bdi_fator * 100.0, 2)

        return {
            "taxa_bdi_percentual": bdi_pct,
            "fator_multiplicador": round(1.0 + bdi_fator, 4),
            "composicao": {
                "administracao_central": administracao_central_pct,
                "seguro_e_garantia": seguro_garantia_pct,
                "risco_e_contingencias": risco_pct,
                "despesas_financeiras": despesas_financeiras_pct,
                "lucro_operacional_liquido": lucro_operacional_pct,
                "tributos_incidentes": tributos_totais_pct
            },
            "norma_referencia": "Acórdão TCU nº 2622/2013 - Plenário"
        }

    @classmethod
    def gerar_orcamento_completo(
        cls,
        materiais_eletrica: List[Dict[str, Any]],
        dados_renovaveis: Optional[Dict[str, Any]] = None,
        bdi_pct: float = 24.2,
        percentual_mao_de_obra: float = 35.0 # Mão de obra típica de montagem e comissionamento
    ) -> Dict[str, Any]:
        """Gera o orçamento sintético e analítico da instalação com BDI."""
        itens_orcamento = []
        custo_materiais_total = 0.0

        # 1. Precificar Materiais de Baixa Tensão
        for m in materiais_eletrica:
            nome = m.get("item", "")
            qtd = float(m.get("quantidade", 1.0))
            un = m.get("unidade", "un")
            
            # Buscar preço unitário aproximado por palavra-chave
            p_unit = 25.0 # valor base fallback
            if "1,5 mm²" in nome: p_unit = 2.45
            elif "2,5 mm²" in nome: p_unit = 3.85
            elif "4,0 mm²" in nome: p_unit = 6.20
            elif "6,0 mm²" in nome: p_unit = 9.40
            elif "25,0 mm²" in nome: p_unit = 38.50
            elif "DN 20" in nome: p_unit = 2.80
            elif "DN 25" in nome: p_unit = 3.60
            elif "DN 32" in nome: p_unit = 5.50
            elif "10A" in nome or "16A" in nome or "20A" in nome: p_unit = 16.50
            elif "25A" in nome or "40A" in nome: p_unit = 22.00
            elif "125A" in nome or "Tripolar" in nome: p_unit = 210.00
            elif "IDR" in nome: p_unit = 185.00
            elif "DPS" in nome: p_unit = 88.00
            elif "QDC" in nome: p_unit = 320.00
            elif "Haste" in nome: p_unit = 78.00

            subtotal = round(qtd * p_unit, 2)
            custo_materiais_total += subtotal
            itens_orcamento.append({
                "item": nome,
                "quantidade": qtd,
                "unidade": un,
                "preco_unitario_r": p_unit,
                "subtotal_r": subtotal,
                "categoria": "Instalação Elétrica NBR 5410"
            })

        # 2. Precificar Pacote Renováveis (se presente)
        custo_renovaveis = 0.0
        if dados_renovaveis and "fontes_integradas" in dados_renovaveis:
            fontes = dados_renovaveis["fontes_integradas"]
            
            # Solar
            if "solar" in fontes:
                s = fontes["solar"]
                pot_kwp = s.get("potencia_pico_kwp", 0.0)
                # Módulos + Inversor + Estrutura ≈ R$ 2.950 por kWp instalado
                custo_s = pot_kwp * 2950.0
                custo_renovaveis += custo_s
                itens_orcamento.append({
                    "item": f"Gerador Solar Fotovoltaico Completo ({pot_kwp:.1f} kWp, Módulos, Inversor, Stringbox e Estruturas)",
                    "quantidade": 1,
                    "unidade": "sistema",
                    "preco_unitario_r": round(custo_s, 2),
                    "subtotal_r": round(custo_s, 2),
                    "categoria": "Energia Solar Fotovoltaica"
                })

            # Eólica
            if "eolica" in fontes:
                e = fontes["eolica"]
                pot_e = e.get("potencia_nominal_kw", 0.0)
                custo_e = pot_e * 3800.0
                custo_renovaveis += custo_e
                itens_orcamento.append({
                    "item": f"Aerogerador Eólico Completo ({pot_e:.1f} kW, Rotor, Torre Estaiada e Inversor)",
                    "quantidade": 1,
                    "unidade": "sistema",
                    "preco_unitario_r": round(custo_e, 2),
                    "subtotal_r": round(custo_e, 2),
                    "categoria": "Geração Eólica"
                })

            # Biodigestor e CHP
            if "biodigestor" in fontes:
                bio = fontes["biodigestor"]
                vol_m3 = bio.get("dimensoes_cava_trapezoidal", {}).get("volume_util_m3", 300.0)
                custo_b = vol_m3 * 95.0
                custo_renovaveis += custo_b
                itens_orcamento.append({
                    "item": f"Biodigestor Anaeróbio Cava Trapezoidal ({vol_m3:.0f} m³ útil com Geomembrana PEAD e Agitadores)",
                    "quantidade": 1,
                    "unidade": "sistema",
                    "preco_unitario_r": round(custo_b, 2),
                    "subtotal_r": round(custo_b, 2),
                    "categoria": "Biogás & Agroindústria"
                })

            if "termeletrica_biogas" in fontes:
                chp = fontes["termeletrica_biogas"]
                pot_chp = chp.get("motogerador_selecionado", {}).get("potencia_eletrica_kw", 75.0)
                custo_chp = pot_chp * 2600.0
                custo_renovaveis += custo_chp
                itens_orcamento.append({
                    "item": f"Grupo Motogerador Cogeração Biogás CHP ({pot_chp:.1f} kWe com Painel de Paralelismo)",
                    "quantidade": 1,
                    "unidade": "unidade",
                    "preco_unitario_r": round(custo_chp, 2),
                    "subtotal_r": round(custo_chp, 2),
                    "categoria": "Biogás & Agroindústria"
                })

            # Hidrelétrica PCH
            if "hidreletrica" in fontes:
                pch = fontes["hidreletrica"]
                pot_pch = pch.get("potencia_eletrica_util_kw", 15.0)
                custo_pch = pot_pch * 4200.0
                custo_renovaveis += custo_pch
                itens_orcamento.append({
                    "item": f"Central Geradora Hidrelétrica PCH ({pot_pch:.1f} kW com Turbina, Conduto Forçado e Painel ELC)",
                    "quantidade": 1,
                    "unidade": "sistema",
                    "preco_unitario_r": round(custo_pch, 2),
                    "subtotal_r": round(custo_pch, 2),
                    "categoria": "Micro-Hidrelétrica PCH"
                })

        # 3. Consolidação Financeira
        custo_direto_materiais = custo_materiais_total + custo_renovaveis
        custo_direto_mao_obra = custo_direto_materiais * (percentual_mao_de_obra / 100.0)
        custo_direto_total = custo_direto_materiais + custo_direto_mao_obra
        
        fator_bdi = 1.0 + (bdi_pct / 100.0)
        preco_venda_global = round(custo_direto_total * fator_bdi, 2)
        lucro_e_impostos_bdi = round(preco_venda_global - custo_direto_total, 2)

        # 4. Indicadores de Viabilidade Econômica (Payback, VPL, TIR e LCOE)
        economia_anual_r = (dados_renovaveis or {}).get("economia_financeira", {}).get("economia_anual_projetada_r", 35000.0)
        geracao_anual_kwh = (dados_renovaveis or {}).get("geracao_total_anual_kwh", 45000.0)
        
        payback_simples_anos = round(preco_venda_global / max(1.0, economia_anual_r), 2)
        
        # Payback Descontado, VPL e TIR (Horizonte 25 anos, TMA 9.5% a.a., Inflação Tarifa 5% a.a.)
        tma = 0.095
        inflacao_tarifa = 0.05
        fluxo_descontado_acum = -preco_venda_global
        payback_descontado_anos = 25.0
        vpl = -preco_venda_global
        
        for ano in range(1, 26):
            econ_ano = economia_anual_r * ((1.0 + inflacao_tarifa) ** (ano - 1))
            fator_desc = 1.0 / ((1.0 + tma) ** ano)
            econ_descontada = econ_ano * fator_desc
            vpl += econ_descontada
            
            if fluxo_descontado_acum < 0 and (fluxo_descontado_acum + econ_descontada) >= 0:
                fracao = abs(fluxo_descontado_acum) / econ_descontada
                payback_descontado_anos = round((ano - 1) + fracao, 2)
            fluxo_descontado_acum += econ_descontada

        # TIR aproximada
        tir_pct = round(((economia_anual_r / max(1.0, preco_venda_global)) * 1.35) * 100.0, 1)

        # LCOE (Levelized Cost of Electricity em R$/kWh em 25 anos)
        energia_total_25_anos_kwh = geracao_anual_kwh * 25.0 * 0.92 # degradação de 8% média
        lcoe_r_kwh = round((preco_venda_global * 1.25) / max(1.0, energia_total_25_anos_kwh), 3)

        return {
            "resumo_financeiro": {
                "custo_direto_materiais_r": round(custo_direto_materiais, 2),
                "custo_direto_mao_obra_r": round(custo_direto_mao_obra, 2),
                "custo_direto_total_r": round(custo_direto_total, 2),
                "taxa_bdi_aplicada_pct": bdi_pct,
                "valor_bdi_r": lucro_e_impostos_bdi,
                "preco_global_venda_r": preco_venda_global
            },
            "viabilidade_economica": {
                "investimento_capex_r": preco_venda_global,
                "economia_anual_estimada_r": round(economia_anual_r, 2),
                "payback_simples_anos": payback_simples_anos,
                "payback_descontado_anos": payback_descontado_anos,
                "vpl_25_anos_r": round(vpl, 2),
                "tir_anual_pct": tir_pct,
                "lcoe_energia_r_kwh": lcoe_r_kwh,
                "status_viabilidade": "ALTAMENTE VIÁVEL" if payback_descontado_anos <= 6.5 else "MODERADAMENTE VIÁVEL"
            },
            "itens_analiticos": itens_orcamento
        }
