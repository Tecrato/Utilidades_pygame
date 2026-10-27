# Resultados del banco de pruebas

Generado por `benchmarks/run_all.py` el **27-10-2026 01:54**.

Todo se mide **headless** (`SDL_VIDEODRIVER=dummy`): no hay ventana real, así
que el coste de presentar es casi cero y las cifras de dibujado son las de
Python + pygame, no las de la GPU. Sirven para comparar **antes y después** de
un cambio en la misma máquina, no como número absoluto de otro equipo.

## Cómo leer las tablas

- **media / mediana / p95** en milisegundos, de `200` frames por prueba
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
5. **`Bloque` no descansa nunca**: su `draw()` no baja `redraw`, así que
   redibuja a todos los hijos en cada frame aunque no haya cambiado nada.
6. **El bucle limpio escala lineal** con el número de objetos: ~0,7 µs por
   objeto y frame solo en `collide()` + `draw()`. Un millón de objetos en la
   lista de dibujo no cabe en 16 ms ni de lejos (medido: ~700 ms); una `List`
   de un millón de elementos es otra cosa (solo blitea lo visible), pero
   **crea una superficie por elemento**: ~3,1 KB y ~14 µs de creación por
   elemento, o sea ~3 GB y ~14 s para el millón.

## Entorno

- Python 3.13.15 (AMD64)
- pygame 2.6.1 / SDL 2.28.4
- Windows 10
- CPUs: 4

## Tablas

### Text

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 Text (1 línea)                      1.314     1.344     1.357      761
crear 50 Text (1 línea)                      6.483     6.437     6.854      154
crear 200 Text (1 línea)                    27.554    27.654    28.418       36
crear 1000 Text (1 línea)                  142.387   141.725   146.315        7
crear Text (párrafo 200 palabras)            5.324     5.100     7.575      188
cambiar texto de un párrafo                  0.004     0.004     0.004   270270
dibujar 50 Text, nada sucio (optimized)      0.237     0.213     0.366     4214
dibujar 50 Text, 1 sucio (optimized)         0.311     0.285     0.449     3215
dibujar 50 Text, todos sucios (always)       0.681     0.626     0.919     1469
dibujar 50 Text, todos sucios, sin presentar     2.501     2.315     3.339      400
dibujar 200 Text, nada sucio (optimized)     0.568     0.423     1.496     1760
dibujar 200 Text, 1 sucio (optimized)        1.020     0.954     1.352      980
dibujar 200 Text, todos sucios (always)      2.226     2.077     2.902      449
dibujar 200 Text, todos sucios, sin presentar    30.035    27.167    41.408       33
dibujar 1000 Text, nada sucio (optimized)     0.796     0.706     1.313     1256
dibujar 1000 Text, 1 sucio (optimized)       4.254     3.900     6.050      235
dibujar 1000 Text, todos sucios (always)     8.424     8.345     9.452      119
dibujar 1000 Text, todos sucios, sin presentar   137.863   131.088   175.049        7
medir 100 cadenas con font.size()           23.236    21.582    34.128       43
medir 100 cadenas con font.render()         31.641    30.002    39.016       32

### Button

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 Button                              0.822     0.761     1.215     1216
dibujar 10 Button, nada sucio                0.193     0.171     0.272     5182
dibujar 10 Button, todos sucios              0.517     0.426     1.040     1935
hover on/off de 10 Button                    0.009     0.009     0.009   114983
crear 50 Button                              4.598     4.032     7.591      217
dibujar 50 Button, nada sucio                0.257     0.218     0.467     3892
dibujar 50 Button, todos sucios              1.572     1.393     2.574      636
hover on/off de 50 Button                    0.042     0.043     0.048    23822
crear 200 Button                            17.827    17.583    19.101       56
dibujar 200 Button, nada sucio               0.339     0.306     0.509     2951
dibujar 200 Button, todos sucios             4.596     4.144     6.528      218
hover on/off de 200 Button                   0.169     0.175     0.194     5929
hover de 1 Button (solo cambio de estado)     0.003     0.002     0.002   340252
dibujar 1 Button tras hover                  0.203     0.173     0.365     4923

### Input

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 1 Input                                0.919     0.888     1.169     1088
dibujar 1 Input, always (re-render por frame)     0.246     0.210     0.439     4070
dibujar 1 Input, always, sin presentar       0.227     0.207     0.359     4401
update de 1 Input (dt=1/60)                  0.001     0.001     0.001  1434720
crear 10 Input                               9.913    10.123    11.494      101
dibujar 10 Input, always (re-render por frame)     0.829     0.609     1.853     1206
dibujar 10 Input, always, sin presentar      0.797     0.559     1.906     1255
update de 10 Input (dt=1/60)                 0.003     0.003     0.003   351062
crear 50 Input                              48.621    48.300    53.143       21
dibujar 50 Input, always (re-render por frame)     2.297     1.885     4.128      435
dibujar 50 Input, always, sin presentar      2.853     2.093     5.908      351
update de 50 Input (dt=1/60)                 0.012     0.012     0.013    80772
escribir 1 letra (add_letter)                0.123     0.116     0.143     8154
escribir 20 letras seguidas                  1.898     1.776     2.439      527
borrar 20 letras seguidas                    2.063     1.944     2.618      485
dibujar 1 Input (always)                     0.227     0.209     0.360     4397

