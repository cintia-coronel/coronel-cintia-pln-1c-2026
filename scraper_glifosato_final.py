import json
import os
import sys
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

try:
    with sync_playwright() as p:
        print("🚀 Iniciando navegador invisible...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for grupo, lista_urls in urls.items():
            for url in lista_urls:
                try:
                    print(f"--- Trabajando en: {url[:40]}...")
                    # wait_until="commit" es mucho más rápido que "networkidle"
                    page.goto(url, wait_until="commit", timeout=45000)
                    page.wait_for_timeout(1000) 

                    texto = page.inner_text("article") if "pagina12" in url else page.inner_text("body")

                    resultados.append({
                        "url": url,
                        "grupo_comparacion": grupo,
                        "texto": texto.strip()
                    })
                    print(f"✅ OK ({len(texto)} caracteres)")
                except Exception as e:
                    print(f"❌ Error en URL: {e}")

        # GUARDADO CRÍTICO: Lo hacemos ANTES de intentar cerrar nada
        print("\n💾 Escribiendo archivo JSON...")
        with open("corpus_raw.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)

        print("✨ ¡Archivo guardado exitosamente!")

        # Salida de emergencia: Forzamos el cierre del script 
        # para que la celda de Jupyter no se quede tildada
        print("Cerrando procesos...")
        browser.close()
        sys.exit(0) 

except Exception as e:
    print(f"Error general: {e}")
    sys.exit(1)
