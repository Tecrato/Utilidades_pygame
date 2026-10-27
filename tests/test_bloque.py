"""Tests del `Bloque` como contenedor tipo `div`.

Lo que se comprueba:
1. Pinta a sus hijos dentro de su rectángulo y **recorta** lo que sobresale.
2. Un hijo que está fuera del cuadro no se dibuja.
3. Respeta los dirty rects: si cambia un hijo, solo se repinta su zona; si no
   cambia nada, `draw()` no hace nada (devuelve `None`... bueno, `[]`).
4. El scroll funciona con un solo eje activo (antes se quedaba en 1).
"""
import pygame as pag

from Utilidades_pygame import Bloque
from Utilidades_pygame.obj_Base import Base


class Caja(Base):
    """Hijo mínimo: un rectángulo de color y un contador de dibujos."""

    def __init__(self, pos=(0, 0), size=(20, 10), color=(255, 0, 0)):
        super().__init__(pos, 'topleft')
        self.rect = pag.Rect(pos, size)
        self.last_rect = self.rect.copy()
        self.color = color
        self.dibujos = 0
        self.ultimo_dt = None

    def draw(self, surface, diff_pos=(0, 0)):
        self.dibujos += 1
        if self.redraw < 1:
            return []
        pag.draw.rect(surface, self.color, self.rect.move(diff_pos))
        r = self.last_rect.union(self.rect).copy()
        self.last_rect = self.rect.copy()
        self.redraw = 0
        return [self.rect.move(diff_pos), r.move(diff_pos)]

    @property
    def width(self):
        return self.rect.w

    @property
    def height(self):
        return self.rect.h

    def update(self, pos=None, dt=1, **kwargs):
        self.ultimo_dt = dt

    def update_hover(self, *args, **kwargs):
        pass

    def on_wheel(self, delta):
        return False

    def click(self, *args, **kwargs):
        return False


def _bloque(hijos=(), size=(100, 80), pos=(50, 40), **kwargs):
    bloque = Bloque(pos, size, dire='topleft', background_color=(10, 10, 10, 255),
                    border_width=1, border_color=(90, 90, 90), **kwargs)
    for hijo in hijos:
        bloque.add(hijo)
    return bloque


def _ventana():
    ventana = pag.Surface((300, 200))
    ventana.fill((0, 0, 0))
    return ventana


# ==================== recorte ====================

def test_pinta_dentro_y_recorta_lo_que_sobresale():
    ventana = _ventana()
    grande = Caja((0, 0), (400, 400), (0, 255, 0))     # más grande que el bloque
    dentro = Caja((10, 10), (20, 10), (255, 0, 0))
    bloque = _bloque([grande, dentro])

    bloque.draw(ventana)

    assert ventana.get_at((50 + 15, 40 + 15))[:3] == (255, 0, 0)   # el hijo de dentro
    assert ventana.get_at((50 + 90, 40 + 60))[:3] == (0, 255, 0)   # el grande, recortado
    assert ventana.get_at((50 + 105, 40 + 15))[:3] == (0, 0, 0)    # nada a la derecha
    assert ventana.get_at((50 - 3, 40 + 15))[:3] == (0, 0, 0)      # nada a la izquierda
    assert ventana.get_at((50 + 50, 40 + 85))[:3] == (0, 0, 0)     # nada debajo


def test_bloque_vacio_pinta_su_fondo():
    """Un div sin hijos sigue siendo una caja: se ve su fondo y colisiona."""
    ventana = _ventana()
    bloque = _bloque([])

    bloque.draw(ventana)

    assert ventana.get_at((50 + 50, 40 + 40))[:3] == (10, 10, 10)
    assert bloque.collide(ventana.get_rect())


def test_bloque_dentro_de_bloque_tambien_se_recorta():
    ventana = _ventana()
    interior = Bloque((10, 10), (200, 200), dire='topleft',
                      background_color=(0, 0, 255, 255), border_width=1)
    interior.add(Caja((0, 0), (400, 400), (0, 255, 0)))
    exterior = _bloque([interior], size=(100, 80))

    exterior.draw(ventana)

    assert ventana.get_at((50 + 15, 40 + 15))[:3] == (0, 255, 0)   # hijo del interior
    assert ventana.get_at((50 + 95, 40 + 75))[:3] == (0, 255, 0)   # recortado al exterior
    assert ventana.get_at((50 + 105, 40 + 40))[:3] == (0, 0, 0)    # fuera del exterior
    assert ventana.get_at((50 + 50, 40 + 85))[:3] == (0, 0, 0)


def test_hijo_fuera_del_cuadro_no_se_dibuja():
    ventana = _ventana()
    fuera = Caja((200, 10), (20, 10), (255, 0, 0))
    bloque = _bloque([fuera])

    bloque.draw(ventana)

    assert fuera.dibujos == 0
    assert ventana.get_at((50 + 205, 40 + 15))[:3] == (0, 0, 0)


# ==================== dirty rects ====================

