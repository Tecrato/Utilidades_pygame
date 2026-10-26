"""Benchmark de `Particles` y `Particle`.

No son widgets de UI, pero viven en el mismo bucle y suelen ser el otro techo
de un juego a 60 FPS. Se mide el ciclo completo (update + draw) con 1 000
partículas, y por separado cada mitad para saber cuál pesa.
"""
from __future__ import annotations

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    sin_presentacion, tabla)
from Utilidades_pygame import Particles

N = (10, 100, 1000)


def _particulas(n: int) -> Particles:
    p = Particles((400, 300), radio=4, velocity=60, auto_spawn=False,
                  max_particles=n, spawn_count=n)
    p.spawn()
    return p


def run(frames: int = 300) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    for n in N:
        out.append(medir(f"crear {n} partículas", lambda n=n: _particulas(n),
                         frames=10, warmup=1))

        p = _particulas(n)
        lista = lista_dibujo(app)
        lista.append(p)
        app.draw_optimized(lista)

        out.append(medir(f"update {n} partículas (dt=1/60)",
                         lambda: p.update(dt=1 / 60), frames=frames))
        out.append(medir(f"draw {n} partículas",
                         lambda: _dibujar(app, p), frames=frames))
        out.append(medir(f"update + draw {n} partículas",
                         lambda: (p.update(dt=1 / 60), _dibujar(app, p)),
                         frames=frames))

        lista.clear()
        app.redraw = True

    cerrar_app(app)
    return out


def _dibujar(app, particulas) -> None:
    with sin_presentacion():
        app.draw_always(lista_dibujo(app))


def main() -> None:
    print(tabla(run(), "Particles"))


if __name__ == "__main__":
    main()
