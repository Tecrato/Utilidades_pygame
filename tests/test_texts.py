"""Tests de `Utilidades_pygame.Text` sin ventana."""
from Utilidades_pygame import Text


def test_texto_tiene_rect_y_una_linea(surface):
    texto = Text("hola mundo", 20, pos=(100, 100))

    assert len(texto.lista_text) == 1
    assert texto.width > 0
    assert texto.height > 0
    assert texto.rect.size == (texto.width, texto.height)


def test_texto_drawing_drena_el_redraw(surface):
    """Protocolo de API-01: dibujar devuelve la zona sucia y deja `redraw` a 0."""
    texto = Text("hola", 20, pos=(100, 100))
    assert texto.draw(surface)
    assert texto.redraw == 0
    assert texto.draw(surface) == []


def test_texto_cambia_de_contenido():
    texto = Text("hola", 20, pos=(100, 100))
    ancho = texto.width

    texto.text = "hola mundo mundo mundo"

    assert texto.text == "hola mundo mundo mundo"
    assert texto.width > ancho
    assert len(texto.lista_text) == 1


def test_texto_envuelve_por_max_width():
    texto = Text("a b c d e f g h i j", 20, pos=(10, 10), max_width=30)

    assert len(texto.lista_text) > 1
    for linea in texto.lista_text:
        assert linea.get_width() <= 30


def test_texto_tamano_cambia_la_altura():
    """`size` rehace la fuente, también cuando se usa la fuente por defecto."""
    texto = Text("hola", 12, pos=(0, 0))
    bajo = texto.height
    texto.size = 48
    assert texto.height > bajo
    assert texto.size == 48


def test_texto_color_y_underline_no_rompen():
    texto = Text("hola", 20, pos=(0, 0))
    texto.color = (255, 0, 0)
    texto.underline = True
    assert texto.underline is True
    assert texto.color == (255, 0, 0)


def test_texto_click_es_falso():
    texto = Text("hola", 20, pos=(0, 0))
    assert texto.click((0, 0)) is False