### List

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear List con 10 elementos                  8.099     7.902    12.696      123
dibujar List(10), sin cambios                0.228     0.188     0.402     4393
dibujar List(10), sucia (blit de lo visible)     0.731     0.591     1.404     1367
scroll List(10) (on_wheel -15)               0.150     0.130     0.271     6659
select List(10)                              0.152     0.139     0.211     6585
append a List(10) + regenerar alto           0.275     0.242     0.406     3635
crear List con 100 elementos                 5.066     5.116     5.684      197
dibujar List(100), sin cambios               0.218     0.181     0.362     4579
dibujar List(100), sucia (blit de lo visible)     0.834     0.680     1.806     1199
scroll List(100) (on_wheel -15)              0.276     0.241     0.451     3617
select List(100)                             0.283     0.243     0.490     3538
append a List(100) + regenerar alto          0.285     0.244     0.529     3513
crear List con 1000 elementos                5.216     5.208     6.147      192
dibujar List(1000), sin cambios              0.205     0.180     0.344     4872
dibujar List(1000), sucia (blit de lo visible)     0.705     0.625     1.040     1418
scroll List(1000) (on_wheel -15)             0.283     0.245     0.443     3530
select List(1000)                            0.283     0.243     0.568     3527
append a List(1000) + regenerar alto         0.294     0.244     0.437     3405
update List(1000) con smoothscroll (dt=1/60)     0.004     0.004     0.005   228232
scroll + draw List(1000) smoothscroll        0.798     0.687     1.561     1253
List: bytes por elemento                 1.0 KiB/elem
List vacía (widget + superficie 300x400) 506.6 KiB/lista

### Bloque

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear Bloque con 10 hijos                    1.761     1.517     3.048      568
dibujar Bloque(10), sin scroll               0.996     0.868     1.853     1004
dibujar Bloque(10) forzado (always)          1.066     0.971     1.906      938
scroll + update + draw Bloque(10)            1.018     0.910     1.824      982
move_objs de Bloque(10) (tras scroll)        0.030     0.026     0.043    33061
crear Bloque con 50 hijos                   10.084    10.016    11.419       99
dibujar Bloque(50), sin scroll               1.202     1.047     2.047      832
dibujar Bloque(50) forzado (always)          1.357     1.091     2.684      737
scroll + update + draw Bloque(50)            1.544     1.399     2.404      648
move_objs de Bloque(50) (tras scroll)        0.116     0.103     0.131     8637
crear Bloque con 100 hijos                  27.526    26.812    41.383       36
dibujar Bloque(100), sin scroll              1.283     1.029     2.753      779
dibujar Bloque(100) forzado (always)         1.185     1.032     2.048      844
scroll + update + draw Bloque(100)           3.066     1.845     8.323      326
move_objs de Bloque(100) (tras scroll)       0.825     0.251     4.558     1213

### Image

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear Image 800x600 sin escalar              0.019     0.017     0.034    52798
crear Image 800x600 → 400x300                0.241     0.234     0.304     4147
crear Image 800x600 → 400x300 girada 30°     0.924     0.797     1.626     1083
Image grande: size = (400, 300)              0.001     0.001     0.001  1490313
Image grande: alternar size 400x300 / 300x400     0.352     0.324     0.615     2840
Image icono 64x64: alternar size 32x32 / 48x48     0.015     0.013     0.027    64696
Image grande: alternar angle 45° / 0°        4.013     4.300    10.027      249
Image icono: alternar angle 45° / 0°         0.065     0.026     0.050    15446
animar ángulo de imagen grande (un frame)     0.829     0.778     1.348     1206
animar ángulo de icono (un frame)            0.029     0.029     0.032    34210
dibujar 100 Image (nada sucio)               0.317     0.284     0.552     3151
dibujar 100 Image (todos sucios)             0.847     0.772     1.319     1181
dibujar Image 800x600 (nada sucio)           0.224     0.219     0.315     4460
dibujar Image 800x600 (sucia)                0.471     0.445     0.635     2122

