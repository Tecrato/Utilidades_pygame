"""Benchmark de `Button`.

`Button` hereda de `Text`, así que su coste de creación y dibujado es el de un
`Text` con fondo y borde. Lo propio de `Button` es el cambio de `hover`, que
toca colores (`color`, `color_rect`, `border_color`) y esos setters pueden
volver a construir el texto. Eso es lo que se mide aparte.
"""
from __future__ import annotations

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    sin_presentacion, tabla)
from Utilidades_pygame import Button

N = (10, 50, 200)


def _botones(n: int) -> list[Button]:
    columnas = 6
    return [
        Button(f"Botón {i}", 16, None,
               pos=(80 + (i % columnas) * 120, 40 + (i // columnas) * 50))
        for i in range(n)
    ]


def run(frames: int = 300) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    for n in N:
        botones = _botones(n)
        out.append(medir(f"crear {n} Button", lambda n=n: _botones(n),
                         frames=30, warmup=2))

        lista = lista_dibujo(app)
        lista.extend(botones)
        app.draw_optimized(lista)

        out.append(medir(f"dibujar {n} Button, nada sucio",
                         lambda: app.draw_optimized(lista), frames=frames))
        out.append(medir(f"dibujar {n} Button, todos sucios",
                         lambda: app.draw_always(lista), frames=frames))
        out.append(medir(f"hover on/off de {n} Button",
                         lambda: _alternar_hover(botones), frames=max(20, frames // 3)))

        lista.clear()
        app.redraw = True

    # ---- hover de un solo botón, aislado -------------------------------
    boton = _botones(1)[0]
    lista_dibujo(app).append(boton)
    app.draw_optimized(lista_dibujo(app))
    out.append(medir("hover de 1 Button (solo cambio de estado)",
                     lambda: _alternar_hover([boton]), frames=frames))
    out.append(medir("dibujar 1 Button tras hover",
                     lambda: (setattr(boton, "hover", True), _dibujar(app)),
                     frames=frames))

    cerrar_app(app)
    return out


def _alternar_hover(botones) -> None:
    for b in botones:
        b.hover = not b.hover


def _dibujar(app) -> None:
    with sin_presentacion():
        app.draw_optimized(lista_dibujo(app))


def main() -> None:
    print(tabla(run(), "Button"))


if __name__ == "__main__":
    main()
