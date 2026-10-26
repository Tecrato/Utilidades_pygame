"""Benchmark combinado: el bucle de `Base_class`, no un widget suelto.

Aquí se mide lo que de verdad decide si llegas a 60 FPS:

1. **Escena mixta** (`Text` + `Button` + `Input` + `List` + `Bloque` + `Image`)
   con 10, 50 y 200 widgets, en `optimized` y en `always`.
2. **Escalado del bucle**: cuánto cuesta un frame *sin nada sucio* con 1 000,
   10 000, 100 000 y 1 000 000 de objetos. Para eso se usan widgets falsos
   (una clase con `__slots__` que solo implementa el contrato), porque crear
   un millón de `Text` de verdad no cabe en RAM ni en tiempo. Esto responde a
   la pregunta "¿aguanto 1 M de objetos a 60 FPS?" sin confundir el coste del
   bucle con el coste de construir textos.
3. **Cascada de dirty rects**: una rejilla de `Text`, se mueve uno, y se
   compara `optimized` con `always`.
4. **Perfil** de 10 frames con `cProfile` para ver quién se lleva el tiempo.

`BENCH_BIG=1` añade el millón al punto 2 (reserva ~1 GB y unos segundos).
"""
from __future__ import annotations

import os
from pathlib import Path

import pygame as pag

from common import (Muestra, cerrar_app, lista_dibujo, medir, nueva_app,
                    perfilar, resumen_perfil, sin_presentacion, tabla)
from Utilidades_pygame import Button, Image, Input, List, Text, Bloque

ESCALAS = (10, 50, 200)
PERFIL = Path(__file__).with_name("bench_app.prof")


class Falso:
    """Widget mínimo: lo justo para que `draw_optimized` lo recorra.

    Sirve para medir el **bucle**, no el widget: un frame limpio lo único que
    hace es una llamada a `collide()` y otra a `draw()` por objeto.
    """
    __slots__ = ("redraw", "visible", "rect")

    def __init__(self) -> None:
        self.redraw = 0
        self.visible = True
        self.rect = pag.Rect(0, 0, 1, 1)

    def collide(self, rect) -> bool:
        return True

    def draw(self, surface):
        return []


