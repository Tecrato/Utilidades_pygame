# Perfil de código — cómo trabajas tú, para que la IA no te haga perder tiempo

> Revisión del **26/10/2026**. Fuentes: `Utilidades` (4.280 líneas), `Utilidades_pygame` (5.513),
> las tres apps que me dejaste — `Acelerador-de-descargas` (~3.800), `Buscaminas` (~250 + copia
> vendorizada de las libs) y `BrickBricker` (~3.700) — y el curso completo
> (`Documents\curso de programacion\Python`: 599 archivos propios, 74.598 líneas).
> Python 3.13.15, pygame 2.6.1.
>
> Este documento **no propone cambios**: describe lo que ya haces, con evidencia del código, para que
> cualquier IA (yo incluido, en la próxima sesión) escriba código que encaje a la primera.
> Las propuestas de mejora viven en `recomendaciones_de_la_IA.md` y llevan ID (`OPT-`, `BUG-`...).

---

## 0. Regla cero

**El código es tuyo.** La IA lee, mide, propone y escribe documentos; **no edita las librerías ni las
apps sin un "hazlo" explícito**. Cuando se autoriza un arreglo, el flujo que ya funcionó es:

1. reproducir el fallo con un número o un test;
2. decir el cambio mínimo y su coste;
3. esperar tu versión (tú primero; la IA solo entra si te atascas);
4. si la IA lo toca, dejar el test en verde y borrar la entrada del documento.

Las únicas zonas de edición libre son `recomendaciones_de_la_IA.md`, este archivo y
`Utilidades_pygame/tests/` + `Utilidades/test/`.

---

## 1. Los dos paquetes y quién manda

| Paquete | Rol | Tamaño | Depende de |
|---|---|---|---|
| `Utilidades` | Base sin pygame: matemáticas, tiempo, hilos, red, colisiones, figuras | 4.280 líneas | `pywin32`, `colorama`, `certifi`, `platformdirs` (+ `psutil` en Linux, ver PKG-02) |
| `Utilidades_pygame` | Framework de UI sobre pygame: bucle, widgets, dirty rects, figuras | 5.513 líneas | `pygame`, `platformdirs`, **`Utilidades`** |

**La dirección de la dependencia es sagrada:** `Utilidades_pygame` importa `Utilidades`, nunca al
revés. Se ve en `Utilidades_pygame/config_default.py`, que usa `Utilidades.maths.Vector2` para la
resolución; y es la razón de que `figuras/` esté duplicado: la versión de pygame usa
`pygame.Vector2` porque va más rápido, y la de `Utilidades` no puede permitirse importar pygame.

Cuando dudes dónde va algo: si necesita `import pygame`, va a `Utilidades_pygame`; si no, a
`Utilidades`.

---

## 2. Las tres apps como banco de pruebas

Cada una prueba una cosa distinta. Sirven para saber qué API toca de verdad y cuál es decorativa.

| App | Usa `Base_class` | Qué demuestra |
|---|---|---|
| `Acelerador-de-descargas` | sí, a fondo | multi-ventana real con `Process`, `Func_pool`, `class_intervals`, `Multi_list`, `Select_box`, `Mini_GUI`, i18n, servidor Flask local |
| `Buscaminas` | sí, pero con trampa | `draw_mode = "always"` + `draw_before` para pintar el tablero a mano; el resto son `Text` |
| `BrickBricker` | **no** | bucle y máquina de estados propios; de la lib solo usa widgets sueltos (`Text`, `Button`, `List`, `Particles`, `Spark`) |

Conclusión útil: **`Base_class` no es obligatorio para usar los widgets.** El protocolo de `draw()`
tiene que funcionar también cuando lo llamas tú a mano, fuera del bucle optimizado. Eso es lo que hoy
rompen `App_menu` y `Grafico_Barras` (BUG-32).

`Buscaminas` además lleva una copia vendorizada de las dos librerías en `lib/`, congelada. Por eso
sigue funcionando aunque las libs hayan cambiado de nombres. Es una decisión defendible para un
ejecutable que reparte: la copia es reproducible. El coste es que no recibe ningún arreglo.

---

## 3. Convenciones de nombres

No es un estándar escrito, pero es consistente y conviene imitarlo.

