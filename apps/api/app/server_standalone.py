"""
Servidor HTTP Standalone Zero-Dependência Externa para o Sistema Antigravity de Engenharia Elétrica
Baseado na biblioteca padrão do Python (http.server.ThreadingHTTPServer).
Totalmente compatível com empacotamento desktop (PyInstaller) e execução 100% offline.
"""

import os
import sys
import json
import time
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Optional

# Configurar caminhos dos pacotes locais
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if getattr(sys, 'frozen', False):
    # Executável PyInstaller (_MEIPASS ou diretório do executável)
    APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    APP_DIR = BASE_DIR

for p in [
    os.path.join(APP_DIR, "packages", "engineering-eletrica-core", "src"),
    os.path.join(APP_DIR, "packages", "engineering-eletrica-core", "src", "engineering_eletrica_core"),
    os.path.join(APP_DIR, "packages", "engineering-eletrica-baixa-tensao"),
    os.path.join(APP_DIR, "packages", "engineering-eletrica-baixa-tensao", "engineering_eletrica_baixa_tensao"),
    os.path.join(APP_DIR, "packages", "drawing-engine-eletrica", "src"),
    os.path.join(APP_DIR, "packages", "drawing-engine-eletrica", "src", "drawing_engine_eletrica"),
    os.path.join(APP_DIR, "packages", "report-generator-eletrica", "src"),
    os.path.join(APP_DIR, "packages", "report-generator-eletrica", "src", "report_generator_eletrica"),
    os.path.join(APP_DIR, "packages", "engineering-eletrica-renovaveis"),
    os.path.join(APP_DIR, "packages", "engineering-eletrica-renovaveis", "engineering_eletrica_renovaveis"),
]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# Importar motores do projeto
from engineering_eletrica_baixa_tensao import ProjetoEletricoResidencial
from drawing_engine_eletrica import (
    GeradorPlantaBaixaEletricaDXF,
    GeradorDiagramaUnifilarQDCDXF,
    GeradorEsquemasRenovaveisDXF,
    GeradorCurvasSeletividadeDXF,
    GeradorDiagramaStringboxDXF
)
from report_generator_eletrica import GeradorMemorialEletricoDOCX
from normas_referencia import NORMAS_ELETRICA_BRASIL
from engineering_eletrica_renovaveis import (
    MicrorredeHibridaIntegrada,
    DimensionadorStringboxCC,
    DimensionadorHidreletricoPCH
)
from seletividade_protecoes import AnalisadorSeletividadeProtecoes
from orcamento_bdi import CalculadoraOrcamentoEletrico
try:
    from engineering_eletrica_core.ai_gateway import (
        AIGatewayService,
        RequisicaoAI,
        MensagemChat,
        AIKeyManager
    )
except ImportError:
    from ai_gateway import (
        AIGatewayService,
        RequisicaoAI,
        MensagemChat,
        AIKeyManager
    )

AI_GATEWAY = AIGatewayService()

# Variável de heartbeat global
ULTIMO_HEARTBEAT = time.time()

# Cache do último projeto calculado
PROJETO_ATUAL = ProjetoEletricoResidencial()
PROJETO_ATUAL.carregar_residencia_padrao()
DADOS_CALCULADOS_ATUAIS = PROJETO_ATUAL.executar_calculos_completos()

# Cache do cenário de renováveis
DADOS_RENOVAVEIS_ATUAIS = MicrorredeHibridaIntegrada.simular_cenario(perfil="fazenda")

# Cache do estudo de seletividade e proteções
DADOS_SELETIVIDADE_ATUAIS = AnalisadorSeletividadeProtecoes.gerar_estudo_completo_instalacao(
    circuitos=DADOS_CALCULADOS_ATUAIS.get("circuitos", []),
    disjuntor_geral_a=125.0
)

# Cache de dimensionamento da Stringbox CC
DADOS_STRINGBOX_ATUAIS = DimensionadorStringboxCC.dimensionar_stringbox(
    modulos_por_string_serie=18,
    quantidade_strings_paralelo=2
)

# Cache do orçamento paramétrico e viabilidade com BDI
DADOS_ORCAMENTO_ATUAIS = CalculadoraOrcamentoEletrico.gerar_orcamento_completo(
    materiais_eletrica=DADOS_CALCULADOS_ATUAIS.get("lista_materiais", []),
    dados_renovaveis=DADOS_RENOVAVEIS_ATUAIS,
    bdi_pct=24.2
)


