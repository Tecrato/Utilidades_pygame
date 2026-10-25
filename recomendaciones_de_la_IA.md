# Recomendaciones de la IA — `Utilidades` + `Utilidades_pygame`

> Revisión hecha el **23/10/2026** sobre el código que hay hoy en `site-packages`, ampliada el mismo día con ejemplos de corrección y el **25/10/2026** con una pasada completa por las tres apps de ejemplo (`Acelerador-de-descargas`, `Buscaminas`, `BrickBricker`). El estilo, los flujos y las convenciones de esas apps están en `perfil_de_codigo.md`.
> **No se ha modificado ni una línea de código de las librerías.** Este archivo es el único que la IA puede editar libremente; las ideas de aquí las implementas tú, a tu manera.
> Cada recomendación tiene un **ID** para que la puedas marcar, discutir o descartar sin perder el hilo.

## Leyenda de estado

| Marca | Significado |
|---|---|
| ✅ | **Verificado ejecutando código** en esta revisión (comando en el Apéndice A) |
| 📖 | **Verificado leyendo el código** (no hace falta ejecutar: se ve a simple vista) |
| 💭 | **Hipótesis de rendimiento**: suena a cuello de botella, pero hay que medirlo antes de tocarlo |
| 🧪 | **Ejemplo de corrección probado aparte** (en un script suelto, nunca editando la librería): hoy `OPT-03` y `OPT-05` |

## Cómo usar este documento

1. Empieza por **§1 (optimización)** y **§2 (corrección)**. El resto puede esperar.
2. No apliques dos cambios grandes a la vez. Cada recomendación trae "cómo verificar", úsalo.
3. Si una recomendación no te convence o no encaja con tu forma de pensar, **descártala y anótalo aquí**. Este documento no es una orden, es una lista de opciones con su coste.
4. Los números de línea cambian en cuanto edites. Por eso cito **archivo + símbolo**, no líneas.
5. Cada punto trae un bloque **«Cómo podría quedar»** con código de ejemplo. Es un **boceto para que lo adaptes**, no un parche garantizado: está escrito contra el código de esta fecha y a veces cambia firmas o comportamiento a propósito. Cuando el cambio tiene un coste (rendimiento, compatibilidad, riesgo), lo digo debajo del bloque.

## Resumen ejecutivo (si solo lees 10 líneas)

1. **La unidad de `dt` ya está unificada** (`UNITS-01`, hecho y medido) y `BUG-18` está cerrado: el `finally` de `__init__` ya solo limpia. §2 recoge ahora los diez bugs que aparecieron al usar las librerías desde fuera, en las tres apps.
2. **La semántica de `redraw` (0/1/2/3) está repartida y es implícita** (`API-01`). Es la mayor fuente futura de parpadeos y de bugs difíciles. Formalizarla no cuesta casi nada y lo ordena todo.
3. **El texto se mide renderizando**, y `Input` re-renderiza su superficie **en cada frame** (`OPT-03`, `OPT-04`). Ahí está el gasto más fácil de eliminar.
4. **`draw_optimized` es O(n²) con copias de listas** (`OPT-01`), pero como los widgets de UI son estáticos, se puede resolver con un índice construido **una vez por pantalla**.
5. Antes de optimizar nada: **mide** (`OPT-00`). No he ejecutado benchmarks, así que todo lo de §1 salvo lo marcado 📖 es hipótesis.

---

# 1. Optimización

## OPT-00 — Medir antes de tocar 📖💭

**Qué hacer.** Un script aparte (fuera de la librería, en `benchmarks/`) que:

- arranque pygame headless: `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`;
- monte una pantalla con N widgets de cada tipo (`Text`, `Button`, `Input`, `Bloque`) para N = 10, 50, 200, 1000;
- dibuje 300 frames con `draw_mode` `optimized` y `always`, midiendo con `time.perf_counter()` alrededor de la llamada, y separando **dibujado** de **update**;
- perfile 10 frames con `cProfile` y guarde el `.prof` (`python -m pstats`).

**Por qué.** Ahora mismo no hay ninguna cifra de referencia. Sin ella, cualquier "optimización" es fe y el riesgo de romper el dirty-rect sin ganar nada es alto.

**Presupuesto de frame** (60 FPS → 16.6 ms). Objetivo razonable, no medido todavía:

| Fase | Presupuesto |
|---|---|
| eventos + update de widgets | ≤ 4 ms |
| dibujado (blits + `display.update`) | ≤ 8 ms |
| margen para tu lógica de juego | resto |

**Cómo verificar.** Guarda la tabla de tiempos en `benchmarks/RESULTADOS.md` antes y después de cada cambio. Si un cambio no mueve la aguja, se revierte. Eso es todo el método.

**Cómo podría quedar** (esqueleto del banco de pruebas):

```python
# benchmarks/bench_ui.py
import os, time
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pag
from Utilidades_pygame import Config, Text
from Utilidades_pygame.base_app_class import Base_class


class Bench(Base_class):
    """Neutraliza el bucle para medir el dibujado a mano (API-04 lo hará innecesario)."""
    def screen_main(self): ...
    def on_exit(self): ...

    def montar(self, n):
        for i in range(n):
            self.lists_screens["main"]["draw"].append(
                Text(f"texto {i}", 16, pos=(i % 20 * 40, i // 20 * 24))
            )


def ms_por_frame(fn, frames=300):
    fn()                                    # calentamiento
    t0 = time.perf_counter()
    for _ in range(frames):
        fn()
    return (time.perf_counter() - t0) * 1000 / frames


app = Bench(Config(resolution=(800, 600)), initial_screen="main")
pag.init(); pag.font.init()                 # __init__ ya llamó a pag.quit()
app.ventana = pag.display.set_mode((800, 600))
app.ventana_rect = app.ventana.get_rect()
app.montar(200)

dibujo = app.lists_screens["main"]["draw"]
print(f"optimized: {ms_por_frame(lambda: app.draw_optimized(dibujo)):.2f} ms/frame")
app.draw_mode = "always"
print(f"always:    {ms_por_frame(lambda: app.draw_always(dibujo)):.2f} ms/frame")
```

**Aviso:** tal como está, ese esqueleto **no arranca**. Con `SDL_VIDEODRIVER=dummy`, `Base_class.__init__` falla en `pag.display.get_wm_info()['window']` con `KeyError` (BUG-26), y además `__init__` termina con `pag.quit()`, así que el `pag.init()` de después no te salva. Arregla BUG-26 (dos líneas) antes de usar el banco; es el mismo cambio que desbloquea los tests de la app entera de API-04.

Para el perfil, envuelve el bucle: `cProfile.runctx("app.draw_optimized(dibujo)", globals(), locals(), "bench.prof")` y luego `python -m pstats bench.prof` → `sort tottime` → `stats 20`.

---

## OPT-01 — El doble bucle de `draw_optimized` 📖💭

**Dónde.** `base_app_class.py` → `Base_class.draw_optimized`.

**Qué cuesta hoy.**

