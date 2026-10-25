"""Tests de `Utilidades_pygame.figuras`.

Aquí vive la regresión de API-07: `rect` es un `pygame.Rect` con `(L, T, W, H)`
y el AABB se recalcula cuando cambia la posición o el tamaño.
"""
import pygame as pag

from Utilidades_pygame import Engranaje, PoligonoIrregular, PoligonoRegular


# ==================== PoligonoRegular ====================

def test_poligono_regular_rect():
    cuadrado = PoligonoRegular(pos=(100, 100), lados=4, radio=20)

    assert len(cuadrado.figura) == 4
    assert cuadrado.rect == pag.Rect(80, 80, 40, 40)
    assert cuadrado.width == 40
    assert cuadrado.height == 40


def test_poligono_regular_rect_sigue_al_pos():
    cuadrado = PoligonoRegular(pos=(100, 100), lados=4, radio=20)
    cuadrado.pos = (50, 60)

    assert cuadrado.rect.center == (50, 60)
    assert cuadrado.rect == pag.Rect(30, 40, 40, 40)
    assert cuadrado.figura[0] == (70.0, 60.0)


def test_poligono_regular_radio():
    triangulo = PoligonoRegular(pos=(0, 0), lados=3, radio=10)
    triangulo.radio = 30

    assert triangulo.rect == pag.Rect(-30, -30, 60, 60)
    assert len(triangulo.figura) == 3


def test_poligono_regular_angiulo_regenera_los_vertices():
    figura = PoligonoRegular(pos=(100, 100), lados=4, radio=20)
    antes = list(figura.figura)

    figura.angle = 45

    assert figura.figura != antes
    assert len(figura.figura) == 4


def test_poligono_regular_drawing_drena_el_redraw(surface):
    """Primera pasada devuelve los rects; si nada cambió, la segunda no dibuja."""
    figura = PoligonoRegular(pos=(100, 100), lados=4, radio=20)

    primero = figura.draw(surface)
    assert len(primero) == 2          # rect actual + unión con el anterior
    assert figura.redraw == 0
    assert figura.draw(surface) == []


def test_poligono_regular_is_hover_y_collide():
    figura = PoligonoRegular(pos=(100, 100), lados=4, radio=20)

    assert figura.is_hover((100, 100))
    assert not figura.is_hover((0, 0))
    assert figura.collide(pag.Rect(90, 90, 10, 10))


# ==================== PoligonoIrregular ====================

def test_poligono_irregular():
    rombo = PoligonoIrregular(
        puntos=[(0, 1), (90, 1), (180, 1), (270, 1)],
        pos=(100, 100),
        radio=20,
    )

    assert len(rombo.figura) == 4
    assert rombo.rect.center == (100, 100)
    assert rombo.rect == pag.Rect(80, 80, 40, 40)


def test_poligono_irregular_gira():
    rombo = PoligonoIrregular(
        puntos=[(0, 1), (90, 1), (180, 1), (270, 1)],
        pos=(0, 0),
        radio=20,
    )
    antes = list(rombo.figura)
    rombo.angle = 45
    assert rombo.figura != antes


# ==================== Engranaje ====================

def test_engranaje_tiene_cuatro_vertices_por_diente():
    engranaje = Engranaje(pos=(100, 100), dientes=10, size_diente=4, radio=20)

    assert len(engranaje.figura) == 40
    assert engranaje.rect == pag.Rect(76, 76, 48, 48)     # radio + diente por lado


def test_engranaje_cambia_de_dientes():
    engranaje = Engranaje(pos=(0, 0), dientes=10, size_diente=4, radio=20)
    engranaje.n_dientes = 20
    assert len(engranaje.figura) == 80


def test_engranaje_dibuja(surface):
    engranaje = Engranaje(pos=(100, 100), dientes=10, size_diente=4, radio=20)
    assert len(engranaje.draw(surface)) == 2
