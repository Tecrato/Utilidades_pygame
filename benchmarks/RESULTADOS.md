# Resultados del banco de pruebas

Generado por `benchmarks/run_all.py` el **27-10-2026 02:34**.

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

## Entorno

- Python 3.13.15 (AMD64)
- pygame 2.6.1 / SDL 2.28.4
- Windows 10
- CPUs: 4

## Tablas

### Text

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 Text (1 línea)                      1.317     1.316     1.330      759
crear 50 Text (1 línea)                      6.317     6.318     6.387      158
crear 200 Text (1 línea)                    27.465    27.530    28.686       36
crear 1000 Text (1 línea)                  138.086   138.523   140.260        7
crear Text (párrafo 200 palabras)            5.015     4.889     5.752      199
cambiar texto de un párrafo                  0.004     0.004     0.005   257069
dibujar 50 Text, nada sucio (optimized)      0.230     0.216     0.307     4343
dibujar 50 Text, 1 sucio (optimized)         0.298     0.278     0.421     3350
dibujar 50 Text, todos sucios (always)       0.686     0.643     0.864     1457
dibujar 50 Text, todos sucios, sin presentar     2.583     2.459     3.094      387
dibujar 200 Text, nada sucio (optimized)     0.451     0.406     0.668     2218
dibujar 200 Text, 1 sucio (optimized)        1.013     0.945     1.287      987
dibujar 200 Text, todos sucios (always)      2.196     2.044     2.831      455
dibujar 200 Text, todos sucios, sin presentar    29.778    28.773    34.686       34
dibujar 1000 Text, nada sucio (optimized)     0.874     0.761     1.524     1144
dibujar 1000 Text, 1 sucio (optimized)       4.991     4.387     7.727      200
dibujar 1000 Text, todos sucios (always)     9.378     8.807    11.905      107
dibujar 1000 Text, todos sucios, sin presentar   154.840   153.525   169.578        6
medir 100 cadenas con font.size()           20.163    19.633    22.669       50
medir 100 cadenas con font.render()         31.992    31.431    34.271       31

### Button

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 Button                              0.875     0.780     1.685     1143
dibujar 10 Button, nada sucio                0.209     0.184     0.316     4783
dibujar 10 Button, todos sucios              0.486     0.424     0.900     2056
hover on/off de 10 Button                    0.009     0.009     0.009   115769
crear 50 Button                              4.578     4.179     5.945      218
dibujar 50 Button, nada sucio                0.251     0.220     0.340     3983
dibujar 50 Button, todos sucios              1.597     1.444     2.462      626
hover on/off de 50 Button                    0.045     0.044     0.061    22123
crear 200 Button                            19.403    18.596    24.091       52
dibujar 200 Button, nada sucio               0.333     0.294     0.440     3004
dibujar 200 Button, todos sucios             4.651     4.304     6.118      215
hover on/off de 200 Button                   0.176     0.176     0.238     5675
hover de 1 Button (solo cambio de estado)     0.002     0.001     0.002   574713
dibujar 1 Button tras hover                  0.201     0.164     0.263     4985

### Input

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 1 Input                                1.023     0.876     2.099      978
dibujar 1 Input, always (re-render por frame)     0.236     0.199     0.371     4229
dibujar 1 Input, always, sin presentar       0.242     0.198     0.309     4140
update de 1 Input (dt=1/60)                  0.001     0.001     0.001  1480385
crear 10 Input                              10.493    11.062    11.996       95
dibujar 10 Input, always (re-render por frame)     0.582     0.490     0.739     1717
dibujar 10 Input, always, sin presentar      0.580     0.491     0.784     1725
update de 10 Input (dt=1/60)                 0.003     0.003     0.003   364100
crear 50 Input                              52.041    51.930    54.917       19
dibujar 50 Input, always (re-render por frame)     2.150     1.855     4.108      465
dibujar 50 Input, always, sin presentar      2.145     1.826     4.312      466
update de 50 Input (dt=1/60)                 0.012     0.011     0.013    81666
escribir 1 letra (add_letter)                0.146     0.118     0.186     6844
escribir 20 letras seguidas                  2.206     1.814     4.665      453
borrar 20 letras seguidas                    2.403     1.892     5.361      416
dibujar 1 Input (always)                     0.253     0.206     0.389     3950