- Por **cada** objeto que se redibuja, recorre dos veces el resto de la lista: `lista[i+1:]` y `lista[:i]`. `lista[i+1:]` **crea una lista nueva cada iteración**, así que con 200 widgets que se redibujan son ~40.000 comparaciones y ~200 copias de lista por frame.
- El orden de las condiciones es `p.collide(y) and p.redraw < 1`: se paga un `colliderect` (aunque es C, es una llamada Python) incluso para objetos que ya sabemos que están sucios. **Invertirlo a `p.redraw < 1 and p.collide(y)` es gratis y no cambia el resultado** (ambos predicados son puros). Esto es lo primero que probaría, una línea.
- La cascada está expresada como dos bucles anidados, pero conceptualmente es un **flood-fill sobre el grafo de solapamientos**: "marca sucio → los que se dibujan después y se solapan, sucios → repetir". Hoy cuesta O(k·n) para k objetos que se redibujan, y paga una copia de lista por cada uno. Una **cola con un `set` de visitados** quita las copias y las pasadas repetidas, pero **por sí sola no cambia la clase de complejidad**: para eso hace falta el índice espacial de (c).

**Tres caminos, de menor a mayor ambición:**

- **(a) Micro.** Cambiar el orden de las condiciones, sustituir los slices por índices (`for j in range(i+1, len(lista))`), y cachear `len(lista)`.
- **(b) Cola de daño.** Un `deque` de `Rect` sucios + un `set` de widgets ya procesados. Mientras queden rects: saca uno, busca los widgets que se solapan y se dibujan **después**, márcales `redraw`, añade sus rects. Termina cuando no aparecen nuevos.
- **(c) Índice espacial de widgets.** Los widgets de UI **no se mueven** entre `goto()` y `goto()`. Construye un índice (puedes reutilizar tu `Collision_handler` con `node_size ≈ 64`) al cambiar de pantalla y al añadir/quitar widgets. Cada frame consultas solo las celdas que tocan los rects sucios.

Mi orden: (a) ya, (b) cuando midas y veas que el dibujado domina, (c) solo si tienes pantallas con cientos de widgets.

**Cuidado.** La cascada hacia **atrás** (`lista[:i]`) solo hace falta cuando el widget **se movió o desapareció** (su rect viejo queda al descubierto y hay que repintar lo de debajo). Tu código ya lo distingue con `if re < 2`. Si lo reescribes como cola, conserva esa distinción explícitamente o perderás repintados y verás "fantasmas".

**Cómo verificar.** Benchmark con 200 `Text` en una cuadrícula, moviendo uno. Mismo resultado visual (compara captura o hash de píxeles antes/después) y menos ms.

**Cómo podría quedar.**

(a) La versión sin slices, que puedes aplicar hoy sin cambiar nada más:

```python
n = len(lista)
for i, x in enumerate(new_list):
    if not x.collide(self.ventana_rect) or not getattr(x, 'visible', True):
        continue
    re = x.redraw
    r = x.draw(self.ventana)
    for s in r:
        self.updates.append(s)
    for y in r:
        for j in range(i + 1, n):           # antes: lista[i+1:]  → copia por rect
            p = lista[j]
            if p.redraw < 1 and p.collide(y):   # antes: collide() y luego redraw
                p.redraw += 1
    if re < 2:
        continue
    for y in r:
        for j in range(min(i, n)):         # min(): el loader y el GUI van tras la lista
            p = lista[j]
            if p.redraw < 1 and p.collide(y):
                p.redraw += 1
```

(b) La cascada como cola. La clave es arrastrar el **índice mínimo**: un objeto solo puede ensuciar a los que se dibujan por encima de él.

```python
from collections import deque

def _cascada(self, lista, semillas):
    """semillas: [(rect, indice_minimo)] — solo marca objetos dibujados por encima."""
    pendientes = deque(semillas)
    while pendientes:
        r, desde = pendientes.popleft()
        for j in range(desde, len(lista)):
            p = lista[j]
            if p.redraw < 1 and p.collide(r):
                p.redraw += 1
                pendientes.append((p.rect, j + 1))

# en draw_optimized, después de dibujar x:
self._cascada(lista, [(y, i + 1) for y in r])     # hacia delante
if re >= 2:
    self._cascada(lista, [(y, 0) for y in r])     # hacia atrás: solo si se movió
```

(c) El índice espacial, que es el que sí baja el coste a O(k): se construye una vez por pantalla y no por frame.

```python
class Widget_Index:
    def __init__(self, cell: int = 64):
        self.cell = cell
        self.cells: dict[tuple[int, int], set[int]] = {}

    def rebuild(self, widgets):
        self.cells.clear()
        for i, w in enumerate(widgets):
            r = w.collide_rect
            for cx in range(r.left // self.cell, (r.right - 1) // self.cell + 1):
                for cy in range(r.top // self.cell, (r.bottom - 1) // self.cell + 1):
                    self.cells.setdefault((cx, cy), set()).add(i)

    def query(self, rect, desde: int = 0) -> set[int]:
        fuera = set()
        for cx in range(rect.left // self.cell, (rect.right - 1) // self.cell + 1):
            for cy in range(rect.top // self.cell, (rect.bottom - 1) // self.cell + 1):
                fuera.update(i for i in self.cells.get((cx, cy), ()) if i >= desde)
        return fuera
```

Y en `draw_optimized` sustituyes los dos bucles por `for j in self._index.query(y, i + 1): ...`. Reconstruye en `goto()`, en `registrar_pantalla()` y cuando añadas o quites widgets de la lista (no en cada frame).

---

## OPT-02 — `ventana.fill()` en cada frame 📖💭

**Dónde.** `draw_optimized` y `draw_always`, primeras líneas.

**Qué pasa.** Si `self.draw_background` es `True`, rellenas **toda** la ventana en **cada** frame, incluso cuando solo se actualizan 2 rects con `display.update(self.updates)`. Ese relleno es trabajo proporcional al área de la ventana (y en 1920×1080 es memoria real) que en la mayoría de frames es invisible: lo que no está en `updates` no llega a pantalla.

**Qué probar.** Rellenar solo cuando `redraw` es `True` (repintado completo) y, en el caso parcial, dejar que cada widget repinte su zona (que es lo que ya hace la cascada). En el camino de **ventana transparente** es distinto: ahí empujas la superficie entera con `UpdateLayeredWindow`, así que el dirty-rect no ahorra nada y el relleno sí es necesario — merece la pena tratarlo como un modo aparte y no compartir código con el camino normal.

**Cómo verificar.** Mismo hash de píxeles con movimiento de un widget. Si aparece basura en los bordes, la cascada tiene un hueco: ese es un bug real que este cambio destapa, no un problema del cambio.

**Cómo podría quedar** (la parte fácil):

```python
# solo se rellena cuando de verdad se va a repintar todo
if self.draw_background and (redraw or self.config.window_transparent):
    self.ventana.fill(self.background_color)
```

**Aviso honesto.** Esa línea sola produce **fantasmas** en cuanto un widget se mueve o se oculta: su hueco ya no lo limpia nadie, porque `Text.draw` no repinta el fondo de su rect. Para que funcione de verdad hay dos caminos:

```python
# 1) cada widget opaco limpia su propia zona antes de dibujarse
#    (en Text, Button, Bloque, ... al principio de draw())
if self.background is not None:
    surface.fill(self.background, self.rect)

# 2) o dejar de usar "cada widget se dibuja" y pasar a "damage + repintar región":
#    por cada rect sucio, rellenar ese rect y volver a dibujar TODOS los widgets
#    que se solapan con él, en orden Z. Es más limpio y escala mejor, pero es
#    un cambio de modelo de dibujado, no una optimización.
```

Recomendación: **no lo toques hasta que el benchmark diga que `fill` pesa**. En 1920×1080 es ~8 MB de memoria por frame, pero es también lo que hoy te da la garantía de que no quedan restos.

---

## OPT-03 — El texto se mide **renderizando** 📖💭