| Patrón | Significado | Ejemplos reales |
|---|---|---|
| Español para dominio y UI | lo que ve el usuario o el negocio | `descargas`, `cola`, `hilos`, `guardar`, `apagar`, `txts`, `lista_palabras`, `extenciones` (clave de config, se queda así) |
| Inglés para infraestructura y API | lo que imita a pygame | `draw`, `update`, `click`, `collide`, `redraw`, `last_rect`, `visible`, `hover` |
| `btn_`, `text_`, `list_`, `input_`, `select_`, `img_` | tipo de widget en el nombre | `btn_main_new_descarga`, `text_config_hilos`, `list_main_descargas` |
| `func_` | callback de un widget | `func_toggle_ldm`, `func_change_idioma` |
| `pv_` | `Process` | `pv_updating_url`, `pv_cola_finalizada` |
| `_algo` / `__algo` | privado / name-mangling | `_pos` en figuras, `__size` en `Text` |
| `raw_` | el valor sin transformar | `raw_text`, `raw_font`, `raw_pos` |
| `default_` | valor de fábrica, restaurable | `default_controles_adyacentes`, `default_border_color` |
| `use_` | capacidad activable | `use_mouse_motion`, `use_mouse_wheel` |
| `is_` / `has_` | booleano derivado, no guardado | `is_hover`, `is_revealed`, `is_fitted` |
| `on_` | callback entrante del sistema | `on_exit`, `on_wheel`, `on_key_down`, `on_mouse_motion` |
| `MAYÚSCULAS` | constante de módulo | `RETURNCODE_FINISH`, `DICT_CONFIG_DEFAULT`, `TILE_SIZE`, `ANIMATION_SPEED` |

Detalles que se repiten:

- **`TypedDict`/`NamedTuple` para cargas estructuradas**, no dicts sueltos: `Animation_Future`
  (`Animator.py`), `ObjectInfo` (`collision_handler.py`), `Bloque(NamedTuple)` y `Music_return`
  (`BrickBricker/constantes.py`).
- **`@override`** (de `typing`, 3.12+) al redefinir un hook del framework. Eso fija el mínimo de
  Python en 3.12, no 3.11.
- **Sin `abc`, sin `Protocol`, sin dataclasses en el código de pygame.** `dataclass` solo aparece en
  `Deltatime`, donde el valor es el dato y no el comportamiento.
- **Sin acentos ni `ñ` en identificadores**; sí en textos y comentarios.
- Comentas **el porqué y el riesgo**, no el qué:
  `# Si ya casi no se mueve, clávalo en el objetivo para que la animación acabe.`

---

## 4. El esqueleto canónico de una ventana

El 90 % de tu UI es esta forma. Una IA que escriba esto a la primera no te hace revisar nada:

```python
from typing import override
import pygame as pag
import Utilidades as uti
import Utilidades_pygame as uti_pag

from Utilidades_pygame.base_app_class import Base_class
from constants import Config, DICT_CONFIG_DEFAULT
from textos import idiomas


class Ventana_algo(Base_class):
    def otras_variables(self):          # 1. estado propio, antes de crear objetos
        self.cosas: list = []

    def load_resources(self):           # 2. configuración, red, ficheros
        self.configs = uti.get('http://127.0.0.1:5000/get_configurations').json
        self.idioma = self.configs.get('idioma', DICT_CONFIG_DEFAULT['idioma'])
        self.txts = idiomas[self.idioma]

    def generate_objs(self):            # 3. construir y registrar widgets
        self.text_titulo = uti_pag.Text(self.txts['title'], 18, self.config.font_mononoki,
                                       (self.ventana_rect.centerx, 20))
        self.btn_aceptar = uti_pag.Button(self.txts['aceptar'], 14, self.config.font_mononoki,
                                         (self.ventana_rect.centerx, 100), func=self.exit)

        self.registrar_pantalla('otra')   # ← solo si hay más de una pantalla

        self.lists_screens["main"]["draw"].extend([self.text_titulo, self.btn_aceptar])
        self.lists_screens["main"]["update"].extend(self.lists_screens["main"]["draw"])
        self.lists_screens["main"]["click"].extend([self.btn_aceptar])

    def post_init(self):                # 4. lo que necesita la ventana ya creada
        if self.enfoques:
            uti.win32_tools.front2(self.hwnd)

    def otro_evento(self, actual_screen, evento):   # 5. teclas y ratón propios
        if evento.type == pag.KEYDOWN and evento.key == pag.K_ESCAPE:
            self.exit()

    @override
    def exit(self):                     # 6. limpiar antes de morir
        try:
            uti.get('http://127.0.0.1:5000/descargas/cancel_update/url')
        except Exception as err:
            uti.debug_print(err, 2)
        return super().exit()


if __name__ == '__main__':              # 7. cada ventana se abre sola para probarla
    Ventana_algo(config=Config(window_resize=False, resolution=(400, 125)))
```

Reglas implícitas de ese esqueleto, que conviene respetar:

1. **`draw` y `update` apuntan a la misma lista.** No es un descuido: sin `update` el widget no
   procesa sus animaciones (`smoothmove`, hover, scroll). `click` sí va aparte.