def _escena(n: int, con_inputs: bool = True) -> list:
    """Mezcla realista de widgets, repartidos por la pantalla."""
    widgets: list = []
    for i in range(n):
        tipo = i % 6
        if tipo == 2 and not con_inputs:
            tipo = 0
        x = 40 + (i % 12) * 60
        y = 30 + (i // 12 % 10) * 50
        if tipo == 0:
            widgets.append(Text(f"etiqueta {i}", 14, pos=(x, y)))
        elif tipo == 1:
            widgets.append(Button(f"ok {i}", 14, None, pos=(x, y), padding=(6, 3)))
        elif tipo == 2:
            widgets.append(Input((x, y), 14, None, width=90, height=24))
        elif tipo == 3:
            widgets.append(Text(f"párrafo {i} ".ljust(60, "x"), 14, pos=(x, y),
                                max_width=120))
        elif tipo == 4:
            widgets.append(Image(_icono(), (x, y)))
        else:
            lista = List((110, 120), (x, y), [f"item {j}" for j in range(8)],
                         text_size=12, font=None)
            widgets.append(lista)
    return widgets


def _icono() -> pag.Surface:
    surf = pag.Surface((32, 32))
    surf.fill((80, 120, 200))
    pag.draw.circle(surf, "white", (16, 16), 10)
    return surf


def _malla(n: int) -> list[Text]:
    columnas = 25
    return [
        Text(f"t{i}", 14, pos=(20 + (i % columnas) * 30, 20 + (i // columnas) * 30))
        for i in range(n)
    ]


def run(frames: int = 300) -> list[Muestra]:
    app = nueva_app()
    out: list[Muestra] = []

    # ---- 1. escena mixta ------------------------------------------------
    for n in ESCALAS:
        widgets = _escena(n)
        lista = lista_dibujo(app)
        lista.extend(widgets)
        app.draw_optimized(lista)

        out.append(medir(f"escena mixta {n} widgets, nada sucio",
                         lambda: app.draw_optimized(lista), frames=frames))
        out.append(medir(f"escena mixta {n} widgets, 1 sucio",
                         lambda: (setattr(widgets[0], "pos", (41, 31)),
                                  app.draw_optimized(lista)),
                         frames=frames))
        out.append(medir(f"escena mixta {n} widgets, always",
                         lambda: app.draw_always(lista), frames=frames))

        lista.clear()
        widgets.clear()
        app.redraw = True

    # ---- 1b. Input se re-marca sucio al dibujarse y dispara la cascada ---
    # `Input.draw` llama a `update_pressed_keys` → `draw_surf`, que deja
    # `redraw = 1`. Al salir del widget ya está limpio otra vez, así que el
    # frame *parece* limpio pero por dentro ha recorrido toda la lista.
    for n in (200,):
        for con_inputs in (False, True):
            widgets = _escena(n, con_inputs=con_inputs)
            lista = lista_dibujo(app)
            lista.extend(widgets)
            for _ in range(3):
                app.draw_optimized(lista)
            etiqueta = "con Input" if con_inputs else "sin Input"
            colisiones = contar_colisiones(app, lista)
            out.append(Muestra(
                nombre=f"escena {n} {etiqueta}: Base.collide por frame",
                n=1, media=float(colisiones), mediana=float(colisiones),
                p95=float(colisiones), minimo=float(colisiones), maximo=float(colisiones),
                extra={"colisiones": colisiones},
                unidad="cuenta",
            ))
            out.append(medir(f"escena {n} {etiqueta}, nada sucio",
                             lambda: app.draw_optimized(lista), frames=frames))
            lista.clear()
            widgets.clear()
            app.redraw = True

    # ---- 2. escalado del bucle con objetos falsos -----------------------
    escalas = (1_000, 10_000, 100_000)
    if os.environ.get("BENCH_BIG"):
        escalas += (1_000_000,)
    for n in escalas:
        falsos = [Falso() for _ in range(n)]
        lista = lista_dibujo(app)
        lista.extend(falsos)
        repeticiones = 60 if n <= 10_000 else 20 if n <= 100_000 else 5
        with sin_presentacion():
            out.append(medir(f"frame limpio con {n:_} objetos".replace("_", " "),
                             lambda: app.draw_optimized(lista),
                             frames=repeticiones, warmup=3))
            out.append(medir(f"frame limpio con {n:_} objetos, sin fill".replace("_", " "),
                             lambda: _sin_fill(app, lista),
                             frames=repeticiones, warmup=3))
        lista.clear()
        del falsos
        app.redraw = True

    # ---- 3. cascada de dirty rects -------------------------------------
    for n in (200, 1000):
        textos = _malla(n)
        lista = lista_dibujo(app)
        lista.extend(textos)
        app.draw_optimized(lista)

        out.append(medir(f"rejilla {n} Text: mover 1, optimized",
                         lambda: (setattr(textos[0], "pos", (25, 25)),
                                  app.draw_optimized(lista)),
                         frames=frames))
        out.append(medir(f"rejilla {n} Text: mover 1, always",
                         lambda: app.draw_always(lista), frames=frames))

        lista.clear()
        textos.clear()
        app.redraw = True

    # ---- 4. update_general ---------------------------------------------
    for n in ESCALAS:
        textos = _malla(n)
        app.lists_screens["main"]["update"] = list(textos)
        out.append(medir(f"update_general con {n} widgets",
                         lambda: app.update_general(), frames=frames))
        app.lists_screens["main"]["update"] = []

    # ---- 5. perfil ------------------------------------------------------
    textos = _malla(200)
    lista = lista_dibujo(app)
    lista.extend(textos)
    app.draw_optimized(lista)
    perfilar(lambda: (setattr(textos[0], "pos", (25, 25)),
                      app.draw_optimized(lista)),
             str(PERFIL), frames=30)

    cerrar_app(app)
    return out


def contar_colisiones(app, lista) -> int:
    """Cuenta las llamadas a `Base.collide` de un frame (una pasada real)."""
    from Utilidades_pygame.obj_Base import Base
    original = Base.collide
    n = 0

    def contador(self, rect) -> bool:
        nonlocal n
        n += 1
        return original(self, rect)

    Base.collide = contador
    try:
        app.draw_optimized(lista)
    finally:
        Base.collide = original
    return n


def _sin_fill(app, lista) -> None:
    """Igual que `draw_optimized` pero sin el `fill` de toda la ventana."""
    app.draw_background = False
    try:
        app.draw_optimized(lista)
    finally:
        app.draw_background = True


def main() -> None:
    muestras = run()
    print(tabla(muestras, "App (bucle completo)"))
    print("\nPerfil (top 12 por tottime):")
    print(resumen_perfil(str(PERFIL), 12))


if __name__ == "__main__":
    main()