**Dónde.** `texts/text.py` → `Text.__generate`, `Text.create_rect`, `Text.get_txt_ajustado`, `Text.font` (setter).

**Qué cuesta hoy.**

- `__generate` recorre palabra por palabra y para **cada** palabra candidata llama `self.__font.render(potential_line, ...).get_width()`. Un párrafo de 40 palabras son ~40 renders completos **solo para medir**. Renderizar crea una superficie con antialiasing; medir no debería costar eso.
- `get_txt_ajustado` va quitando letras desde el final y **renderizando una vez por letra** hasta que cabe. Peor caso: `len(texto)` renders por línea truncada.
- El setter de `font` renderiza `'hola|-|█'` solo para sacar el alto.

**Qué probar.**

- Medir con `font.size(texto)` → `(ancho, alto)` **sin crear superficie**. Es la API pensada para esto.
- Para `get_txt_ajustado`, el ancho es **monótono** con la longitud del prefijo: búsqueda binaria sobre el número de caracteres en vez de lineal. Pasa de ~n renders a ~log₂(n) mediciones.
- Cachear el resultado de `render` en un dict pequeño con tope (LRU casero o `functools.lru_cache` sobre una función pura `(texto, color, aa) -> Surface`). En una UI hay muchísimo texto repetido (etiquetas, "OK", "Cancelar").
- El alto del texto se puede sacar de `font.get_height()` / `font.get_linesize()`, sin render de prueba.

**Cómo verificar.** Un test que compare `size(t)` con `render(t).get_size()` para un puñado de cadenas y fuentes. Si coinciden (deberían, salvo detalles de padding), el cambio es seguro. Después, benchmark de un `Text` de 200 palabras que cambia 60 veces.

**Cómo podría quedar.**

```python
# 1) medir sin renderizar, en __generate
potential_width = self.__font.size(potential_line)[0]      # antes: .render(...).get_width()

# 2) truncar por bisección: el ancho crece con el prefijo (get_txt_ajustado)
def get_txt_ajustado(self, text, always_elipsis=False):
    fuente, tope = self.__font, self.max_width
    cola = '...' if always_elipsis else ''
    if fuente.size(text + cola)[0] <= tope:
        return fuente.render(text + cola, True, self.__color)
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if fuente.size(text[:mid] + '...')[0] <= tope:
            lo = mid
        else:
            hi = mid - 1
    return fuente.render(text[:lo] + '...', True, self.__color)

# 3) el alto sin render de prueba (font y size setter)
self.text_height = self.__font.get_height()

# 4) caché acotada de renders: en una UI hay muchísimo texto repetido
from collections import deque
_render_cache: dict[tuple, pag.Surface] = {}
_cache_order: deque = deque()

def render_cached(font, texto: str, color, aa: bool = True) -> pag.Surface:
    key = (font, texto, color, aa)          # el font en la clave lo mantiene vivo
    surf = _render_cache.get(key)
    if surf is None:
        if len(_cache_order) >= 512:
            _render_cache.pop(_cache_order.popleft(), None)
        surf = _render_cache[key] = font.render(texto, aa, color)
        _cache_order.append(key)
    return surf
```

**Esto sí lo medí** (pygame 2.6.1, fuente por defecto, `SDL_VIDEODRIVER=dummy`, 300 cadenas aleatorias con acentos):

- `font.size(t)[0]` coincide **exactamente** con `font.render(t).get_width()` → 0 discrepancias de 300.
- `font.get_height()` coincide con `render('hola|-|█').get_height()` → 16 en ambos.
- La bisección devuelve el mismo corte que la versión lineal → 0 discrepancias de 300.

O sea: aquí no hay coste de fidelidad. Aun así deja el test en el repo, porque eso está medido con **una** fuente y **una** versión de pygame.

---

## OPT-04 — `Input` re-renderiza cada frame (y cada tecla) 📖💭

**Dónde.** `texts/input.py` → `update_pressed_keys`, `draw_surf`, `add_letter`.

**Qué cuesta hoy.**

- `update_pressed_keys()` termina llamando `self.draw_surf()` **incondicionalmente** dentro del bloque `if time.time() - self.button_pressed_time > .5:`, que en régimen normal es siempre cierto. Y `draw_surf` limpia la superficie, redibuja el texto entero y la línea del cursor. Con `draw_mode='always'` eso son **60 re-renders por segundo por cada `Input` de la pantalla**, aunque nadie escriba; con `'optimized'`, cada vez que el widget entra en el dirty-rect. Es el gasto más tonto y más fácil de quitar de toda la librería.
- `add_letter` mide la letra nueva renderizando **todo el prefijo** y restándole la suma acumulada: `render(raw_text[:pos]+t).get_width() - sum(letter_pos[:pos])`. O(n) de render + O(n) de suma por tecla. Con `font.size(nuevo) - font.size(viejo)` tienes el delta exacto con dos mediciones sin superficie.
- `update_pressed_keys` usa `time.time()` y umbrales fijos (`.5`, `.03`) en vez de `dt`, así que el autorepeat depende del reloj, no del frame.

**Qué probar.** `draw_surf()` solo cuando algo cambió (ya lo llamas en `add_letter`, `del_letter`, `center_text`, `click`, `clear`, `set`); en el bucle de autorepeat, solo cuando de verdad se borra/mueve una letra. El parpadeo del cursor puede seguir teniendo su temporizador propio.

**Cómo verificar.** 10 `Input` en pantalla, sin escribir, 300 frames: antes/después. Debería ser una diferencia grande y visible en el perfil.

**Cómo podría quedar.**

```python
def update_pressed_keys(self):
    """Autorepeat. Ya no redibuja: del_letter/to_left/to_right llaman a center_text(),
    que a su vez llama a draw_surf() solo cuando el texto cambia de verdad."""
    ahora = time.time()
    if ahora - self.button_pressed_time <= .5:
        return
    if self.backspace and ahora - self.del_time > .03:
        self.del_letter()
        self.del_time = ahora
    elif self.left_b and ahora - self.left_time > .03:
        self.to_left()
        self.left_time = ahora
    elif self.right_b and ahora - self.right_time > .03:
        self.to_right()
        self.right_time = ahora


def add_letter(self, t) -> None:
    ...
    # antes: render de todo el prefijo menos sum(letter_pos)  → O(n) render + O(n) suma
    antes = self.font_loaded.size(self.raw_text[:self.typing_pos])[0]
    despues = self.font_loaded.size(self.raw_text[:self.typing_pos] + str(t))[0]
    self.letter_pos.insert(self.typing_pos, despues - antes)
    ...
```

El parpadeo del cursor sigue igual: `draw()` lo alterna cada 0.6 s con `typing_line`, y ese `draw_surf()` sí es necesario. Lo que desaparece es el redibujado **por frame** sin cambios.

---

## OPT-05 — `Collision_handler.move_obj` 📖💭

**Dónde.** `Utilidades/collision_handler.py` → `move_obj`.

**Qué pasa.** `move_obj` hace `del_element` + `add_element`: `Rect(*rect)` nuevo, `set()` de zonas nuevo, `set.discard/add` por celda, `dict.pop` + `dict` nuevo para `ObjectInfo`. Para una entidad que se mueve **dentro de la misma celda** (el caso mayoritario), todo ese trabajo es idéntico al anterior.

**Qué probar.** `update_element(id, rect)` que:

1. calcula `(row_min,row_max,col_min,col_max)` nuevos;
2. si coinciden con las zonas guardadas, **solo** reemplaza `objects[id]["rect"]` (una asignación);
3. si no, hace el diff: quita el id de las celdas que salen, lo añade a las que entran, y actualiza el set.