### List

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear List con 10 elementos                  3.791     3.471     4.975      264
dibujar List(10), sin cambios                0.209     0.164     0.254     4781
dibujar List(10), sucia (blit de lo visible)     0.582     0.492     0.798     1718
scroll List(10) (on_wheel -15)               0.141     0.129     0.169     7111
select List(10)                              0.159     0.140     0.219     6302
append a List(10) + regenerar alto           0.298     0.244     0.348     3350
crear List con 100 elementos                 5.209     4.508     7.200      192
dibujar List(100), sin cambios               0.191     0.158     0.252     5240
dibujar List(100), sucia (blit de lo visible)     0.725     0.616     1.191     1380
scroll List(100) (on_wheel -15)              0.297     0.240     0.573     3373
select List(100)                             0.290     0.245     0.412     3451
append a List(100) + regenerar alto          0.313     0.243     0.683     3190
crear List con 1000 elementos                5.342     4.399     7.914      187
dibujar List(1000), sin cambios              0.191     0.159     0.261     5248
dibujar List(1000), sucia (blit de lo visible)     0.717     0.600     1.193     1394
scroll List(1000) (on_wheel -15)             0.293     0.248     0.433     3409
select List(1000)                            0.297     0.249     0.440     3364
append a List(1000) + regenerar alto         0.302     0.250     0.645     3313
update List(1000) con smoothscroll (dt=1/60)     0.004     0.004     0.004   236211
scroll + draw List(1000) smoothscroll        0.771     0.646     1.670     1297
List: bytes por elemento                 0.0 KiB/elem
List vacía (widget + superficie 300x400) 526.4 KiB/lista

### Bloque

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear Bloque con 10 hijos                    1.680     1.532     3.041      595
dibujar Bloque(10), sin scroll               0.231     0.207     0.387     4325
dibujar Bloque(10) forzado (always)          0.949     0.884     1.727     1054
dibujar Bloque(10) con 1 hijo sucio          0.272     0.242     0.378     3670
scroll + update + draw Bloque(10)            0.903     0.825     1.668     1108
move_objs de Bloque(10) (tras scroll)        0.025     0.023     0.035    39414
crear Bloque con 50 hijos                    9.434     9.373    11.182      106
dibujar Bloque(50), sin scroll               0.196     0.170     0.260     5093
dibujar Bloque(50) forzado (always)          1.024     0.921     1.760      977
dibujar Bloque(50) con 1 hijo sucio          0.340     0.301     0.447     2943
scroll + update + draw Bloque(50)            1.258     1.144     2.140      795
move_objs de Bloque(50) (tras scroll)        0.115     0.098     0.154     8704
crear Bloque con 100 hijos                  23.830    23.532    27.227       42
dibujar Bloque(100), sin scroll              0.215     0.186     0.300     4642
dibujar Bloque(100) forzado (always)         1.155     1.018     1.994      866
dibujar Bloque(100) con 1 hijo sucio         0.432     0.369     0.656     2313
scroll + update + draw Bloque(100)           1.602     1.490     2.696      624
move_objs de Bloque(100) (tras scroll)       0.212     0.186     0.303     4709

### Image

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear Image 800x600 sin escalar              0.018     0.017     0.021    56967
crear Image 800x600 → 400x300                0.268     0.237     0.270     3733
crear Image 800x600 → 400x300 girada 30°     0.954     0.795     2.231     1048
Image grande: size = (400, 300)              0.001     0.001     0.001  1527884
Image grande: alternar size 400x300 / 300x400     0.315     0.323     0.466     3173
Image icono 64x64: alternar size 32x32 / 48x48     0.013     0.013     0.013    79558
Image grande: alternar angle 45° / 0°        2.915     3.290     7.290      343
Image icono: alternar angle 45° / 0°         0.021     0.030     0.046    47950
animar ángulo de imagen grande (un frame)     1.094     1.038     2.405      914
animar ángulo de icono (un frame)            0.028     0.029     0.033    35132
dibujar 100 Image (nada sucio)               0.296     0.247     0.435     3375
dibujar 100 Image (todos sucios)             0.742     0.655     1.272     1348
dibujar Image 800x600 (nada sucio)           0.250     0.214     0.335     4000
dibujar Image 800x600 (sucia)                0.550     0.469     0.846     1819

### Figuras

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 PoligonoRegular                     0.110     0.109     0.119     9074
dibujar 10 PoligonoRegular (nada sucio)      0.197     0.176     0.269     5081
dibujar 10 PoligonoRegular (todas sucias)     0.282     0.238     0.379     3544
girar 10 PoligonoRegular (regenera vértices)     0.063     0.063     0.064    15854
crear 100 PoligonoRegular                    1.326     1.149     3.092      754
dibujar 100 PoligonoRegular (nada sucio)     0.290     0.251     0.403     3450
dibujar 100 PoligonoRegular (todas sucias)     1.005     0.879     1.961      995
girar 100 PoligonoRegular (regenera vértices)     0.688     0.628     0.859     1454
crear 1000 PoligonoRegular                  13.134    13.370    13.784       76
dibujar 1000 PoligonoRegular (nada sucio)     0.762     0.665     1.069     1312
dibujar 1000 PoligonoRegular (todas sucias)     7.598     7.065     9.202      132
girar 1000 PoligonoRegular (regenera vértices)     7.365     6.885     8.785      136
crear 100 Engranaje                          5.736     5.376     7.029      174
dibujar 100 Engranaje (nada sucio)           0.307     0.263     0.436     3255
dibujar 100 Engranaje (todos sucios)         3.221     2.890     5.154      310

