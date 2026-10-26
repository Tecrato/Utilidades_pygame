"""Infraestructura común de los benchmarks de `Utilidades_pygame`.

Todo corre **sin ventana** (`SDL_VIDEODRIVER=dummy`) y sin entrar al bucle de
la app: `Base_class(..., autostart=False)` deja la app montada y `draw()` se
llama a mano, que es justo lo que se quiere medir.

Uso típico:

    from common import nueva_app, medir, tabla

    app = nueva_app()
    textos = [Text(f"texto {i}", 16, pos=(...)) for i in range(200)]
    for t in textos:
        app.lists_screens["main"]["draw"].append(t)
    print(tabla([medir("dibujar 200 Text", lambda: app.draw_optimized(...))]))

Cada archivo `bench_*.py` se puede ejecutar solo:

    python benchmarks/bench_text.py

y `python benchmarks/run_all.py` los ejecuta todos y escribe `RESULTADOS.md`.
"""
from __future__ import annotations

import gc
import os
import statistics
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

# Los drivers *dummy* tienen que estar puestos ANTES de importar pygame.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

# La consola de Windows es cp1252: sin esto, imprimir "→" o "≈" revienta.
for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# site-packages (este archivo vive en Utilidades_pygame/benchmarks/)
SITE_PACKAGES = Path(__file__).resolve().parents[2]
if str(SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(SITE_PACKAGES))

import pygame as pag  # noqa: E402

from Utilidades_pygame import Config  # noqa: E402
from Utilidades_pygame.base_app_class import Base_class  # noqa: E402

RESOLUTION = (800, 600)


class Bench_app(Base_class):
    """`Base_class` sin bucle: la app se monta, se dibuja a mano y se cierra."""

    def screen_main(self) -> None:      # nunca se llama: autostart=False
        ...

    def on_exit(self) -> None:
        ...


def nueva_app(resolution: tuple[int, int] = RESOLUTION, **kwargs) -> Bench_app:
    """Crea la app headless. `resolution` por defecto 800x600."""
    app = Bench_app(Config(resolution=resolution, title="bench", max_fps=60),
                    autostart=False, initial_screen="main", **kwargs)
    return app


def cerrar_app(app: Bench_app) -> None:
    """Cierra el display sin pasar por `Base_class.run()`."""
    pag.display.quit()
    pag.font.quit()
    pag.quit()


def lista_dibujo(app: Bench_app) -> list:
    return app.lists_screens[app.actual_screen]["draw"]


def mostrar_fps(app: Bench_app, widgets: list) -> None:
    """Mete los widgets en la pantalla actual para dibujarlos con el bucle."""
    lista_dibujo(app).extend(widgets)


# ==================== medición ====================

@dataclass
class Muestra:
    """Resultado de una medición. Todos los tiempos en milisegundos."""
    nombre: str
    n: int
    media: float
    mediana: float
    p95: float
    minimo: float
    maximo: float
    desv: float = 0.0
    extra: dict = field(default_factory=dict)
    unidad: str = "ms"          # "ms", "MiB" o "cuenta" (no son tiempos)

    @property
    def fps(self) -> float:
        return 1000.0 / self.media if self.media > 0 else float("inf")


def medir(nombre: str, fn, *, frames: int = 300, warmup: int = 20,
          gc_off: bool = True, **extra) -> Muestra:
    """Ejecuta `fn` `frames` veces y devuelve las estadísticas en ms.

    `warmup` llamadas previas se descartan (caches, JIT de CPython, superficies).
    Desactivar el GC evita que una recolección caiga justo en la medición; se
    vuelve a activar al terminar.
    """
    for _ in range(warmup):
        fn()
    estaba = gc.isenabled()
    if gc_off:
        gc.disable()
    try:
        tiempos = []
        for _ in range(frames):
            t0 = time.perf_counter_ns()
            fn()
            tiempos.append((time.perf_counter_ns() - t0) / 1_000_000)
    finally:
        if estaba and gc_off:
            gc.enable()
    tiempos.sort()
    return Muestra(
        nombre=nombre,
        n=frames,
        media=statistics.fmean(tiempos),
        mediana=statistics.median(tiempos),
        p95=tiempos[min(len(tiempos) - 1, int(len(tiempos) * 0.95))],
        minimo=tiempos[0],
        maximo=tiempos[-1],
        desv=statistics.pstdev(tiempos) if len(tiempos) > 1 else 0.0,
        extra=extra,
    )


@contextmanager
def sin_presentacion():
    """Anula `pag.display.update()` mientras dure el bloque.

    Sirve para separar "lo que cuesta dibujar" de "lo que cuesta empujar los
    píxeles a la pantalla". Con el driver *dummy* presentar es casi gratis,
    así que la diferencia entre medir con y sin esto es pequeña; con ventana
    real es la diferencia entre 8 ms y 0.1 ms.
    """
    original = pag.display.update

    def noop(*args, **kwargs):
        return None

    pag.display.update = noop
    try:
        yield
    finally:
        pag.display.update = original