def test_solo_repinta_la_zona_sucia():
    ventana = _ventana()
    roja = Caja((10, 10), (20, 10), (255, 0, 0))
    verde = Caja((10, 50), (20, 10), (0, 255, 0))
    bloque = _bloque([roja, verde])
    bloque.draw(ventana)

    roja.dibujos = verde.dibujos = 0
    roja.color = (0, 0, 255)
    roja.redraw = 1

    rects = bloque.draw(ventana)

    assert roja.dibujos == 1
    assert verde.dibujos == 0                      # el limpio no se toca
    assert rects
    assert all(r.width <= 22 and r.height <= 12 for r in rects)   # no es todo el bloque
    assert ventana.get_at((50 + 15, 40 + 15))[:3] == (0, 0, 255)
    assert ventana.get_at((50 + 15, 40 + 55))[:3] == (0, 255, 0)


def test_hijo_que_se_mueve_limpia_el_hueco():
    ventana = _ventana()
    caja = Caja((10, 10), (20, 10), (255, 0, 0))
    bloque = _bloque([caja])
    bloque.draw(ventana)

    caja.move((60, 40))
    bloque.draw(ventana)

    assert ventana.get_at((50 + 15, 40 + 15))[:3] == (10, 10, 10)      # hueco limpio
    assert ventana.get_at((50 + 65, 40 + 45))[:3] == (255, 0, 0)       # nueva posición


def test_add_y_clear_ensucian_el_bloque():
    ventana = _ventana()
    bloque = _bloque([])
    bloque.draw(ventana)

    bloque.add(Caja((10, 10), (20, 10), (0, 0, 255)))
    assert bloque.redraw >= 1
    bloque.draw(ventana)
    assert ventana.get_at((50 + 15, 40 + 15))[:3] == (0, 0, 255)

    bloque.clear()
    assert bloque.redraw >= 1
    bloque.draw(ventana)
    assert ventana.get_at((50 + 15, 40 + 15))[:3] == (10, 10, 10)


def test_hover_no_se_fuga_fuera_del_cuadro():
    caja = Caja((10, 10), (20, 10), (255, 0, 0))
    bloque = _bloque([caja], size=(100, 80), pos=(50, 40))
    vistos = []
    caja.update_hover = lambda mouse_pos=None, **k: vistos.append(mouse_pos)

    bloque.update_hover((50 + 15, 40 + 15))     # dentro del cuadro
    bloque.update_hover((0, 0))                 # fuera del cuadro

    assert tuple(vistos[0]) == (15, 15)
    assert vistos[1][0] < -1000


def test_update_pasa_dt_a_los_hijos():
    caja = Caja((10, 10))
    bloque = _bloque([caja])

    bloque.update(dt=0.25)

    assert caja.ultimo_dt == 0.25


def test_sin_cambios_no_dibuja_nada():
    ventana = _ventana()
    bloque = _bloque([Caja((10, 10))])
    bloque.draw(ventana)

    assert bloque.draw(ventana) == []


def test_redraw_par_repinta_todo_el_bloque():
    ventana = _ventana()
    bloque = _bloque([Caja((10, 10))])
    bloque.draw(ventana)

    bloque.redraw = 2
    rects = bloque.draw(ventana)

    assert len(rects) == 2
    assert rects[0].width >= 100 and rects[0].height >= 80


# ==================== scroll ====================

def test_scroll_vertical_con_el_horizontal_apagado():
    hijos = [Caja((10, 10 + i * 30), (40, 20)) for i in range(6)]
    bloque = _bloque(hijos, size=(100, 60), pos=(0, 0), scroll_y=True, scroll_x=False)

    # contenido de 10 + 5*30 + 20 = 180px en un cuadro de 60: hay scroll
    assert bloque.scroll_class.inside_height == 180
    assert bloque.scroll_class.bar_active is True

    bloque.on_wheel(-20)
    for _ in range(120):
        bloque.update()

    assert bloque.scroll_class.diff != 0
    assert bloque.scroll_y is True


def test_scroll_desplaza_el_contenido_en_pixeles():
    ventana = _ventana()
    roja = Caja((10, 40), (20, 10), (255, 0, 0))
    verde = Caja((10, 100), (20, 10), (0, 255, 0))     # alarga el contenido a 110
    bloque = _bloque([roja, verde], size=(100, 60), pos=(0, 0),
                     scroll_y=True, scroll_x=False)
    bloque.draw(ventana)
    assert ventana.get_at((15, 45))[:3] == (255, 0, 0)

    bloque.on_wheel(-20)
    for _ in range(120):
        bloque.update()
    d = int(bloque.scroll_class.diff)
    assert d < 0

    bloque.redraw = 2
    bloque.draw(ventana)

    # el contenido subió: la caja roja está en 40 + d, y donde estaba queda el fondo
    assert ventana.get_at((15, 40 + d + 5))[:3] == (255, 0, 0)
    assert ventana.get_at((15, 45))[:3] == (10, 10, 10)


def test_scroll_no_dibuja_lo_que_sale_por_arriba():
    hijos = [Caja((10, 10 + i * 30), (40, 20)) for i in range(6)]
    ventana = _ventana()
    bloque = _bloque(hijos, size=(100, 60), pos=(0, 0), scroll_y=True, scroll_x=False)
    bloque.draw(ventana)

    bloque.on_wheel(-40)
    for _ in range(120):
        bloque.update()
    desplazamiento = bloque.scroll_class.diff
    assert desplazamiento < 0

    for hijo in hijos:
        hijo.dibujos = 0
    bloque.redraw = 2
    bloque.draw(ventana)

    # tras desplazar el contenido, los de arriba se han ido del cuadro
    assert hijos[0].dibujos == 0
    assert all(h.dibujos >= 0 for h in hijos)
