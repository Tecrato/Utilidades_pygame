"""Benchmark de `Text` — el widget que más se repite en cualquier UI.

Mide tres cosas distintas, porque cuestan muy distinto:

1. **Crear** el widget (una vez): lo que paga el arranque de la pantalla.
2. **Dibujar en reposo** (nada cambió): lo que paga un frame normal.
3. **Dibujar con todos sucios**: el techo, lo que paga `draw_mode='always'`.

Además mide por separado `font.size()` y `font.render()`, que es el núcleo de
OPT-03: medir texto no debería necesitar crear una superficie.
"""
from __future__ import annotations

import pygame as pag

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    sin_presentacion, tabla)
from Utilidades_pygame import Text

N = (10, 50, 200, 1000)
TEXTO = "texto de interfaz"
PARRAFO = " ".join(["palabra"] * 200)


def _textos(n: int) -> list[Text]:
    columnas = 8
    return [
        Text(f"{TEXTO} {i}", 16, pos=(60 + (i % columnas) * 90, 30 + (i // columnas) * 26))
        for i in range(n)
    ]


def _texto_parrafo() -> Text:
    return Text(PARRAFO, 16, pos=(20, 20), max_width=300)


def run(frames: int = 300) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    # ---- creación ------------------------------------------------------
    for n in N:
        textos = _textos(n)
        del textos
        out.append(medir(f"crear {n} Text (1 línea)", lambda n=n: _textos(n),
                         frames=max(5, frames // 15), warmup=2))

    out.append(medir("crear Text (párrafo 200 palabras)", _texto_parrafo,
                     frames=max(5, frames // 15), warmup=2))
    parrafo = _texto_parrafo()
    out.append(medir("cambiar texto de un párrafo",
                     lambda: setattr(parrafo, "text", PARRAFO[::-1]),
                     frames=max(10, frames // 5), warmup=2))

    # ---- dibujo --------------------------------------------------------
    for n in (50, 200, 1000):
        textos = _textos(n)
        lista = lista_dibujo(app)
        lista.extend(textos)
        app.draw_optimized(lista)                       # primer frame: todo sucio

        out.append(medir(f"dibujar {n} Text, nada sucio (optimized)",
                         lambda: app.draw_optimized(lista), frames=frames))

        out.append(medir(f"dibujar {n} Text, 1 sucio (optimized)",
                         lambda: (setattr(textos[0], "pos", (60, 300)),
                                  app.draw_optimized(lista)),
                         frames=frames))

        out.append(medir(f"dibujar {n} Text, todos sucios (always)",
                         lambda: app.draw_always(lista), frames=frames))

        out.append(medir(f"dibujar {n} Text, todos sucios, sin presentar",
                         lambda: _dibujar_todos(app, textos, lista),
                         frames=frames))

        lista.clear()
        textos.clear()
        app.redraw = True

    # ---- OPT-03: medir vs renderizar -----------------------------------
    muestras = [PARRAFO[::-1][: 20 + i * 40] for i in range(100)]
    fuente = pag.font.Font(None, 16)
    out.append(medir("medir 100 cadenas con font.size()",
                     lambda: [fuente.size(t) for t in muestras], frames=frames))
    out.append(medir("medir 100 cadenas con font.render()",
                     lambda: [fuente.render(t, True, "white").get_width() for t in muestras],
                     frames=frames))

    cerrar_app(app)
    return out


def _dibujar_todos(app, textos, lista) -> None:
    for t in textos:
        t.redraw = 2
    with sin_presentacion():
        app.draw_optimized(lista)


def main() -> None:
    print(tabla(run(), "Text"))


if __name__ == "__main__":
    main()
