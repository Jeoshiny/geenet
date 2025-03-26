import asyncio
import json
import os
from datetime import datetime
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright

# Caminhos e constantes
CAMINHO_JSON = r"C:\Users\335775\Desktop\Macros\GEENET\dados.json"
CAMINHO_HISTORICO = Path(r"C:\Users\335775\Desktop\Macros\GEENET\historico.csv")

async def coletar_valor():
    # Carregar login e senha
    with open(CAMINHO_JSON, 'r') as f:
        dados = json.load(f)
        login = dados['login']
        senha = dados['senha']

    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        pagina = await navegador.new_page()

        await pagina.goto("https://gee.aptuscloud.com.br/portal/Login/Index?ReturnUrl=%2Fportal")

        # Login
        await pagina.fill("#login", login)
        await pagina.fill("#senha", senha)
        await pagina.click("#wrapper > div > div > div > div > form > div.form-group.text-center > button")
        await pagina.wait_for_load_state("networkidle")

        # Espera condicional para o popup
        try:
            await pagina.wait_for_selector("#alerta-xml-modal > div > div > div > div.modal-footer > button", timeout=5000)
            await pagina.click("#alerta-xml-modal > div > div > div > div.modal-footer > button")
        except:
            pass  # Popup não apareceu

        # Acessar o menu
        await pagina.wait_for_selector("#main-menu > li:nth-child(5) > a", timeout=60000)
        await pagina.click("#main-menu > li:nth-child(5) > a")

        # Esperar e capturar o valor
        await pagina.wait_for_selector("#example > tbody > tr.treegrid-1 > td.text-success > b")
        valor = await pagina.inner_text("#example > tbody > tr.treegrid-1 > td.text-success > b")

        await navegador.close()
        return valor

def salvar_historico(valor):
    agora = datetime.now()
    data = agora.strftime("%Y-%m-%d")
    hora = agora.strftime("%H:%M")

    nova_linha = pd.DataFrame([[data, hora, valor]], columns=['Data', 'Hora', 'Valor'])

    if CAMINHO_HISTORICO.exists():
        historico = pd.read_csv(CAMINHO_HISTORICO)
        historico = pd.concat([historico, nova_linha], ignore_index=True)
    else:
        historico = nova_linha

    historico.to_csv(CAMINHO_HISTORICO, index=False)

async def main():
    valor = await coletar_valor()
    salvar_historico(valor)

if __name__ == "__main__":
    asyncio.run(main())