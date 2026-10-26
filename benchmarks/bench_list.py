"""Benchmark de `List` — el widget de la lista larga.

Tu caso de uso es "una lista con muchísimos elementos a 60 FPS", así que el
punto interesante no es dibujar, es **crear** y **desplazar**: `List` guarda
solo las palabras y `draw_surf` renderiza al vuelo las visibles, así que crear
es barato y el millón de elementos es viable. Aquí se mide cada pieza por
separado, y con la pendiente de RSS se estima la memoria por elemento y el
coste fijo del widget.

`BENCH_BIG=1` añade 100 000 elementos (tarda y come RAM a propósito).
"""
from __future__ import annotations

import os

from common import (Muestra, cerrar_app, lista_dibujo, medir,
                    memoria_por_unidad, nueva_app, sin_presentacion, tabla)
from Utilidades_pygame import List

N = (10, 100, 1000)
ELEMENTOS = [f"elemento {i}" for i in range(100_000)]


def _lista(n: int, smooth: bool = False) -> List:
    lst = List((300, 400), (20, 20), ELEMENTOS[:n], text_size=16, font=None,
               smoothscroll=smooth, separation=2)
    lst.hover = True
    return lst


def run(frames: int = 300) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    for n in N:
        out.append(medir(f"crear List con {n} elementos", lambda n=n: _lista(n),
                         frames=10, warmup=1))

        lst = _lista(n)
        lista = lista_dibujo(app)
        lista.append(lst)
        app.draw_optimized(lista)

        out.append(medir(f"dibujar List({n}), sin cambios",
                         lambda: app.draw_optimized(lista), frames=frames))
        out.append(medir(f"dibujar List({n}), sucia (blit de lo visible)",
                         lambda: _dibujar_sucia(app, lst), frames=frames))
        out.append(medir(f"scroll List({n}) (on_wheel -15)",
                         lambda: lst.on_wheel(-15), frames=frames))
        out.append(medir(f"select List({n})",
                         lambda: lst.select(n // 2), frames=100))
        out.append(medir(f"append a List({n}) + regenerar alto",
                         lambda: lst.append("nuevo"), frames=50))

        lista.clear()
        del lst
        app.redraw = True

    # ---- smoothscroll: update por frame --------------------------------
    lst = _lista(1000, smooth=True)
    lista_dibujo(app).append(lst)
    out.append(medir("update List(1000) con smoothscroll (dt=1/60)",
                     lambda: lst.update(dt=1 / 60), frames=frames))
    out.append(medir("scroll + draw List(1000) smoothscroll",
                     lambda: (lst.on_wheel(-15), lst.update(dt=1 / 60),
                              _dibujar_sucia(app, lst)),
                     frames=frames))

    # ---- memoria -------------------------------------------------------
    # List guarda solo las palabras (draw_surf renderiza lo visible), así que
    # lo que se mide es el coste marginal de una fila más y el del widget vacío.
    por_elemento, metodo = memoria_por_unidad(_lista, n=500)
    fijo, _ = memoria_por_unidad(lambda k: [_lista(0) for _ in range(k)], n=20)
    out.append(Muestra(
        nombre="List: bytes por elemento",
        n=500, media=por_elemento / 1024, mediana=por_elemento / 1024,
        p95=por_elemento / 1024, minimo=por_elemento / 1024,
        maximo=por_elemento / 1024,
        extra={"bytes": por_elemento, "metodo": metodo,
               "estimado_1M": por_elemento * 1_000_000 / 1024 ** 3},
        unidad="KiB/elem",
    ))
    out.append(Muestra(
        nombre="List vacía (widget + superficie 300x400)",
        n=20, media=fijo / 1024, mediana=fijo / 1024, p95=fijo / 1024,
        minimo=fijo / 1024, maximo=fijo / 1024,
        extra={"bytes": fijo, "metodo": metodo},
        unidad="KiB/lista",
    ))

    if os.environ.get("BENCH_BIG"):
        out.append(medir("crear List con 100 000 elementos",
                         lambda: _lista(100_000), frames=1, warmup=0))

    cerrar_app(app)
    return out


def _dibujar_sucia(app, lst) -> None:
    lst.redraw = max(lst.redraw, 2)
    with sin_presentacion():
        app.draw_optimized(lista_dibujo(app))


def main() -> None:
    muestras = run()
    print(tabla(muestras, "List"))
    memoria = next((m for m in muestras if "estimado_1M" in m.extra), None)
    fijo = next((m for m in muestras if "KiB/lista" == m.unidad), None)
    if memoria is None:
        return
    e = memoria.extra
    print(f"\nMemoria de List: {e['bytes'] / 1024:.2f} KiB por elemento "
          f"({e['metodo']}); 1 000 000 de elementos ≈ {e['estimado_1M']:.1f} GiB "
          f"más el widget.", flush=True)
    if fijo is not None:
        print(f"  Widget vacío de 300x400: {fijo.extra['bytes'] / 1024:.0f} KiB "
              f"(la superficie de dibujo es w*h*4 = 480 KiB).", flush=True)


if __name__ == "__main__":
    main()