Además:

- `zone_matrix` como **lista plana** con `idx = y * num_nodes[0] + x` en vez de lista de listas: un `[]` menos por acceso y mejor localidad.
- `generate_zone_matrix` hace `l.copy()` al añadir a `zone_matrix`: es una copia inútil de cada fila.
- `get_rects_in_zone` devuelve `Rect` en vez de ids; casi siempre lo que quieres después son los ids (y así te ahorras el `dict` lookup inverso).
- `get_collides` construye un `set` de ids y luego otro `set` de colisiones: se puede devolver el set directamente si no te importa el orden (ya no lo tienes).

**Cómo verificar.** Test de propiedad: tras cualquier secuencia de `move_obj`, el conjunto `zone_matrix[y][x].objs` debe ser exactamente el que saldría de reconstruir el handler desde cero. Es fácil de escribir y te protege de corromper el índice.

**Cómo podría quedar.**

```python
def update_element(self, id_obj, rect) -> bool:
    """Mueve un objeto. Si sigue en las mismas celdas, no toca el índice."""
    obj = self.objects[id_obj]
    nuevo = Rect(*rect)
    row_min, row_max, col_min, col_max = self.get_zones_matrix_number_in(nuevo)
    zonas_nuevas = {
        (x, y)
        for y in range(int(row_min), int(row_max) + 1)
        for x in range(int(col_min), int(col_max) + 1)
    }

    if zonas_nuevas == obj["zones"]:        # el caso mayoritario: mismo sitio
        obj["rect"] = nuevo                 # una asignación, sin sets ni dicts
        return False

    for (x, y) in obj["zones"] - zonas_nuevas:      # sale de estas celdas
        self.zone_matrix[y][x].objs.discard(id_obj)
    for (x, y) in zonas_nuevas - obj["zones"]:      # entra en estas
        self.zone_matrix[y][x].objs.add(id_obj)
    obj["rect"] = nuevo
    obj["zones"] = zonas_nuevas
    return True


def move_obj(self, id_obj, r):
    return self.update_element(id_obj, r)
```

Y las dos limpiezas baratas del constructor:

```python
def generate_zone_matrix(self):
    self.zone_matrix.clear()
    for y in range(self.num_nodes[1]):
        fila = [Zone_node(self.node_size * x, self.node_size * y,
                          self.node_size, self.node_size)
                for x in range(self.num_nodes[0])]
        self.zone_matrix.append(fila)       # antes: fila.copy(), una copia inútil

# get_collides puede devolver el set directamente: ya no hay orden que preservar
def get_collides(self, id_obj):
    mi_rect = self.objects[id_obj]["rect"]
    return {o for o in self.get_objects_in_zone(id_obj)
            if rect_colition(mi_rect, self.objects[o]["rect"])}
```

**Probado de verdad.** Implementé este `update_element` en un script aparte (sin tocar la librería), 30 objetos y 500 movimientos aleatorios, y la rejilla queda **idéntica** a reconstruirla desde cero. También comprobé que el test de propiedad de arriba pasa con el `add_element`/`move_obj` actuales, así que sirve de red antes de cambiar nada.

**Coste.** `update_element` cambia el valor de retorno de `move_obj` (antes `None`); si algún código hacía `if move_obj(...)`, revisa esos usos. El diff de zonas es correcto solo si `"zones"` y `zone_matrix` no se desincronizan nunca: por eso el test de propiedad no es opcional.

---

## OPT-06 — Superficies y blits 📖💭

- `pag.Surface(size)` sin más crea una superficie en el formato "genérico". Una vez creada y si no cambia, `convert()` (opaca) o `convert_alpha()` (con alfa) la pone en el formato de la pantalla y los blits pasan a ser copia de memoria. Para las superficies internas de `Input`/`Text` que se reutilizan, esto es dinero.
- Si un widget es opaco, `set_colorkey` suele ser más barato que alfa por píxel.
- `last_rect.union(self.rect.copy())` — `union` **ya devuelve un `Rect` nuevo**; el `.copy()` previo es una asignación extra por widget y por frame.
- En `Text.draw` haces `self.rect_border.move(diff_pos)` varias veces por frame; calcula el desplazamiento una vez.
- `Base` tiene ~20 atributos por instancia y no usa `__slots__`. Con miles de widgets eso pesa en memoria, pero **rompe `Base.copy()`** (que hace `__dict__.update`). Si algún día lo haces, cambia `copy()` a un `__copy__` explícito.

**Cómo podría quedar**:

```python
# superficies internas que se reutilizan: al formato de la pantalla, una sola vez
self.input_surface = pag.Surface(self.rect2.size).convert()

# union() ya devuelve un Rect nuevo; el .copy() previo sobra
self.last_rect = self.last_rect.union(self.rect_border)

# un desplazamiento calculado una vez por frame, no por línea
salto = self.rect_border.move(diff_pos)
```

`convert()` necesita que el display esté inicializado. Si puedes crear el widget antes de `set_mode`, guarda la superficie y llama a `convert()` en el primer `draw()`.

---

## OPT-07 — Bucle de eventos 📖💭

- `pag.event.get()` devuelve **todos** los eventos, incluidos los que nunca usas (`WINDOWFOCUS*`, `AUDIO*`, `JOY*`...). `pag.event.set_blocked([...])` para los que no manejas reduce allocaciones por frame.
- `sorted(enumerate(...), reverse=True)` aparece muchas veces para recorrer en orden Z inverso. Funciona **solo** porque los índices son únicos: si alguna vez se repiten, Python intentará comparar los objetos y lanzará `TypeError`. Usa `key=lambda p: p[0]` y duerme tranquilo. Es gratis.
- En `Animator.update` el borrado se hace con `sorted(enumerate(to_del), reverse=True)`, que ordena pares `(posición, índice)` y funciona por casualidad (porque `to_del` ya viene ascendente). `for i in reversed(to_del): pop(i)` es más corto, más rápido y no depende de esa casualidad.

**Cómo podría quedar**:

```python
# una vez, al inicializar la app: bloquea lo que nunca miras
pag.event.set_blocked([
    pag.WINDOWENTER, pag.WINDOWLEAVE, pag.AUDIODEVICEADDED,
    pag.AUDIODEVICEREMOVED, pag.JOYAXISMOTION, pag.JOYBALLMOTION,
    pag.JOYHATMOTION, pag.JOYBUTTONUP, pag.JOYDEVICEADDED,
])
# ojo: NO bloquees WINDOWFOCUSLOST/TAKEFOCUS/RESIZED ni MOUSEMOTION, que sí usas

# orden Z inverso sin comparar objetos
for i, x in sorted(enumerate(controles), key=lambda p: p[0], reverse=True):
    ...

# Animator: borrado independiente del orden de los índices
for i in reversed(to_del):
    self.list_funcs.pop(i)
```

---

## OPT-08 — Lo que **no** optimizaría todavía

- `Second_Order_Dinamics` está bien: `__slots__`, integración estable, clamp de `dt`. No lo toques.
- `maths.line_to_polygon_intersection` con spatial hashing es correcto por diseño; primero mide si tu juego lo llama lo suficiente como para importar.
- `Vector2` propio frente a `pygame.Vector2`: el tuyo con `__slots__` evita el puente Python↔C por atributo, pero pierde las operaciones vectorizadas de pygame. **Mide los dos** en el caso real (mover 1.000 partículas) antes de decidir. No hay respuesta universal.

