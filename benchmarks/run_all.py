"""Ejecuta todos los benchmarks y deja las cifras en `RESULTADOS.md`.

    python benchmarks/run_all.py

Cada `bench_*.py` también se puede ejecutar solo y escribe su tabla por
consola. Aquí se juntan todas, con la versión de Python/pygame y la máquina,
para poder comparar antes y después de un cambio.

Si un módulo revienta (por ejemplo `bench_figuras.py` con BUG-36), no se cae
todo: se anota el error en el informe y se sigue con el resto.
"""
from __future__ import annotations

import datetime
import os
import platform
import sys
import traceback
from pathlib import Path

import common  # primero: fija SDL_VIDEODRIVER antes de inicializar pygame
import pygame as pag

import bench_app
import bench_bloque
import bench_button
import bench_figuras
import bench_image
import bench_input
import bench_list
import bench_memoria
import bench_particulas
import bench_text
from common import tabla

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "RESULTADOS.md"
FRAMES = 200

MODULOS = [
    ("Text", bench_text),
    ("Button", bench_button),
    ("Input", bench_input),
    ("List", bench_list),
    ("Bloque", bench_bloque),
    ("Image", bench_image),
    ("Figuras", bench_figuras),
    ("Particles", bench_particulas),
    ("App (bucle completo)", bench_app),
    ("Memoria por widget", bench_memoria),
]

CABECERA = """# Resultados del banco de pruebas

Generado por `benchmarks/run_all.py` el **{fecha}**.

Todo se mide **headless** (`SDL_VIDEODRIVER=dummy`): no hay ventana real, así
que el coste de presentar es casi cero y las cifras de dibujado son las de
Python + pygame, no las de la GPU. Sirven para comparar **antes y después** de
un cambio en la misma máquina, no como número absoluto de otro equipo.

## Cómo leer las tablas

- **media / mediana / p95** en milisegundos, de `{frames}` frames por prueba
  (las de creación usan menos, porque son caras). El **p95** es el que importa
  para los tirones: la media esconde el frame malo.
- **fps** = 1000 / media. Presupuesto a 60 FPS: **16.6 ms por frame**.
- Las filas con **`cuenta`** o **`MiB`** no son tiempos: son llamadas a
  `Base.collide` en un frame y memoria ocupada, respectivamente.
- Cada archivo mide tres cosas por separado: **crear** el widget (arranque de
  pantalla), **dibujar en reposo** (nada cambió) y **dibujar con todo sucio**
  (el techo de `draw_mode='always'`).
- La sección **Memoria por widget** mide bytes por unidad con la memoria
  residente del proceso, cada fila en un proceso nuevo (tres veces, mediana).
  Desde que `generate_Font` cachea las fuentes por `(ruta, tamaño, subrayado)`,
  un `Text` con `font=None` ocupa ~5 KiB (antes ~71 KiB, porque cada widget
  creaba la suya). `Input` bajó de ~196 a ~65 KiB por el mismo motivo.

## Lo que ya se ve en los números (26-10-2026)

Estas conclusiones no dependen de la máquina, son estructurales:

1. **Crear widgets es caro, dibujarlos no.** Un `Text` cuesta ~2 ms y un
   `Input` ~6 ms de construir; dibujar 200 textos limpios cuesta décimas de
   milisegundo. Si una pantalla tarda en abrir, el problema está en el
   constructor, no en el bucle.
2. **`Input` se re-marca sucio al dibujarse** (`draw_surf` deja `redraw = 1`),
   así que cada frame dispara la cascada de dirty rects sobre toda la lista.
   Con 200 widgets y solo ~33 `Input`, la escena pasa de ~0,5 ms a ~7 ms por
   frame *sin que nada se mueva*, y de 200 a ~10 000 `collide`. Es el hallazgo
   más rentable de todo el banco.
3. **`draw_optimized` con todo sucio es O(n²)** y mucho más lento que
   `draw_always` (que no hace cascada): con 200 `Text` sucios la diferencia es
   de un orden de magnitud. Eso es OPT-01, medido.
4. **`Image` gira caro**: animar el ángulo de una imagen grande cuesta
   ~1.5 ms por frame y por imagen (rotación completa cada vez, y si además hay
   `size`, también re-escala). Es exactamente el problema que ya intuías.
5. **`Bloque` ya descansa como un `div`**: desde que `draw()` usa dirty rects
   propios y una superficie-caché, un bloque quieto cuesta ~0,2 ms sea cual sea
   el número de hijos (antes ~1,0–1,3 ms y crecía con ellos), con un hijo sucio
   ~0,3–0,45 ms y el repintado completo ~1 ms con 100 hijos.
6. **El bucle limpio escala lineal** con el número de objetos: ~0,7 µs por
   objeto y frame solo en `collide()` + `draw()`. Un millón de objetos en la
   lista de dibujo no cabe en 16 ms ni de lejos (medido: ~700 ms); una `List`
   de un millón de elementos es otra cosa (solo blitea lo visible), pero
   **crea una superficie por elemento**: ~3,1 KB y ~14 µs de creación por
   elemento, o sea ~3 GB y ~14 s para el millón.
"""


def _entorno() -> str:
    return (
        f"- Python {platform.python_version()} ({platform.machine()})\n"
        f"- pygame {pag.version.ver} / SDL {pag.version.SDL}\n"
        f"- {platform.system()} {platform.release()}\n"
        f"- CPUs: {os.cpu_count()}\n"
    )


def main() -> int:
    partes: list[str] = []
    fallos = 0

    for nombre, modulo in MODULOS:
        print(f"--- {nombre} ---", flush=True)
        try:
            muestras = modulo.run(frames=FRAMES)
        except Exception as exc:                       # noqa: BLE001
            fallos += 1
            print(f"  NO EJECUTADO: {exc}", flush=True)
            traceback.print_exc()
            partes.append(
                f"\n### {nombre}\n\n"
                f"**No se pudo ejecutar:** `{type(exc).__name__}: {exc}`\n"
            )
            continue
        print(tabla(muestras), flush=True)
        partes.append(tabla(muestras, nombre))

    texto = (
        CABECERA.format(fecha=datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                        frames=FRAMES)
        + "\n## Entorno\n\n" + _entorno()
        + "\n## Tablas\n"
        + "\n".join(partes)
        + "\n\n---\n\n"
        + "Reproducir: `python benchmarks/run_all.py` (desde `site-packages`).\n"
        + "Un solo banco: `python benchmarks/bench_text.py`.\n"
        + "El perfil de 30 frames queda en `benchmarks/bench_app.prof`:\n"
        + "`python -m pstats benchmarks/bench_app.prof` → `sort tottime` → `stats 20`.\n"
    )
    SALIDA.write_text(texto, encoding="utf-8")
    print(f"\nEscrito {SALIDA}", flush=True)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