class RequisicaoEletricaHandler(BaseHTTPRequestHandler):
    """Manipulador de requisições HTTP para a plataforma de Engenharia Elétrica."""
    
    server_version = "AntigravityEletricaServer/1.0"
    
    def log_message(self, format, *args):
        # Silencia logs verbosos no console
        pass

    def _atualizar_heartbeat(self):
        global ULTIMO_HEARTBEAT
        ULTIMO_HEARTBEAT = time.time()
        if hasattr(self.server, 'ULTIMO_HEARTBEAT'):
            self.server.ULTIMO_HEARTBEAT = ULTIMO_HEARTBEAT

    def _enviar_json(self, dados: dict, status: int = 200):
        self._atualizar_heartbeat()
        payload = json.dumps(dados, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def _enviar_arquivo_binario(self, caminho: str, content_type: str, nome_download: Optional[str] = None):
        self._atualizar_heartbeat()
        if not os.path.exists(caminho):
            self.send_error(404, f"Arquivo não encontrado: {os.path.basename(caminho)}")
            return
            
        with open(caminho, "rb") as f:
            conteudo = f.read()
            
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(conteudo)))
        if nome_download:
            self.send_header("Content-Disposition", f'attachment; filename="{nome_download}"')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(conteudo)

    def do_OPTIONS(self):
        self._atualizar_heartbeat()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self._atualizar_heartbeat()
        parsed = urllib.parse.urlparse(self.path)
        rota = parsed.path
        
        # 1. Healthcheck e Heartbeat
        if rota == "/healthz" or rota == "/api/v1/desktop/heartbeat":
            self._enviar_json({"status": "ok", "servidor": "Antigravity Engenharia Elétrica", "timestamp": time.time()})
            return

        # 2. Obter Repositório de Normas Técnicas
        if rota == "/api/v1/eletrica/normas":
            self._enviar_json(NORMAS_ELETRICA_BRASIL)
            return

        # 3. Obter Dados do Projeto Atual Calculado
        if rota == "/api/v1/eletrica/dados-projeto":
            self._enviar_json(DADOS_CALCULADOS_ATUAIS)
            return

        # 4. Exportação do DXF da Planta Baixa
        if rota == "/api/v1/eletrica/export/dxf-planta":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "planta_baixa_residencial.dxf")
            gerador = GeradorPlantaBaixaEletricaDXF(DADOS_CALCULADOS_ATUAIS)
            gerador.gerar_dxf(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Planta_Baixa_Eletrica_NBR5410.dxf")
            return

        # 5. Exportação do DXF do Diagrama Unifilar QDC
        if rota == "/api/v1/eletrica/export/dxf-unifilar":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "diagrama_unifilar_qdc.dxf")
            gerador = GeradorDiagramaUnifilarQDCDXF(DADOS_CALCULADOS_ATUAIS)
            gerador.gerar_dxf(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Diagrama_Unifilar_QDC_NBR5410.dxf")
            return

        # 6. Exportação do Laudo / Memorial em DOCX
        if rota == "/api/v1/eletrica/export/docx-memorial":
            docx_dir = os.path.join(APP_DIR, "exports_docx")
            os.makedirs(docx_dir, exist_ok=True)
            caminho_docx = os.path.join(docx_dir, "memorial_descritivo_eletrico_nbr5410.docx")
            gerador = GeradorMemorialEletricoDOCX(DADOS_CALCULADOS_ATUAIS)
            gerador.gerar_memorial(caminho_docx)
            self._enviar_arquivo_binario(
                caminho_docx,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "Memorial_Descritivo_Eletrico_NBR5410.docx"
            )
            return

        # 7. Obter Dados de Renováveis, Eólica e Biogás
        if rota == "/api/v1/renovaveis/dados":
            self._enviar_json(DADOS_RENOVAVEIS_ATUAIS)
            return

        # 8. Exportação DXF Solar Fotovoltaico
        if rota == "/api/v1/renovaveis/export/dxf-solar":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "usina_solar_fotovoltaica.dxf")
            gerador = GeradorEsquemasRenovaveisDXF(DADOS_RENOVAVEIS_ATUAIS)
            gerador.gerar_dxf_solar(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Usina_Solar_Fotovoltaica_NBR16690.dxf")
            return

        # 9. Exportação DXF Aerogerador Eólico
        if rota == "/api/v1/renovaveis/export/dxf-eolica":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "aerogerador_eolica.dxf")
            gerador = GeradorEsquemasRenovaveisDXF(DADOS_RENOVAVEIS_ATUAIS)
            gerador.gerar_dxf_eolica(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Aerogerador_Eolico_IEC61400.dxf")
            return

        # 10. Exportação DXF Biodigestor e Usina a Biogás CHP
        if rota == "/api/v1/renovaveis/export/dxf-biodigestor":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "biodigestor_usina_biogas.dxf")
            gerador = GeradorEsquemasRenovaveisDXF(DADOS_RENOVAVEIS_ATUAIS)
            gerador.gerar_dxf_biodigestor(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Biodigestor_Usina_Biogas_CHP.dxf")
            return

        # 11. Estudo de Seletividade e Proteções (JSON)
        if rota == "/api/v1/eletrica/seletividade":
            self._enviar_json(DADOS_SELETIVIDADE_ATUAIS)
            return

        # 12. Exportação DXF Curvas de Seletividade e Proteções NBR 5410
        if rota == "/api/v1/eletrica/export/dxf-seletividade":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "curvas_seletividade_protecoes.dxf")
            gerador = GeradorCurvasSeletividadeDXF(DADOS_SELETIVIDADE_ATUAIS)
            gerador.gerar_dxf(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Curvas_Seletividade_NBR5410.dxf")
            return

        # 13. Dados da Stringbox Solar CC (JSON)
        if rota == "/api/v1/renovaveis/stringbox":
            self._enviar_json(DADOS_STRINGBOX_ATUAIS)
            return

        # 14. Exportação DXF Diagrama Multifilar Stringbox Solar CC
        if rota == "/api/v1/renovaveis/export/dxf-stringbox":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "diagrama_stringbox_solar_cc.dxf")
            gerador = GeradorDiagramaStringboxDXF(DADOS_STRINGBOX_ATUAIS)
            gerador.gerar_dxf(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Diagrama_Stringbox_Solar_NBR16690.dxf")
            return

        # 15. Exportação DXF Micro-Hidrelétrica PCH Rural
        if rota == "/api/v1/renovaveis/export/dxf-hidreletrica":
            cad_dir = os.path.join(APP_DIR, "cad_export")
            os.makedirs(cad_dir, exist_ok=True)
            caminho_dxf = os.path.join(cad_dir, "micro_hidreletrica_pch.dxf")
            gerador = GeradorEsquemasRenovaveisDXF(DADOS_RENOVAVEIS_ATUAIS)
            gerador.gerar_dxf_hidreletrica(caminho_dxf)
            self._enviar_arquivo_binario(caminho_dxf, "application/dxf", "Micro_Hidreletrica_PCH_Rural.dxf")
            return

        # 16. Orçamento Paramétrico, BDI e Viabilidade (JSON)
        if rota == "/api/v1/eletrica/orcamento":
            self._enviar_json(DADOS_ORCAMENTO_ATUAIS)
            return

        # 17. Listar Provedores de IA Suportados
        if rota == "/api/v1/ai/provedores":
            self._enviar_json({"status": "sucesso", "provedores": [p.to_dict() for p in AI_GATEWAY.listar_provedores()]})
            return

        # 18. Servir Central de Agentes de IA
        if rota in ["/ia", "/ia.html", "/ia_central_agentes_eletrica.html"]:
            caminho_ia = os.path.join(APP_DIR, "ia_central_agentes_eletrica.html")
            if not os.path.exists(caminho_ia):
                caminho_ia = os.path.join(BASE_DIR, "ia_central_agentes_eletrica.html")
            if os.path.exists(caminho_ia):
                self._enviar_arquivo_binario(caminho_ia, "text/html; charset=utf-8")
                return

        # 11. Servir Página Principal e Arquivos Estáticos
        # Se rota for / ou /dossie, busca dossie_engenharia_eletrica_consolidado.html
        if rota in ["/", "/index.html", "/dossie", "/dossie.html"]:
            caminho_html = os.path.join(APP_DIR, "dossie_engenharia_eletrica_consolidado.html")
            if not os.path.exists(caminho_html):
                caminho_html = os.path.join(BASE_DIR, "dossie_engenharia_eletrica_consolidado.html")
            if os.path.exists(caminho_html):
                self._enviar_arquivo_binario(caminho_html, "text/html; charset=utf-8")
                return

        # Servir outros arquivos locais (CSS, JS, imagens)
        caminho_solicitado = os.path.abspath(os.path.join(APP_DIR, rota.lstrip("/")))
        if not (os.path.exists(caminho_solicitado) and os.path.isfile(caminho_solicitado)):
            caminho_solicitado = os.path.abspath(os.path.join(APP_DIR, "apps", "web", "public", rota.lstrip("/")))
        if os.path.exists(caminho_solicitado) and os.path.isfile(caminho_solicitado):
            ext = os.path.splitext(caminho_solicitado)[1].lower()
            tipos = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".json": "application/json; charset=utf-8",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
                ".dxf": "application/dxf",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
            content_type = tipos.get(ext, "application/octet-stream")
            self._enviar_arquivo_binario(caminho_solicitado, content_type)
            return

        self.send_error(404, f"Rota não encontrada: {rota}")

    def do_POST(self):
        self._atualizar_heartbeat()
        parsed = urllib.parse.urlparse(self.path)
        rota = parsed.path
        
        # Recálculo com parâmetros personalizados
        if rota == "/api/v1/eletrica/calcular":
            global PROJETO_ATUAL, DADOS_CALCULADOS_ATUAIS
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len)
                params = json.loads(body.decode('utf-8')) if body else {}
                
                # Inicializar novo projeto com os parâmetros recebidos
                nome = params.get("nome_projeto", "Residência Unifamiliar NBR 5410")
                fornec = params.get("tipo_fornecimento", "trifasico")
                v_fn = int(params.get("tensao_fn", 127))
                v_ff = int(params.get("tensao_ff", 220))
                temp = int(params.get("temperatura_ambiente", 30))
                
                novo_proj = ProjetoEletricoResidencial(
                    nome_projeto=nome,
                    tipo_fornecimento=fornec,
                    tensao_fn=v_fn,
                    tensao_ff=v_ff,
                    temperatura_ambiente=temp
                )
                novo_proj.carregar_residencia_padrao()
                
                # Permite customizar ou adicionar cômodos extras enviados no payload
                comodos_custom = params.get("comodos_customizados")
                if comodos_custom and isinstance(comodos_custom, list):
                    # Se foram enviados cômodos específicos, substitui
                    from engineering_eletrica_baixa_tensao import ComodoResidencial
                    novo_proj.comodos = []
                    for c_data in comodos_custom:
                        com = ComodoResidencial(
                            id_comodo=c_data["id"],
                            nome=c_data["nome"],
                            tipo=c_data["tipo"],
                            largura=float(c_data["largura"]),
                            comprimento=float(c_data["comprimento"])
                        )
                        for tue in c_data.get("tues", []):
                            com.adicionar_tue(tue.get("chave", "chuveiro_eletrico_7500"), tensao_v=tue.get("tensao_v"))
                        novo_proj.comodos.append(com)
                
                PROJETO_ATUAL = novo_proj
                DADOS_CALCULADOS_ATUAIS = novo_proj.executar_calculos_completos()
                self._enviar_json(DADOS_CALCULADOS_ATUAIS)
            except Exception as e:
                self._enviar_json({"erro": str(e), "status": "falha"}, status=400)
            return

        # Recálculo de Microrrede Renovável e Biogás
        if rota == "/api/v1/renovaveis/calcular":
            global DADOS_RENOVAVEIS_ATUAIS
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len)
                params = json.loads(body.decode('utf-8')) if body else {}

                perfil = params.get("perfil", "fazenda")
                consumo = float(params.get("consumo_mensal_kwh", 8500.0))
                solar = bool(params.get("incluir_solar", True))
                eolica = bool(params.get("incluir_eolica", True))
                biogas = bool(params.get("incluir_biogas", True))
                plantel = int(params.get("plantel_animais", 1000))
                tipo_criacao = params.get("tipo_criacao", "suinos_terminacao")

                DADOS_RENOVAVEIS_ATUAIS = MicrorredeHibridaIntegrada.simular_cenario(
                    perfil=perfil,
                    consumo_mensal_kwh=consumo,
                    incluir_solar=solar,
                    incluir_eolica=eolica,
                    incluir_biogas=biogas,
                    plantel_animais=plantel,
                    tipo_criacao=tipo_criacao
                )
                self._enviar_json(DADOS_RENOVAVEIS_ATUAIS)
            except Exception as e:
                self._enviar_json({"erro": str(e), "status": "falha"}, status=400)
            return

        # Consultar Copilot / Agente de IA
        if rota == "/api/v1/ai/consultar":
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len)
                data = json.loads(body.decode('utf-8')) if body else {}

                historico = []
                for h in data.get("historico", []):
                    historico.append(MensagemChat(role=h.get("role", "user"), content=h.get("content", "")))

                ctx = dict(DADOS_CALCULADOS_ATUAIS)
                ctx["renovaveis"] = DADOS_RENOVAVEIS_ATUAIS
                ctx.update(data.get("contexto_engenharia", {}))

                req = RequisicaoAI(
                    pergunta=str(data.get("pergunta", "Qual a seção mínima de condutor pela NBR 5410?")),
                    provedor=str(data.get("provedor", "offline")),
                    modelo=data.get("modelo"),
                    contexto_engenharia=ctx,
                    historico=historico,
                    temperatura=float(data.get("temperatura", 0.2)),
                    max_tokens=int(data.get("max_tokens", 2048)),
                    api_key_override=data.get("api_key")
                )

                resp = AI_GATEWAY.consultar(req)
                self._enviar_json(resp.to_dict())
            except Exception as e:
                self._enviar_json({"status": "erro", "mensagem": str(e)}, 400)
            return

        # Salvar Chave de API Localmente
        elif rota == "/api/v1/ai/config/chave":
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len)
                data = json.loads(body.decode('utf-8')) if body else {}
                prov = data.get("provedor", "").lower()
                chave = data.get("chave", "")
                if not prov or not chave:
                    self._enviar_json({"status": "erro", "mensagem": "Provedor e chave são obrigatórios."}, 400)
                    return
                sucesso = AIKeyManager.salvar_chave(prov, chave)
                if sucesso:
                    self._enviar_json({"status": "sucesso", "mensagem": f"Chave para {prov.upper()} configurada com sucesso!"})
                else:
                    self._enviar_json({"status": "erro", "mensagem": "Falha ao persistir chave localmente."}, 500)
            except Exception as e:
                self._enviar_json({"status": "erro", "mensagem": str(e)}, 400)
            return

        # Auditoria Automática de Conformidade do Projeto Atual
        elif rota == "/api/v1/ai/auditar_projeto":
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len)
                data = json.loads(body.decode('utf-8')) if body else {}
                dados_proj = data.get("dados_projeto") or DADOS_CALCULADOS_ATUAIS
                prov = data.get("provedor", "offline")
                mod = data.get("modelo")
                res = AI_GATEWAY.auditar_projeto(dados_proj, provedor=prov, modelo=mod)
                resp_dict = res.to_dict()
                resp_dict["parecer_auditoria"] = resp_dict.get("texto", "")
                resp_dict["aprovado"] = ("não conforme" not in resp_dict.get("texto", "").lower() and "reprovado" not in resp_dict.get("texto", "").lower())
                self._enviar_json(resp_dict)
            except Exception as e:
                self._enviar_json({"status": "erro", "mensagem": str(e)}, 400)
            return

        self.send_error(404, f"Rota POST não encontrada: {rota}")


def criar_servidor(porta: int = 8080, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    """Instancia o servidor HTTP multithread."""
    server_address = (host, porta)
    httpd = ThreadingHTTPServer(server_address, RequisicaoEletricaHandler)
    httpd.ULTIMO_HEARTBEAT = time.time()
    return httpd

def iniciar_servidor_http(porta: int = 8080, host: str = "127.0.0.1"):
    """Inicia o servidor e entra no loop serve_forever."""
    srv = criar_servidor(porta, host)
    srv.serve_forever()

if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Iniciando Servidor Antigravity Engenharia Elétrica na porta {porta}...")
    iniciar_servidor_http(porta)
