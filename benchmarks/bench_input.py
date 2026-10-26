"""Benchmark de `Input`.

Aquí el sospechoso es OPT-04: `update_pressed_keys()` llama a `draw_surf()`
en cada frame, y `draw_surf()` vuelve a renderizar el texto entero. Con
`draw_mode='always'` eso es un re-render por `Input` y por frame aunque nadie
escriba. El benchmark separa "dibujar" de "teclear".
"""
from __future__ import annotations

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    sin_presentacion, tabla)
from Utilidades_pygame import Input

N = (1, 10, 50)
TEXTO = "hola mundo"


def _inputs(n: int, texto: str = "") -> list[Input]:
    creados = []
    for i in range(n):
        inp = Input((20 + (i % 4) * 190, 20 + (i // 4) * 40), 16, None,
                    text_value="escribe aquí", width=180, height=28)
        if texto:
            inp.set(texto)
        creados.append(inp)
    return creados


def run(frames: int = 300) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    for n in N:
        inputs = _inputs(n)
        lista = lista_dibujo(app)
        lista.extend(inputs)

        out.append(medir(f"crear {n} Input", lambda n=n: _inputs(n),
                         frames=30, warmup=2))
        out.append(medir(f"dibujar {n} Input, always (re-render por frame)",
                         lambda: app.draw_always(lista), frames=frames))
        out.append(medir(f"dibujar {n} Input, always, sin presentar",
                         lambda: _siempre(app, lista), frames=frames))
        out.append(medir(f"update de {n} Input (dt=1/60)",
                         lambda: [x.update(dt=1 / 60) for x in inputs], frames=frames))

        lista.clear()
        app.redraw = True

    # ---- teclear: 20 letras en un Input --------------------------------
    inp = _inputs(1, TEXTO)[0]
    lista_dibujo(app).append(inp)
    out.append(medir("escribir 1 letra (add_letter)",
                     lambda: (inp.add_letter("a"), inp.clear()),
                     frames=100, warmup=2))
    out.append(medir("escribir 20 letras seguidas",
                     lambda: _teclear(inp, 20), frames=50, warmup=2))
    out.append(medir("borrar 20 letras seguidas",
                     lambda: _teclear(inp, 20, borrar=True), frames=50, warmup=2))
    out.append(medir("dibujar 1 Input (always)",
                     lambda: app.draw_always(lista_dibujo(app)), frames=frames))

    cerrar_app(app)
    return out


def _siempre(app, lista) -> None:
    with sin_presentacion():
        app.draw_always(lista)


def _teclear(inp: Input, n: int, borrar: bool = False) -> None:
    inp.clear()
    if borrar:
        inp.set("x" * n)
        for _ in range(n):
            inp.del_letter()
    else:
        for _ in range(n):
            inp.add_letter("a")


def main() -> None:
    print(tabla(run(), "Input"))


if __name__ == "__main__":
    main()