2. **Al construir se puede usar `.extend()`; al regenerar, asignar** (`[...]["draw"] = [...]`). Si
   `generate_objs()` se puede llamar dos veces (cambio de idioma), extender duplica los widgets.
   Está escrito en `consideraciones.txt` y lo cumples.
3. **El orden de la lista es el orden Z**: lo que se añade después se dibuja encima. Por eso los
   `Select_box` van al final.
4. **`draw_before` es para fondo de pantalla**, no para widgets: pinta directo en `self.ventana`
   (así hace Buscaminas con el tablero y Acelerador con el fondo del modal).
5. **`exit()` sobreescrito siempre llama a `super().exit()`** y devuelve su resultado; ahí es donde
   se libera GDI en ventana transparente.
6. **`if __name__ == '__main__'` en cada ventana**: es tu banco de pruebas manual. Vale oro.

---

## 5. Tus cuatro formas de modelar estado

| Patrón | Dónde | Cuándo lo usas |
|---|---|---|
| Banderas booleanas + `if` en `update`/`draw` | `BrickBricker` (`title_screen`, `pausado`, `low_detail_mode`) | juego con pocos modos |
| `while` anidados por modo | `BrickBricker` (`while self.bool_title_extras:`, `while self.pausado:`) | pantallas que se comportan como subprogramas |
| Pantallas registradas + `goto(alias)` | `Acelerador` (`registrar_pantalla`, `goto`, `lists_screens`) | app con navegación de UI |
| Estado dentro del widget + `redraw` | toda la lib (`redraw`, `hover`, `typing`) | animaciones y dirty rects |

El patrón de `goto` lo sobreescribes para meter código al entrar a una pantalla
(`V_principal.goto`: limpia el formulario antes de `super().goto(screen)`). Ese es el punto de
extensión, y por eso no hace falta un sistema de eventos de navegación.

---

## 6. Concurrencia: tus cinco herramientas

| Herramienta | Uso típico | Regla que se deduce |
|---|---|---|
| `Thread(target=..., daemon=True).start()` | una operación de red puntual | daemon siempre, para no bloquear el cierre |
| `Func_pool.add(alias, *funcs)` + `.start(alias)` | secuencia de pasos nombrada (`'descargar'` = conectar y bajar) | los alias se registran en `otras_variables`/`post_init` y se lanzan desde un botón |
| `class_intervals.add(alias, func, seg, start=True)` | trabajo periódico: progreso 0,1 s, velocidad 0,4 s, ETA 1 s (`V_download`) | el intervalo nunca toca widgets sin `app_lock` |
| `self.loading += 1 / -= 1` | bloquear clics mientras se trabaja | **siempre en `try/finally`** |
| `Process(target=Ventana_X, args=(Config(...),))` | una ventana = un proceso | el resultado viaja en `config.returncode`; el proceso hace `sys.exit(config.returncode)` |

Detalles de estilo que ya aplicas bien:

- **`self.args` / `self.kwargs`** como transporte de argumentos a través de `Base_class`
  (`Downloader` lee `self.args[0]`, `self.args[1]`).
- **`config.returncode` como canal de salida** entre procesos: `RETURNCODE_ERROR/FINISH/FINISH_SHUTDOWN`.
- **`self.app_lock`** envuelve el dibujado y lo que un hilo cambia.
- **`self.Func_pool.start('...')` nunca bloquea** el frame; el resultado se ve en la siguiente
  recarga de la lista.

Dónde se te escapa el patrón (anotado, no tocado):

- `V_download.finish_download` hace `self.loading += 1` y el `try` solo cubre la ruta del archivo;
  el bucle que une las partes queda fuera. Si esa unión falla, `loading` se queda en 1 y la app deja
  de responder a clics para siempre (`eventos_en_comun` descarta todo con `loading > 0`).
- `V_principal.func_reload_lista_descargas` sí lo hace bien (`try/except/finally`). Ese es el molde.

---

## 7. Configuración, datos e idiomas

**Configuración por diccionario + tipos.** `DICT_CONFIG_DEFAULT` da los valores y
`DICT_CONFIG_DEFAULT_TYPES` los tipos, para convertir lo que llega de JSON. Los nombres de las
claves son **frases en español con espacios** (`'apagar al finalizar cola'`) porque viajan tal cual
al JSON del servidor y a la UI. No los cambies: rompen configuraciones guardadas.

**`Config` de la app envuelve el de la librería.** Mismo *duck type* (`title`, `resolution`,
`min_resolution`, `max_fps`, `returncode`, `screenshots_dir`...) más campos propios
(`font_mononoki`, `font_symbols`, `config_dir`, `cache_dir`). La librería acepta `**kwargs` y hace
`setattr`, así que añadir un campo es gratis. Ese es el mecanismo de extensión: no hace falta heredar.

