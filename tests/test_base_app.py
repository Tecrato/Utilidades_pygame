"""Tests de `Base_class` sin bucle (API-04).

`Base_class(..., autostart=False)` monta la app y devuelve el objeto sin
entrar en `screen_main()` ni llamar a `pag.quit()`, que es lo que permite
dibujar un frame a mano en un test o en un benchmark.
"""
import pygame as pag

from Utilidades_pygame import Config, Text
from Utilidades_pygame.base_app_class import Base_class


class App(Base_class):
    def screen_main(self):          # nunca debería ejecutarse con autostart=False
        raise AssertionError("screen_main no debe arrancar solo")

    def on_exit(self):
        self.salida = True


def _app() -> App:
    return App(Config(resolution=(320, 240), title="test_headless"),
               autostart=False, initial_screen="main")


def test_construye_sin_arrancar_el_bucle():
    app = _app()

    assert app.actual_screen == "main"
    assert app.running is True
    assert not getattr(app, "salida", False)


def test_hwnd_es_none_sin_ventana_real():
    """Con SDL_VIDEODRIVER=dummy no hay `window` en `get_wm_info()`."""
    app = _app()

    assert app.hwnd is None
    assert app.ventana.get_size() == (320, 240)


def test_draw_optimized_dibuja_un_frame_y_luego_duerme(pantalla):
    app = _app()
    texto = Text("hola", 16, pos=(40, 40))
    lista = app.lists_screens["main"]["draw"]
    lista.append(texto)

    app.draw_optimized(lista)
    assert texto.redraw == 0
    assert app.updates                      # el primer frame sucio devuelve rects

    app.draw_optimized(lista)
    assert app.updates == []                # nada cambió: no se dibuja nada


def test_draw_always_no_revienta(pantalla):
    app = _app()
    lista = app.lists_screens["main"]["draw"]
    lista.append(Text("hola", 16, pos=(40, 40)))

    app.draw_always(lista)                  # no debe lanzar

    assert pag.display.get_surface() is not None