---

# 2. Corrección

Última pasada: 25-10-2026. Ya resueltos y probados, fuera de esta lista para no arrastrarlos: BUG-01, BUG-02, BUG-03, BUG-04, BUG-05, BUG-06, BUG-07, BUG-08, BUG-09, BUG-10, BUG-11..13, BUG-14, BUG-15, BUG-16, BUG-17, BUG-18, BUG-19, BUG-20, BUG-21, BUG-22, BUG-23, BUG-24, BUG-25 y UNITS-01.

Los de abajo salieron de usar las librerías **desde fuera** (las tres apps), que es donde no llegan los tests actuales. Todos están reproducidos con un script suelto y el resultado está en la fila, así que van con ✅.

| ID | Estado | Dónde | Qué pasa |
|---|---|---|---|
| BUG-26 | ✅ | `base_app_class.py` → `__init__` | `pag.display.get_wm_info()['window']` lanza `KeyError: 'window'` con `SDL_VIDEODRIVER=dummy`: la app no se puede crear headless y el banco de pruebas de `OPT-00` no llega a arrancar. |
| BUG-27 | ✅ | `bloque.py` → `move_objs`, `collide` | `move_objs` sale en `if not self.scroll_y: return`, así que con scroll horizontal pero no vertical el `inside_height` del eje X se queda en 1 y la barra no aparece nunca. Y `collide` solo mira a los hijos, no a su propio `rect`: un `Bloque` vacío no colisiona con la ventana y `draw_optimized` lo salta sin dibujarlo. |
| BUG-28 | ✅ | `Barras_progreso.py` → `pulsando` | Rama horizontal: `self.rect.w = self.rect2.left + m_x` debería ser `m_x - self.rect2.left`. Medido con la barra en x=100 y ancho 200: clic en x=150 y clic en x=250 dan **volumen 1.0** los dos. En vertical funciona. |
| BUG-29 | ✅ | `texts/multilist.py` → `__init__` | `Multi_list((100,100),(10,10))` con los valores por defecto revienta: `AttributeError: 'NoneType' object has no attribute 'height'` al leer `self.listas[0].text_header.height`, porque `header=True` y `header_text=None`. Solo funciona pasando `header_text` o `header=False`. |
| BUG-30 | ✅ | `texts/text.py` → setter de `size` | El setter recrea la fuente pero no le repone el subrayado (el setter de `font` sí lo hace). Medido: con `underline=True`, la fuente nace subrayada y tras `size = 48` `get_underline()` da `False` mientras `texto.underline` sigue diciendo `True`. |
| BUG-31 | ✅ | `obj_Base.py` → `copy` | Copia bien `rect`/`pos`/animación, pero las listas quedan **compartidas**: `lista_text` y `lista_text_rects` son el mismo objeto en original y copia. Medido: copiar un `Text` multilínea y cambiarle el texto deja 7 rects en el original, cuyo texto no cambió. `Select_box` y `mini_GUI.select` viven de `Text.copy()`. |
| BUG-32 | ✅ | `texts/app_menu.py`, `graficas/grafico_barras.py` | `App_menu.draw` y `Grafico_Barras.draw` devuelven `None` → `for s in r` lanza `TypeError: 'NoneType' object is not iterable` dentro de `draw_optimized`. Además `Barra` llama `Second_Order_Dynamics(60,2,1.0,1.1,(0,0))` con 5 argumentos (la clase toma 4), así que no se puede ni instanciar, y `Grafico_Barras` no está exportado. |
| BUG-33 | ✅ | `image.py` → `draw` | La rama `redraw < 2` devuelve `[self.rect_border]` **sin** `diff_pos`; la otra sí lo aplica. Medido con `diff_pos=(30,30)`: devuelve `(45,45)` y después `(75,75)`. Dentro de un `Bloque` con scroll ensucia el rect equivocado. |
| BUG-34 | ✅ | `Utilidades/multithread.py` → `Interval_funcs.__start_func` | Si la función del intervalo lanza, el hilo muere y el intervalo **deja de existir en silencio**: medido, 1 ejecución y `is_alive()` en `False`, sin log. En `V_download` eso son tres intervalos que pueden desaparecer sin avisar. |
| BUG-35 | ✅ | `texts/list.py`, `texts/input.py`, `texts/select_box.py` | No aceptan `diff_pos` y `Select_box` ni siquiera tiene `pos`, así que no pueden ir dentro de un `Bloque`: `TypeError: List.draw() got an unexpected keyword argument 'diff_pos'` y `AttributeError: 'Select_box' object has no attribute 'pos'`. |

## Correcciones, con código

Un bloque por fila de la tabla. Son **el cambio mínimo**, no el parche final: van escritos contra el código de esta fecha y algunos tocan firmas. Donde hay una trampa, la digo debajo.

### BUG-26 · `hwnd` cuando no hay ventana real

```python
self.hwnd: int|None = pag.display.get_wm_info().get('window')
```

Y donde se usa (`take_window_snapshot` del F12, `win32_tools.front2`), comprobar `if self.hwnd is None: return`. Es lo que desbloquea el banco de `OPT-00` y cualquier test de la app entera.

### BUG-28 · la barra horizontal

```python
elif self.__orientacion == 'horizontal':
    rel = m_x - self.rect2.left                 # antes: self.rect2.left + m_x (en las tres ramas)
    self.rect.w = min(max(rel, 0), self.__size.x)
```

Es el mismo patrón que ya usas en vertical (`rect2.bottom - m_y`), solo que con el signo bien. Ojo con un detalle aparte que vi al medirlo: `pulsando()` ignora el `mouse_pos` que recibe y lee `pag.mouse.get_pos()`. En la app coincide, pero hace que la barra no se pueda probar sin ventana real.

### BUG-30 · el subrayado al cambiar de tamaño

```python
self.__font = pag.font.Font(self.raw_font, self.__size)
self.__font.set_underline(self.__underline)      # ← lo que falta
```

### BUG-29 · cabecera sin texto

```python
# en Multi_list.__init__, antes del bucle de columnas
header_h = self.listas[0].text_header.height if (self.header and self.listas[0].text_header) else 0
# y usar header_h en las dos líneas que hoy hacen .text_header.height
```

### BUG-34 · un intervalo que sobrevive a sus errores

```python
from .logger import debug_print        # multithread no importa logger: no hay ciclo

def __start_func(self, alias, stop: Event):
    while not stop.wait(self.task_dict[alias]['time']):
        try:
            self.task_dict[alias]['func']()
        except Exception:
            debug_print(f'intervalo {alias} lanzó una excepción', priority=3)
```

Así el intervalo sigue vivo y te enteras. Si prefieres que muera, al menos que lo diga en el log: hoy el `Thread` escupe el traceback a stderr y el objeto queda como si estuviera funcionando.

---

# 3. Consistencia y API

## API-01 — `redraw` merece un tipo, no números mágicos 📖

**Qué pasa.** `redraw` es un entero con significados distintos según la clase y el sitio:

- `Text.create_rect` hace `+= 3`; `Base.direccion` hace `+= 2`; `pos.setter` hace `+= 1`; `Text.update` hace `+= 2`.
- Al dibujar, cada clase interpreta `< 1`, `< 2` y el resto como "nada / solo yo / yo y mi rect viejo".
- `draw_optimized` usa `re < 2` para decidir si hay que repintar lo de debajo.

Eso es un protocolo implícito repartido en 8 archivos. Funciona porque lo llevas en la cabeza; en cuanto pasen dos semanas, no.

