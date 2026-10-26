"""Memoria por widget — cuánto ocupa cada cosa que creas.

Mide con la **memoria residente del proceso** (RSS), no con `tracemalloc`: las
superficies de pygame viven en C y `tracemalloc` no las ve.

Cada fila se mide en un **proceso nuevo**, tres veces, y se queda la mediana.
No es capricho: en un mismo proceso, el allocator reutiliza las páginas que
acaba de liberar la fila anterior y la segunda medida sale 0. Un proceso limpio
por fila es la única forma de que el número signifique algo.

Dentro de ese proceso limpio se mide la **pendiente**: se construye un primer
lote, se lee el RSS, se construye un segundo lote igual y se lee otra vez. Lo
que crece entre las dos lecturas, dividido entre las unidades del lote, es el
coste por unidad. Así se cancela todo lo que ya estaba cargado (pygame, la
fuente compartida, las páginas que el allocator regala) y no hay que restar
ningún "contenedor vacío".

La sorpresa está en las fuentes: cada `Text`/`Button` que no recibe un
`font.Font` crea **su propia** `pag.font.Font`, y una fuente por defecto cuesta
~19 KiB (medido aquí) más la superficie del texto.

Todo lo que sea "por elemento / por hijo / por partícula" mide eso: el coste
marginal de una unidad más, no el contenedor entero.
"""
from __future__ import annotations

import gc
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

import pygame as pag

from common import Muestra, nueva_app, rss_bytes, tabla
from Utilidades_pygame import (Bloque, Button, Image, Input, List, Particles,
                               Spark, Text)

PARRAFO = " ".join(["palabra"] * 200)
ELEMENTOS = [f"elemento {i}" for i in range(2000)]
RUTA_FUENTE = next(
    (p for p in (
        r"C:\Windows\Fonts\ARIALN.TTF",
        r"C:\Windows\Fonts\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ) if os.path.exists(p)),
    None,
)
REPETICIONES = 3

_fuente_compartida: pag.font.Font | None = None
_base_imagen: pag.Surface | None = None


# ==================== fábricas (k unidades) ====================

def _textos(k: int):
    return [Text(f"texto {i}", 16, pos=(10, 10)) for i in range(k)]


def _textos_fuente(k: int):
    return [Text(f"texto {i}", 16, _fuente_compartida, pos=(10, 10)) for i in range(k)]


def _textos_ruta(k: int):
    return [Text(f"texto {i}", 16, RUTA_FUENTE, pos=(10, 10)) for i in range(k)]


def _parrafos(k: int):
    return [Text(PARRAFO, 16, pos=(10, 10), max_width=300) for _ in range(k)]


def _botones(k: int):
    return [Button(f"botón {i}", 16, None, pos=(10, 10)) for i in range(k)]


def _inputs(k: int):
    return [Input((10, 10), 16, None, width=180, height=28) for _ in range(k)]


def _fuentes(k: int):
    return [pag.font.Font(None, 16) for _ in range(k)]


def _lista(k: int):
    return List((300, 400), (20, 20), ELEMENTOS[:k], text_size=16, font=None)


def _bloque(k: int):
    bloque = Bloque((10, 10), (500, 400), dire="topleft", background_color=(0, 0, 0))
    for i in range(k):
        bloque.add(Text(f"fila {i}", 16, pos=(5, 5 + i * 20), dire="topleft"))
    return bloque


def _imagenes(k: int):
    return [Image(_base_imagen, (10, 10)) for _ in range(k)]


def _imagenes_escaladas(k: int):
    return [Image(_base_imagen, (10, 10), size=(32, 32)) for _ in range(k)]


def _particulas(k: int):
    p = Particles((100, 100), radio=4, velocity=60, auto_spawn=False,
                  max_particles=k, spawn_count=k)
    p.spawn()
    return p


def _sparks(k: int):
    return [Spark((10, 10), 0.5, 100, "white") for _ in range(k)]


# nombre, fábrica, n, nota
FILAS = [
    ("Fuente suelta: pag.font.Font(None, 16)", _fuentes, 200, "el coste escondido de cada Text"),
    ("Text 16px (font=None)", _textos, 100, "crea su propia fuente"),
    ("Text 16px (font=Font compartida)", _textos_fuente, 100, "reutiliza una sola fuente"),
    ("Text 16px (font=ruta .ttf)", _textos_ruta, 100, "carga el archivo por widget"),
    ("Text párrafo 200 palabras", _parrafos, 30, "wrap a max_width=300"),
    ("Button 16px (font=None)", _botones, 100, "Text + colores"),
    ("Input 16px (font=None)", _inputs, 50, "crea 3 Text + superficie"),
    ("List: por elemento", _lista, 500, "solo las palabras; dibuja al vuelo"),
    ("Bloque: por hijo", _bloque, 80, "hijo Text + libro de scroll"),
    ("Image: por imagen (surface compartida)", _imagenes, 200, "no copia la superficie"),
    ("Image: por imagen escalada 64→32", _imagenes_escaladas, 100, "copia + smoothscale"),
    ("Particles: por partícula (radio 4)", _particulas, 500, "incluye su superficie radial"),
    ("Spark: por chispa", _sparks, 5000, "sin superficie propia"),
]


# ==================== medición en proceso limpio ====================

def _preparar() -> None:
    global _fuente_compartida, _base_imagen
    _fuente_compartida = pag.font.Font(None, 16)
    _base_imagen = pag.Surface((64, 64))
    _base_imagen.fill((80, 120, 200))


def _delta_en_este_proceso(indice: int, k: int) -> float:
    """Bytes que crece el RSS al pasar de un lote de `k` a otro lote de `k`.

    Los lotes se quedan vivos: si se borrasen, el siguiente reutilizaría sus
    páginas y la medida saldría ~0. Se hacen dos pendientes seguidas y se queda
    la menor: la primera todavía incluye costes fijos que el allocator no puede
    reutilizar (una superficie grande que no cabe en un hueco libre, por
    ejemplo), la segunda ya no. El proceso es nuevo, así que tampoco hay páginas
    recicladas de filas anteriores.
    """
    nombre, fabrica, _n, _nota = FILAS[indice]
    if nombre.startswith("Text 16px (font=ruta") and RUTA_FUENTE is None:
        raise RuntimeError("no hay ninguna fuente .ttf en este sistema")

    _app = nueva_app()          # noqa: F841  (mantiene la ventana viva)
    _preparar()
    gc.collect()

    caliente = fabrica(k)       # noqa: F841  (calienta fuentes y allocator)
    gc.collect()
    base = rss_bytes()
    lote = fabrica(k)
    gc.collect()
    medio = rss_bytes()
    otro = fabrica(k)
    gc.collect()
    fin = rss_bytes()
    if base is None or medio is None or fin is None:
        raise RuntimeError("no se puede leer la memoria residente del proceso")

    del caliente, lote, otro
    return float(min(medio - base, fin - medio))


def _medir_delta(indice: int, k: int, repeticiones: int) -> float:
    """Corre `_delta_en_este_proceso` en procesos nuevos y devuelve la mediana."""
    valores = []
    for _ in range(repeticiones):
        resultado = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()),
             "--fila", str(indice), "--n", str(k)],
            capture_output=True, text=True, timeout=300,
        )
        if resultado.returncode != 0:
            raise RuntimeError(resultado.stderr.strip().splitlines()[-1])
        valores.append(json.loads(resultado.stdout.strip().splitlines()[-1])["bytes"])
    return statistics.median(valores)


