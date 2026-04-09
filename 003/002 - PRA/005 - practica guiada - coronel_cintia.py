# Práctica guiada: Procesamiento digital de imágenes

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import skimage as ski


def mostrar_imagenes(imagenes, titulos, cmap=None, figsize=(14, 4)):
    fig, axes = plt.subplots(1, len(imagenes), figsize=figsize)
    if len(imagenes) == 1:
        axes = [axes]

    for ax, imagen, titulo in zip(axes, imagenes, titulos):
        if imagen.ndim == 2:
            ax.imshow(imagen, cmap=cmap or "gray")
        else:
            ax.imshow(imagen)
        ax.set_title(titulo)
        ax.axis("off")

    plt.tight_layout()
    plt.show()


def segmentar_por_umbral(imagen, umbral):
    mascara = np.zeros_like(imagen, dtype=np.uint8)
    mascara[imagen > umbral] = 255
    return mascara

base = Path(".")

cv2.imwrite(str(base / "paisaje.png"), cv2.cvtColor(ski.data.astronaut(), cv2.COLOR_RGB2BGR))
cv2.imwrite(str(base / "texto.png"), ski.data.page())
cv2.imwrite(str(base / "monedas.png"), ski.data.coins())

print("Archivos de práctica listos: paisaje.png, texto.png y monedas.png")

## Ejercicio 1: Color y canales

# 1. Cargar la imagen
img_bgr = cv2.imread("paisaje.png")

# 2. Convertirla a RGB
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# 3. Extraer canales
canal_rojo = img_bgr[:, :, 2]
canal_verde = img_bgr[:, :, 1]
canal_azul = img_bgr[:, :, 0]

# 4. Visualizar resultados
mostrar_imagenes(
    [img_rgb, canal_rojo, canal_verde, canal_azul],
    ["Original", "Rojo", "Verde", "Azul"],
)

observacion_canales = (
    "En los distintos canales observo las variaciones de escalas de grises, "
    "dependiendo de a qué color refiera cada uno. En el canal rojo aparece más "
    "brillante, asociado al blanco, el traje de la astronauta y también la piel. "
    "En el canal verde aparece más brillante lo neutro, me costó visualizarlo "
    "ya que en la original no hay tantos verdes. "
    "En el canal azul resaltan los detalles en azul del traje."
)
print(observacion_canales)

## Ejercicio 2: Recorte y redimensionado

# Definí los índices de tu región de interés.
y1, y2 = 50, 150
x1, x2 = 50, 150

roi = img_rgb[y1:y2, x1:x2]
roi_grande = cv2.resize(roi, (220, 220))

# Armá un mosaico 2 x 2.
fila_superior = cv2.hconcat([roi_grande, roi_grande])
fila_inferior = cv2.hconcat([roi_grande, roi_grande])
mosaico = cv2.vconcat([fila_superior, fila_inferior])

mostrar_imagenes(
    [roi, roi_grande, mosaico],
    ["ROI", "ROI redimensionada", "Mosaico"],
    figsize=(15, 4),
)

explicacion_geometria = "En las imagenes resultantes veo que el ROI es una porción limitada, pixelada, mientras que ROI redimensionada cambia el tamaño de la imagen interpolando, además que puede generar una imagen borrosa"
print(explicacion_geometria)

## Ejercicio 3: Bordes y umbralización

#Carga de la imagen en escala de grises
img_texto = cv2.imread("texto.png", cv2.IMREAD_GRAYSCALE)

canny_a = cv2.Canny(img_texto, 50, 150)
canny_b = cv2.Canny(img_texto, 180, 240)

mostrar_imagenes(
    [img_texto, canny_a, canny_b],
    ["Texto original", "Canny A", "Canny B"],
    figsize=(15, 4),
)

img_monedas = cv2.imread("monedas.png", cv2.IMREAD_GRAYSCALE)

seg_a = segmentar_por_umbral(img_monedas, 100)
seg_b = segmentar_por_umbral(img_monedas, 170)

mostrar_imagenes(
    [img_monedas, seg_a, seg_b],
    ["Monedas originales", "Umbral A", "Umbral B"],
    figsize=(15, 4),
)

# si quiero detectar que son monedas, creo que el Canny A es mejor, mientras que los detalles se ven mejor en la opción B


## Cierre breve

#Antes de pasar al laboratorio, revisá si podés responder estas preguntas:

# ¿cuándo conviene mirar canales por separado?
# Conviene al querer mirar o resaltar un color predominante.

# ¿qué cambia al modificar los umbrales de `Canny`?
# Nos deja los bordes relevantes

# ¿por qué una segmentación por umbral puede funcionar bien en una imagen y mal en otra?
# Depende de la imagen, de lo que queremos detectar y cómo está organizada esa información 
