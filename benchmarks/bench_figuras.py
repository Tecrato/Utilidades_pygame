"""Benchmark de `PoligonoRegular`, `PoligonoIrregular` y `Engranaje`.

Mide crear figuras, regenerar vértices al girar y dibujar N figuras.

Este archivo nació documentando el BUG-36 (los atributos con doble guion bajo
en `BasePolygon` no eran los que leían las subclases). Ya está arreglado con
la opción 2: la base mantiene `__pos`/`__figure` privados y las subclases
usan los getters públicos (`self.pos`, `self.radio`, `self.angle`) y los huecos
`_generate()` / `_set_figura()` / `_update_bounding_box()`.
El preflight de `run()` se queda por si algún día vuelve el manglado.
"""
from __future__ import annotations

import pygame as pag

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    sin_presentacion, tabla)
from Utilidades_pygame import Engranaje, PoligonoIrregular, PoligonoRegular

N = (10, 100, 1000)


def _poligonos(n: int) -> list[PoligonoRegular]:
    return [
        PoligonoRegular(pos=(60 + (i % 20) * 35, 60 + (i // 20) * 35),
                        lados=5, radio=14)
        for i in range(n)
    ]


def run(frames: int = 300) -> list[Muestra]:
    # Preflight: si esto revienta, el resto del archivo no tiene sentido.
    try:
        PoligonoRegular(pos=(10, 10), lados=4, radio=5)
        Engranaje(pos=(10, 10), dientes=8, size_diente=2, radio=5)
        PoligonoIrregular(puntos=[(0, 1), (90, 1), (180, 1)], pos=(10, 10), radio=5)
    except AttributeError as exc:
        raise RuntimeError(
            "figuras rotas por name mangling (BUG-36): " + str(exc)
        ) from exc

    app = nueva_app()
    out: list[Muestra] = []

    for n in N:
        out.append(medir(f"crear {n} PoligonoRegular", lambda n=n: _poligonos(n),
                         frames=20, warmup=2))

        figuras = _poligonos(n)
        lista = lista_dibujo(app)
        lista.extend(figuras)
        app.draw_optimized(lista)

        out.append(medir(f"dibujar {n} PoligonoRegular (nada sucio)",
                         lambda: app.draw_optimized(lista), frames=frames))
        out.append(medir(f"dibujar {n} PoligonoRegular (todas sucias)",
                         lambda: app.draw_always(lista), frames=frames))
        out.append(medir(f"girar {n} PoligonoRegular (regenera vértices)",
                         lambda: _girar(figuras), frames=max(20, frames // 3)))

        lista.clear()
        app.redraw = True

    # ---- Engranaje: 4 vértices por diente, más caro de generar ----------
    engranajes = [Engranaje(pos=(60 + (i % 10) * 70, 60 + (i // 10) * 70),
                            dientes=12, size_diente=4, radio=20)
                  for i in range(100)]
    out.append(medir("crear 100 Engranaje", lambda: [
        Engranaje(pos=(60, 60), dientes=12, size_diente=4, radio=20)
        for _ in range(100)], frames=10, warmup=1))
    lista = lista_dibujo(app)
    lista.extend(engranajes)
    app.draw_optimized(lista)
    out.append(medir("dibujar 100 Engranaje (nada sucio)",
                     lambda: app.draw_optimized(lista), frames=frames))
    out.append(medir("dibujar 100 Engranaje (todos sucios)",
                     lambda: app.draw_always(lista), frames=frames))

    cerrar_app(app)
    return out


def _girar(figuras) -> None:
    for f in figuras:
        f.angle = (f.angle + 3) % 360


def main() -> None:
    print(tabla(run(), "Figuras"))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"NO EJECUTADO — {exc}", flush=True)
