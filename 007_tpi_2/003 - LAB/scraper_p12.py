import json
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
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    for grupo, lista_urls in urls.items():
        for url in lista_urls:
            print(f"Scrapeando: {url}")
            page.goto(url)
            page.wait_for_timeout(3000)

            # Cerramos modales si aparecen
            try:
                boton = page.wait_for_selector('button:has-text("Aceptar")', timeout=3000)
                if boton:
                    boton.click()
            except:
                pass

            texto = page.evaluate("() => document.body.innerText")
            resultados.append({
                "url": url,
                "grupo_comparacion": grupo,
                "texto": texto
            })

    browser.close()

with open("corpus_raw.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("Listo. Guardado en corpus_raw.json")