### Particles

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 partículas                          0.080     0.079     0.088    12511
update 10 partículas (dt=1/60)               0.032     0.023     0.055    31656
draw 10 partículas                           0.230     0.189     0.341     4345
update + draw 10 partículas                  0.250     0.216     0.331     4004
crear 100 partículas                         0.900     0.776     1.847     1111
update 100 partículas (dt=1/60)              0.231     0.203     0.293     4325
draw 100 partículas                          0.474     0.411     0.618     2111
update + draw 100 partículas                 0.679     0.616     0.915     1473
crear 1000 partículas                        8.835     8.781    10.306      113
update 1000 partículas (dt=1/60)             2.378     2.038     4.448      420
draw 1000 partículas                         2.974     2.547     5.071      336
update + draw 1000 partículas                5.100     4.707     7.294      196

### App (bucle completo)

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
escena mixta 10 widgets, nada sucio          0.373     0.303     0.569     2681
escena mixta 10 widgets, 1 sucio             0.387     0.332     0.626     2586
escena mixta 10 widgets, always              0.497     0.425     0.691     2013
escena mixta 50 widgets, nada sucio          1.020     0.924     1.790      980
escena mixta 50 widgets, 1 sucio             1.097     0.986     1.852      911
escena mixta 50 widgets, always              1.739     1.594     2.667      575
escena mixta 200 widgets, nada sucio         8.104     7.298    10.372      123
escena mixta 200 widgets, 1 sucio            7.621     7.029     9.105      131
escena mixta 200 widgets, always            10.990    11.624    12.565       91
escena 200 sin Input: Base.collide por frame 200 cuenta
escena 200 sin Input, nada sucio             0.533     0.436     0.893     1877
escena 200 con Input: Base.collide por frame 10100 cuenta
escena 200 con Input, nada sucio             7.826     7.035    10.221      128
frame limpio con 1 000 objetos               0.881     0.749     2.313     1134
frame limpio con 1 000 objetos, sin fill     0.699     0.582     1.995     1431
frame limpio con 10 000 objetos              8.335     6.799    15.021      120
frame limpio con 10 000 objetos, sin fill     7.473     6.566     9.006      134
frame limpio con 100 000 objetos            74.439    74.503    77.514       13
frame limpio con 100 000 objetos, sin fill    71.538    71.088    76.555       14
rejilla 200 Text: mover 1, optimized         0.645     0.565     0.956     1550
rejilla 200 Text: mover 1, always            1.971     1.805     2.853      507
rejilla 1000 Text: mover 1, optimized        2.065     1.910     3.034      484
rejilla 1000 Text: mover 1, always           9.012     8.976    10.506      111
update_general con 10 widgets                0.055     0.047     0.089    18167
update_general con 50 widgets                0.245     0.219     0.348     4087
update_general con 200 widgets               0.987     0.886     1.821     1013

### Memoria por widget

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
Fuente suelta: pag.font.Font(None, 16)   45.7 KiB/widget
Text 16px (font=None)                    5.7 KiB/widget
Text 16px (font=Font compartida)         6.1 KiB/widget
Text 16px (font=ruta .ttf)               7.7 KiB/widget
Text párrafo 200 palabras                416.0 KiB/widget
Button 16px (font=None)                  5.6 KiB/widget
Input 16px (font=None)                   63.9 KiB/widget
List: por elemento                       1.4 KiB/widget
Bloque: por hijo                         14.7 KiB/widget
Image: por imagen (surface compartida)   0.6 KiB/widget
Image: por imagen escalada 64→32         5.0 KiB/widget
Particles: por partícula (radio 4)       0.4 KiB/widget
Spark: por chispa                        0.2 KiB/widget

---

Reproducir: `python benchmarks/run_all.py` (desde `site-packages`).
Un solo banco: `python benchmarks/bench_text.py`.
El perfil de 30 frames queda en `benchmarks/bench_app.prof`:
`python -m pstats benchmarks/bench_app.prof` → `sort tottime` → `stats 20`.
