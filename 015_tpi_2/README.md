---
title: Archivo Historio SM
emoji: 📚
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 6.19.0
python_version: '3.13'
app_file: app.py
pinned: false
---
# Sistema RAG - Archivo Histórico Digital: Colección San Martín

**IFTS N°24 - Técnicas de Procesamiento del Lenguaje Natural**

Profesor: Matías Barreto 

Estudiante: Cintia Coronel


**Descripción:** Este proyecto implementa un Sistema de Retrieval-Augmented Generation (RAG) capaz de responder preguntas basadas en un corpus de documentos históricos sobre José de San Martín, utilizando:

- Embeddings locales (intfloat/multilingual-e5-large)
- ChromaDB como base vectorial (en memoria)
- Qwen2.5-7B-Instruct como modelo generador, vía HuggingFace Inference Providers (Together AI)
- Gradio como interfaz web

Este sistema permite consultar la biografía, el pensamiento y los hechos documentados de José de San Martín, citando el documento y la página de origen de cada respuesta.

**Demo:** [https://huggingface.co/spaces/halurodeag/archivo-historio-SM]

**Ejecución local:**
```bash
python app.py
```

El sistema requiere una API key gratuita de HuggingFace (HF_TOKEN) y no requiere GPU. El LLM corre vía API; los embeddings corren localmente con CPU.
## Problema que resuelve
Estudiar una figura histórica a través de un texto plano puede ser árido y poco interactivo. Este sistema:
- Permite preguntar directamente sobre la biografía, el pensamiento y los hechos documentados de San Martín.
- Recupera los fragmentos más relevantes del corpus y genera una respuesta basada únicamente en ellos.
- Muestra siempre los fragmentos consultados (documento, página y extracto) para que la respuesta pueda verificarse contra la fuente original.
RAG permite combinar la información real de los documentos históricos con la capacidad generativa del modelo, evitando alucinaciones y respuestas sin fuente verificable.
## Arquitectura del sistema
Pipeline RAG
1. Ingesta
- Los PDFs base (biografía, ideas y pensamiento, frases documentadas, etc.) se suben desde la pestaña "Cargar documentos" de la interfaz.
- Cada PDF se procesa con PyPDFLoader, que conserva la metadata de archivo y página.
2. Chunking
- Se utiliza `RecursiveCharacterTextSplitter`
- `chunk_size = 800`
- `chunk_overlap = 80`
- Esto permite que los fragmentos tengan suficiente contexto.

3. Embeddings
Modelo utilizado: intfloat/multilingual-e5-large
Motivos:

- Buen desempeño en español
- Corre localmente sin necesidad de GPU
- No requiere API key adicional

4. Almacenamiento (Vectorstore)
Se usa `Chroma(collection_name="proyecto_rag_spaces", embedding_function=modelo_embeddings)`, en memoria (no quedan en el disco), recomendado para evitar errores de permisos en HuggingFace Spaces.

5. Retrieval
Estrategia:

- Búsqueda por similitud
- `k = 3` documentos relevantes por consulta

6. Modelo generativo: Qwen/Qwen2.5-7B-Instruct

Integrado con:
- HuggingFaceEndpoint (task="text-generation", provider="together")
- ChatHuggingFace como wrapper de chat
- Pipeline armado con LangChain Expression Language (LCEL)

7. Interfaz
Gradio:

- Pestaña "Cargar documentos": carga y reindexado de PDFs adicionales
- Pestaña "Consultá al Asistente Histórico": campo de pregunta, historial de conversación, y cuadro de fragmentos consultados (documento, página y extracto del texto fuente)

## Stack tecnológico
```
gradio
langchain
langchain-core
langchain-community
langchain-chroma
langchain-huggingface
langchain-text-splitters
pypdf
sentence-transformers
huggingface_hub
```

## Errores encontrados y soluciones
Principales errores durante el desarrollo.

- Error: ModuleNotFoundError: No module named 'pyaudioop' (Gradio + Python 3.13 en HuggingFace Spaces)

- Error: No API found al consultar un modelo de Meta (Llama)

- Error: model_not_supported con distintos modelos (Phi-3.5, Llama 3.2)

- Respuestas con datos mezclados entre personas distintas (ej. confundir la fecha de nacimiento de San Martín con la de su hija Mercedes)

- El campo "Fragmentos consultados" solo mostraba el nombre del archivo y la página


## Ejemplos de consultas

- ¿En qué año y ciudad nació San Martín?
- ¿Qué pasó en la entrevista de Guayaquil con Bolívar?
- ¿San Martín fue conquistador o libertador?
- ¿Qué decían las Máximas que escribió para su hija Mercedes?
