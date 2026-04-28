!pip install playwright
!playwright install chromium

%%writefile extraccion_noticias.py
import pandas as pd
from playwright.sync_api import sync_playwright

def extraer_datos(url):
    with sync_playwright() as p:
        # Usamos headless=True para que corra de fondo sin abrir ventanas
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Procesando: {url}")
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            titulo = page.inner_text("h1")
            
            # Selectores para Infobae, Perfil, Cenital y Página 12
            selector_cuerpo = ".article-body-container p, .article-body p, .post-content p, .article-main-content p"
            parrafos = page.query_selector_all(selector_cuerpo)
            texto = "\n".join([p.inner_text() for p in parrafos])
            
            return {"url": url, "titulo": titulo, "contenido": texto}
        except Exception as e:
            return {"url": url, "titulo": "Error", "contenido": str(e)}
        finally:
            browser.close()

if __name__ == "__main__":
    urls = [
        "https://www.infobae.com/tecno/2026/03/25/openai-confirma-que-abandonara-sora-su-aplicacion-para-generar-videos-con-ia/",
        "https://www.perfil.com/noticias/columnistas/el-futuro-que-duro-seis-meses-por-joan-cwaik.phtml",
        "https://cenital.com/la-inteligencia-artificial-no-muestra-el-pasado-lo-reescribe/"
    ]
    
    resultados = [extraer_datos(u) for u in urls]
    df = pd.DataFrame(resultados)
    df.to_csv("noticias_tpi.csv", index=False, encoding="utf-8")
    print("Archivo 'noticias_tpi.csv' creado exitosamente.")