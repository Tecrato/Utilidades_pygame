"""Benchmark de `Image` — escalar y girar.

El punto que te preocupa: no hay forma barata de cambiar tamaño o ángulo. Cada
`size = ...` o `angle = ...` llama a `generate_img()`, que **vuelve a escalar y
rotar desde la imagen original**, así que un `angle += 1` por frame cuesta una
rotación completa (y a veces también un `smoothscale`) por frame.

Aquí se mide:
- escala sola, rotación sola, y las dos;
- el caso real de animar el ángulo o el tamaño cada frame;
- una imagen pequeña (icono) frente a una grande (fondo), porque el coste
  crece con los píxeles.
"""
from __future__ import annotations

import pygame as pag

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    sin_presentacion, tabla)
from Utilidades_pygame import Image


def _fondo(w: int, h: int) -> pag.Surface:
    """Superficie opaca con un degradado, para que no sea un caso degenerado."""
    surf = pag.Surface((w, h))
    for y in range(h):
        surf.fill((y * 255 // max(1, h - 1), 80, 255 - y * 255 // max(1, h - 1)),
                  (0, y, w, 1))
    return surf


def run(frames: int = 200) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    grande = _fondo(800, 600)
    icono = _fondo(64, 64)

    # ---- construcción ---------------------------------------------------
    out.append(medir("crear Image 800x600 sin escalar",
                     lambda: Image(grande, (400, 300)), frames=50, warmup=2))
    out.append(medir("crear Image 800x600 → 400x300",
                     lambda: Image(grande, (400, 300), size=(400, 300)), frames=50, warmup=2))
    out.append(medir("crear Image 800x600 → 400x300 girada 30°",
                     lambda: Image(grande, (400, 300), size=(400, 300), angle=30),
                     frames=30, warmup=2))

    # ---- cambios de propiedad ------------------------------------------
    img = Image(grande, (400, 300))
    out.append(medir("Image grande: size = (400, 300)",
                     lambda: setattr(img, "size", (400, 300)),
                     frames=frames, warmup=5))
    # el setter corta si el tamaño no cambió: alternar dos tamaños lo fuerza
    img2 = Image(grande, (400, 300))
    out.append(medir("Image grande: alternar size 400x300 / 300x400",
                     _alternar(img2, "size", [(400, 300), (300, 400)]),
                     frames=frames, warmup=5))
    img3 = Image(icono, (400, 300))
    out.append(medir("Image icono 64x64: alternar size 32x32 / 48x48",
                     _alternar(img3, "size", [(32, 32), (48, 48)]),
                     frames=frames, warmup=5))

    img4 = Image(grande, (400, 300))
    out.append(medir("Image grande: alternar angle 45° / 0°",
                     _alternar(img4, "angle", [45, 0]),
                     frames=frames, warmup=5))
    img5 = Image(icono, (400, 300))
    out.append(medir("Image icono: alternar angle 45° / 0°",
                     _alternar(img5, "angle", [45, 0]),
                     frames=frames, warmup=5))

    # ---- el caso real: animar cada frame --------------------------------
    img6 = Image(grande, (400, 300), size=(400, 300))
    out.append(medir("animar ángulo de imagen grande (un frame)",
                     lambda: _girar(img6, 3), frames=frames, warmup=5))
    img7 = Image(icono, (400, 300))
    out.append(medir("animar ángulo de icono (un frame)",
                     lambda: _girar(img7, 3), frames=frames, warmup=5))

    # ---- dibujo ---------------------------------------------------------
    imagenes = [Image(icono, (60 + (i % 8) * 90, 60 + (i // 8) * 60)) for i in range(100)]
    lista = lista_dibujo(app)
    lista.extend(imagenes)
    app.draw_optimized(lista)
    out.append(medir("dibujar 100 Image (nada sucio)",
                     lambda: app.draw_optimized(lista), frames=frames))
    out.append(medir("dibujar 100 Image (todos sucios)",
                     lambda: app.draw_always(lista), frames=frames))

    lista.clear()
    imagenes.clear()
    app.redraw = True

    # ---- dibujo de una imagen grande -----------------------------------
    img8 = Image(grande, (400, 300))
    lista.append(img8)
    app.draw_optimized(lista)
    out.append(medir("dibujar Image 800x600 (nada sucio)",
                     lambda: app.draw_optimized(lista), frames=frames))
    out.append(medir("dibujar Image 800x600 (sucia)",
                     lambda: _dibujar_sucia(app, img8), frames=frames))

    cerrar_app(app)
    return out


def _alternar(obj, prop: str, valores):
    """Devuelve una función que va rotando los valores (ida y vuelta).

    No vale con `valores.reverse()` dentro del lambda: la lista se recrea en
    cada llamada, así que siempre se asignaría el mismo valor y el setter
    cortaría por "no cambió nada".
    """
    estado = {"i": 0}

    def paso() -> None:
        setattr(obj, prop, valores[estado["i"]])
        estado["i"] = (estado["i"] + 1) % len(valores)

    return paso


def _girar(img: Image, grados: int) -> None:
    img.angle = (img.angle + grados) % 360


def _dibujar_sucia(app, img) -> None:
    img.redraw = 2
    with sin_presentacion():
        app.draw_optimized(lista_dibujo(app))


def main() -> None:
    print(tabla(run(), "Image"))


if __name__ == "__main__":
    main()