### Figuras

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 PoligonoRegular                     0.109     0.108     0.120     9136
dibujar 10 PoligonoRegular (nada sucio)      0.186     0.169     0.251     5389
dibujar 10 PoligonoRegular (todas sucias)     0.278     0.251     0.409     3602
girar 10 PoligonoRegular (regenera vértices)     0.084     0.061     0.126    11976
crear 100 PoligonoRegular                    1.236     1.133     1.886      809
dibujar 100 PoligonoRegular (nada sucio)     0.303     0.267     0.482     3304
dibujar 100 PoligonoRegular (todas sucias)     0.957     0.880     1.349     1045
girar 100 PoligonoRegular (regenera vértices)     0.655     0.610     0.879     1526
crear 1000 PoligonoRegular                  13.799    13.721    16.745       72
dibujar 1000 PoligonoRegular (nada sucio)     0.818     0.684     1.426     1223
dibujar 1000 PoligonoRegular (todas sucias)     9.506     8.033    20.186      105
girar 1000 PoligonoRegular (regenera vértices)     7.153     6.888     8.519      140
crear 100 Engranaje                         11.439     7.367    38.337       87
dibujar 100 Engranaje (nada sucio)           0.303     0.267     0.432     3299
dibujar 100 Engranaje (todos sucios)         3.406     3.031     5.585      294

### Particles

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 partículas                          0.078     0.077     0.085    12770
update 10 partículas (dt=1/60)               0.023     0.021     0.026    44365
draw 10 partículas                           0.241     0.194     0.373     4147
update + draw 10 partículas                  0.250     0.219     0.372     3996
crear 100 partículas                         0.840     0.750     1.254     1191
update 100 partículas (dt=1/60)              0.197     0.187     0.235     5077
draw 100 partículas                          0.415     0.385     0.579     2409
update + draw 100 partículas                 0.592     0.570     0.838     1688
crear 1000 partículas                        8.058     8.083     8.745      124
update 1000 partículas (dt=1/60)             2.042     1.922     2.665      490
draw 1000 partículas                         2.438     2.275     3.322      410
update + draw 1000 partículas                4.127     4.161     5.116      242

### App (bucle completo)

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
escena mixta 10 widgets, nada sucio          0.316     0.292     0.499     3162
escena mixta 10 widgets, 1 sucio             0.347     0.322     0.518     2882
escena mixta 10 widgets, always              0.460     0.421     0.687     2174
escena mixta 50 widgets, nada sucio          0.956     0.884     1.400     1045
escena mixta 50 widgets, 1 sucio             1.125     0.964     1.895      889
escena mixta 50 widgets, always              1.664     1.539     2.404      601
escena mixta 200 widgets, nada sucio         6.844     6.640     8.720      146
escena mixta 200 widgets, 1 sucio            7.415     7.237     9.577      135
escena mixta 200 widgets, always             9.691     9.827    10.649      103
escena 200 sin Input: Base.collide por frame 200 cuenta
escena 200 sin Input, nada sucio             0.471     0.436     0.688     2121
escena 200 con Input: Base.collide por frame 10100 cuenta
escena 200 con Input, nada sucio             6.640     6.410     7.446      151
frame limpio con 1 000 objetos               0.789     0.746     1.013     1267
frame limpio con 1 000 objetos, sin fill     0.606     0.574     0.793     1649
frame limpio con 10 000 objetos              6.652     6.508     7.605      150
frame limpio con 10 000 objetos, sin fill     6.787     6.465     8.188      147
frame limpio con 100 000 objetos            67.109    66.804    69.985       15
frame limpio con 100 000 objetos, sin fill    66.570    66.478    68.458       15
rejilla 200 Text: mover 1, optimized         0.586     0.552     0.815     1707
rejilla 200 Text: mover 1, always            1.776     1.670     2.310      563
rejilla 1000 Text: mover 1, optimized        1.843     1.693     2.824      543
rejilla 1000 Text: mover 1, always           8.125     8.000     8.863      123
update_general con 10 widgets                0.051     0.047     0.065    19509
update_general con 50 widgets                0.227     0.216     0.306     4401
update_general con 200 widgets               0.932     0.866     1.327     1073

### Memoria por widget

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
Fuente suelta: pag.font.Font(None, 16)   45.7 KiB/widget
Text 16px (font=None)                    5.4 KiB/widget
Text 16px (font=Font compartida)         5.4 KiB/widget
Text 16px (font=ruta .ttf)               7.0 KiB/widget
Text párrafo 200 palabras                416.5 KiB/widget
Button 16px (font=None)                  5.5 KiB/widget
Input 16px (font=None)                   64.5 KiB/widget
List: por elemento                       1.4 KiB/widget
Bloque: por hijo                         14.8 KiB/widget
Image: por imagen (surface compartida)   0.6 KiB/widget
Image: por imagen escalada 64→32         5.0 KiB/widget
Particles: por partícula (radio 4)       0.4 KiB/widget
Spark: por chispa                        0.2 KiB/widget

---

Reproducir: `python benchmarks/run_all.py` (desde `site-packages`).
Un solo banco: `python benchmarks/bench_text.py`.
El perfil de 30 frames queda en `benchmarks/bench_app.prof`:
`python -m pstats benchmarks/bench_app.prof` → `sort tottime` → `stats 20`.
