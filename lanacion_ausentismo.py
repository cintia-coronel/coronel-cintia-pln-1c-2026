import json
from playwright.sync_api import sync_playwright

noticias = []

urls_lanacion = [
    "https://www.lanacion.com.ar/editoriales/ausentismo-escolar-antesala-de-abandono-nid01032026/",
    "https://www.lanacion.com.ar/sociedad/estamos-a-tiempo-de-revertir-esta-situacion-la-carta-que-revela-la-alarma-por-el-ausentismo-en-las-nid13032026/",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    for url in urls_lanacion:
        page = context.new_page()
        try:
            page.goto(url)
            # cerrar modal de cookies si aparece
            try:
                boton = page.wait_for_selector('button:has-text("Aceptar")', timeout=3000)
                if boton: boton.click()
            except:
                pass

            page.wait_for_selector("article", timeout=8000)

            texto = page.evaluate("""
            () => {
                const parrafos = document.querySelectorAll('article p');
                return Array.from(parrafos).map(p => p.innerText.trim()).filter(t => t.length > 30).join(' ');
            }
            """)

            titulo = page.title()

            if texto:
                noticias.append({
                    "titulo": titulo,
                    "texto": texto,
                    "origen": "json",
                    "url_o_path": url
                })
                print(f"OK: {titulo[:60]}")
            else:
                print(f"Sin texto: {url}")

        except Exception as e:
            print(f"Error en {url}: {e}")
        finally:
            page.close()

    browser.close()

with open("corpus_anterior.json", "w", encoding="utf-8") as f:
    json.dump(noticias, f, ensure_ascii=False, indent=2)

print(f"JSON guardado con {len(noticias)} noticias.")