def _medir_fila(indice: int) -> float:
    """Bytes por unidad: pendiente de RSS entre dos lotes de `n`, entre `n`."""
    _nombre, _fabrica, n, _nota = FILAS[indice]
    return max(0.0, _medir_delta(indice, n, REPETICIONES) / n)


def run(frames: int = 200) -> list[Muestra]:
    out: list[Muestra] = []
    for indice, (nombre, _fabrica, n, nota) in enumerate(FILAS):
        if nombre.startswith("Text 16px (font=ruta") and RUTA_FUENTE is None:
            continue
        bytes_unidad = _medir_fila(indice)
        out.append(Muestra(
            nombre=nombre,
            n=n,
            media=bytes_unidad / 1024,
            mediana=bytes_unidad / 1024,
            p95=bytes_unidad / 1024,
            minimo=bytes_unidad / 1024,
            maximo=bytes_unidad / 1024,
            extra={"bytes": bytes_unidad, "nota": nota},
            unidad="KiB/widget",
        ))
    return out


def main() -> None:
    muestras = run()
    print(tabla(muestras, "Memoria por widget"))
    print(f"\n{'widget':<44} {'B/widget':>10} {'1 000 uds':>10}   nota")
    print("-" * 96)
    for m in muestras:
        e = m.extra
        print(f"{m.nombre:<44} {e['bytes']:>10.0f} {e['bytes'] * 1000 / 1048576:>7.1f} MiB"
              f"   {e['nota']}")
    print("\nCada fila se mide en un proceso nuevo (3 veces, mediana), por la "
          "pendiente entre dos lotes.\n"
          "Método: RSS, así que incluye las superficies de pygame.")


if __name__ == "__main__":
    if "--fila" in sys.argv:
        i = int(sys.argv[sys.argv.index("--fila") + 1])
        k = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else FILAS[i][2]
        print(json.dumps({"bytes": _delta_en_este_proceso(i, k)}))
    else:
        main()
