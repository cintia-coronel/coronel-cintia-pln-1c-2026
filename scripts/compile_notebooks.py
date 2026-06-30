#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de compilación de cuadernos Jupyter para el Asistente RAG.
Desarrollado para la materia de Introducción al PLN, LLMs y Agentic AI — IFTS 24.
"""

import os
import json
import re

# Directorios a ignorar en la búsqueda de cuadernos
EXCLUDE_DIRS = {'.git', '.github', '.venv', 'venv', 'env', 'node_modules', 'playground'}

def clean_anchor(text):
    """Genera un identificador de ancla compatible con Markdown."""
    anchor = text.lower()
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'[^a-z0-9\-_]', '', anchor)
    return anchor

def shift_headers(text, shift=2):
    """
    Desplaza los encabezados de Markdown hacia abajo para mantener la
    jerarquía en el documento consolidado.
    """
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        # Busca líneas que comiencen con '#' seguidas de espacios
        match = re.match(r'^(#+)(\s+.*)$', line)
        if match:
            hashes, content = match.groups()
            new_len = len(hashes) + shift
            if new_len > 6:
                new_len = 6
            new_lines.append('#' * new_len + content)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

def get_source_text(cell):
    """Obtiene el texto de la celda de forma robusta."""
    source = cell.get('source', '')
    if isinstance(source, list):
        return ''.join(source)
    return str(source)

def parse_notebook(filepath, rel_path):
    """Parsea un archivo .ipynb y lo convierte a formato Markdown estructurado."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"✗ Error al leer o decodificar {rel_path}: {e}")
        return None

    cells = data.get('cells', [])
    parsed_cells = []

    for idx, cell in enumerate(cells):
        cell_type = cell.get('cell_type')
        source_text = get_source_text(cell)
        
        # Omitir celdas vacías
        if not source_text.strip():
            continue

        if cell_type == 'markdown':
            # Desplazar encabezados para que encajen debajo del H2 del cuaderno
            shifted_text = shift_headers(source_text, shift=2)
            parsed_cells.append(shifted_text)
            
        elif cell_type == 'code':
            # Agregar el código de Python en un bloque
            code_block = (
                f"```python\n"
                f"# --- Código de: {rel_path} (Celda {idx + 1}) ---\n"
                f"{source_text.strip()}\n"
                f"```"
            )
            parsed_cells.append(code_block)

    # Unir las celdas con separación limpia
    notebook_content = "\n\n".join(parsed_cells)
    
    # Agregar encabezado del cuaderno con formato premium
    header = f"## ✦ Cuaderno: {rel_path}\n\n"
    header += f"**Ruta del archivo:** `file:///{rel_path}`\n\n"
    header += "---\n\n"
    
    return header + notebook_content

def compile_workspace(root_dir, output_file):
    """Busca, parsea y consolida todos los cuadernos válidos."""
    print("✎ Iniciando escaneo de cuadernos Jupyter...")
    
    notebook_paths = []
    
    # Recorrer directorios de forma recursiva
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filtrar directorios a omitir
        dirnames[:] = [
            d for d in dirnames 
            if not d.startswith('.') 
            and not d.startswith('_') 
            and d.lower() not in EXCLUDE_DIRS
        ]
        
        for filename in filenames:
            if filename.endswith('.ipynb'):
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)
                
                # Exclusión explícita adicional por segmentos de ruta
                parts = rel_path.split(os.sep)
                if any(p.lower() == 'playground' or p.startswith('.') or p.startswith('_') for p in parts):
                    continue
                
                notebook_paths.append((rel_path, full_path))
                
    # Ordenar alfabéticamente (garantiza orden 001_, 002_, ..., Guias, etc.)
    notebook_paths.sort(key=lambda x: x[0])
    
    if not notebook_paths:
        print("✗ No se encontraron cuadernos Jupyter válidos para compilar.")
        return
        
    print(f"✓ Se encontraron {len(notebook_paths)} cuadernos para compilar.")
    
    # Crear el contenido del archivo consolidado
    markdown_document = []
    
    # Título principal del corpus
    markdown_document.append(
        "# Corpus de Laboratorio de PLN, LLMs y Agentic AI — Cursada 2026\n\n"
        "**Material compilado de la materia Introducción al PLN, LLMs y Agentic AI**\n\n"
        "**Espacio:** IFTS Nº 24 — Ciencia de Datos e Inteligencia Artificial\n\n"
        "**Profesor:** Matías Barreto\n\n"
        "---\n\n"
        "## ◈ Descripción General\n\n"
        "Este documento consolida las explicaciones teóricas, guías prácticas y ejemplos de código "
        "de los cuadernos de la materia. Ha sido diseñado específicamente para servir como base de conocimiento "
        "para un asistente RAG (Retrieval-Augmented Generation) para facilitar consultas, armado de "
        "guías, cuestionarios y evaluaciones.\n\n"
        "---\n"
    )
    
    # Generar Índice de Contenidos (TOC)
    markdown_document.append("## 📋 Índice de Contenidos\n")
    for rel_path, _ in notebook_paths:
        anchor_name = clean_anchor(f"✦ Cuaderno: {rel_path}")
        markdown_document.append(f"- [{rel_path}](#{anchor_name})")
    markdown_document.append("\n---\n")
    
    # Compilar cada cuaderno
    for idx, (rel_path, full_path) in enumerate(notebook_paths, 1):
        print(f"[{idx}/{len(notebook_paths)}] Procesando: {rel_path}...")
        parsed_nb = parse_notebook(full_path, rel_path)
        if parsed_nb:
            markdown_document.append(parsed_nb)
            markdown_document.append("\n\n---\n\n")
            
    # Guardar en archivo
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(markdown_document))
        print(f"\n✓ ¡Compilación exitosa! Archivo guardado en: {output_file}")
        print(f"✓ Tamaño del corpus generado: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"\n✗ Error al guardar el archivo consolidado: {e}")

if __name__ == "__main__":
    # La raíz del repositorio es la carpeta contenedora de este script
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output = os.path.join(root, "corpus_rag_cursada.md")
    compile_workspace(root, output)
