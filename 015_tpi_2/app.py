
import os
from pathlib import Path
import gradio as gr
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# ─── Configuración ────────────────────────────────────────────────────────────
HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

if not HF_TOKEN:
    raise ValueError("Configurá el secreto HF_TOKEN en el Space.")

# ─── Embeddings locales (corren en la CPU del Space) ──────────────────────────
modelo_embeddings = SentenceTransformerEmbeddings(
    model_name="intfloat/multilingual-e5-large"
)

# ─── ChromaDB en memoria (sin disco para Spaces) ──────────────────────────────
vectorstore = Chroma(
    collection_name="proyecto_rag_spaces",
    embedding_function=modelo_embeddings
)

# ─── Divisor de texto ─────────────────────────────────────────────────────────
divisor = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=80,
    separators=["\n\n", "\n", ". ", " "]
)

# ─── LLM vía HuggingFace Serverless Inference ─────────────────────────────────
llm_endpoint = HuggingFaceEndpoint(
    repo_id=MODEL_ID,
    task="text-generation",
    provider="together",
    max_new_tokens=512,
    temperature=0.1,
    huggingfacehub_api_token=HF_TOKEN
)

llm = ChatHuggingFace(llm=llm_endpoint)

# ─── Pipeline RAG ─────────────────────────────────────────────────────────────
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


def formatear_documentos(docs):
    return "\n\n".join(doc.page_content for doc in docs)


TEMPLATE = """Respondé la siguiente pregunta usando ÚNICAMENTE los documentos proporcionados.
Si la respuesta no está en los documentos, decilo claramente.
Documentos:
{context}
Pregunta: {question}
Respuesta:"""

prompt = PromptTemplate(
    template=TEMPLATE,
    input_variables=["context", "question"]
)

pipeline_rag = (
    {"context": retriever | formatear_documentos, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# ─── Funciones de la interfaz ─────────────────────────────────────────────────
def cargar_pdfs_interfaz(archivos):
    if not archivos:
        return "No se seleccionaron archivos."

    nuevas_paginas = []
    nombres = []

    for archivo in archivos:
        loader = PyPDFLoader(archivo.name)
        paginas = loader.load()
        nuevas_paginas.extend(paginas)
        nombres.append(Path(archivo.name).name)

    nuevos_fragmentos = divisor.split_documents(nuevas_paginas)
    vectorstore.add_documents(nuevos_fragmentos)

    return f"✓ Archivos: {', '.join(nombres)}\n✓ Fragmentos: {len(nuevos_fragmentos)}"


def responder_pregunta(pregunta, history):
    if not pregunta.strip():
        return history, ""

    try:
        respuesta = pipeline_rag.invoke(pregunta)
    except Exception as e:
        respuesta = f"Ocurrió un error al generar la respuesta: {e}"

    fragmentos_fuente = retriever.invoke(pregunta)
    lineas_fuente = []
    for frag in fragmentos_fuente:
        fuente = Path(frag.metadata.get("source", "desconocida")).name
        pagina = frag.metadata.get("page", "?")
        extracto = frag.page_content[:200].replace("\n", " ").strip()
        lineas_fuente.append(f"• {fuente} (pág. {pagina}):\n  \"{extracto}...\"")

    history = history + [
        {"role": "user", "content": pregunta},
        {"role": "assistant", "content": respuesta}
    ]
    return history, "\n".join(lineas_fuente)


# ─── Construcción de la interfaz ──────────────────────────────────────────────
with gr.Blocks(title="Archivo Histórico Digital: Colección San Martín", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Archivo Histórico Digital: Colección San Martín")
    gr.Markdown("**Proyecto Integrador — Laboratorio de PLN (IFTS 24)**")

    with gr.Tab("📄 Cargar documentos"):
        gr.Markdown("Subí uno o más PDFs para agregarlos a la base de conocimiento.")
        upload_component = gr.File(
            label="Seleccioná tus PDFs",
            file_types=[".pdf"],
            file_count="multiple"
        )
        boton_cargar = gr.Button("Indexar documentos", variant="primary")
        estado_carga = gr.Textbox(label="Estado", interactive=False, lines=3)
        boton_cargar.click(
            fn=cargar_pdfs_interfaz,
            inputs=[upload_component],
            outputs=[estado_carga]
        )

    with gr.Tab("💬 Consultá al Asistente Histórico"):
        chatbot_componente = gr.Chatbot(label="Conversación", height=400)
        with gr.Row():
            pregunta_componente = gr.Textbox(
                label="Tu pregunta",
                placeholder="¿En qué año y ciudad nació San Martín?",
                scale=4
            )
            boton_preguntar = gr.Button("Preguntar", variant="primary", scale=1)
        fuentes_componente = gr.Textbox(
            label="Fragmentos consultados",
            interactive=False,
            lines=3
        )
        boton_preguntar.click(
            fn=responder_pregunta,
            inputs=[pregunta_componente, chatbot_componente],
            outputs=[chatbot_componente, fuentes_componente]
        )
        pregunta_componente.submit(
            fn=responder_pregunta,
            inputs=[pregunta_componente, chatbot_componente],
            outputs=[chatbot_componente, fuentes_componente]
        )

    gr.Markdown(
        """
        ---
        ⚠️ Las respuestas son generadas de forma automática por un modelo de lenguaje analizando los documentos provistos. Pueden existir inexactitudes. Se recomienda auditar la información desplegando la pestaña de 'fragmentos consultados' para leer la cita original.
        """
    )

if __name__ == "__main__":
    demo.launch(share=False)