**Qué probar, sin cambiar el comportamiento:**

1. Un `IntEnum` (`CLEAN = 0`, `SELF = 1`, `MOVED = 2`, `FULL = 3`) o simplemente constantes con nombre en `constants.py`.
2. Métodos en `Base`: `mark_dirty()` (yo), `mark_moved()` (yo + rect viejo), `mark_full()` (todo).
3. Un test que afirme la invariante: tras `draw()`, `redraw == CLEAN`; tras `pos=`, `redraw >= MOVED`; etc.

Esto no acelera nada, pero **elimina la clase de bug más molesta de un framework de UI** (restos visuales intermitentes). Es la recomendación de diseño que más valor tiene de toda la lista.

**Cómo podría quedar**:

```python
# constants.py
from enum import IntEnum

class Redraw(IntEnum):
    CLEAN = 0      # no hay nada que dibujar
    SELF  = 1      # cambió mi apariencia: repintar mi rect
    MOVED = 2      # cambié de sitio: mi rect + el anterior (limpiar el hueco)
    FULL  = 3      # todo (cambio de pantalla, resize)

# obj_Base.Base
def mark_dirty(self):
    if self.redraw < Redraw.SELF:
        self.redraw = Redraw.SELF

def mark_moved(self):
    if self.redraw < Redraw.MOVED:
        self.redraw = Redraw.MOVED

def mark_full(self):
    self.redraw = Redraw.FULL
```

Detalle que hoy se pierde: `redraw += 2` sobre un objeto que ya vale 3 lo deja en 5. Sigue funcionando porque solo comparas `< 1` y `< 2`, pero el número ya no significa nada. Con `mark_*` el estado nunca se sale de rango y puedes escribir el test de invariantes sin ambigüedad.

## API-02 — El contrato de un widget no está escrito 📖

`draw_optimized`, `goto`, `on_mouse_click_general` y compañía esperan de cada objeto: `redraw`, `draw(surface)`, `update(mouse_pos, dt)`, `collide(rect)`, `visible`, `pos`, `hover`, `update_hover()`, `click()`, `eventos_teclado()`, `use_mouse_motion`, `use_mouse_wheel`... Eso está en tu cabeza y en `consideraciones.txt`, no en el código.

**Qué probar.** Un `typing.Protocol` (`Widget`) con los métodos obligatorios y los opcionales documentados, y `isinstance` con `runtime_checkable` solo en un test que verifique que todos tus widgets lo cumplen. Además te da autocompletado y errores en el editor sin cambiar una línea de lógica.

## API-04 — `__init__` que arranca el bucle 📖

**Lo que descarto.** Pygame no tiene multiventana: `pygame.display` es único por proceso, y una segunda ventana exige otro `Process` con su propio `pag.init()` y su propio estado (para hablar entre procesos ya tienes `for_socket`). Así que "dos ventanas en la misma app" no es un objetivo de diseño: fuera de la lista y anotado en `consideraciones.txt` para no darle más vueltas.

**Lo que sí cuesta.** Sin llegar a eso, que `__init__` termine en `screen_main()` tiene tres efectos reales:

1. No puedes construir la app sin entrar al bucle: un test de integración se queda colgado en el primer frame.
2. `pag.quit()` dentro del constructor mata SDL antes de devolverte el objeto: la instancia ya no sirve para dibujar un frame, reabrir ni inspeccionarse.
3. `Base_class` no se puede usar como pieza dentro de otro programa que gestione su propio display y su propio `quit()`.

Nada de eso es "cambiar cosas después de crear la ventana": es poder crear la app **sin ejecutarla**.

**Qué probar.** `__init__` construye; `run()` arranca el bucle y limpia. Con `autostart=True` por defecto tus scripts actuales no cambian; con `autostart=False` montas la app, mueves objetos, dibujas un frame y la cierras — el requisito de los tests headless de §5.

```python
def __init__(self, config=None, autostart: bool = True, **kwargs) -> None:
    ...
    self.post_init()
    self.goto(self.actual_screen)
    if autostart:
        self.run()

def run(self) -> int:
    try:
        self.screen_main()
    finally:                       # cubre cierre normal y error
        self.on_exit()
        pag.quit()
    return self.config.returncode
```

**Coste:** unas 10 líneas y un parámetro con default. Si no vas a escribir tests de la app entera, es prescindible; el resto del documento no depende de esto.

## API-05 — Windows en el paquete "general" 📖

`base_app_class.py` importa `win32gui`/`win32con` a nivel de módulo (y usa GDI para la transparencia). Las dos consecuencias: la lib no arranca en Linux/Mac, y el import de la clase base falla con un error de `ModuleNotFoundError` que no explica nada. `Utilidades/constants.py` incluso contiene `BITMAPINFOHEADER`/`BLENDFUNCTION`, y `Logger.open_folder` usa `os.startfile`.

**Qué probar.** Mover la parte Windows al paquete de pygame o a `win32_tools`, e importar **dentro** de la función que la usa. Para la transparencia, un backend por plataforma con `NotImplementedError` claro ("la ventana transparente no está implementada en Linux todavía"). Fallar con un mensaje honesto es infinitamente mejor que fallar al importar.

```python
# base_app_class.py — fuera los imports de win32gui/win32con del nivel de módulo
import sys

# dentro de __init__, solo cuando se pide transparencia
if self.config.window_transparent:
    if sys.platform != 'win32':
        raise NotImplementedError(
            'window_transparent todavía no está implementado fuera de Windows'
        )
    import ctypes
    import win32gui, win32con
    gdi32 = ctypes.WinDLL('gdi32')
    user32 = ctypes.WinDLL('user32')
    ...
```

Ojo: `gdi32 = ctypes.WinDLL('gdi32')` también está a nivel de módulo y también revienta fuera de Windows. Todo lo que sea GDI tiene que vivir dentro de esa rama o en un backend aparte.

## API-08 — Código duplicado que ya divergió 📖

`figuras/*` y `Animaciones.py` existen **dos veces**, una por librería, y ya no son iguales (esa duplicación ya causó un bug real). `Bloque`/`scroll`/`Multi_list` se solapan en funcionalidad. `Logger` reimplementa `logging` (sin niveles, sin rotación, sin lock en la escritura, sin flush).

**Qué probar.** Una sola fuente de verdad y reexportar desde la otra librería. Para `Logger`: envolver `logging` (20 líneas) en vez de mantener el tuyo; te llevas handlers, rotación, niveles y thread-safety gratis.

**Ya no es solo duplicado: los contratos divergieron.** Verificado leyendo las dos versiones.

| Miembro | `Utilidades` | `Utilidades_pygame` | Consecuencia |
|---|---|---|---|
| `Curva_de_Bezier.update` | devuelve `Vector2` siempre, y `is_finished()` aparte | devuelve `True` al acabar | `obj_Base` y `Select_box` comprueban `r == True`: con la versión de `Utilidades` **la animación no termina nunca** (siempre recibe un `Vector2`) |
| `Simple_acceleration.follow` | multiplica por 60 | no multiplica | la misma llamada va 60× más rápido en una librería, y las dos se llaman igual |

No hace falta arreglarlo hoy: basta con que sepas que importar `Curva_de_Bezier` del paquete equivocado no da error, solo una animación que se queda a medias. Si algún día unificas, el contrato bueno es el de `Utilidades` (`is_finished()` explícito) y adaptar los dos `r == True`.

## API-09 — `**kwargs` se traga los errores de escritura 📖✅