def ms(fn, frames: int = 300, warmup: int = 20) -> float:
    """Atajo: mediana en ms de `fn`."""
    return medir("", fn, frames=frames, warmup=warmup).mediana


# ==================== memoria ====================

def rss_bytes() -> int | None:
    """Memoria residente del proceso, en bytes. `None` si no se puede saber.

    En Windows usa `GetProcessMemoryInfo` (psapi) vía ctypes, así no hace falta
    `psutil`; en Linux lee `/proc/self/statm`. Incluye las superficies de pygame,
    que viven en C y por eso `tracemalloc` no las ve.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class _PMC(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            kernel32 = ctypes.WinDLL("kernel32")
            psapi = ctypes.WinDLL("psapi")
            kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

            pmc = _PMC()
            pmc.cb = ctypes.sizeof(_PMC)
            ok = psapi.GetProcessMemoryInfo(
                kernel32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
            return int(pmc.WorkingSetSize) if ok else None
        except (OSError, AttributeError):
            return None
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/self/statm", encoding="ascii") as f:
                paginas = int(f.read().split()[1])
            return paginas * os.sysconf("SC_PAGE_SIZE")
        except (OSError, ValueError, IndexError):
            return None
    return None


def memoria_por_unidad(fabrica, n: int = 100, repeticiones: int = 3) -> tuple[float, str]:
    """Bytes por unidad que crea `fabrica(k)` (k objetos o un contenedor con k).

    Se mide la **pendiente** de la memoria residente entre lotes de `n`
    unidades, no el salto desde cero: así se cancela lo que la librería ya tenía
    cargado y lo que el allocator redondea. Se hacen dos pendientes seguidas y
    se queda la menor, porque la primera todavía paga costes fijos que el
    allocator no reutiliza (por ejemplo la superficie del primer `List`). Se
    repite y se toma la mediana.

    Devuelve `(bytes_por_unidad, metodo)`. Si no hay RSS disponible, cae a
    `tracemalloc` (que solo ve objetos de Python, no las superficies de pygame).
    """
    if rss_bytes() is None:
        tracemalloc.start()
        lote = fabrica(n)
        actual, _ = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        del lote
        return actual / n, "tracemalloc (solo Python)"

    valores = []
    for _ in range(repeticiones):
        gc.collect()
        caliente = fabrica(n)          # primer lote: calienta fuentes/caches
        base = rss_bytes()
        lote = fabrica(n)
        medio = rss_bytes()
        otro = fabrica(n)
        fin = rss_bytes()
        if base is None or medio is None or fin is None:
            return 0.0, "sin RSS"
        valores.append(min(medio - base, fin - medio) / n)
        del caliente, lote, otro
        gc.collect()

    valores.sort()
    return valores[len(valores) // 2], "RSS"


# ==================== presentación ====================

def tabla(muestras: list[Muestra], titulo: str = "") -> str:
    """Tabla de texto alineada, lista para pegar en RESULTADOS.md."""
    lineas = []
    if titulo:
        lineas.append(f"\n### {titulo}\n")
    lineas.append(f"{'benchmark':<40} {'media':>9} {'mediana':>9} {'p95':>9} {'fps':>8}")
    lineas.append("-" * 80)
    for m in muestras:
        if m.unidad != "ms":                    # cuentas y memoria: sin fps
            valor = f"{m.media:.0f}" if m.unidad == "cuenta" else f"{m.media:.1f}"
            lineas.append(f"{m.nombre:<40} {valor + ' ' + m.unidad:>9}")
            continue
        fps = f"{m.fps:8.0f}" if m.media > 0 else "     inf"
        lineas.append(f"{m.nombre:<40} {m.media:9.3f} {m.mediana:9.3f} {m.p95:9.3f} {fps}")
    return "\n".join(lineas)


def marcar_seccion(nombre: str) -> None:
    print(f"\n=== {nombre} ===", flush=True)


def perfilar(fn, archivo: str = "bench.prof", frames: int = 10) -> str:
    """Corre `fn` `frames` veces bajo cProfile. Devuelve la ruta del .prof."""
    import cProfile
    prof = cProfile.Profile()
    prof.enable()
    for _ in range(frames):
        fn()
    prof.disable()
    prof.dump_stats(archivo)
    return archivo


def resumen_perfil(archivo: str = "bench.prof", lineas: int = 12) -> str:
    """Top `lineas` por `tottime`, como texto (para pegar en el informe)."""
    import pstats
    stats = pstats.Stats(archivo)
    stats.sort_stats("tottime")
    # pstats imprime a stdout; lo más simple y estable es capturarlo.
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        stats.print_stats(lineas)
    return buf.getvalue()
