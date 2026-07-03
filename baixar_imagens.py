import os
import re
import time
import requests

from urllib.parse import urljoin
from unidecode import unidecode
from playwright.sync_api import sync_playwright


PASTA_DOWNLOAD = "downloads"
os.makedirs(PASTA_DOWNLOAD, exist_ok=True)


def limpar_nome(nome):
    nome = unidecode(nome or "item")
    nome = nome.lower()
    nome = nome.replace("/", "-")
    nome = re.sub(r"[^a-z0-9\s-]", "", nome)
    nome = re.sub(r"\s+", "-", nome)
    nome = re.sub(r"-+", "-", nome)
    return nome.strip("-") or "item"


def baixar_arquivo(url, nome):

    try:
        r = requests.get(
            url,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if r.status_code != 200:
            print(f"Erro {r.status_code}: {url}")
            return

        ext = os.path.splitext(url.split("?")[0])[1].lower()

        if ext not in [".gif", ".png", ".jpg", ".jpeg", ".webp"]:
            ct = r.headers.get("Content-Type", "").lower()

            if "gif" in ct:
                ext = ".gif"
            elif "png" in ct:
                ext = ".png"
            elif "jpeg" in ct or "jpg" in ct:
                ext = ".jpg"
            elif "webp" in ct:
                ext = ".webp"
            else:
                ext = ".gif"

        caminho = os.path.join(PASTA_DOWNLOAD, nome + ext)

        if os.path.exists(caminho):
            print(f"Já existe -> {nome}")
            return

        with open(caminho, "wb") as f:
            f.write(r.content)

        print(f"Baixado -> {os.path.basename(caminho)}")

    except Exception as e:
        print("Erro download:", e)


def scroll(page):
    last = 0

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        h = page.evaluate("document.body.scrollHeight")

        if h == last:
            break

        last = h


def pegar_url_modal(page):
    """
    tenta encontrar imagem/gif dentro de qualquer modal
    (genérico, sem depender de ID fixo)
    """

    seletores = [
        "img[src*='gif']",
        "img[src]",
        "video source",
        "video",
        "img"
    ]

    for sel in seletores:
        try:
            el = page.locator(sel).first
            src = el.get_attribute("src")
            if src:
                return urljoin(page.url, src)
        except:
            pass

    return None


def fechar_modal(page):
    """
    tenta múltiplas formas de fechar modal
    """

    seletores_close = [
        "#close-modal",
        ".close",
        "[aria-label='close']",
        "button:has-text('Fechar')",
        "button:has-text('Close')"
    ]

    for sel in seletores_close:
        try:
            if page.locator(sel).count() > 0:
                page.locator(sel).first.click()
                return
        except:
            pass

    # fallback
    page.keyboard.press("Escape")


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    url = input("URL: ")
    page.goto(url, wait_until="networkidle")

    time.sleep(2)

    scroll(page)

    # tenta pegar botões comuns de modal
    botoes = page.locator(
        "button:has-text('Visualizar'), button, a, div"
    )

    total = botoes.count()
    print(f"\nPossíveis itens: {total}\n")

    usados = {}

    for i in range(min(total, 200)):  # proteção

        try:
            print(f"\nItem {i+1}")

            botoes.nth(i).click()
            time.sleep(2)

            url_media = pegar_url_modal(page)

            if url_media:

                nome = page.locator("h1, h2, h3").first.inner_text()
                nome = limpar_nome(nome)

                if nome in usados:
                    usados[nome] += 1
                    nome_final = f"{nome}-{usados[nome]}"
                else:
                    usados[nome] = 1
                    nome_final = nome

                baixar_arquivo(url_media, nome_final)

            else:
                print("Nada encontrado no modal")

            fechar_modal(page)
            time.sleep(1)

        except Exception as e:
            print("Erro:", e)
            try:
                fechar_modal(page)
            except:
                pass

    browser.close()

print("\nFinalizado!")