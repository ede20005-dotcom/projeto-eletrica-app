"""
Script Orquestrador e Gerador da Plataforma Completa Antigravity de Engenharia Elétrica & Renováveis
Concatena os módulos de template, gera o dossiê consolidado e sincroniza as páginas da aplicação.
"""

import os
import shutil
import subprocess

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES_DIR = os.path.join(BASE_DIR, "tools", "templates")

PARTES_TEMPLATE = [
    "01_head_css.html",
    "02_sidebar.html",
    "03_header_tabs.html",
    "04_panes_eletrica.html",
    "05_panes_seletividade.html",
    "06_panes_cad2d.html",
    "07_panes_stringbox.html",
    "08_panes_3d.html",
    "09_panes_renovaveis.html",
    "10_panes_hidreletrica.html",
    "11_panes_orcamento.html",
    "12_panes_materiais.html",
    "11b_pane_ia_copilot.html",
    "13_scripts.js"
]

def main():
    print("=== GERANDO PLATAFORMA INTEGRADA DE ENGENHARIA ELÉTRICA & RENOVÁVEIS ===")
    
    conteudo_completo = []
    for arq in PARTES_TEMPLATE:
        caminho_parte = os.path.join(TEMPLATES_DIR, arq)
        if not os.path.exists(caminho_parte):
            raise FileNotFoundError(f"Arquivo de template não encontrado: {caminho_parte}")
        with open(caminho_parte, "r", encoding="utf-8") as f:
            conteudo_completo.append(f.read())
            
    html_final = "\n".join(conteudo_completo)

    # 1. Salvar Dossiê Consolidado
    target_dossie = os.path.join(BASE_DIR, "dossie_engenharia_eletrica_consolidado.html")
    with open(target_dossie, "w", encoding="utf-8") as f:
        f.write(html_final)
    print(f"Salvo: {target_dossie} ({os.path.getsize(target_dossie)} bytes)")

    # 2. Sincronizar com index.html raiz
    target_index = os.path.join(BASE_DIR, "index.html")
    shutil.copy2(target_dossie, target_index)
    print(f"Sincronizado: {target_index}")

    # 3. Sincronizar com apps/web/public/index.html
    target_web = os.path.join(BASE_DIR, "apps", "web", "public", "index.html")
    os.makedirs(os.path.dirname(target_web), exist_ok=True)
    shutil.copy2(target_dossie, target_web)
    print(f"Sincronizado: {target_web}")

    print("Verificando integridade e sintaxe JavaScript...")
    res = subprocess.run([
        sys.executable if "sys" in globals() else "python",
        "-c",
        """
import re, subprocess, tempfile
with open('dossie_engenharia_eletrica_consolidado.html', 'r', encoding='utf-8') as f:
    html = f.read()
scripts = re.findall(r'<script(?:\\s+[^>]*)?>(.*?)</script>', html, flags=re.DOTALL | re.IGNORECASE)
for i, s in enumerate(scripts):
    if not s.strip(): continue
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
        tf.write(s)
        temp_name = tf.name
    res = subprocess.run(['node', '--check', temp_name], capture_output=True, text=True)
    if res.returncode != 0:
        print(f'ERRO JS no script {i}:', res.stderr)
        exit(1)
print('Todos os scripts JavaScript validados com SUCESSO (node --check)!')
"""
    ], cwd=BASE_DIR, capture_output=True, text=True)

    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        raise RuntimeError("Falha na validação de sintaxe JS!")

    print("=== Dossiê Completo Gerado com Êxito! ===")

if __name__ == "__main__":
    main()
