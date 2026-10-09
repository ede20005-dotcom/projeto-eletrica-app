  <!-- Lógica JavaScript: Requisições REST, Canvas 2D, Three.js 3D e Navegação Segura -->
  <script>
    let dadosProjeto = null;
    let dadosRenovaveis = null;
    let dadosSeletividade = null;
    let dadosStringbox = null;
    let dadosOrcamento = null;
    let perfilAtualRenovaveis = 'fazenda';
    let correnteFaltaSimulada = null;

    // ========================================================
    // NAVEGAÇÃO SEGURA E ROBUSTA DE ABAS (SEM FALHAS DE EVENT)
    // ========================================================
    function navegarParaAba(abaId, focoOpcional) {
      try {
        // 1. Ocultar todos os painéis e desativar abas
        document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.nav-subitem').forEach(el => el.classList.remove('active'));

        // 2. Ativar painel desejado
        const pane = document.getElementById(abaId);
        if (pane) {
          pane.classList.add('active');
        }

        // 3. Ativar botão na barra superior
        const btnTopo = document.querySelector(`.tab-btn[data-tab="${abaId}"]`);
        if (btnTopo) {
          btnTopo.classList.add('active');
          btnTopo.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }

        // 4. Ativar item correspondente no sidebar
        const itemSidebar = document.querySelector(`.nav-subitem[data-tab="${abaId}"]`);
        if (itemSidebar) {
          itemSidebar.classList.add('active');
        }

        // 5. Tratar inicializações e redimensionamentos específicos
        if (abaId === 'aba-2d') {
          setTimeout(desenharPlantaBaixa2D, 120);
        } else if (abaId === 'aba-seletividade') {
          setTimeout(desenharGraficoSeletividade, 120);
          if (focoOpcional === 'matriz') {
            const card = document.getElementById('cardMatrizSeletividade');
            if (card) card.scrollIntoView({ behavior: 'smooth' });
          }
        } else if (abaId === 'aba-stringbox') {
          setTimeout(desenharDiagramaStringboxCanvas, 120);
        } else if (abaId === 'aba-3d') {
          setTimeout(() => {
            initThreeScene();
            if (focoOpcional) alternarCenario3D(focoOpcional);
          }, 120);
        } else if (abaId === 'aba-orcamento') {
          if (focoOpcional === 'bdi') {
            const card = document.getElementById('cardCalculadoraBdi');
            if (card) card.scrollIntoView({ behavior: 'smooth' });
          }
        } else if (abaId === 'aba-ia-copilot') {
          setTimeout(carregarProvedoresCopilot, 50);
          if (focoOpcional === 'auditoria') {
            setTimeout(auditarProjetoComCopilot, 200);
          } else if (focoOpcional === 'seletividade') {
            setTimeout(() => aplicarCenarioCopilot('seletividade'), 200);
          } else if (focoOpcional === 'stringbox') {
            setTimeout(() => aplicarCenarioCopilot('stringbox'), 200);
          }
        }
      } catch (err) {
        console.error("Erro na navegação de aba:", err);
      }
    }

    // ========================================================
    // GERENCIAMENTO DO MENU LATERAL (SIDEBAR)
    // ========================================================
    function toggleSidebar() {
      const sb = document.getElementById('sidebar');
      const btn = document.getElementById('btnToggleSidebar');
      if (!sb) return;
      sb.classList.toggle('collapsed');
      if (btn) {
        btn.innerText = sb.classList.contains('collapsed') ? '▶' : '◀';
      }
      setTimeout(() => {
        if (renderer3D && camera3D) {
          const canvas = document.getElementById('threeCanvas');
          if (canvas) {
            const w = canvas.parentElement.clientWidth;
            const h = canvas.parentElement.clientHeight;
            camera3D.aspect = w / h;
            camera3D.updateProjectionMatrix();
            renderer3D.setSize(w, h);
          }
        }
        desenharPlantaBaixa2D();
        desenharGraficoSeletividade();
        desenharDiagramaStringboxCanvas();
      }, 300);
    }

    function toggleGrupo(grupoId) {
      const grp = document.getElementById(grupoId);
      if (!grp) return;
      const hdr = grp.querySelector('.nav-group-header');
      grp.classList.toggle('open');
      if (hdr) hdr.classList.toggle('open');
    }

    function filtrarSidebar() {
      const q = (document.getElementById('navSearchInput').value || '').toLowerCase().trim();
      document.querySelectorAll('.nav-group').forEach(grp => {
        const itens = grp.querySelectorAll('.nav-subitem');
        let encontrou = false;
        itens.forEach(it => {
          const txt = it.innerText.toLowerCase();
          if (!q || txt.includes(q)) {
            it.style.display = 'flex';
            encontrou = true;
          } else {
            it.style.display = 'none';
          }
        });
        if (encontrou || !q) {
          grp.style.display = 'block';
          if (q) grp.classList.add('open');
        } else {
          grp.style.display = 'none';
        }
      });
    }

    // ========================================================
    // CARREGAMENTO DE DADOS REST (STANDALONE + FALLBACK)
    // ========================================================
    async function carregarTodosDados() {
      await Promise.all([
        carregarDadosProjeto(),
        carregarDadosRenovaveis('fazenda'),
        carregarDadosSeletividade(),
        carregarDadosStringbox(),
        carregarDadosOrcamento()
      ]);
    }

    async function carregarDadosProjeto() {
      try {
        const resp = await fetch('/api/v1/eletrica/dados-projeto');
        if (resp.ok) dadosProjeto = await resp.json();
      } catch (err) {
        console.warn("Utilizando dados calculados padrão em memória.");
      }
      renderizarTabelasEletricas();
    }

    async function carregarDadosRenovaveis(perfil) {
      perfilAtualRenovaveis = perfil;
      try {
        const resp = await fetch('/api/v1/renovaveis/dados');
        if (resp.ok) {
          dadosRenovaveis = await resp.json();
          renderizarDadosRenovaveis();
          return;
        }
      } catch (e) {
        console.warn("Utilizando preset de renováveis em memória.");
      }
      aplicarPresetRenovaveis(perfil);
    }

    async function selecionarPerfilRenovaveis(perfil) {
      document.querySelectorAll('.profile-btn').forEach(b => b.classList.remove('active'));
      const btn = document.getElementById(`pbtn-${perfil}`);
      if (btn) btn.classList.add('active');

      try {
        const resp = await fetch('/api/v1/renovaveis/calcular', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ perfil: perfil })
        });
        if (resp.ok) {
          dadosRenovaveis = await resp.json();
          renderizarDadosRenovaveis();
          return;
        }
      } catch (e) {
        console.warn("Fallback offline de cálculo de perfil.");
      }
      aplicarPresetRenovaveis(perfil);
    }

    async function carregarDadosSeletividade() {
      try {
        const resp = await fetch('/api/v1/eletrica/seletividade');
        if (resp.ok) {
          dadosSeletividade = await resp.json();
          renderizarTabelaSeletividade();
          desenharGraficoSeletividade();
          return;
        }
      } catch (e) {
        console.warn("Carregando seletividade padrão em memória.");
      }
      renderizarTabelaSeletividade();
      desenharGraficoSeletividade();
    }

    async function carregarDadosStringbox() {
      try {
        const resp = await fetch('/api/v1/renovaveis/stringbox');
        if (resp.ok) dadosStringbox = await resp.json();
      } catch (e) {
        console.warn("Carregando dados da stringbox em memória.");
      }
    }

    async function carregarDadosOrcamento() {
      try {
        const resp = await fetch('/api/v1/eletrica/orcamento');
        if (resp.ok) {
          dadosOrcamento = await resp.json();
          renderizarDadosOrcamento();
          return;
        }
      } catch (e) {
        console.warn("Carregando dados de orçamento em memória.");
      }
      renderizarDadosOrcamento();
    }

    // ========================================================
    // RENDERIZAÇÃO DE DADOS DAS ABAS
    // ========================================================
    function renderizarTabelasEletricas() {
      const dem = (dadosProjeto && dadosProjeto.demanda_instalacao) || {};
      const eq = (dadosProjeto && dadosProjeto.balanceamento_fases) || {};
      
      document.getElementById('valPotInstalada').innerText = (dem.potencia_instalada_total_kw || 48.2) + ' kW';
      document.getElementById('valDemanda').innerText = (dem.demanda_total_kva || 34.6) + ' kVA';
      document.getElementById('valDesequilibrio').innerText = (eq.desequilibrio_percentual || 1.43) + '%';
      
      const pots = eq.potencias_por_fase_va || { R: 16953, S: 16828, T: 16711 };
      document.getElementById('valFaseR').innerText = pots.R.toLocaleString() + ' VA';
      document.getElementById('valFaseS').innerText = pots.S.toLocaleString() + ' VA';
      document.getElementById('valFaseT').innerText = pots.T.toLocaleString() + ' VA';

      // 1. Cômodos
      const comodos = (dadosProjeto && dadosProjeto.comodos) || [
        { nome: "Garagem / Acesso", largura: 3.8, comprimento: 5.0, area_m2: 19.0, perimetro_m: 17.6, iluminacao: { potencia_va: 220, qtd_pontos: 2 }, tug: { qtd: 4, potencia_total_va: 400 }, tue: [], potencia_total_va: 620 },
        { nome: "Varanda Frontal", largura: 4.5, comprimento: 2.2, area_m2: 9.9, perimetro_m: 13.4, iluminacao: { potencia_va: 160, qtd_pontos: 1 }, tug: { qtd: 3, potencia_total_va: 300 }, tue: [], potencia_total_va: 460 },
        { nome: "Sala de Estar / Jantar", largura: 4.8, comprimento: 3.8, area_m2: 18.24, perimetro_m: 17.2, iluminacao: { potencia_va: 220, qtd_pontos: 2 }, tug: { qtd: 4, potencia_total_va: 400 }, tue: [{ nome: "Ar Condicionado 12k BTU", potencia_w: 1400 }], potencia_total_va: 2020 },
        { nome: "Cozinha Técnica", largura: 4.0, comprimento: 3.2, area_m2: 12.8, perimetro_m: 14.4, iluminacao: { potencia_va: 160, qtd_pontos: 2 }, tug: { qtd: 4, potencia_total_va: 2100 }, tue: [{ nome: "Forno Elétrico Embutir", potencia_w: 4400 }, { nome: "Micro-ondas", potencia_w: 2000 }], potencia_total_va: 8660 },
        { nome: "Área de Serviço", largura: 2.8, comprimento: 2.0, area_m2: 5.6, perimetro_m: 9.6, iluminacao: { potencia_va: 100, qtd_pontos: 1 }, tug: { qtd: 3, potencia_total_va: 1800 }, tue: [{ nome: "Lavadora e Secadora", potencia_w: 2500 }], potencia_total_va: 4400 },
        { nome: "Circulação / Hall", largura: 3.0, comprimento: 1.2, area_m2: 3.6, perimetro_m: 8.4, iluminacao: { potencia_va: 100, qtd_pontos: 1 }, tug: { qtd: 2, potencia_total_va: 200 }, tue: [], potencia_total_va: 300 },
        { nome: "BWC Social", largura: 1.6, comprimento: 2.4, area_m2: 3.84, perimetro_m: 8.0, iluminacao: { potencia_va: 100, qtd_pontos: 1 }, tug: { qtd: 1, potencia_total_va: 600 }, tue: [{ nome: "Chuveiro Eletrônico", potencia_w: 7500 }], potencia_total_va: 8200 },
        { nome: "Dormitório 1", largura: 3.2, comprimento: 3.0, area_m2: 9.6, perimetro_m: 12.4, iluminacao: { potencia_va: 160, qtd_pontos: 1 }, tug: { qtd: 3, potencia_total_va: 300 }, tue: [{ nome: "Ar Condicionado 9k BTU", potencia_w: 1000 }], potencia_total_va: 1460 },
        { nome: "Dormitório 2", largura: 3.2, comprimento: 2.8, area_m2: 8.96, perimetro_m: 12.0, iluminacao: { potencia_va: 100, qtd_pontos: 1 }, tug: { qtd: 3, potencia_total_va: 300 }, tue: [{ nome: "Ar Condicionado 9k BTU", potencia_w: 1000 }], potencia_total_va: 1400 },
        { nome: "Suíte Master", largura: 3.8, comprimento: 3.8, area_m2: 14.44, perimetro_m: 15.2, iluminacao: { potencia_va: 220, qtd_pontos: 2 }, tug: { qtd: 4, potencia_total_va: 400 }, tue: [{ nome: "Ar Condicionado 12k BTU", potencia_w: 1400 }], potencia_total_va: 2020 },
        { nome: "BWC Suíte", largura: 1.5, comprimento: 2.5, area_m2: 3.75, perimetro_m: 8.0, iluminacao: { potencia_va: 100, qtd_pontos: 1 }, tug: { qtd: 1, potencia_total_va: 600 }, tue: [{ nome: "Chuveiro Eletrônico Suíte", potencia_w: 7500 }], potencia_total_va: 8200 }
      ];

      const tbodyCom = document.getElementById('tbodyComodos');
      if (tbodyCom) {
        tbodyCom.innerHTML = '';
        comodos.forEach(c => {
          const tuesStr = (c.tue || []).map(t => `${t.nome} (${t.potencia_w}W)`).join(', ') || '<span style="color:#64748b">Nenhuma</span>';
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><strong>${c.nome}</strong></td>
            <td>${c.largura} x ${c.comprimento} m</td>
            <td>${c.area_m2} m²</td>
            <td>${c.perimetro_m} m</td>
            <td><span class="tag tag-yellow">${c.iluminacao.potencia_va} VA</span> (${c.iluminacao.qtd_pontos} pt)</td>
            <td>${c.tug.qtd} tomadas (${c.tug.potencia_total_va} VA)</td>
            <td>${tuesStr}</td>
            <td><strong>${c.potencia_total_va} VA</strong></td>
          `;
          tbodyCom.appendChild(tr);
        });
      }

      // 2. Circuitos QDC
      const circuitos = (dadosProjeto && dadosProjeto.circuitos) || [
        { numero: 1, descricao: "Iluminação Social e Garagem", tensao_v: 220, fases: ["R"], potencia_va: 860, potencia_w: 860, corrente_projeto_ib: 3.9, secao_condutor_mm2: 1.5, secao_neutro_mm2: 1.5, secao_pe_mm2: 1.5, disjuntor_in_a: 10, queda_tensao_percentual: 0.52, eletroduto_trecho_dn_mm: 20, dr_obrigatorio: false },
        { numero: 2, descricao: "Iluminação Íntima e Dormitórios", tensao_v: 220, fases: ["S"], potencia_va: 780, potencia_w: 780, corrente_projeto_ib: 3.5, secao_condutor_mm2: 1.5, secao_neutro_mm2: 1.5, secao_pe_mm2: 1.5, disjuntor_in_a: 10, queda_tensao_percentual: 0.48, eletroduto_trecho_dn_mm: 20, dr_obrigatorio: false },
        { numero: 3, descricao: "TUGs Salas e Circulação", tensao_v: 220, fases: ["T"], potencia_va: 600, potencia_w: 480, corrente_projeto_ib: 2.7, secao_condutor_mm2: 2.5, secao_neutro_mm2: 2.5, secao_pe_mm2: 2.5, disjuntor_in_a: 16, queda_tensao_percentual: 0.35, eletroduto_trecho_dn_mm: 20, dr_obrigatorio: true },
        { numero: 4, descricao: "TUGs Cozinha Bancada 1", tensao_v: 220, fases: ["R"], potencia_va: 1200, potencia_w: 960, corrente_projeto_ib: 5.5, secao_condutor_mm2: 2.5, secao_neutro_mm2: 2.5, secao_pe_mm2: 2.5, disjuntor_in_a: 20, queda_tensao_percentual: 0.62, eletroduto_trecho_dn_mm: 25, dr_obrigatorio: true },
        { numero: 5, descricao: "TUGs Cozinha Bancada 2", tensao_v: 220, fases: ["S"], potencia_va: 900, potencia_w: 720, corrente_projeto_ib: 4.1, secao_condutor_mm2: 2.5, secao_neutro_mm2: 2.5, secao_pe_mm2: 2.5, disjuntor_in_a: 16, queda_tensao_percentual: 0.45, eletroduto_trecho_dn_mm: 20, dr_obrigatorio: true },
        { numero: 6, descricao: "TUGs Área de Serviço e Lavanderia", tensao_v: 220, fases: ["T"], potencia_va: 1800, potencia_w: 1440, corrente_projeto_ib: 8.2, secao_condutor_mm2: 2.5, secao_neutro_mm2: 2.5, secao_pe_mm2: 2.5, disjuntor_in_a: 20, queda_tensao_percentual: 0.78, eletroduto_trecho_dn_mm: 25, dr_obrigatorio: true },
        { numero: 7, descricao: "TUE Chuveiro BWC Social", tensao_v: 220, fases: ["R"], potencia_va: 7500, potencia_w: 7500, corrente_projeto_ib: 34.1, secao_condutor_mm2: 6.0, secao_neutro_mm2: 6.0, secao_pe_mm2: 6.0, disjuntor_in_a: 40, queda_tensao_percentual: 1.85, eletroduto_trecho_dn_mm: 32, dr_obrigatorio: true },
        { numero: 8, descricao: "TUE Chuveiro BWC Suíte Master", tensao_v: 220, fases: ["S"], potencia_va: 7500, potencia_w: 7500, corrente_projeto_ib: 34.1, secao_condutor_mm2: 6.0, secao_neutro_mm2: 6.0, secao_pe_mm2: 6.0, disjuntor_in_a: 40, queda_tensao_percentual: 1.92, eletroduto_trecho_dn_mm: 32, dr_obrigatorio: true },
        { numero: 9, descricao: "TUE Forno Elétrico Cozinha", tensao_v: 220, fases: ["T"], potencia_va: 4400, potencia_w: 4400, corrente_projeto_ib: 20.0, secao_condutor_mm2: 4.0, secao_neutro_mm2: 4.0, secao_pe_mm2: 4.0, disjuntor_in_a: 25, queda_tensao_percentual: 1.15, eletroduto_trecho_dn_mm: 25, dr_obrigatorio: true },
        { numero: 10, descricao: "TUE Lavadora e Secadora", tensao_v: 220, fases: ["R"], potencia_va: 2500, potencia_w: 2500, corrente_projeto_ib: 11.4, secao_condutor_mm2: 2.5, secao_neutro_mm2: 2.5, secao_pe_mm2: 2.5, disjuntor_in_a: 16, queda_tensao_percentual: 0.92, eletroduto_trecho_dn_mm: 25, dr_obrigatorio: true },
        { numero: 11, descricao: "TUE Ar Condicionado Suíte 12k", tensao_v: 220, fases: ["S"], potencia_va: 1400, potencia_w: 1400, corrente_projeto_ib: 6.4, secao_condutor_mm2: 2.5, secao_neutro_mm2: 2.5, secao_pe_mm2: 2.5, disjuntor_in_a: 16, queda_tensao_percentual: 0.58, eletroduto_trecho_dn_mm: 20, dr_obrigatorio: false },
        { numero: 12, descricao: "TUE Ar Condicionado Sala 12k", tensao_v: 220, fases: ["T"], potencia_va: 1400, potencia_w: 1400, corrente_projeto_ib: 6.4, secao_condutor_mm2: 2.5, secao_neutro_mm2: 2.5, secao_pe_mm2: 2.5, disjuntor_in_a: 16, queda_tensao_percentual: 0.55, eletroduto_trecho_dn_mm: 20, dr_obrigatorio: false }
      ];

      const tbodyCirc = document.getElementById('tbodyCircuitos');
      if (tbodyCirc) {
        tbodyCirc.innerHTML = '';
        circuitos.forEach(circ => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><strong>#${circ.numero}</strong></td>
            <td>${circ.descricao}</td>
            <td>${circ.tensao_v}V</td>
            <td><span class="tag tag-${circ.fases[0] === 'R' ? 'red' : circ.fases[0] === 'S' ? 'yellow' : 'blue'}">${circ.fases.join(',')}</span></td>
            <td>${circ.potencia_va}</td>
            <td>${circ.potencia_w}</td>
            <td>${circ.corrente_projeto_ib} A</td>
            <td><strong># ${circ.secao_condutor_mm2} mm²</strong></td>
            <td># ${circ.secao_neutro_mm2 || '-'} mm²</td>
            <td># ${circ.secao_pe_mm2} mm²</td>
            <td><span class="tag tag-yellow">${circ.disjuntor_in_a}A DIN</span></td>
            <td>${circ.queda_tensao_percentual}%</td>
            <td>DN ${circ.eletroduto_trecho_dn_mm} mm</td>
            <td>${circ.dr_obrigatorio ? '<span class="tag tag-green">DR 30mA</span>' : '<span style="color:#64748b">Disp.</span>'}</td>
          `;
          tbodyCirc.appendChild(tr);
        });
      }

      // 3. Materiais
      const materiais = (dadosProjeto && dadosProjeto.lista_materiais) || [
        { item: "Cabo de Cobre Flexível 750V 1,5 mm² Antichama (Fase/Neutro/Retorno)", quantidade: "145.0", unidade: "metros" },
        { item: "Cabo de Cobre Flexível 750V 2,5 mm² Antichama (Fases/Neutro/Terra)", quantidade: "380.0", unidade: "metros" },
        { item: "Cabo de Cobre Flexível 750V 4,0 mm² Antichama (Forno Elétrico)", quantidade: "45.0", unidade: "metros" },
        { item: "Cabo de Cobre Flexível 750V 6,0 mm² Antichama (Chuveiros)", quantidade: "70.0", unidade: "metros" },
        { item: "Cabo de Cobre Flexível 1kV 25,0 mm² Alimentador Geral Trifásico", quantidade: "35.0", unidade: "metros" },
        { item: "Eletroduto Corrugado Flexível Reforçado Amarelo/Laranja DN 20 mm (3/4 pol.)", quantidade: "110.0", unidade: "metros" },
        { item: "Eletroduto Corrugado Flexível Reforçado Amarelo/Laranja DN 25 mm (1 pol.)", quantidade: "65.0", unidade: "metros" },
        { item: "Eletroduto Corrugado Flexível Reforçado Laranja DN 32 mm (1.1/4 pol.)", quantidade: "28.0", unidade: "metros" },
        { item: "Disjuntor Termomagnético DIN Curva C Monopolar 10A", quantidade: "6", unidade: "peças" },
        { item: "Disjuntor Termomagnético DIN Curva C Monopolar 16A", quantidade: "7", unidade: "peças" },
        { item: "Disjuntor Termomagnético DIN Curva C Monopolar 20A", quantidade: "2", unidade: "peças" },
        { item: "Disjuntor Termomagnético DIN Curva C Monopolar 25A", quantidade: "1", unidade: "peças" },
        { item: "Disjuntor Termomagnético DIN Curva C Monopolar 40A", quantidade: "2", unidade: "peças" },
        { item: "Disjuntor Termomagnético Geral DIN Curva C Tripolar 125A", quantidade: "1", unidade: "peça" },
        { item: "Interruptor Diferencial Residual (IDR) Tetrapolar 40A / 30mA", quantidade: "2", unidade: "peças" },
        { item: "Dispositivo de Proteção contra Surtos (DPS) Classe II 45kA / 275V", quantidade: "4", unidade: "peças" },
        { item: "Quadro de Distribuição de Embutir QDC 24/36 Módulos DIN com Barramentos", quantidade: "1", unidade: "peça" },
        { item: "Haste de Aterramento Aço Cobreado 5/8 pol. x 2,40m com Caixa de Inspeção", quantidade: "3", unidade: "peças" }
      ];

      const tbodyMat = document.getElementById('tbodyMateriais');
      if (tbodyMat) {
        tbodyMat.innerHTML = '';
        materiais.forEach((m, idx) => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${idx + 1}</td>
            <td>${m.item}</td>
            <td><strong>${m.quantidade}</strong></td>
            <td>${m.unidade}</td>
          `;
          tbodyMat.appendChild(tr);
        });
      }
    }

    function renderizarTabelaSeletividade() {
      const tbody = document.getElementById('tbodySeletividade');
      if (!tbody) return;
      tbody.innerHTML = '';

      const matriz = (dadosSeletividade && dadosSeletividade.matriz_seletividade) || [
        { circuito_num: 1, descricao: "Iluminação Social e Garagem", disjuntor_in_a: 10, curva: "B", razao_geral: 12.5, grau_seletividade: "TOTAL", limite_seletividade_a: 625, parecer: "Totalmente seletivo (Razão 12.5x > 1.6x). Sem desarme do geral." },
        { circuito_num: 3, descricao: "TUGs Salas e Circulação", disjuntor_in_a: 16, curva: "C", razao_geral: 7.81, grau_seletividade: "TOTAL", limite_seletividade_a: 625, parecer: "Totalmente seletivo (Razão 7.81x > 1.6x). Protegido com DR 30mA." },
        { circuito_num: 4, descricao: "TUGs Cozinha Bancada 1", disjuntor_in_a: 20, curva: "C", razao_geral: 6.25, grau_seletividade: "TOTAL", limite_seletividade_a: 625, parecer: "Totalmente seletivo. Suporta picos de motores eletrodomésticos." },
        { circuito_num: 7, descricao: "TUE Chuveiro BWC Social", disjuntor_in_a: 40, curva: "C", razao_geral: 3.12, grau_seletividade: "TOTAL", limite_seletividade_a: 625, parecer: "Totalmente seletivo (Razão 3.12x > 1.6x). Desarme pontual." },
        { circuito_num: 8, descricao: "TUE Chuveiro Suíte Master", disjuntor_in_a: 40, curva: "C", razao_geral: 3.12, grau_seletividade: "TOTAL", limite_seletividade_a: 625, parecer: "Totalmente seletivo. Sem interrupção da alimentação geral." }
      ];

      matriz.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>#${item.circuito_num}</strong></td>
          <td>${item.descricao}</td>
          <td><span class="tag tag-yellow">${item.disjuntor_in_a}A (${item.curva})</span></td>
          <td><span class="tag tag-red">125A (C)</span></td>
          <td><strong>${item.razao_geral} x</strong></td>
          <td>${item.limite_seletividade_a} A</td>
          <td><span class="tag tag-green">${item.grau_seletividade}</span></td>
          <td>${item.parecer}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderizarDadosOrcamento() {
      if (!dadosOrcamento) return;
      const res = dadosOrcamento.resumo_financeiro || {};
      const viab = dadosOrcamento.viabilidade_economica || {};

      document.getElementById('valOrcPrecoGlobal').innerText = 'R$ ' + (res.preco_global_venda_r || 804435.39).toLocaleString('pt-BR', {minimumFractionDigits: 2});
      document.getElementById('valOrcDescBdi').innerText = `Com BDI TCU de ${res.taxa_bdi_aplicada_pct || 24.20}% Aplicado`;
      document.getElementById('valOrcPayback').innerText = `${viab.payback_simples_anos || 4.9} / ${viab.payback_descontado_anos || 6.2} anos`;
      document.getElementById('valOrcVpl').innerText = 'R$ ' + (viab.vpl_25_anos_r || 684210.00).toLocaleString('pt-BR', {minimumFractionDigits: 2});
      document.getElementById('valOrcLcoe').innerText = 'R$ ' + (viab.lcoe_energia_r_kwh || 0.185).toLocaleString('pt-BR', {minimumFractionDigits: 3}) + ' / kWh';

      const tbody = document.getElementById('tbodyOrcamentoAnalitico');
      if (tbody && dadosOrcamento.itens_analiticos) {
        tbody.innerHTML = '';
        dadosOrcamento.itens_analiticos.forEach(it => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><strong>${it.item}</strong></td>
            <td><span class="tag tag-blue">${it.categoria}</span></td>
            <td>${it.quantidade}</td>
            <td>${it.unidade}</td>
            <td>R$ ${it.preco_unitario_r.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
            <td><strong>R$ ${it.subtotal_r.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</strong></td>
          `;
          tbody.appendChild(tr);
        });
      }
    }

    function recalcularBdiInterativo() {
      const ac = parseFloat(document.getElementById('sliderAC').value) / 100.0;
      const s = parseFloat(document.getElementById('sliderS').value) / 100.0;
      const r = parseFloat(document.getElementById('sliderR').value) / 100.0;
      const df = parseFloat(document.getElementById('sliderDF').value) / 100.0;
      const l = parseFloat(document.getElementById('sliderL').value) / 100.0;
      const t = parseFloat(document.getElementById('sliderT').value) / 100.0;

      document.getElementById('dispAC').innerText = (ac * 100).toFixed(1) + ' %';
      document.getElementById('dispS').innerText = (s * 100).toFixed(1) + ' %';
      document.getElementById('dispR').innerText = (r * 100).toFixed(1) + ' %';
      document.getElementById('dispDF').innerText = (df * 100).toFixed(1) + ' %';
      document.getElementById('dispL').innerText = (l * 100).toFixed(1) + ' %';
      document.getElementById('dispT').innerText = (t * 100).toFixed(2) + ' %';

      // Fórmula TCU: [ (1 + AC + S + R) * (1 + DF) * (1 + L) / (1 - T) ] - 1
      const num = (1.0 + ac + s + r) * (1.0 + df) * (1.0 + l);
      const den = 1.0 - t;
      const bdiCalc = ((num / den) - 1.0) * 100.0;
      
      document.getElementById('lblBdiCalculado').innerText = bdiCalc.toFixed(2) + ' %';
      
      const custoDiretoBase = (dadosOrcamento && dadosOrcamento.resumo_financeiro && dadosOrcamento.resumo_financeiro.custo_direto_total_r) || 647862.50;
      const precoNovo = custoDiretoBase * (1.0 + bdiCalc / 100.0);
      document.getElementById('valOrcPrecoGlobal').innerText = 'R$ ' + precoNovo.toLocaleString('pt-BR', {minimumFractionDigits: 2});
      document.getElementById('valOrcDescBdi').innerText = `Com BDI recalculado de ${bdiCalc.toFixed(2)}%`;
    }

    function renderizarDadosRenovaveis() {
      if (!dadosRenovaveis) return;
      const res = dadosRenovaveis;
      document.getElementById('valRenGeracaoMensal').innerText = (res.geracao_total_mensal_kwh || 14850).toLocaleString() + ' kWh/mês';
      document.getElementById('valRenGeracaoAnual').innerText = (res.geracao_total_anual_kwh || 178200).toLocaleString() + ' kWh/ano acumulados';
      document.getElementById('valRenAutossuficiencia').innerText = (res.taxa_autossuficiencia_pct || 174.7).toFixed(1) + ' %';
      document.getElementById('valRenStatus').innerText = res.status_operacional || 'Operação Otimizada';

      const eco = res.economia_financeira || {};
      document.getElementById('valRenEconomiaAnual').innerText = 'R$ ' + (eco.economia_anual_projetada_r || 117199).toLocaleString('pt-BR', {minimumFractionDigits: 2});
      document.getElementById('valRenEconomiaMensal').innerText = 'R$ ' + (eco.economia_mensal_estimada_r || 7225).toLocaleString('pt-BR', {minimumFractionDigits: 2}) + ' / mês em tarifa evitada';

      const esg = res.impacto_ambiental_esg || {};
      document.getElementById('valRenCO2').innerText = (esg.co2_equivalente_evitado_ano_ton || 369.8).toFixed(1) + ' t CO₂e / ano';
      document.getElementById('valRenArvores').innerText = 'Equivalente a ' + (esg.equivalente_arvores_plantadas || 2662).toLocaleString() + ' árvores preservadas';

      const f = res.fontes_integradas || {};
      if (f.solar) {
        document.getElementById('specSolarPico').innerText = f.solar.potencia_pico_kwp + ' kWp';
        document.getElementById('specSolarGeracao').innerText = (f.solar.geracao_estimada_kwh_mes || 0).toLocaleString() + ' kWh';
        const mod = f.solar.modulos || {};
        document.getElementById('specSolarModulos').innerText = `${mod.quantidade_modulos} un x ${mod.potencia_unitaria_wp}W ${mod.tecnologia || ''}`;
        const str = f.solar.strings || {};
        document.getElementById('specSolarStrings').innerText = `${str.quantidade_strings_paralelo || 10} strings x ${str.modulos_por_string_serie || 23} módulos`;
        document.getElementById('specSolarTensao').innerText = `${str.tensao_voc_max_arranjo_v || 1136} Vcc (MPPT: 500-850V)`;
        const inv = f.solar.inversor || {};
        document.getElementById('specSolarInversor').innerText = `${inv.potencia_nominal_kw} kW ${inv.tipo_conexao || 'Trifásico'} (Eficiência ${inv.eficiencia_pct || 98.6}%)`;
      }

      if (f.eolica) {
        document.getElementById('specEolicaModelo').innerText = f.eolica.modelo_aerogerador || 'HAWT Tripá';
        document.getElementById('specEolicaPotencia').innerText = `${f.eolica.potencia_nominal_kw} kW @ ${f.eolica.velocidade_vento_considerada_ms || 10.5} m/s`;
        document.getElementById('specEolicaGeracao').innerText = (f.eolica.geracao_mensal_kwh || 0).toLocaleString() + ' kWh';
        const mec = f.eolica.especificacoes_mecanicas || {};
        document.getElementById('specEolicaDiametro').innerText = `${mec.diametro_rotor_m || 9.2} metros`;
        document.getElementById('specEolicaTorre').innerText = `${mec.altura_torre_m || 24} metros estaiada`;
      }

      if (f.biodigestor) {
        document.getElementById('boxBiodigestorContent').style.display = 'block';
        document.getElementById('boxBiodigestorDispensado').style.display = 'none';
        const bio = f.biodigestor;
        document.getElementById('specBioOrigem').innerText = `${bio.plantel_animais} ${bio.tipo_criacao || 'animais'}`;
        const bal = bio.balanco_hidraulico || {};
        document.getElementById('specBioVazao').innerText = `${bal.vazao_dejetos_diaria_m3_dia} m³/dia (TRH = ${bal.tempo_retencao_hidraulica_dias} dias)`;
        const cav = bio.dimensoes_cava_trapezoidal || {};
        document.getElementById('specBioCava').innerText = `Comp. ${cav.comprimento_m}m x Crista ${cav.largura_topo_m}m x Prof. ${cav.profundidade_m}m`;
        document.getElementById('specBioVolume').innerText = `${cav.volume_util_m3} m³ útil`;
        const pot = bio.potencial_energetico_biogas || {};
        document.getElementById('specBioGas').innerText = `${pot.producao_biogas_m3_dia} m³/dia (${pot.percentual_metano_ch4_pct}% CH₄)`;
      } else {
        document.getElementById('boxBiodigestorContent').style.display = 'none';
        document.getElementById('boxBiodigestorDispensado').style.display = 'block';
      }

      atualizarTabelaBalanco([
        { vetor: "☀️ Solar Fotovoltaica", tech: "Usina de Solo Monoposte 18°", pot: "150.0 kWp", ger: "19.500", reg: "Diurno Intermitente", int: "Inversor 125kW Trifásico 380V" },
        { vetor: "💨 Eólica de Médio Porte", tech: "Aerogerador Tripá Torre 24m", pot: "20.0 kW", ger: "3.850", reg: "Ventos Rurais Contínuos", int: "Inversor Grid-Tie com Dump Load" },
        { vetor: "🧪 Biodigestor Anaeróbio", tech: "Cava Trapezoidal Geomembrana PEAD", pot: "250 m³/dia", ger: "Biogás", reg: "Digestão Mesofílica Contínua", int: "Filtro H₂S, Purgadores e Flare" },
        { vetor: "🔥 Motogerador a Biogás CHP", tech: "Motor Ciclo Otto Cogeração", pot: "75.0 kW (112kWt)", ger: "9.000", reg: "Despacho Firme / Base", int: "Sincronismo Paralelo com a Rede" },
        { vetor: "💧 Micro-Hidrelétrica PCH", tech: "Turbina Pelton com Conduto PEAD", pot: "15.0 kW", ger: "9.240", reg: "Despacho 24h Base Contínua", int: "Regulador ELC e Gerador Síncrono" }
      ]);
    }

    function aplicarPresetRenovaveis(perfil) {
      if (perfil === 'residencial') {
        document.getElementById('valRenGeracaoMensal').innerText = '1.420 kWh/mês';
        document.getElementById('valRenGeracaoAnual').innerText = '17.040 kWh/ano acumulados';
        document.getElementById('valRenAutossuficiencia').innerText = '100.0 %';
        document.getElementById('valRenStatus').innerText = 'Equilíbrio Pleno com a Concessionária';
        document.getElementById('valRenEconomiaAnual').innerText = 'R$ 14.484 / ano';
        document.getElementById('valRenEconomiaMensal').innerText = 'R$ 1.207 / mês em tarifa evitada';
        document.getElementById('valRenCO2').innerText = '35.4 t CO₂e / ano';
        document.getElementById('valRenArvores').innerText = 'Equivalente a 255 árvores preservadas';

        document.getElementById('specSolarPico').innerText = '8.8 kWp';
        document.getElementById('specSolarModulos').innerText = '16 un x 550W Monocristalino Half-Cell';
        document.getElementById('specSolarStrings').innerText = '2 strings x 8 módulos em série';
        document.getElementById('specSolarTensao').innerText = '396 Vcc (Faixa MPPT: 160-500V)';
        document.getElementById('specSolarInversor').innerText = '8.0 kW Monofásico/Bifásico (Eficiência 97.8%)';
        document.getElementById('specSolarEstrutura').innerText = 'Telhado Cerâmico / Metálico inclinado';
        document.getElementById('specSolarGeracao').innerText = '1.144 kWh/mês';

        document.getElementById('specEolicaModelo').innerText = 'VAWT Eixo Vertical Darrieus/Savonius';
        document.getElementById('specEolicaPotencia').innerText = '2.0 kW @ 9.0 m/s (Baixo ruído)';
        document.getElementById('specEolicaDiametro').innerText = '2.4 m diâmetro x 3.0 m altura';
        document.getElementById('specEolicaTorre').innerText = '6.0 metros autoportante de cobertura';
        document.getElementById('specEolicaGeracao').innerText = '276 kWh/mês';

        document.getElementById('boxBiodigestorContent').style.display = 'none';
        document.getElementById('boxBiodigestorDispensado').style.display = 'block';
        document.getElementById('boxChpContent').style.display = 'none';
        document.getElementById('boxChpDispensado').style.display = 'block';

        atualizarTabelaBalanco([
          { vetor: "☀️ Solar Fotovoltaica", tech: "Módulos Mono-PERC de Telhado", pot: "8.8 kWp", ger: "1.144", reg: "Diurno Intermitente", int: "Inversor On-Grid Stringbox CC" },
          { vetor: "💨 Microeólica Urbana", tech: "Aerogerador Vertical VAWT", pot: "2.0 kW", ger: "276", reg: "Contínuo (Dia e Noite)", int: "Retificador AC/DC e Inversor Grid-Tie" }
        ]);
      } else if (perfil === 'predial') {
        document.getElementById('valRenGeracaoMensal').innerText = '6.850 kWh/mês';
        document.getElementById('valRenGeracaoAnual').innerText = '82.200 kWh/ano acumulados';
        document.getElementById('valRenAutossuficiencia').innerText = '122.5 %';
        document.getElementById('valRenStatus').innerText = 'Geração Compartilhada (EMUC Lei 14.300)';
        document.getElementById('valRenEconomiaAnual').innerText = 'R$ 69.870 / ano';
        document.getElementById('valRenEconomiaMensal').innerText = 'R$ 5.822 / mês em créditos';
        document.getElementById('valRenCO2').innerText = '170.9 t CO₂e / ano';
        document.getElementById('valRenArvores').innerText = 'Equivalente a 1.230 árvores preservadas';

        document.getElementById('specSolarPico').innerText = '49.5 kWp';
        document.getElementById('specSolarModulos').innerText = '90 un x 550W Monocristalino N-Type';
        document.getElementById('specSolarStrings').innerText = '5 strings x 18 módulos em série';
        document.getElementById('specSolarTensao').innerText = '891 Vcc (Faixa MPPT: 350-800V)';
        document.getElementById('specSolarInversor').innerText = '40.0 kW Trifásico 380V (Eficiência 98.4%)';
        document.getElementById('specSolarEstrutura').innerText = 'Laje plana de cobertura com lastro 15° Norte';
        document.getElementById('specSolarGeracao').innerText = '6.435 kWh/mês';

        document.getElementById('specEolicaModelo').innerText = 'VAWT Helicoide de Baixo Ruído Acústico';
        document.getElementById('specEolicaPotencia').innerText = '3.0 kW @ 9.5 m/s';
        document.getElementById('specEolicaDiametro').innerText = '3.0 m diâmetro x 4.2 m altura';
        document.getElementById('specEolicaTorre').innerText = '8.0 m mastro de topo predial';
        document.getElementById('specEolicaGeracao').innerText = '415 kWh/mês';

        document.getElementById('boxBiodigestorContent').style.display = 'none';
        document.getElementById('boxBiodigestorDispensado').style.display = 'block';
        document.getElementById('boxChpContent').style.display = 'none';
        document.getElementById('boxChpDispensado').style.display = 'block';

        atualizarTabelaBalanco([
          { vetor: "☀️ Solar Fotovoltaica", tech: "Arranjo Cobertura Predial Lastrada", pot: "49.5 kWp", ger: "6.435", reg: "Diurno Intermitente", int: "Inversor Central Trifásico 380V" },
          { vetor: "💨 Eólica de Topo", tech: "Aerogerador Vertical Silencioso", pot: "3.0 kW", ger: "415", reg: "Ventos de Altitude", int: "Acoplamento CC com Inversor Híbrido" }
        ]);
      } else {
        renderizarDadosRenovaveis();
      }
    }

    function atualizarTabelaBalanco(itens) {
      const tbody = document.getElementById('tbodyBalancoRenovaveis');
      if (!tbody) return;
      tbody.innerHTML = '';
      itens.forEach(it => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${it.vetor}</strong></td>
          <td>${it.tech}</td>
          <td><span class="tag tag-yellow">${it.pot}</span></td>
          <td><strong>${it.ger}</strong></td>
          <td>${it.reg}</td>
          <td><span class="tag tag-blue">${it.int}</span></td>
        `;
        tbody.appendChild(tr);
      });
    }

    // ========================================================
    // RENDERIZADOR 2D CAD (PLANTA BAIXA RESIDENCIAL CANVAS)
    // ========================================================
    function desenharPlantaBaixa2D() {
      const canvas = document.getElementById('cadCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.parentElement.clientWidth;
      const h = canvas.parentElement.clientHeight;
      canvas.width = w;
      canvas.height = h;

      // Fundo escuro CAD
      ctx.fillStyle = '#050811';
      ctx.fillRect(0, 0, w, h);

      // Grade milimetrada de fundo
      ctx.strokeStyle = '#111827';
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
      }
      for (let y = 0; y < h; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
      }

      // Escala e centro
      const escala = Math.min(w / 16, h / 12) * 0.85;
      const ox = w * 0.32;
      const oy = h * 0.65;

      function toScreen(x, y) {
        return { x: ox + x * escala, y: oy - y * escala };
      }

      // Cômodos Arquitetônicos
      const layout = [
        { id: "garagem", x: -4.0, y: 0.0, w: 3.8, h: 5.0, nome: "GARAGEM" },
        { id: "varanda", x: 0.0, y: -2.4, w: 4.5, h: 2.2, nome: "VARANDA" },
        { id: "sala", x: 0.0, y: 0.0, w: 4.8, h: 3.8, nome: "SALA ESTAR" },
        { id: "cozinha", x: 5.0, y: 0.0, w: 4.0, h: 3.2, nome: "COZINHA" },
        { id: "servico", x: 5.0, y: 3.4, w: 2.8, h: 2.0, nome: "ÁREA SERV." },
        { id: "hall", x: 0.0, y: 4.0, w: 3.0, h: 1.2, nome: "CIRCULAÇÃO" },
        { id: "bwc_soc", x: 3.2, y: 4.0, w: 1.6, h: 2.4, nome: "BWC" },
        { id: "dorm1", x: 0.0, y: 5.4, w: 3.2, h: 3.0, nome: "QUARTO 1" },
        { id: "dorm2", x: 3.4, y: 5.6, w: 3.2, h: 2.8, nome: "QUARTO 2" },
        { id: "suite", x: 6.8, y: 4.6, w: 3.8, h: 3.8, nome: "SUÍTE" }
      ];

      // Desenhar Paredes
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 3;
      layout.forEach(c => {
        const p1 = toScreen(c.x, c.y);
        const p2 = toScreen(c.x + c.w, c.y + c.h);
        ctx.strokeRect(p1.x, p2.y, p2.x - p1.x, p1.y - p2.y);

        ctx.fillStyle = '#64748b';
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'center';
        const pc = toScreen(c.x + c.w / 2, c.y + c.h / 2);
        ctx.fillText(c.nome, pc.x, pc.y + 16);
      });

      // Posição do QDC (Parede da Circulação)
      const qdcPos = toScreen(3.0, 3.6);
      ctx.fillStyle = '#d946ef';
      ctx.fillRect(qdcPos.x - 14, qdcPos.y - 8, 28, 16);
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 9px sans-serif';
      ctx.fillText('QDC', qdcPos.x, qdcPos.y + 3);

      // Pontos de Luz e Eletrodutos
      layout.forEach((c, idx) => {
        const pl = toScreen(c.x + c.w / 2, c.y + c.h / 2);

        // Linha de Eletroduto até o QDC
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(pl.x, pl.y);
        ctx.lineTo(qdcPos.x, qdcPos.y);
        ctx.stroke();

        // Traços NBR 5444
        const mx = (pl.x + qdcPos.x) / 2;
        const my = (pl.y + qdcPos.y) / 2;
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(mx, my - 6); ctx.lineTo(mx, my + 6); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(mx + 6, my - 6); ctx.lineTo(mx + 6, my + 6); ctx.lineTo(mx + 2, my - 6); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(mx - 6, my - 6); ctx.lineTo(mx - 6, my + 6); ctx.moveTo(mx - 9, my - 6); ctx.lineTo(mx - 3, my - 6); ctx.stroke();

        // Ponto de Luz no Teto
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 2;
        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.arc(pl.x, pl.y, 14, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(pl.x - 14, pl.y);
        ctx.lineTo(pl.x + 14, pl.y);
        ctx.stroke();

        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 9px sans-serif';
        ctx.fillText(`C${idx < 5 ? 1 : 2}`, pl.x, pl.y - 3);
        ctx.font = '8px sans-serif';
        ctx.fillText('100', pl.x, pl.y + 9);
      });
    }

    // ========================================================
    // RENDERIZADOR 2D CANVAS: GRÁFICO LOG-LOG DE SELETIVIDADE
    // ========================================================
    function desenharGraficoSeletividade() {
      const canvas = document.getElementById('seletividadeCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.parentElement.clientWidth;
      const h = canvas.parentElement.clientHeight;
      canvas.width = w;
      canvas.height = h;

      ctx.fillStyle = '#050811';
      ctx.fillRect(0, 0, w, h);

      const margemEsq = 65, margemDir = 30, margemSup = 30, margemInf = 50;
      const gw = w - margemEsq - margemDir;
      const gh = h - margemSup - margemInf;

      const logImin = Math.log10(1.0), logImax = Math.log10(10000.0);
      const logTmin = Math.log10(0.01), logTmax = Math.log10(1000.0);

      function coordLog(iVal, tVal) {
        const u = (Math.log10(Math.max(1.0, iVal)) - logImin) / (logImax - logImin);
        const v = (Math.log10(Math.max(0.01, tVal)) - logTmin) / (logTmax - logTmin);
        return { x: margemEsq + u * gw, y: (margemSup + gh) - v * gh };
      }

      // Grade Logarítmica
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1;
      const decadasT = [0.01, 0.1, 1, 10, 100, 1000];
      decadasT.forEach(t => {
        const p = coordLog(1.0, t);
        ctx.beginPath(); ctx.moveTo(margemEsq, p.y); ctx.lineTo(margemEsq + gw, p.y); ctx.stroke();
        ctx.fillStyle = '#64748b';
        ctx.font = '10px monospace';
        ctx.textAlign = 'right';
        ctx.fillText(t >= 1 ? `${t}s` : `${t}s`, margemEsq - 8, p.y + 3);
      });

      const decadasI = [1, 10, 100, 1000, 10000];
      decadasI.forEach(i => {
        const p = coordLog(i, 0.01);
        ctx.beginPath(); ctx.moveTo(p.x, margemSup); ctx.lineTo(p.x, margemSup + gh); ctx.stroke();
        ctx.fillStyle = '#64748b';
        ctx.font = '10px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`${i}A`, p.x, margemSup + gh + 18);
      });

      // Bordas principais
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(margemEsq, margemSup, gw, gh);

      // Função auxiliar para plotar curva
      function plotarCurva(pontos, cor) {
        if (!pontos || pontos.length < 2) return;
        ctx.strokeStyle = cor;
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        pontos.forEach((pt, idx) => {
          const p = coordLog(pt.corrente_a, pt.tempo_max_s);
          if (idx === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
        });
        ctx.stroke();
      }

      const curvas = (dadosSeletividade && dadosSeletividade.curvas_plotagem_log_log) || {};
      plotarCurva(curvas.geral_125a_c, '#ef4444');
      plotarCurva(curvas.chuveiro_40a_c, '#f59e0b');
      plotarCurva(curvas.tomadas_20a_c, '#10b981');
      plotarCurva(curvas.iluminacao_10a_b, '#06b6d4');

      // Se houver corrente de falta simulada, traça linha vertical amarela tracejada
      if (correnteFaltaSimulada) {
        const pf = coordLog(correnteFaltaSimulada, 0.01);
        ctx.strokeStyle = '#facc15';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath(); ctx.moveTo(pf.x, margemSup); ctx.lineTo(pf.x, margemSup + gh); ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = '#facc15';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`⚡ Falta Simulada: ${correnteFaltaSimulada}A`, pf.x, margemSup - 10);
      }
    }

    function simularFaltaSeletividade(correnteA) {
      correnteFaltaSimulada = correnteA;
      desenharGraficoSeletividade();
    }

    // ========================================================
    // RENDERIZADOR 2D CANVAS: STRINGBOX SOLAR CC
    // ========================================================
    function desenharDiagramaStringboxCanvas() {
      const canvas = document.getElementById('stringboxCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.parentElement.clientWidth;
      const h = canvas.parentElement.clientHeight;
      canvas.width = w;
      canvas.height = h;

      ctx.fillStyle = '#050811';
      ctx.fillRect(0, 0, w, h);

      // Caixa da Stringbox IP65
      const bx = w * 0.22, by = h * 0.12, bw = w * 0.52, bh = h * 0.76;
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 2.5;
      ctx.strokeRect(bx, by, bw, bh);

      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 13px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('STRINGBOX SOLAR CC (IP65)', bx + bw / 2, by - 12);

      // Módulos Fotovoltaicos à Esquerda
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.fillRect(40, by + 40, 70, 90); ctx.strokeRect(40, by + 40, 70, 90);
      ctx.fillRect(40, by + bh - 130, 70, 90); ctx.strokeRect(40, by + bh - 130, 70, 90);

      ctx.fillStyle = '#fff';
      ctx.font = 'bold 10px sans-serif';
      ctx.fillText('STRING 1', 75, by + 85);
      ctx.fillText('STRING 2', 75, by + bh - 85);

      // Condutores CC (+) e (-) entrando na Stringbox
      const y1p = by + 65, y1n = by + 105;
      const y2p = by + bh - 105, y2n = by + bh - 65;

      ctx.strokeStyle = '#ef4444'; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.moveTo(110, y1p); ctx.lineTo(bx + 80, y1p); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(110, y2p); ctx.lineTo(bx + 80, y2p); ctx.stroke();

      ctx.strokeStyle = '#64748b'; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.moveTo(110, y1n); ctx.lineTo(bx + 80, y1n); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(110, y2n); ctx.lineTo(bx + 80, y2n); ctx.stroke();

      // Porta Fusíveis gPV
      const fWidth = 45, fHeight = 26;
      [y1p, y1n, y2p, y2n].forEach((fy, idx) => {
        ctx.fillStyle = '#0f172a';
        ctx.strokeStyle = '#06b6d4';
        ctx.lineWidth = 1.5;
        ctx.fillRect(bx + 80, fy - fHeight / 2, fWidth, fHeight);
        ctx.strokeRect(bx + 80, fy - fHeight / 2, fWidth, fHeight);

        ctx.fillStyle = idx % 2 === 0 ? '#ef4444' : '#94a3b8';
        ctx.font = '9px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('gPV 20A', bx + 80 + fWidth / 2, fy + 3);
      });

      // DPS em Y
      const dpsX = bx + bw * 0.48, dpsY = by + bh - 160;
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.fillRect(dpsX, dpsY, 90, 80);
      ctx.strokeRect(dpsX, dpsY, 90, 80);
      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 10px sans-serif';
      ctx.fillText('DPS CC (Y)', dpsX + 45, dpsY + 28);
      ctx.font = '9px sans-serif';
      ctx.fillText('1000V / 40kA', dpsX + 45, dpsY + 46);

      // Chave Seccionadora CC Rotativa
      const secX = bx + bw * 0.72, secY = by + 85;
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2;
      ctx.fillRect(secX, secY, 70, 70);
      ctx.strokeRect(secX, secY, 70, 70);
      ctx.fillStyle = '#f59e0b';
      ctx.font = 'bold 10px sans-serif';
      ctx.fillText('CHAVE CC', secX + 35, secY + 30);
      ctx.font = '9px sans-serif';
      ctx.fillText('63A DC-PV2', secX + 35, secY + 48);

      // Barramento de Aterramento BEP
      const bepY = by + bh - 30;
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 4;
      ctx.beginPath(); ctx.moveTo(bx + 20, bepY); ctx.lineTo(bx + bw - 20, bepY); ctx.stroke();
      ctx.fillStyle = '#10b981';
      ctx.font = 'bold 9px sans-serif';
      ctx.fillText('BARRAMENTO BEP (ATERRAMENTO PE 16 mm²)', bx + bw / 2, bepY - 8);

      // Conexão DPS ao BEP
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(dpsX + 45, dpsY + 80); ctx.lineTo(dpsX + 45, bepY); ctx.stroke();

      // Saída para Inversor Solar
      const invX = w - 100, invY = by + 60;
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 2;
      ctx.fillRect(invX, invY, 75, 120);
      ctx.strokeRect(invX, invY, 75, 120);
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 10px sans-serif';
      ctx.fillText('INVERSOR', invX + 37, invY + 55);
      ctx.fillText('GRID-TIE', invX + 37, invY + 70);

      // Linhas da Chave ao Inversor
      ctx.strokeStyle = '#ef4444'; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.moveTo(secX + 70, secY + 25); ctx.lineTo(invX, secY + 25); ctx.stroke();
      ctx.strokeStyle = '#64748b'; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.moveTo(secX + 70, secY + 45); ctx.lineTo(invX, secY + 45); ctx.stroke();
    }

    // ========================================================
    // RENDERIZADOR 3D WEBGL (THREE.JS)
    // ========================================================
    let scene3D, camera3D, renderer3D, controls3D;
    let cenarioResidencialGroup = new THREE.Group();
    let cenarioAgroGroup = new THREE.Group();
    let paredesGroup = new THREE.Group();
    let tubulacoesGroup = new THREE.Group();
    let aparelhosGroup = new THREE.Group();
    let bladesMesh = null;
    let flareLight = null;
    let turbinaPeltonMesh = null;

    function initThreeScene() {
      const canvas = document.getElementById('threeCanvas');
      if (!canvas || renderer3D) return;

      const w = canvas.parentElement.clientWidth;
      const h = canvas.parentElement.clientHeight;

      scene3D = new THREE.Scene();
      scene3D.background = new THREE.Color(0x060913);

      camera3D = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000);
      camera3D.position.set(24, 25, 32);

      renderer3D = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
      renderer3D.setSize(w, h);
      renderer3D.shadowMap.enabled = true;

      controls3D = new THREE.OrbitControls(camera3D, renderer3D.domElement);
      controls3D.enableDamping = true;
      controls3D.dampingFactor = 0.05;
      controls3D.target.set(5, 2, 5);

      const ambLight = new THREE.AmbientLight(0xffffff, 0.85);
      scene3D.add(ambLight);

      const dirLight = new THREE.DirectionalLight(0xffffff, 1.4);
      dirLight.position.set(30, 50, 30);
      scene3D.add(dirLight);

      const grid = new THREE.GridHelper(60, 60, 0x334155, 0x1e293b);
      scene3D.add(grid);

      cenarioResidencialGroup.add(paredesGroup);
      cenarioResidencialGroup.add(tubulacoesGroup);
      cenarioResidencialGroup.add(aparelhosGroup);
      scene3D.add(cenarioResidencialGroup);
      scene3D.add(cenarioAgroGroup);

      construirCenarioResidencial3D();
      construirCenarioAgro3D();
      animar3D();
    }

    function alternarCenario3D(modo) {
      document.querySelectorAll('.scene-btn').forEach(b => b.classList.remove('active'));
      if (modo === 'residencial') {
        const btn = document.getElementById('btnSceneResidencial');
        if (btn) btn.classList.add('active');
        cenarioResidencialGroup.visible = true;
        cenarioAgroGroup.visible = false;
        camera3D.position.set(16, 18, 22);
        controls3D.target.set(3, 1, 3);
      } else if (modo === 'agro') {
        const btn = document.getElementById('btnSceneAgro');
        if (btn) btn.classList.add('active');
        cenarioResidencialGroup.visible = false;
        cenarioAgroGroup.visible = true;
        camera3D.position.set(26, 26, 30);
        controls3D.target.set(12, 4, 10);
      } else {
        const btn = document.getElementById('btnSceneIntegrado');
        if (btn) btn.classList.add('active');
        cenarioResidencialGroup.visible = true;
        cenarioAgroGroup.visible = true;
        camera3D.position.set(36, 36, 46);
        controls3D.target.set(8, 2, 8);
      }
    }

    function construirCenarioResidencial3D() {
      const matParedes = new THREE.MeshStandardMaterial({ color: 0x334155, transparent: true, opacity: 0.75 });
      const matPiso = new THREE.MeshStandardMaterial({ color: 0x0f172a });

      const pisoGeo = new THREE.BoxGeometry(16, 0.2, 14);
      const piso = new THREE.Mesh(pisoGeo, matPiso);
      piso.position.set(3, -0.1, 3);
      cenarioResidencialGroup.add(piso);

      function criarParede(x, z, w, d, h = 3.0) {
        const geo = new THREE.BoxGeometry(w, h, d);
        const mesh = new THREE.Mesh(geo, matParedes);
        mesh.position.set(x, h / 2, z);
        paredesGroup.add(mesh);
      }

      criarParede(3, -4, 16, 0.25);
      criarParede(3, 10, 16, 0.25);
      criarParede(-5, 3, 0.25, 14);
      criarParede(11, 3, 0.25, 14);
      criarParede(1, 3, 0.2, 14);
      criarParede(3, 3, 8, 0.2);

      const qdcGeo = new THREE.BoxGeometry(0.8, 1.2, 0.2);
      const qdcMat = new THREE.MeshStandardMaterial({ color: 0xd946ef, metalness: 0.5, roughness: 0.3 });
      const qdcMesh = new THREE.Mesh(qdcGeo, qdcMat);
      qdcMesh.position.set(1.1, 1.6, 3);
      aparelhosGroup.add(qdcMesh);

      const matTubo = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.2 });
      const pontosTubo = [
        new THREE.Vector3(1.1, 2.8, 3),
        new THREE.Vector3(1.1, 3.2, 3),
        new THREE.Vector3(5, 3.2, 3),
        new THREE.Vector3(5, 3.2, 6),
        new THREE.Vector3(5, 2.4, 6)
      ];
      const curve = new THREE.CatmullRomCurve3(pontosTubo);
      const tubeGeo = new THREE.TubeGeometry(curve, 32, 0.08, 8, false);
      const tubeMesh = new THREE.Mesh(tubeGeo, matTubo);
      tubulacoesGroup.add(tubeMesh);

      const matLuz = new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xf59e0b, emissiveIntensity: 0.8 });
      const luzGeo = new THREE.CylinderGeometry(0.3, 0.3, 0.08, 16);
      const luzMesh = new THREE.Mesh(luzGeo, matLuz);
      luzMesh.position.set(5, 3.15, 6);
      aparelhosGroup.add(luzMesh);
    }

    function construirCenarioAgro3D() {
      // 1. Usina Solar Fotovoltaica (Solo)
      const mesaGroup = new THREE.Group();
      const painelMat = new THREE.MeshStandardMaterial({ color: 0x1e3a8a, metalness: 0.8, roughness: 0.2 });
      const molduraMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9 });

      for (let r = 0; r < 2; r++) {
        for (let c = 0; c < 6; c++) {
          const modMesh = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.05, 2.4), painelMat);
          modMesh.position.set(c * 1.7, 0.8 + r * 0.7, r * 2.2);
          modMesh.rotation.x = -Math.PI / 10;
          mesaGroup.add(modMesh);
        }
      }
      mesaGroup.position.set(14, 0, -2);
      cenarioAgroGroup.add(mesaGroup);

      // 2. Aerogerador Eólico
      const eolicaGroup = new THREE.Group();
      const torreGeo = new THREE.CylinderGeometry(0.4, 0.8, 18, 16);
      const metalMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, metalness: 0.8, roughness: 0.3 });
      const torreMesh = new THREE.Mesh(torreGeo, metalMat);
      torreMesh.position.y = 9;
      eolicaGroup.add(torreMesh);

      const nacelleGeo = new THREE.BoxGeometry(1.4, 1.2, 3.0);
      const nacelleMesh = new THREE.Mesh(nacelleGeo, metalMat);
      nacelleMesh.position.set(0, 18, 0.5);
      eolicaGroup.add(nacelleMesh);

      bladesMesh = new THREE.Group();
      const bladeGeo = new THREE.BoxGeometry(0.3, 4.5, 0.1);
      for (let i = 0; i < 3; i++) {
        const b = new THREE.Mesh(bladeGeo, metalMat);
        b.rotation.z = (i * Math.PI * 2) / 3;
        b.position.y = Math.cos((i * Math.PI * 2) / 3) * 2.2;
        b.position.x = -Math.sin((i * Math.PI * 2) / 3) * 2.2;
        bladesMesh.add(b);
      }
      bladesMesh.position.set(0, 18, 2.1);
      eolicaGroup.add(bladesMesh);

      eolicaGroup.position.set(22, 0, 14);
      cenarioAgroGroup.add(eolicaGroup);

      // 3. Biodigestor Rural
      const bioGroup = new THREE.Group();
      const cúpulaGeo = new THREE.SphereGeometry(4.5, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);
      const peadMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.9 });
      const cupulaMesh = new THREE.Mesh(cúpulaGeo, peadMat);
      cupulaMesh.scale.set(1.6, 0.7, 1.2);
      bioGroup.add(cupulaMesh);

      flareLight = new THREE.PointLight(0xf97316, 1.5, 12);
      flareLight.position.set(0, 5, 0);
      bioGroup.add(flareLight);

      bioGroup.position.set(14, 0, 8);
      cenarioAgroGroup.add(bioGroup);

      // 4. Casa de Força CHP
      const chpGroup = new THREE.Group();
      const chpGeo = new THREE.BoxGeometry(3.5, 3.0, 4.5);
      const chpMat = new THREE.MeshStandardMaterial({ color: 0x334155 });
      const chpPredio = new THREE.Mesh(chpGeo, chpMat);
      chpPredio.position.y = 1.5;
      chpGroup.add(chpPredio);

      const chamGeo = new THREE.CylinderGeometry(0.12, 0.12, 4.2, 12);
      const chamMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8 });
      const chamMesh = new THREE.Mesh(chamGeo, chamMat);
      chamMesh.position.set(1.4, 3.5, 0);
      chpGroup.add(chamMesh);

      chpGroup.position.set(14, 0, 16);
      cenarioAgroGroup.add(chpGroup);

      // 5. Micro-Hidrelétrica PCH Rural (Rio, Barramento, Conduto e Casa de Força)
      const pchGroup = new THREE.Group();
      
      // Rio / Curso d'Água Sinuoso
      const rioGeo = new THREE.PlaneGeometry(10, 36);
      const rioMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.1, metalness: 0.6 });
      const rioMesh = new THREE.Mesh(rioGeo, rioMat);
      rioMesh.rotation.x = -Math.PI / 2;
      rioMesh.position.set(0, -0.05, 6);
      pchGroup.add(rioMesh);

      // Barramento de Captação
      const barGeo = new THREE.BoxGeometry(10, 1.8, 1.5);
      const barMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.7 });
      const barMesh = new THREE.Mesh(barGeo, barMat);
      barMesh.position.set(0, 0.9, -10);
      pchGroup.add(barMesh);

      // Conduto Forçado PEAD Descendo o Declive
      const pontosPch = [
        new THREE.Vector3(3.5, 1.2, -9.5),
        new THREE.Vector3(5.5, 0.8, -2.0),
        new THREE.Vector3(7.5, 0.5, 8.0),
        new THREE.Vector3(7.5, 0.3, 14.0)
      ];
      const curvePch = new THREE.CatmullRomCurve3(pontosPch);
      const tubPchGeo = new THREE.TubeGeometry(curvePch, 32, 0.22, 10, false);
      const tubPchMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.5 });
      const tubPchMesh = new THREE.Mesh(tubPchGeo, tubPchMat);
      pchGroup.add(tubPchMesh);

      // Casa de Força PCH
      const pchPredioGeo = new THREE.BoxGeometry(3.0, 2.5, 3.5);
      const pchPredioMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.3 });
      const pchPredio = new THREE.Mesh(pchPredioGeo, pchPredioMat);
      pchPredio.position.set(8.5, 1.25, 15.5);
      pchGroup.add(pchPredio);

      // Turbina Pelton Rotação
      turbinaPeltonMesh = new THREE.Mesh(
        new THREE.CylinderGeometry(0.5, 0.5, 0.2, 16),
        new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.9 })
      );
      turbinaPeltonMesh.position.set(8.5, 0.6, 17.5);
      pchGroup.add(turbinaPeltonMesh);

      pchGroup.position.set(-6, 0, 0);
      cenarioAgroGroup.add(pchGroup);
    }

    function toggleModoWireframe() {
      paredesGroup.traverse(child => {
        if (child.isMesh) child.material.wireframe = !child.material.wireframe;
      });
    }

    function isolarTubulacao() {
      paredesGroup.visible = !paredesGroup.visible;
    }

    function resetarCamera3D() {
      if (camera3D && controls3D) {
        camera3D.position.set(24, 25, 32);
        controls3D.target.set(5, 2, 5);
        controls3D.update();
      }
    }

    function animar3D() {
      requestAnimationFrame(animar3D);
      if (bladesMesh) bladesMesh.rotation.z += 0.04;
      if (turbinaPeltonMesh) turbinaPeltonMesh.rotation.y += 0.06;
      if (flareLight) flareLight.intensity = 1.2 + Math.sin(Date.now() * 0.01) * 0.4;
      if (controls3D) controls3D.update();
      if (renderer3D && scene3D && camera3D) renderer3D.render(scene3D, camera3D);
    }

    // ========================================================
    // COPILOT IA NORMATIVO & AUDITORIA DE ENGENHARIA ELÉTRICA
    // ========================================================
    let provedoresCopilot = [];
    let provedorCopilotAtivo = 'offline';
    let modeloCopilotAtivo = 'expert-analytical-eletrica-v1';

    const PROVEDORES_COPILOT_PADRAO = [
      {
        id: "offline",
        nome: "Motor Offline Antigravity",
        icone: "⚡",
        chave_configurada: true,
        modelos: [
          { id: "expert-analytical-eletrica-v1", nome: "Motor Analítico NBR 5410/5419/16690" }
        ]
      },
      {
        id: "gemini",
        nome: "Google Gemini",
        icone: "✨",
        chave_configurada: false,
        modelos: [
          { id: "gemini-3.8-flash", nome: "Gemini 3.8 Flash (Recomendado - Mais Novo)" },
          { id: "gemini-3.5-flash", nome: "Gemini 3.5 Flash" },
          { id: "gemini-2.0-flash", nome: "Gemini 2.0 Flash" },
          { id: "gemini-1.5-flash", nome: "Gemini 1.5 Flash" }
        ]
      },
      {
        id: "openai",
        nome: "OpenAI ChatGPT",
        icone: "🟢",
        chave_configurada: false,
        modelos: [
          { id: "gpt-4o", nome: "GPT-4o (Omni)" },
          { id: "gpt-4o-mini", nome: "GPT-4o Mini" }
        ]
      },
      {
        id: "claude",
        nome: "Anthropic Claude",
        icone: "🟣",
        chave_configurada: false,
        modelos: [
          { id: "claude-3-5-sonnet-20241022", nome: "Claude 3.5 Sonnet" }
        ]
      },
      {
        id: "deepseek",
        nome: "DeepSeek AI",
        icone: "🐋",
        chave_configurada: false,
        modelos: [
          { id: "deepseek-chat", nome: "DeepSeek V3" },
          { id: "deepseek-reasoner", nome: "DeepSeek R1" }
        ]
      },
      {
        id: "ollama",
        nome: "Ollama Local",
        icone: "🦙",
        chave_configurada: true,
        modelos: [
          { id: "llama3.2", nome: "Meta LLaMA 3.2 (Local)" }
        ]
      }
    ];

    async function carregarProvedoresCopilot() {
      try {
        const resp = await fetch('/api/v1/ai/provedores');
        const data = await resp.json();
        provedoresCopilot = data.provedores || PROVEDORES_COPILOT_PADRAO;
      } catch (e) {
        provedoresCopilot = PROVEDORES_COPILOT_PADRAO;
      }
      renderizarSelectProvedorCopilot();
      trocarProvedorCopilot();
    }

    function renderizarSelectProvedorCopilot() {
      const sel = document.getElementById('copilot-sel-provedor');
      if (!sel) return;
      sel.innerHTML = '';
      provedoresCopilot.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = `${p.icone} ${p.nome}`;
        if (p.id === provedorCopilotAtivo) opt.selected = true;
        sel.appendChild(opt);
      });
    }

    function trocarProvedorCopilot() {
      const selProv = document.getElementById('copilot-sel-provedor');
      if (!selProv) return;
      provedorCopilotAtivo = selProv.value;

      const prov = provedoresCopilot.find(p => p.id === provedorCopilotAtivo) || PROVEDORES_COPILOT_PADRAO[0];
      const selMod = document.getElementById('copilot-sel-modelo');
      if (selMod) {
        selMod.innerHTML = '';
        (prov.modelos || []).forEach(m => {
          const opt = document.createElement('option');
          opt.value = m.id;
          opt.textContent = m.nome;
          selMod.appendChild(opt);
        });
        modeloCopilotAtivo = prov.modelos?.[0]?.id || '';
      }

      const inpKey = document.getElementById('copilot-inp-key');
      const badge = document.getElementById('copilot-status-badge');
      const chaveSalva = localStorage.getItem(`antigravity_key_${prov.id}`) || '';
      if (inpKey) {
        inpKey.value = chaveSalva;
        inpKey.placeholder = (prov.chave_configurada || chaveSalva) ? `Chave ativa para ${prov.nome}` : `Cole sua chave para ${prov.nome}...`;
      }
      if (badge) {
        if (prov.id === 'offline') {
          badge.style.background = '#065f46';
          badge.style.color = '#34d399';
          badge.innerText = '● Modo Offline Local';
        } else if (prov.chave_configurada || chaveSalva) {
          badge.style.background = '#1e3a8a';
          badge.style.color = '#93c5fd';
          badge.innerText = '● Chave Configurada';
        } else {
          badge.style.background = '#374151';
          badge.style.color = '#9ca3af';
          badge.innerText = '○ Sem Chave (Fallback Ativo)';
        }
      }
    }

    async function salvarChaveCopilot() {
      const inpKey = document.getElementById('copilot-inp-key');
      if (!inpKey) return;
      const chave = inpKey.value.trim();
      if (!chave) {
        alert("Cole uma chave válida antes de salvar.");
        return;
      }
      localStorage.setItem(`antigravity_key_${provedorCopilotAtivo}`, chave);
      try {
        const resp = await fetch('/api/v1/ai/config/chave', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ provedor: provedorCopilotAtivo, chave: chave })
        });
        const data = await resp.json();
        alert(data.mensagem || "Chave salva com sucesso!");
        await carregarProvedoresCopilot();
      } catch (e) {
        alert("Chave salva com segurança na sessão do navegador!");
        trocarProvedorCopilot();
      }
    }

    function aplicarCenarioCopilot(tipo) {
      const inp = document.getElementById('copilot-inp-prompt');
      if (!inp) return;
      if (tipo === 'queda') {
        inp.value = "Para um circuito terminal monofásico de 127 V com 4.400 W e comprimento de 28 metros em condutores de cobre e eletroduto embutido em alvenaria (Método B1), qual a bitola mínima que atende à ampacidade e ao limite de 4% de queda de tensão da NBR 5410?";
      } else if (tipo === 'seletividade') {
        inp.value = "Como coordenar disjuntores DIN Curva B de 32 A nos circuitos de chuveiro contra o Disjuntor Geral Curva C de 63 A no QDC para garantir seletividade total sem desarmes intempestivos do IDR de 30 mA?";
      } else if (tipo === 'stringbox') {
        inp.value = "Conforme a NBR 16690:2019, quais são os critérios obrigatórios para dimensionamento de fusíveis gPV, chaves seccionadoras sob carga e DPS Classe II CC em arranjos fotovoltaicos com 2 e 3 strings em paralelo?";
      } else if (tipo === 'eolica') {
        inp.value = "Para um pequeno aerogerador de 5 kW segundo a IEC 61400-2, como estimar a potência gerada com vento de 11 m/s aplicando o limite de Betz e quais sistemas de frenagem (cut-out) são mandatórios?";
      } else if (tipo === 'biogas') {
        inp.value = "Em uma fazenda com 1.000 suínos em terminação, qual é o volume diário esperado de biogás em lagoa coberta de PEAD e qual a potência elétrica contínua entregue por um motogerador Ciclo Otto CHP?";
      } else if (tipo === 'pch') {
        inp.value = "Qual a potência elétrica de uma micro-hidrelétrica PCH rural com vazão de 40 L/s e desnível bruto de 25 m? Como calcular a sobrepressão do golpe de aríete no conduto forçado de PEAD PN10?";
      } else if (tipo === 'lei14300') {
        inp.value = "Quais as regras tarifárias de transição da Lei 14.300/2022 para a cobrança da componente TUSD Fio B na microgeração distribuída solar e como maximizar o autoconsumo instantâneo na propriedade?";
      }
      inp.focus();
    }

    function limparChatCopilot() {
      const stream = document.getElementById('copilot-chat-stream');
      if (stream) stream.innerHTML = '';
      const hero = document.getElementById('copilot-welcome-hero');
      if (hero) hero.style.display = 'block';
      const topBar = document.getElementById('copilot-top-bar');
      if (topBar) topBar.style.display = 'none';
    }

    async function auditarProjetoComCopilot() {
      navegarParaAba('aba-ia-copilot');
      const inp = document.getElementById('copilot-inp-prompt');
      if (inp) {
        inp.value = "Auditar conformidade normativa da instalação elétrica e microrrede calculada.";
      }
      await enviarMensagemCopilot();
    }

    async function enviarMensagemCopilot(e) {
      if (e) e.preventDefault();
      const inp = document.getElementById('copilot-inp-prompt');
      if (!inp) return;
      const pergunta = inp.value.trim();
      if (!pergunta) return;

      inp.value = '';
      inp.style.height = 'auto';

      const hero = document.getElementById('copilot-welcome-hero');
      if (hero) hero.style.display = 'none';
      const topBar = document.getElementById('copilot-top-bar');
      if (topBar) topBar.style.display = 'flex';

      const stream = document.getElementById('copilot-chat-stream');
      const btnSend = document.getElementById('copilot-btn-send');
      const msgId = Date.now();

      // Bolha do Usuário
      const userBubble = document.createElement('div');
      userBubble.style.cssText = 'align-self: flex-end; background: linear-gradient(135deg, #1e40af, #2563eb); color: #fff; padding: 12px 16px; border-radius: 14px 14px 4px 14px; max-width: 82%; font-size: 13.5px; border: 1px solid #3b82f6;';
      userBubble.innerHTML = `<div style="font-size: 10px; font-weight: 700; color: #bfdbfe; margin-bottom: 4px;">👤 ENGENHEIRO / USUÁRIO:</div><div>${escaparHTML(pergunta)}</div>`;
      stream.appendChild(userBubble);

      // Card de Carregamento da IA
      const aiCard = document.createElement('div');
      aiCard.style.cssText = 'align-self: flex-start; background: #0f172a; border: 1px solid #1e293b; border-radius: 14px 14px 14px 4px; padding: 18px; max-width: 96%; width: 100%;';
      aiCard.id = `copilot-card-${msgId}`;
      aiCard.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px; color: #fde047; font-size: 13px;">
          <span>⏳</span>
          <span>Consultando <strong>${(provedorCopilotAtivo).toUpperCase()}</strong> (${modeloCopilotAtivo || 'modelo padrão'})...</span>
        </div>
      `;
      stream.appendChild(aiCard);
      stream.scrollTop = stream.scrollHeight;

      if (btnSend) {
        btnSend.disabled = true;
        btnSend.innerText = 'Processando...';
      }

      const apiKey = localStorage.getItem(`antigravity_key_${provedorCopilotAtivo}`) || undefined;

      try {
        const resp = await fetch('/api/v1/ai/consultar', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            pergunta: pergunta,
            provedor: provedorCopilotAtivo,
            modelo: modeloCopilotAtivo,
            api_key: apiKey
          })
        });
        const data = await resp.json();
        renderizarCardMensagemCopilot(aiCard, data, msgId);
      } catch (err) {
        const fallback = fallbackCopilotLocal(pergunta);
        renderizarCardMensagemCopilot(aiCard, fallback, msgId);
      } finally {
        if (btnSend) {
          btnSend.disabled = false;
          btnSend.innerText = '⚡ Consultar';
        }
        stream.scrollTop = stream.scrollHeight;
      }
    }

    function fallbackCopilotLocal(pergunta) {
      const p = pergunta.toLowerCase();
      let texto = "";
      let normas = ["ABNT NBR 5410:2004", "NR-10", "Lei 14.300/2022"];
      let formulas = ["Delta_V <= 4,00%", "Iz = Iz_tab * Fca * Fct >= In >= Ib"];

      if (p.includes("queda") || p.includes("condutor") || p.includes("bitola") || p.includes("fio")) {
        texto = "### Parecer Técnico de Condutores e Queda de Tensão (NBR 5410)\n\n" +
          "Conforme a **ABNT NBR 5410:2004** (Tabela 47 e Seção 6.2.7):\n" +
          "• A seção mínima é de 1,5 mm² para iluminação e 2,5 mm² para tomadas (TUG/TUE);\n" +
          "• A queda de tensão máxima acumulada nos circuitos terminais não deve exceder **4,00%**;\n" +
          "• A ampacidade corrigida do condutor deve satisfazer `Ib <= In <= Iz`, aplicando fatores de agrupamento (Fca) e temperatura (Fct).";
      } else if (p.includes("seletividade") || p.includes("disjuntor")) {
        texto = "### Coordenação e Seletividade de Proteções (NBR 5410 & NM 60898)\n\n" +
          "• Disjuntores Curva B disparam entre 3 e 5x In (ideais para chuveiros resistivos);\n" +
          "• Disjuntores Curva C disparam entre 5 e 10x In (recomendados para circuitos de tomadas e cargas indutivas gerais);\n" +
          "• A seletividade amperimétrica exige relação mínima de 1,6x entre o disjuntor à montante (Geral) e jusante.";
      } else {
        texto = "### Motor Analítico Antigravity Elétrica (Modo Offline Local)\n\n" +
          "Sua consulta foi processada com base nas normas ABNT NBR 5410, NBR 16690 e NBR 5419.\n" +
          "No ecossistema Antigravity Elétrica, todos os dimensionamentos obedecem a critérios estritos de segurança contra choques, sobrecorrentes e arcos elétricos.";
      }

      return {
        texto: texto,
        provedor_usado: "offline-browser",
        modelo_usado: "expert-client-engine",
        latencia_ms: 30,
        tokens_estimados: 310,
        normas_referenciadas: normas,
        formulas_aplicadas: formulas,
        aviso: "Resposta gerada pelo motor analítico offline embutido."
      };
    }

    function renderizarCardMensagemCopilot(card, data, msgId) {
      const prov = (data.provedor_usado || provedorCopilotAtivo).toUpperCase();
      const mod = data.modelo_usado || modeloCopilotAtivo;
      const latencia = data.latencia_ms || 0;
      const tokens = data.tokens_estimados || 0;
      const cot = data.raciocinio_cot;
      const texto = data.texto || data.resposta_tecnica || "Sem resposta.";
      const normas = data.normas_referenciadas || [];

      let avisoHtml = '';
      if (data.aviso) {
        avisoHtml = `<div style="background: rgba(234, 179, 8, 0.15); border: 1px solid #eab308; color: #fde047; padding: 8px 12px; border-radius: 6px; font-size: 11.5px; margin-bottom: 10px;">⚠️ ${escaparHTML(data.aviso)}</div>`;
      }

      let normasHtml = '';
      if (normas && normas.length > 0) {
        normasHtml = `<div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #1f2937; display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">
          <span style="font-size: 11px; color: #9ca3af; font-weight: 600;">Normas:</span>
          ${normas.map(n => `<span style="font-size: 10.5px; background: #1e293b; color: #fde047; padding: 2px 7px; border-radius: 4px; border: 1px solid #334155;">${escaparHTML(n)}</span>`).join('')}
        </div>`;
      }

      let cotHtml = '';
      if (cot) {
        cotHtml = `<div style="background: #090d16; border: 1px solid #374151; border-radius: 6px; margin-bottom: 12px;">
          <div onclick="toggleCotCopilot('${msgId}')" style="padding: 8px 12px; font-size: 11.5px; font-weight: 700; color: #a78bfa; cursor: pointer; display: flex; justify-content: space-between;">
            <span>🧠 Raciocínio Passo a Passo (Chain-of-Thought)</span>
            <span id="copilot-cot-chev-${msgId}">▸</span>
          </div>
          <div id="copilot-cot-content-${msgId}" style="display: none; padding: 10px; font-size: 11.5px; color: #c4b5fd; line-height: 1.5; font-family: monospace; max-height: 200px; overflow-y: auto;">
            ${escaparHTML(cot)}
          </div>
        </div>`;
      }

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f2937; padding-bottom: 10px; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
            <span style="font-size: 11px; background: #1e3a8a; color: #fde047; font-weight: 700; padding: 2px 7px; border-radius: 4px;">${escaparHTML(prov)}</span>
            <span style="font-size: 11px; background: #1e293b; color: #93c5fd; padding: 2px 7px; border-radius: 4px; border: 1px solid #334155;">${escaparHTML(mod)}</span>
            <span style="font-size: 11px; color: #6ee7b7;">⏱️ ${latencia} ms</span>
            ${tokens ? `<span style="font-size: 11px; color: #9ca3af;">📊 ${tokens} tokens</span>` : ''}
          </div>
          <div>
            <button type="button" onclick="copiarTextoCopilot('${msgId}')" style="background: #1e293b; border: 1px solid #374151; color: #cbd5e1; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer;">📋 Copiar</button>
          </div>
        </div>
        ${avisoHtml}
        ${cotHtml}
        <div id="copilot-text-${msgId}" style="font-size: 13.5px; line-height: 1.6; color: #e2e8f0; white-space: pre-wrap;">
          ${formatarMarkdownBasico(texto)}
        </div>
        ${normasHtml}
      `;
    }

    function toggleCotCopilot(msgId) {
      const c = document.getElementById(`copilot-cot-content-${msgId}`);
      const chev = document.getElementById(`copilot-cot-chev-${msgId}`);
      if (!c || !chev) return;
      if (c.style.display === 'none') {
        c.style.display = 'block';
        chev.innerText = '▾';
      } else {
        c.style.display = 'none';
        chev.innerText = '▸';
      }
    }

    function copiarTextoCopilot(msgId) {
      const el = document.getElementById(`copilot-text-${msgId}`);
      if (el) {
        navigator.clipboard.writeText(el.innerText);
        alert("Parecer do Copilot copiado!");
      }
    }

    function formatarMarkdownBasico(txt) {
      return txt
        .replace(/^### (.*$)/gim, '<h3 style="color:#facc15; font-size:15px; margin:10px 0 4px 0;">$1</h3>')
        .replace(/^#### (.*$)/gim, '<h4 style="color:#38bdf8; font-size:13.5px; margin:8px 0 4px 0;">$1</h4>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong style="color:#fff;">$1</strong>')
        .replace(/`(.*?)`/gim, '<code style="background:#1e293b; color:#67e8f9; padding:2px 5px; border-radius:4px; font-size:12px; font-family:Consolas,monospace;">$1</code>');
    }

    // Heartbeat regular a cada 5 segundos
    setInterval(async () => {
      try {
        const r = await fetch('/api/v1/desktop/heartbeat');
        if (r.ok) {
          const el = document.getElementById('heartbeatStatus');
          if (el) el.innerText = 'Servidor Conectado (Porta Ativa)';
        }
      } catch (e) {
        const el = document.getElementById('heartbeatStatus');
        if (el) el.innerText = 'Servidor Offline / Modo Standalone Local';
      }
    }, 5000);

    // Inicialização ao carregar
    window.addEventListener('load', () => {
      carregarTodosDados();
      setTimeout(desenharPlantaBaixa2D, 200);
    });
  </script>

  <!-- Widget de Janela Flutuante do Copilot IA (Engenharia Elétrica & Renováveis) -->
  <script src="static/js/antigravity_copilot.js"></script>
</body>
</html>
