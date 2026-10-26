"""Benchmark de `Bloque` — el contenedor con scroll.

`Bloque` no usa dirty rects: en cada `draw()` que pasa el filtro rellena su
superficie y **marca sucios a todos los hijos** para redibujarlos dentro. Por
eso aquí lo que se mide es el coste de un frame con el bloque visible, con y
sin scroll, y cuánto pesa `move_objs()` al desplazar.
"""
from __future__ import annotations

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    sin_presentacion, tabla)
from Utilidades_pygame import Bloque, Text

N = (10, 50, 100)


def _bloque(n: int) -> Bloque:
    bloque = Bloque((50, 40), (500, 400), dire="topleft",
                    background_color=(30, 30, 30), border_width=1,
                    border_color=(90, 90, 90))
    for i in range(n):
        bloque.add(Text(f"fila {i}", 16, pos=(40, 20 + i * 24), dire="topleft"))
    return bloque


def run(frames: int = 300) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    for n in N:
        out.append(medir(f"crear Bloque con {n} hijos", lambda n=n: _bloque(n),
                         frames=20, warmup=2))

        bloque = _bloque(n)
        lista = lista_dibujo(app)
        lista.append(bloque)
        app.draw_optimized(lista)

        out.append(medir(f"dibujar Bloque({n}), sin scroll",
                         lambda: app.draw_optimized(lista), frames=frames))
        out.append(medir(f"dibujar Bloque({n}) forzado (always)",
                         lambda: app.draw_always(lista), frames=frames))

        bloque.on_wheel(-40)
        out.append(medir(f"scroll + update + draw Bloque({n})",
                         lambda: (bloque.on_wheel(-40), bloque.update(),
                                  _dibujar_forzado(app, bloque)),
                         frames=frames))
        out.append(medir(f"move_objs de Bloque({n}) (tras scroll)",
                         lambda: (bloque.scroll_class.rodar(-15), bloque.move_objs()),
                         frames=frames))

        lista.clear()
        app.redraw = True

    cerrar_app(app)
    return out


def _dibujar_forzado(app, bloque) -> None:
    bloque.redraw = 2
    with sin_presentacion():
        app.draw_optimized(lista_dibujo(app))


def main() -> None:
    print(tabla(run(), "Bloque"))


if __name__ == "__main__":
    main()
