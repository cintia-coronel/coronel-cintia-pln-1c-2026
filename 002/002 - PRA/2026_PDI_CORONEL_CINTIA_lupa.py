import py5

img = None

def setup():
    global img
    py5.size(800, 400)
    img = py5.load_image("C:/Users/cin_c/OneDrive/Desktop/IFTS 24/2026 1°C PDI/TP2/img/avatars-000092802502-yopezf-t1080x1080.jpg") 
    img.resize(400, 400)

def draw():
    py5.background(255)

    # Mostrar la imagen en la mitad izquierda
    py5.image(img, 0, 0)

    # Limitar las coordenadas del mouse al área de la imagen
    # Esto evita errores si el cursor sale de la imagen
    mx = py5.constrain(py5.mouse_x, 0, 399)
    my = py5.constrain(py5.mouse_y, 0, 399)

    # Obtener el color del píxel en esa posición
    color_pixel = py5.get_pixels(int(mx), int(my))

    # Separar el color en sus tres canales
    r = py5.red(color_pixel)
    g = py5.green(color_pixel)
    b = py5.blue(color_pixel)

    # Mostrar el color como un cuadrado en la mitad derecha (la "lupa")
    py5.fill(color_pixel)
    py5.stroke(0)
    py5.rect(450, 50, 300, 300)

    # Mostrar los valores numéricos
    py5.fill(0)
    py5.text_size(18)
    py5.text(f"Posición: ({mx}, {my})", 450, 30)
    py5.text(f"R: {r:.0f}   G: {g:.0f}   B: {b:.0f}", 450, 380)

py5.run_sketch()

# no llegué a probar las otras variantes