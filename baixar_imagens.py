import os
import re
import time
import requests

from urllib.parse import urlparse
from unidecode import unidecode
from playwright.sync_api import sync_playwright


PASTA_DOWNLOAD = "downloads"
os.makedirs(PASTA_DOWNLOAD, exist_ok=True)

capturados = set()


def limpar_nome(nome):
    nome = unidecode(nome or "item")
    nome = nome.lower()
    nome = re.sub(r"[^a-z0-9\s-]", "", nome)
    nome = re.sub(r"\s+", "-", nome)
    nome = re.sub(r"-+", "-", nome)
    return nome.strip("-") or "item"


def baixar(url, nome):

    try:
        r = requests.get(
            url,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if r.status_code != 200:
            return

        ext = os.path.splitext(urlparse(url).path)[1].lower()

        if ext not in [".gif", ".png", ".jpg", ".jpeg", ".webp"]:
            ct = r.headers.get("Content-Type", "")

            if "gif" in ct:
                ext = ".gif"
            elif "png" in ct:
                ext = ".png"
            elif "jpeg" in ct or "jpg" in ct:
                ext = ".jpg"
            else:
                ext = ".gif"

        caminho = os.path.join(PASTA_DOWNLOAD, nome + ext)

        if os.path.exists(caminho):
            return

        with open(caminho, "wb") as f:
            f.write(r.content)

        print(f"✔ {nome}{ext}")

    except:
        pass


def scroll(page):

    last = 0

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        h = page.evaluate("document.body.scrollHeight")

        if h == last:
            break

        last = h


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context()

    page = context.new_page()

    url = input("URL: ")
    page.goto(url, wait_until="networkidle")

    print("\nScroll inicial...\n")
    scroll(page)

    print("\nCapturando tráfego de rede...\n")

    def interceptar(route, request):

        url_req = request.url.lower()

        if any(ext in url_req for ext in [".gif", ".png", ".jpg", ".jpeg", ".webp"]):

            if url_req not in capturados:

                capturados.add(url_req)

                nome = limpar_nome(urlparse(request.url).path.split("/")[-1])

                print("capturado:", request.url)

                baixar(request.url, nome)

        route.continue_()

    page.route("**/*", interceptar)

    # força interação leve pra disparar requests
    page.mouse.wheel(0, 3000)
    time.sleep(3)
    page.mouse.wheel(0, 3000)
    time.sleep(3)

    print("\nFinalizando captura...\n")

    time.sleep(5)

    browser.close()

print("\nConcluído")