**Qué pasa.** `Text`, `Button`, `Input`, `List`, `Multi_list`, `Bloque`, `Screen_scroll`... aceptan `**kwargs` y no comprueban las claves. Un nombre mal escrito no falla: se pierde.

**Medido**, y es el caso real de tus apps:

```
List((100,100), (10,10), ["a"], smothscroll=True)   -> smoothscroll sigue en False, sin aviso
lista.smothscroll = True                             -> crea un atributo suelto, la property no cambia
```

Eso deja el "modo bajo consumo" de `Acelerador` sin efecto en las cinco llamadas que pasan `smothscroll=`. Es el peor tipo de regresión: la app arranca, el botón se pulsa y no pasa nada.

**El arreglo mínimo**, cinco líneas al final del `__init__` de cada clase con kwargs:

```python
sobrantes = set(kwargs) - set(getattr(self, 'kwargs_validos', ()))
if sobrantes:
    raise TypeError(f'argumentos desconocidos: {", ".join(sorted(sobrantes))}')
```

O, si prefieres no listar lo válido, un `pop` explícito por clave en vez de `kwargs.get(...)` para las que importan. Cuesta poco y te encuentra los renombrados el día que los haces.

## API-10 — El contrato de `draw` no es el mismo en todos 📖✅

Existen tres firmas distintas y tres formas de devolver, y el bucle llama a todas igual:

| Clase | Firma | Devuelve |
|---|---|---|
| `Text`, `Button`, `Bloque`, `Image` | `draw(surface, always_draw=False, diff_pos=(0,0))` | `list[Rect]` — `Image` olvida `diff_pos` en la rama `< 2` (BUG-33) |
| `List` | `draw(surface, always_draw=False)` | `list[Rect]` |
| `Input` | `draw(surface)` | `list[Rect]` |
| `Multi_list` | `draw(surface)` | `tuple[Rect]` |
| `Select_box` | `draw(surface, always_draw=False)` | `list[Rect]` |
| `mini_GUI.Base` / `select` | `draw(surface)` | **un `Rect` suelto** |
| `App_menu`, `Grafico_Barras`, `Multilist` | `draw(surface)` | **`None`** |

Consecuencias medidas: `for s in App_menu.draw(...)` lanza `TypeError`; `list(mini_GUI.Base.draw(...))` da `[0, 0, 0, 0]` y `display.update` lo acepta como un rect de área cero (el popup se dibuja pero nunca entra en el dirty rect, así que deja restos al moverse); `List` dentro de `Bloque` lanza `TypeError` por el `diff_pos` (BUG-35).

El contrato que ya usas en `Text`/`Image`/`Bloque` funciona. Lo barato es hacer que todos lo cumplan:

```python
def draw(self, surface, *, always_draw=False, diff_pos=(0, 0)) -> list[pag.Rect]:
    if always_draw:
        self.redraw = 2
    if self.redraw < 1:
        return []
    ...
    return [self.rect, r] if self.redraw > 1 else [self.rect]
```

Y `App_menu`/`Grafico_Barras` devolviendo la lista de rects que ya podrían calcular (hoy dibujan y tiran esa información).

---

# 4. Empaquetado y estructura

## PKG-01 — Salir de `site-packages` 📖

Ahora mismo el código vive en `Python313/Lib/site-packages/Utilidades` y `.../Utilidades_pygame`. Cualquier reinstalación/reparación de Python se los lleva por delante, y no hay forma de trabajar en las dos a la vez sin `pip install -e`.

**Qué probar.**

```
Utilidades/        (repo, ya tiene .git ✅)
Utilidades_pygame/ (repo, ya tiene .git ✅)
  pyproject.toml
  src/Utilidades_pygame/...
  tests/
```

`pip install -e .` desde cada carpeta. Si las quieres juntas, un repo con dos paquetes (`packages = ["Utilidades", "Utilidades_pygame"]`) o un `requirements` con `-e ../Utilidades`.

## PKG-02 — `pyproject.toml` y versión 📖

Falta lo mínimo para que sea instalable y reproducible:

- `[project] name/version/description/requires-python`;
- `requires-python` tiene que ser **`>=3.12`**, no 3.11: usas `typing.override` (`mini_GUI/base.py`) y f-strings con las mismas comillas dentro y fuera (`List.__str__`, PEP 701). En 3.11 la librería no compila;
- dependencias reales: `Utilidades_pygame` **importa `Utilidades`** pero su `requirements.txt` solo tiene `pygame` y `platformdirs`;
- `Utilidades` usa `pywin32`/`pystray`/`Pillow`/`certifi`/`colorama`/`platformdirs` — márcalas con `platform_system` como ya hiciste en el `requirements.txt` (bien hecho), pero eso en `pyproject` se expresa con marcadores de entorno;
- **falta `psutil`** en `requirements.txt`: `linux_tools.py` lo importa a nivel de módulo, así que en Linux la librería no arranca hasta instalarlo. En Windows no se nota porque ese módulo no se importa;
- `__version__` en el `__init__` (el README dice 2.3.0 y el código no lo sabe);
- un `classifiers`/`keywords` básicos si algún día lo publicas.

**Esqueleto de `pyproject.toml`** (uno por repositorio, este es el de pygame):

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "Utilidades-pygame"
version = "2.3.0"
description = "Framework de UI y utilidades sobre pygame"
requires-python = ">=3.12"
dependencies = [
    "pygame>=2.5",
    "platformdirs>=4",
    "Utilidades>=2.3",          # importas Utilidades: es dependencia real, no opcional
]

[project.optional-dependencies]
dev = ["pytest>=8", "hypothesis>=6", "ruff", "pyright"]