**Persistencia:** JSON por HTTP contra el Flask local (fuente única de verdad de la config),
`sqlite3` para descargas, `configparser` (`config.ini`) en Buscaminas. Directorios con
`platformdirs`, nunca rutas relativas al CWD (excepto assets, y ahí hay `os.chdir` al inicio).

**i18n:** `textos.py` con `textos_español` / `textos_ingles`, claves en español y en minúsculas
(`'bajo consumo'`, `'añadir a la cola'`). En la ventana: `self.txts = idiomas[self.idioma]` y
`self.txts['clave']`. Falta-traducción se resuelve con `.get('clave', 'texto por defecto')`.

---

## 8. Errores y diagnóstico

- **`uti.debug_print(x, priority=n)`** es tu `print` con nivel: 0 Debug, 1 Info, 2 Warning,
  3 Error, 4 Critical. Imprime archivo y línea del llamador, y saca el traceback si `priority >= 2`
  y hay excepción activa. Por eso es verboso: está pensado para eso.
- **`except Exception as err:` + `debug_print` + seguir o `raise`**. Cuando el fallo es visible al
  usuario, aparece un `Mini_GUI.aviso1` en la esquina y el error se relanza
  (`func_reload_lista_descargas`).
- **`try/finally`** para contadores (`loading`) y para liberar recursos.
- Excepciones desnudas (`except:`) o `except: pass` en sitios puntuales; están localizadas y no
  propagan. Si algún día quieres una lista, `ruff`/`pyright` las sacan todas en una pasada.
- En las apps, el texto de los errores es para ti, no para el usuario final; el usuario ve un
  mensaje corto desde `textos.py`.

---

## 9. Qué espera el framework de un widget (el contrato real)

No está escrito en el código, está repartido. Esta es la tabla; si algún día escribes el `Protocol`
de API-02, este es su contenido.

| Miembro | Quién lo llama | Obligatorio | Si falta |
|---|---|---|---|
| `redraw: int` | bucle, `Bloque`, `Text` | sí | `AttributeError` en `draw_optimized` |
| `draw(surface) -> list[Rect]` | bucle, `Bloque`, `Mini_GUI` | sí | se rompe el dirty rect |
| `update(mouse_pos=..., dt=...)` | `update_general` | sí (en la lista `update`) | `TypeError` |
| `collide(rect) -> bool` | `draw_optimized`, `Bloque` | sí | no se dibuja nunca |
| `collide_rect` | `collide_all` | recomendado | — |
| `is_hover(pos)` / `update_hover(pos)` | ratón, navegación por teclas | sí para `click` | no hay hover |
| `click(pos)` | `on_mouse_click_general` | sí en la lista `click` | — |
| `pos`, `topleft`, `center`, `width`, `height` | layout, `Bloque` | práctica | `Bloque.add` revienta |
| `visible` | todos los bucles | sí | se asume `True` con `getattr` |
| `use_mouse_motion`, `use_mouse_wheel` | eventos | opcional (`getattr`) | — |
| `keys_using`, `on_key_down`, `on_key_up` | teclado | opcional | no captura teclas |
| `on_wheel(delta)` | rueda | opcional | — |
| `cursor: int` | cursor del ratón | opcional | se queda la flecha |

Heredar de `obj_Base.Base` te da **todo menos `draw`**. `Text`, `Image` y `Bloque` lo implementan;
`Particle`, `Spark`, `Particles`, `Graficador`, `App_menu` y `Select_box` no heredan y lo emulan a
mano — y ahí están las inconsistencias (ver API-10).

---

## 10. Estado real de las tres apps contra las librerías de hoy

