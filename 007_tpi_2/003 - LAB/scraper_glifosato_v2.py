import json
import os
from playwright.sync_api import sync_playwright

urls = {
    "pagina12": [
        "https://www.pagina12.com.ar/825014-la-corte-suprema-de-santa-fe-reconocio-el-dano-genetico-prov/",
        "https://www.pagina12.com.ar/235451-glifosato-una-investigacion-argentina-confirma-su-peligro/",
        "https://www.pagina12.com.ar/275246-nuevo-estudio-vincula-al-glifosato-con-el-cancer-malformacio/",
    ],
    "clarin": [
        "https://www.clarin.com/rural/productores-podran-seguir-usando-glifosato-misiones_0_HQRRFpwW2j.html",
        "https://www.clarin.com/rural/soja-rr-glifosato_0_YdlYzZ4H-.html",
        "https://www.clarin.com/viste/que-es-el-glifosato-y-cual-es-su-impacto-en-la-economia-y-en-la-ecologia_0_95xysQIZlO.html",
    ]
}

resultados = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for grupo, lista_urls in urls.items():
        for url in lista_urls:
            try:
                print(f"Scrapeando [{grupo}]: {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)

                try:
                    page.click('button:has-text("Aceptar")', timeout=2000)
                except:
                    pass

                selector = "article" if "pagina12" in url else ".article-body, article, main"
                elemento = page.query_selector(selector)
                texto = elemento.inner_text() if elemento else page.inner_text("body")

                resultados.append({
                    "url": url,
                    "grupo_comparacion": grupo,
                    "texto": texto.strip()
                })
                print(f"OK: {len(texto)} caracteres extraídos.")

            except Exception as e:
                print(f"Error en {url}: {e}")

# Fuera del with — navegador ya cerrado
ruta_destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus_raw.json")
print(f"Guardando en: {ruta_destino}")

with open(ruta_destino, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"Listo. {len(resultados)} artículos guardados.")