[tool.setuptools.packages.find]
include = ["Utilidades_pygame*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

El nombre del proyecto y el del paquete pueden diferir; lo que no puede diferir es la versión entre `pyproject` y `__version__`. Ponle un test que compare las dos y no vuelvas a pensarlo.

## PKG-03 — Imports con efectos secundarios 📖

Corrección a lo que decía antes: **medido hoy, los imports son silenciosos**. `import Utilidades` + `import Utilidades_pygame` no escriben nada en stdout (el único texto es el banner de pygame). Se ve que ya limpiaste los `print`, así que este punto baja a dos detalles menores: `logger.py` llama a `colorama.init()` a nivel de módulo (modifica el stdout global de quien importe) y `Config()` crea dos carpetas al construirse, lo cual es razonable pero conviene saberlo. La regla general sigue en pie: **un import no debería crear carpetas ni tocar la consola.**

## PKG-04 — Tipado 📖

Tienes anotaciones (bien), pero con ruido: `Hipotenusa(...) -> int` devuelve un `float`, `@property`/`@x.setter` con tipos distintos, `Literal[False]` en `click` de `Text` (siempre `False`) mezclado con `click` que sí hace cosas, `Particle.angle` anotado como `Vector2` y devolviendo `float`, `collide_all(self, lista) -> str`. Pasar `pyright --basic` o `mypy` una vez te da una lista larga pero muy barata de arreglar, y te encuentra usos de `None` que hoy revientan en runtime (`Multi_list` con header, por ejemplo).

## PKG-05 — Nombres que no salen del paquete 📖✅

Hay código terminado al que no se puede llegar desde `import Utilidades`. Medido con `hasattr(uti, nombre)`:

| Nombre | `hasattr(uti, ...)` | Dónde vive |
|---|---|---|
| `Interval_funcs` | ❌ | `uti.multithread.Interval_funcs` (así lo usa `base_app_class`) |
| `notacion_cientifica`, `Angulo_radians`, `Angulo_solo` | ❌ | `uti.maths.*` |
| `fibonacci`, `calcular_pendiente`, `calcular_centroide`, `calcular_integral`, `rect_get_center` | ❌ | `uti.maths.*` |
| `Animator` | ✅ pero es el **módulo**, no la clase | `uti.Animator.Animator` |

Y en `Utilidades_pygame/graficas/__init__.py` solo se exporta `Graficador`: `Grafico_Barras` y `Barra` son inalcanzables desde el paquete (y además no se pueden instanciar, BUG-32).

Lo mismo, en pequeño, con `GUI/__init__.py`: exporta `Desicion` e `Info` pero no `Classic_window`, que es la clase de la que heredan las dos. `up.GUI.Classic_window` no existe; hay que ir a `up.GUI.objs.Classic_window`.

**Qué probar.** Añadirlos al `from .x import` y al `__all__`. Para `Animator`, decidir si quieres `uti.Animator` como clase (como `Logger`, `Collision_handler`) o como módulo; hoy es el único módulo suelto en el `__init__`.

---

# 5. Tests y CI

## TST-01 — pytest ya está, úsalo ✅

Hay dos carpetas de tests, escritas y en verde. Desde `site-packages`:

```
python -m pytest Utilidades/test Utilidades_pygame/tests -q
```

Estado al 25-10-2026: **97 tests, todos en verde en un par de segundos**. Los tres bugs que aparecieron al escribirlos ya están arreglados y sus tests siguen ahí: lo que hoy es una regresión fue ayer un bug, y así no vuelve.

| Carpeta | Archivos | Qué cubre |
|---|---|---|
| `Utilidades/test/` | `test_maths`, `test_mytime`, `test_animaciones`, `test_multithread`, `test_collision_handler` | puro, sin pygame |
| `Utilidades_pygame/tests/` | `test_figuras`, `test_texts` | headless, `SDL_VIDEODRIVER=dummy` |

Lo que hace que no sean frágiles:

- `Deltatime` se prueba con un `perf_counter` falso vía `monkeypatch`: 0.02 s son 0.02 s siempre, sin `sleep` ni depender de la máquina.
- Las animaciones se miden con `dt` explícito; ningún test mide fps reales.
- El `conftest.py` de cada carpeta añade `site-packages` a `sys.path`, y el de pygame fija los drivers *dummy* **antes** de importar pygame.
- La única espera real está en `multithread` (hilos y timers), con timeouts de 5 s.

Pirámide, para lo que queda: (1) puro —hecho—, (2) headless —hecho en figuras y `Text`—, (3) golden, (4) propiedades con `hypothesis`.

## TST-02 — Lo que falta de la pirámide 📖

- `Base.copy()` no debe compartir `rect` ni animación entre el original y la copia.
- Un golden para detectar regresiones visuales (abajo).
- `hypothesis` para `rect_collision`, `line_to_polygon_intersection` y `calcular_pendiente`: son funciones puras y aquí brillan de verdad.

Golden, cuando tengas algo estable que no quieras romper sin enterarte:

```python
# tests/test_visual.py
import hashlib
import pygame as pag
from Utilidades_pygame import Text

def test_texto_renderiza_igual():
    surf = pag.Surface((200, 60))
    surf.fill((0, 0, 0))
    Text("hola", 24, pos=(100, 30)).draw(surf)
    digest = hashlib.md5(pag.image.tobytes(surf, "RGB")).hexdigest()
    assert digest == "REEMPLAZA_ESTO"      # el valor se saca en la primera ejecución
```

No pongas el hash a ciegas: execute el test una vez, mira que la imagen sea la correcta y copia el valor. Un golden sin revisar solo congela el bug.

## TST-03 — CI 📖

GitHub Actions: matriz `windows-latest` × `ubuntu-latest`, Python 3.11/3.12/3.13, `pip install -e ".[test]"`, `pytest -q`. En Linux, `SDL_VIDEODRIVER=dummy` en el `env`. Es media hora de trabajo y te dice si `win32gui` se coló en un import.

---

# 6. Hoja de ruta sugerida

Ordenado por **impacto / riesgo**. No es obligatorio seguirlo, pero cada paso es independiente y verificable.

| # | Qué | IDs | Riesgo | Por qué ahora |
|---|---|---|---|---|
| 1 | Los diez bugs de §2 que rompen widgets | BUG-26..35 | Ninguno | Cada uno está reproducido con un comando; son bugs, no decisiones de diseño. |
| 1b | Montar el CI | TST-02, TST-03 | Ninguno | El suelo ya está puesto (97 tests): queda el golden y saber que las libs importan en Linux. |
| 2 | Quitar el re-render por frame de `Input` | OPT-04 | Bajo | La mejora más barata que hay. |
| 3 | Medir + arreglar el doble bucle | OPT-00, OPT-01 | Medio | Aquí está el techo de escalabilidad de la UI. |
| 4 | Medir texto con `font.size` + caché | OPT-03 | Bajo | Segundo mayor gasto, y aislado en un archivo. |
| 5 | Formalizar `redraw` | API-01 | Bajo | Evita la clase de bug más cara de depurar. |
| 6 | `pyproject.toml` + salir de `site-packages` | PKG-01, PKG-02 | Bajo | Trabajar cómodo y no perder el código. |
| 7 | Separar `run()` de `__init__` | API-04 | Medio | Desbloquea tests headless de la app entera. |
| 8 | Una sola fuente de verdad | API-08 | Medio | Evita que vuelva a divergir. |

## Lo que no cambiaría

- La idea del dirty-rect con `display.update(rects)`: es la decisión correcta para UI.
- `Second_Order_Dynamics` y `Curva_de_Bezier` como clases separadas con la misma interfaz (`update(dt)`, `is_finished()`): es composición limpia.
- `Collision_handler` con rejilla uniforme y sets de ids: elegante y suficiente.
- `consideraciones.txt`: es el mejor documento del proyecto. Promovido a `docs/` y con un ejemplo por widget, vale más que cualquier README.

---

# Apéndice A — Comandos de reproducción

Los bugs de §2 no necesitan comando suelto: cada uno se reproduce con un par de líneas (los que no son de pygame) o con la suite (desde `site-packages`):

```
python -m pytest Utilidades/test Utilidades_pygame/tests -q
```

Cuando aparezca uno nuevo, añade aquí su comando y conviértelo en test (`TST-02`) en vez de dejarlo en la terminal. Así la lista de §2 nunca vuelve a caducar.

# Apéndice B — Checklist

Copia esta sección a medida que avances (o marca aquí mismo).

**Corrección** (solo lo pendiente; lo resuelto no se lista)
- [ ] BUG-26..35 — los diez de §2 (uno por commit, con su test)

**Optimización**
- [ ] OPT-00 benchmark
- [ ] OPT-01 doble bucle
- [ ] OPT-02 `fill` por frame
- [ ] OPT-03 medir texto sin render
- [ ] OPT-04 `Input` por frame
- [ ] OPT-05 `move_obj`
- [ ] OPT-06 superficies
- [ ] OPT-07 eventos

**Deuda**
- [ ] API-01 `redraw` con nombre
- [ ] API-02 `Protocol` de widget
- [ ] API-04 `run()` separado
- [ ] API-05 Windows aislado
- [ ] API-08 fuente única
- [ ] PKG-01..04 empaquetado
- [ ] TST-02 lo que falta de la pirámide
- [ ] TST-03 CI