Verificado con `grep` sobre el código de las apps y con la suite de las libs (**101 tests, 2,2 s**;
101 en verde (el 27-10-2026 se arregló el `BUG-36` de figuras). Las apps **no** están cubiertas por tests, y
es justo el hueco donde aparecen estos desajustes:

| Nombre que usan las apps | Nombre de hoy | Dónde | Efecto |
|---|---|---|---|
| `Hipotenuza` | `Hipotenusa` | `Buscaminas/main.py`, `BrickBricker.py` (×4), `BrickBricker2.py`, `snake.py` (×2), `lvl_creator.py` | `ImportError` / `AttributeError` al arrancar |
| `Second_Order_Dinamics` | `Second_Order_Dynamics` | `BrickBricker/player.py` | `ImportError` al importar el jugador |
| `smothscroll=True` | `smoothscroll` | `V_principal.py` (×3), `V_download.py`, `BrickBricker.py`, `BrickBricker2.py` | **no falla**: entra por `**kwargs` y se ignora → el modo bajo consumo deja de desactivar el scroll suave |
| `.smothscroll = ...` (atributo) | `.smoothscroll` (property) | `V_principal.py:814` | se crea un atributo suelto; la property no cambia |

Dos consecuencias prácticas:

1. **Romper nombres fue una decisión tuya y está bien** (las erratas eran peores), pero conviene
   saber el estado exacto: `BrickBricker` **no arranca** (`ImportError: cannot import name 'Hipotenuza'`),
   y `Acelerador` **sí arranca** —todas sus importaciones existen— pero su modo bajo consumo está
   muerto en silencio porque `smothscroll` entra por `**kwargs`. Ese caso es peor que el
   `ImportError`, y es API-09.
2. Para volver a arrancar las apps solo hay que renombrar esos usos; no hay lógica que dependa del
   nombre viejo. `Buscaminas` seguirá funcionando por su copia en `lib/` aunque no lo toques.

---

## 11. Cómo escribir para ti (lista operativa para la IA)

1. **Español** en comentarios, docstrings y nombres de dominio. Inglés en la API que imita pygame.
2. **No añadas dependencias.** `math`, `itertools`, `collections`, `ctypes` y lo que ya está.
3. **No refactorices de paso.** Un cambio, un motivo, un commit por librería.
4. **No introduzcas `logging`, `attrs`, `pydantic` ni frameworks.** Tu `Logger` y tus `TypedDict`
   son la casa.
5. **Docstring de clase con `### More options`** cuando el widget acepta `**kwargs` por nombre
   (`Text`, `Button`, `List`, `Multi_list`, `Screen_scroll`). Es tu forma de documentar sin firmas
   gigantes.
6. **Tipos siempre**, aunque Python no los compruebe. `@override` al redefinir hooks.
7. **Nada de `print`** en las librerías; `debug_print` con prioridad.
8. **Si mides algo, da el número.** Si no lo mediste, dilo ("hipótesis"). Ya está marcado así en el
   otro documento con 📖/💭/✅.
9. **Erratas: se corrigen una vez y se aceptan los rotos.** Nada de alias de compatibilidad
   (`Hipotenuza = Hipotenusa`) para no arrastrar dos nombres para siempre.
10. **Windows primero.** `win32gui`, GDI y `os.startfile` son parte del producto, no un accidente;
    lo que sí conviene es que el resto siga importando fuera de Windows (API-05).
11. **No toques `consideraciones.txt` sin avisar**: es la documentación real del framework.
12. **Antes de proponer un cambio de API, mira las tres apps.** Si rompe las tres, el coste hay que
    decirlo en la misma frase que la propuesta.

---

## 12. Deudas de estilo que sí merecen una pasada

Ninguna es "estética": todas han producido ya un error real o lo producirán.

- **Los argumentos posicionales largos.** `Button('', 26, font, (0,0), 10, 'topright', 'white',
  (20,20,20), (50,50,50), 0, -1, border_width=-1)`: doce posicionales donde el 10 es `padding` y el
  -1 es `border_radius`. Funciona porque lo escribiste tú; para cualquiera (o para ti en un mes) es
  opaco. La propuesta está en API-02/API-09: dejar los 4 primeros posicionales y el resto
  keyword-only es un cambio de una línea por firma, pero **rompe todas las llamadas de las apps**, así
  que decide tú el momento.
- **`**kwargs` que se traga los errores de escritura.** Es la causa de que `smothscroll` no avise.
  Un `kwargs.pop` explícito, o un `raise TypeError(f'argumento desconocido: {k}')` al final, cuesta
  cinco líneas por clase y convierte un fallo silencioso en uno de un segundo.
- **`eval` en `Select_box`.** Las animaciones se guardan como cadenas y se evalúan al abrir
  (`dict_animations`). Funciona porque las cadenas las escribes tú, pero no se puede leer ni
  depurar, y un `eval` dentro de una librería es un olor fuerte.
- **Import muerto**: `from turtle import delay` en `Buscaminas/main.py` (además arrastra Tk).
- **Duplicados por copia**: `Animator` existe en `Utilidades` y otra vez en `Buscaminas/Animator.py`
  (con otra firma); `figuras/` y `Animaciones.py` en las dos librerías, ya divergentes (API-08).
- **`except:` desnudo** en 6 sitios de las libs; sustituirlo por `except Exception:` es gratis y no
  cambia el comportamiento salvo para `KeyboardInterrupt`/`SystemExit`, que sí quieres dejar pasar.

---

## 13. Lo que no te discutiría

- **Dirty rects con `display.update(rects)`**: es la decisión correcta, y el `redraw` 0/1/2 es un
  protocolo que funciona. Solo le falta el nombre (API-01).
- **`Second_Order_Dynamics`** con `__slots__` e integración estable: está mejor que la mayoría del
  código de animación que se ve por ahí. No lo toques.
- **`Collision_handler`** con rejilla uniforme y sets de ids: suficiente y sin dependencias.
- **`Config` como bolsa de atributos**: para una app de un solo autor es más rápido que un esquema
  formal, y el `setattr` de `**kwargs` te deja crecer sin tocar la librería.
- **`draw_mode = "always"`** en juegos: con cientos de objetos que se mueven cada frame, el dirty
  rect solo añade trabajo. Elegirlo por app y no por librería está bien.
- **Bucle propio en `BrickBricker`**: un juego con `while` por estado se lee mejor que la misma
  máquina metida en hooks. El coste es no tener la navegación por teclado ni el `loading` gratis.
- **Copia vendorizada en `Buscaminas/lib/`**: para un .exe que reparte, la copia congelada es
  reproducible. Solo hay que saber que no recibe arreglos.

---

## 14. Historia: de dónde viene todo esto

> Pasada del **26/10/2026** por `C:\Users\Edouard\Documents\curso de programacion\Python`:
> **599 archivos `.py` propios** (sin `.venv`, sin `Ejemplos` de terceros), **74.598 líneas**, 2,8 MB.
> Se inventariaron todos (tamaño, docstring, imports, duplicados por hash) y se leyeron completos
> los que explican la evolución. Esta sección es el *porqué* del código de hoy; las propuestas
> siguen en `recomendaciones_de_la_IA.md`.

### 14.1 Las etapas, en orden

| Etapa | Archivos testigo | Qué se ve |
|---|---|---|
| **1. Fundamentos** | `Numeros.py`, `numeros2.py`, `numeros3.py`, `Metodos de cadenas.py`, `cosas_random/p2/` | `print` de todo, variables de una letra (`a`, `b`, `q`), listas/dicts/sets, `for`/`while`/`break`/`else`, funciones con `*args`/`**kwargs`, decoradores. La curiosidad por el lenguaje antes que por el programa. |
| **2. Pygame crudo** | `Pygame/Inicio.py` | 34 líneas: `while True` + `clock.tick(60)` + `fill` + `flip` + dos `Rect`. Ese esqueleto aparece **113 veces** en el curso. |
| **3. Primer framework** | `Pygame/inicio remastered.py` | Ya está *todo*: clase con `load_resources` / `generate_objs` / `move_objs` / `eventos_en_comun` / `main_cycle`, listas `list_to_draw`, `list_to_click`, `redraw` global y `display.update(rects)`. Es literalmente el antecesor de `Base_class`, con dos intentos que luego se cayeron: `ciclo_general` + `cicle_try` (navegar entre pantallas sin anidar bucles) y un `isinstance` por tipo dentro del bucle de dibujo. De ahí salieron `goto()` y el método `draw()` uniforme. |
| **4. Primer `Text`** | `Pygame/Juegos/Tower Defense/Utilidades/text.py`, `.../"Texto con superficies"/text.py`, `aplicaciones/inventario sencillo/NegocioV3/Utilidades/text.py` | `Create_text` con `mode = 1` (una línea) y `mode = 2` (lista de `Create_text` por línea). El multilínea nació **creando un widget por línea** y de ahí pasó a `lista_text` de superficies. Ya están `padding` como `Vector2`, `border_radius == 10000` para “redondo”, `with_rect`, `color_rect` y el `try/except` para detectar si el texto es una lista. Casi todos los `**kwargs` actuales vienen de aquí. |
| **5. Animación** | `NegocioV2.py` (dentro de una app de inventario), luego `Utilidades/Animaciones.py` | `Second_Order_Dinamics` escrita a mano en el archivo, con `k1/k2/k3`, `k2_stable` y `Vector2`. Después se movió a la librería y se le puso `__slots__`. No es una librería que encontraste: la derivaste y la probaste dentro de una app real. |
| **6. Colisiones** | `pruebas variadas/colicion_check_manager/` (dos versiones) | La v1 (`Colition_check_manager`) guarda listas de aristas, nodos adyacentes y objetos por zona, y busca la zona moviéndose por distancia. La v2 (`Collision_handler`) tira todo eso y se queda con rejilla uniforme + `dict` de objetos + `set` de ids. La comparación de los dos archivos es la decisión de diseño: **menos flexibilidad, más velocidad**. |
| **7. Rendimiento** | `Pygame/test FPS/`, `Pygame/prueba_modernGL/rendimiento*.py`, `Pygame/pruebas/pruebas_poligonos_rendimiento.py` | Medías FPS a mano (`1/(end-start)`), probaste **caché de 181 rotaciones** (`img_cached = [rotate(img, x) for x in range(181)]`), `ventana.blits(...)`, un `Thread` que actualiza a `sleep(1/60)`, shaders con moderngl, raylib, y 900 polígonos dibujados con `draw_after` + `pag.draw.polygon` **saltándote el `draw()` de cada figura** porque era más rápido. De ahí viene tu obsesión (correcta) por el coste por frame y por el dirty rect. |
| **8. Primer layout** | `Pygame/UI maker/` | Clase `Base` que **envuelve** un widget y reexporta `pos/left/center/...`, con `pos_type='zone_rel'` y `reset_pos()` que calcula la posición como porcentaje del tamaño de la zona. Es el primer intento de layout declarativo; quedó en experimento, pero es el antecesor de `dire` y de `move_objs`. También ahí aparece el patrón de duplicar la property `pos` dos veces seguidas (copiar/pegar). |
| **9. Era de apps** | `API's/`, `aplicaciones/`, `Juegos/`, `flet/`, `HTML/`, `raylib/`, `IA/`, `Autoclicker/`, `Seguridad/` | Acelerador (Flask + SQLite + procesos + i18n), Buscaminas, BrickBricker, Tamagotchi, Minimarket, TecraTools, Regedit Changer, File transfer (flet), Django, FastAPI, sockets, Telegram, OpenCV, warp/numba, Cython, ctypes, Tkinter. Cada carpeta es un experimento aislado, no un producto. |

### 14.2 Cómo evolucionó `Base_class` (mismo archivo, dos épocas)

Comparando `Juegos/Tamagotchi/Utilidades_pygame/base_app_class.py` (515 líneas) con el de hoy:

| Antes | Ahora | Qué cuenta |
|---|---|---|
| `def __init__(self, config: Config = Config(), ...)` | `config: Config\|None = None` | El default mutable se sustituyó por `None`: un `Config` compartido entre instancias era una bomba. |
| `self.relog` | `self.clock` | Renombraste a un nombre que se lee mejor. |
| `navegate_with_keys` | `navigate_with_keys` | Errata corregida, sin alias de compatibilidad. |
| `self.screen_main()` directo en el constructor | `if autostart: self.run()` | Lo que acabas de autorizar: construir no es ejecutar. `run()` además envuelve en `try/finally`. |
| `self.app_lock.acquire()` / `.release()` a mano | `with self.app_lock:` | Si `draw` lanzaba, el lock se quedaba tomado y la app se congelaba. |
| `self.hwnd = pag.display.get_wm_info()['window']` | `.get('window')` | Un `KeyError` en headless; ahora es `None` y quien lo usa lo comprueba. |
| Sin `on_keyup_general`, sin `exit()` con GDI, sin `window_transparent` | Todo eso | La app creció por casos reales (cerrar liberando GDI, teclas mantenidas, transparencia). |
| `update_general` actualizaba widgets y luego llamaba a `self.update()` | `update()` propio va **antes** | Cambio deliberado: tu lógica mueve cosas y los widgets ven el estado nuevo en el mismo frame. |
| `move_hover` solo `Button`/`Input` | `accept_to_move_with_arrows`, con `Barra_de_progreso` | La navegación por teclado se generalizó a un tipo configurable. |

Ese diff es el mejor resumen de cómo trabajas: **no diseñas el framework en abstracto, lo extraes de una app que ya funciona**. Todo lo que hoy tiene `Base_class` existía antes dentro de `Tower Defense`, `Buscaminas` o `Acelerador`.

### 14.3 Lo que el corpus dice de tu forma de aprender

Contando **todas** las copias del curso (incluidas las vendorizadas):

| Señal | Veces | Lectura |
|---|---|---|
| `print(` | 1 029 | El curso entero es un cuaderno de laboratorio; las libs ya no imprimen. |
| `debug_print` | 207 | El sustituto llegó para quedarse: prioridad, archivo y línea. |
| `while True` | 113 | Bucle crudo primero; `Base_class` vino después. |
| `pag.time.Clock` | 91 | El FPS siempre estuvo controlado. |
| `display.flip()` / `display.update(` | 100 / 32 | Se ve el cambio de “pinto todo” a “pinto rects”. El segundo ganó en las libs. |
| `except:` desnudo / `except Exception` | 144 / 160 | El desnudo es de la época de pruebas; en las libs conviven los dos. |
| `eval(` / `exec(` | 57 / 10 | Casi todos de `Select_box` y experimentos. Es el olor más fuerte que queda. |
| `os.chdir` | 32 | Cada app se pone en su carpeta de assets al arrancar. Explica por qué las rutas relativas funcionan en tus apps y no en una librería. |
| `Thread(` / `Process(` | 105 / 24 | Concurrencia de verdad, no de juguete: descargas por partes y ventanas en procesos. |
| `lru_cache` / `__slots__` | 29 / 12 | Las dos optimizaciones que sí usas; el resto es medir y simplificar. |
| `cProfile` / `perf_counter` | 0 / 21 | Mides **a mano**, con `perf_counter` y contadores de FPS, nunca con el perfilador. Es el hueco más grande de tu método, y lo que llena `benchmarks/`. |

### 14.4 Patrones que se repiten y conviene saber

- **Cada juego acaba con su copia de la librería.** `Buscaminas/lib/`, `Tamagotchi/Utilidades*/`, `Tower Defense/Utilidades/`, `NegocioV3/Utilidades/`. Hay **20 archivos idénticos** entre carpetas. No es descuido: es congelar lo que funciona para no romper el juego mientras la librería cambia. El coste ya lo conoces (los arreglos no llegan).
- **Copia-pegar-adaptar es el método.** Se ve en `UI maker/Cosas/Base.py` (la property `pos` duplicada dos veces), en `Create_text` (`mode 1`/`mode 2`) y en las versiones de `collision_handler`. Cuando algo funciona, se clona y se poda; no se reescribe desde cero.
- **Español para el negocio, inglés para la API.** `descargas`, `cola`, `hilos`, `perro`, `hambre`; `draw`, `update`, `click`, `redraw`. Se mantiene desde `Numeros.py` hasta hoy.
- **Los nombres largos y explícitos llegan tarde.** En el curso joven: `a`, `b`, `q`, `lol`, `cosas`. En las libs: `letter_pos`, `desplazamiento_smooth`, `default_controles_adyacentes`. La mejora es real y es tuya.
- **Los comentarios empiezan a explicar el porqué**, no el qué: `# Si ya casi no se mueve, clávalo en el objetivo para que la animación acabe.` Eso es lo que hay que conservar.
- **Todo lo que sabes de rendimiento salió de un experimento propio**: caché de rotaciones, `blits`, hilos de update, moderngl, raylib, 900 polígonos dibujados a mano. Por eso el banco de `benchmarks/` tiene sentido: es la versión ordenada de esos scripts sueltos.

### 14.5 Desajustes esperables en el curso (no se toca nada)

Como avisaste, hay nombres viejos y código a medias. Los más útiles para entender por qué la librería cambió:

- `Hipotenuza` → `Hipotenusa`, `smothmove`/`smothscroll` → `smoothmove`/`smoothscroll`, `Second_Order_Dinamics` → `Second_Order_Dynamics`, `navegate_with_keys` → `navigate_with_keys`. Los archivos del curso se quedaron con los viejos; las libs ya no.
- `Utilidades.Create_boton`, `Utilidades.Text`, `Utilidades.Input_text` (funciones fábrica) → clases `Button`, `Text`, `Input`. El `UI maker` es el único sitio que usa las fábricas.
- `Pygame/Juegos/Tower Defense/Utilidades/Texto con superficies/text.py` y `text.py` son dos intentos del mismo widget; el bueno es el de superficies, que es el que sobrevivió en `texts/text.py`.
- Hay archivos que no parsean (`cosas_random/prueba maquida de estados finito`, `Transformada_de_Fourier(DFT)`, `matematicas/regresion lineal multiple/ejemplo1.py`, `API's/get_from_api.py`): son borradores, no código en uso.

---

## Apéndice — cómo se comprobó

```
# suite de las dos librerías (desde site-packages), 26-10-2026
python -m pytest Utilidades/test Utilidades_pygame/tests -q
# → 101 passed (el 27-10-2026: figuras arregladas con la opción 2 del BUG-36)

# banco de pruebas, headless
python Utilidades_pygame/benchmarks/run_all.py
BENCH_BIG=1 python Utilidades_pygame/benchmarks/run_all.py

# inventario del curso: 599 .py propios, 74.598 líneas, duplicados por sha1
# (script de una sola pasada, solo lectura: tamaño, docstring, imports, hashes)

# todo lo demás se comprobó con scripts sueltos en el temporal, sin tocar las librerías:
#   Barra_de_progreso horizontal, Text.size/underline, Text.copy, Multi_list por defecto,
#   Image.draw con diff_pos, App_menu/Grafico_Barras devolviendo None, Interval_funcs con excepción,
#   Logger sin close, get_wm_info() con SDL dummy, kwargs desconocidos.
```
