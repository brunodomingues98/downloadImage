import os
import re
import requests

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from unidecode import unidecode
from playwright.sync_api import sync_playwright


PASTA_DOWNLOAD = "downloads"

os.makedirs(PASTA_DOWNLOAD, exist_ok=True)


def limpar_nome(nome):
    nome = unidecode(nome)
    nome = nome.lower()
    nome = nome.replace("/", "-")
    nome = re.sub(r"[^a-z0-9\s-]", "", nome)
    nome = re.sub(r"\s+", "-", nome)
    nome = re.sub(r"-+", "-", nome)
    return nome.strip("-")


def baixar_imagem(url, nome):

    try:

        resposta = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if resposta.status_code != 200:
            print(f"Erro {resposta.status_code}: {url}")
            return

        extensao = os.path.splitext(url.split("?")[0])[1].lower()

        if extensao not in [".gif", ".png", ".jpg", ".jpeg", ".webp"]:

            tipo = resposta.headers.get("Content-Type", "").lower()

            if "gif" in tipo:
                extensao = ".gif"

            elif "png" in tipo:
                extensao = ".png"

            elif "jpeg" in tipo or "jpg" in tipo:
                extensao = ".jpg"

            elif "webp" in tipo:
                extensao = ".webp"

            else:
                extensao = ".jpg"

        caminho = os.path.join(
            PASTA_DOWNLOAD,
            nome + extensao
        )

        if os.path.exists(caminho):
            print(f"Já existe -> {nome}")
            return

        with open(caminho, "wb") as f:
            f.write(resposta.content)

        print(f"Baixado -> {os.path.basename(caminho)}")

    except Exception as e:
        print(f"Erro ao baixar {url}")
        print(e)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    url = input("Digite a URL: ")

    page.goto(
        url,
        wait_until="networkidle"
    )

    print()
    print("=" * 60)
    print("Navegue normalmente pelo site.")
    print("Quando terminar pressione ENTER.")
    print("=" * 60)

    input()

    html = page.content()

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    imagens = soup.find_all("img")

    usados = {}

    contador = 1

    print(f"\nEncontradas {len(imagens)} imagens.\n")

    for img in imagens:

        src = img.get("src")

        if not src:
            continue

        src = urljoin(page.url, src)

        nome = (
            img.get("alt")
            or img.get("title")
            or f"imagem-{contador}"
        )

        nome = limpar_nome(nome)

        if nome in usados:
            usados[nome] += 1
            nome = f"{nome}-{usados[nome]}"
        else:
            usados[nome] = 1

        baixar_imagem(src, nome)

        contador += 1

    browser.close()

print("\nDownload concluído!")