"""
Antigravity Desktop Launcher — Lançador Executável de Janela Nativa Windows
Plataforma Integrada de Engenharia Elétrica (NBR 5410 / NR-10 / NBR 5419)
"""

import os
import sys
import time
import socket
import threading
import subprocess
import urllib.request
import webbrowser

LOG_FILE = os.path.join(os.getenv("TEMP", "."), "antigravity_eletrica_launcher.log")

class SafeStream:
    """Stream seguro que substitui sys.stdout/sys.stderr em aplicações GUI Windows sem console."""
    def __init__(self, log_path):
        self.log_path = log_path
    def write(self, s):
        if not s: return
        try:
            with open(self.log_path, "a", encoding="utf-8", errors="replace") as f:
                f.write(s)
        except Exception:
            pass
    def flush(self):
        pass
    def reconfigure(self, **kwargs):
        pass

# 1. Configurar streams seguros (evita 'NoneType' object has no attribute 'reconfigure' ou charmap errors)
if sys.stdout is None or not hasattr(sys.stdout, 'write'):
    sys.stdout = SafeStream(LOG_FILE)
if sys.stderr is None or not hasattr(sys.stderr, 'write'):
    sys.stderr = SafeStream(LOG_FILE)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def log(msg: str):
    """Escreve mensagem de log de forma 100% segura sem falhas de codec charmap."""
    texto = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as f:
            f.write(texto + "\n")
    except Exception:
        pass
    try:
        if sys.stdout:
            sys.stdout.write(texto + "\n")
            sys.stdout.flush()
    except Exception:
        pass


# 2. Definir diretório raiz da aplicação
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    if hasattr(sys, '_MEIPASS'):
        BUNDLE_DIR = sys._MEIPASS
    elif os.path.isdir(os.path.join(BASE_DIR, "_internal")):
        BUNDLE_DIR = os.path.join(BASE_DIR, "_internal")
    else:
        BUNDLE_DIR = BASE_DIR
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_DIR

log(f"=== INICIANDO ANTIGRAVITY ENGENHARIA ELÉTRICA ===")
log(f"BASE_DIR: {BASE_DIR}")
log(f"BUNDLE_DIR: {BUNDLE_DIR}")

# Apontar ANTIGRAVITY_ROOT_DIR
if os.path.exists(os.path.join(BUNDLE_DIR, "dossie_engenharia_eletrica_consolidado.html")):
    os.environ["ANTIGRAVITY_ROOT_DIR"] = BUNDLE_DIR
elif os.path.exists(os.path.join(BASE_DIR, "_internal", "dossie_engenharia_eletrica_consolidado.html")):
    os.environ["ANTIGRAVITY_ROOT_DIR"] = os.path.join(BASE_DIR, "_internal")
else:
    os.environ["ANTIGRAVITY_ROOT_DIR"] = BASE_DIR

# Incluir caminhos de pacotes no sys.path
for base_root in set([BASE_DIR, BUNDLE_DIR]):
    for sub in [
        "",
        os.path.join("apps", "api", "app"),
        os.path.join("packages", "engineering-eletrica-core", "src"),
        os.path.join("packages", "engineering-eletrica-core", "src", "engineering_eletrica_core"),
        os.path.join("packages", "engineering-eletrica-baixa-tensao"),
        os.path.join("packages", "engineering-eletrica-baixa-tensao", "engineering_eletrica_baixa_tensao"),
        os.path.join("packages", "drawing-engine-eletrica", "src"),
        os.path.join("packages", "drawing-engine-eletrica", "src", "drawing_engine_eletrica"),
        os.path.join("packages", "report-generator-eletrica", "src"),
        os.path.join("packages", "report-generator-eletrica", "src", "report_generator_eletrica"),
    ]:
        p = os.path.join(base_root, sub)
        if p not in sys.path:
            sys.path.insert(0, p)


def encontrar_porta_livre(porta_inicial: int = 8000) -> int:
    for porta in range(porta_inicial, porta_inicial + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(('127.0.0.1', porta))
                return porta
            except OSError:
                continue
    return porta_inicial


def rodar_servidor(porta: int):
    """Inicializa o servidor HTTP multi-thread da engenharia elétrica."""
    try:
        try:
            from apps.api.app.server_standalone import iniciar_servidor_http
        except ImportError:
            from server_standalone import iniciar_servidor_http
        iniciar_servidor_http(porta=porta, host="127.0.0.1")
    except Exception as e:
        import traceback
        log(f"[ERRO CRÍTICO] Falha ao iniciar servidor HTTP: {e}\n{traceback.format_exc()}")


def aguardar_servidor(porta: int, timeout: float = 15.0) -> bool:
    """Aguarda até que o endpoint /healthz responda 200 OK."""
    url = f"http://127.0.0.1:{porta}/healthz"
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def abrir_janela_nativa(url: str, titulo: str):
    """Abre a interface em janela nativa dedicada do Microsoft Edge em modo aplicativo."""
    caminhos_edge = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
    ]
    edge_bin = None
    for c in caminhos_edge:
        if os.path.exists(c):
            edge_bin = c
            break

    proc = None
    if edge_bin:
        profile_dir = os.path.join(
            os.getenv("LOCALAPPDATA", os.getenv("TEMP", ".")),
            "AntigravityEletrica",
            "Profile"
        )
        os.makedirs(profile_dir, exist_ok=True)
        cmd = [
            edge_bin,
            f"--app={url}",
            "--window-size=1420,920",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        log(f"Abrindo Microsoft Edge App Mode: {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(cmd)
            return proc
        except Exception as e:
            log(f"Falha ao executar Edge: {e}. Abrindo navegador padrão.")

    log("Abrindo navegador padrao do sistema...")
    webbrowser.open(url)
    return proc


def monitor_vida_util(proc, porta: int):
    """Monitora o ciclo de vida da janela nativa e heartbeat."""
    url_hb = f"http://127.0.0.1:{porta}/api/v1/desktop/heartbeat"
    inicio = time.time()
    ultimo_sinal = time.time()
    time.sleep(5)

    while True:
        time.sleep(2)

        # 1. Se o processo Edge direto está ativo, mantém o servidor ativo
        if proc and proc.poll() is None:
            continue

        # 2. Testa o heartbeat
        try:
            with urllib.request.urlopen(url_hb, timeout=1.5) as r:
                if r.status == 200:
                    ultimo_sinal = time.time()
        except Exception:
            pass

        decorrido = time.time() - inicio
        sem_sinal = time.time() - ultimo_sinal

        # Tolerância inicial de 60 segundos
        if decorrido > 60 and sem_sinal > 30:
            log(f"[FINALIZAÇÃO] Janela fechada ({sem_sinal:.1f}s sem atividade). Encerrando.")
            break


def main():
    porta = encontrar_porta_livre(8080)
    log(f"Porta alocada: {porta}")

    # Subir o servidor em thread daemon
    th = threading.Thread(target=rodar_servidor, args=(porta,), daemon=True)
    th.start()

    log(f"Aguardando prontidão do servidor na porta {porta}...")
    if not aguardar_servidor(porta, timeout=15.0):
        log("[ERRO CRÍTICO] Servidor não respondeu ao healthcheck dentro do tempo limite.")
        sys.exit(1)

    log("Servidor pronto e respondendo 200 OK.")
    url = f"http://127.0.0.1:{porta}/"

    proc = abrir_janela_nativa(url, "Antigravity — Engenharia Elétrica NBR 5410")
    monitor_vida_util(proc, porta)
    log("=== APLICAÇÃO FINALIZADA COM SUCESSO ===")


if __name__ == "__main__":
    main()
