# Resultados del banco de pruebas

Generado por `benchmarks/run_all.py` el **26-10-2026 01:06**.

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
  Un `Text` con `font=None` ocupa ~77 KiB porque **crea su propia fuente**;
  con una `Font` compartida baja a ~8,5 KiB.

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
crear 10 Text (1 línea)                     17.725    17.658    18.637       56
crear 50 Text (1 línea)                    107.968   108.881   123.870        9
crear 200 Text (1 línea)                   448.846   433.420   540.973        2
crear 1000 Text (1 línea)                 2207.866  2034.659  2841.943        0
crear Text (párrafo 200 palabras)            6.323     6.023     7.199      158
cambiar texto de un párrafo                  0.003     0.003     0.004   294768
dibujar 50 Text, nada sucio (optimized)      0.256     0.229     0.422     3906
dibujar 50 Text, 1 sucio (optimized)         0.347     0.296     0.549     2882
dibujar 50 Text, todos sucios (always)       0.667     0.621     0.911     1499
dibujar 50 Text, todos sucios, sin presentar     2.474     2.293     3.089      404
dibujar 200 Text, nada sucio (optimized)     0.565     0.408     1.194     1768
dibujar 200 Text, 1 sucio (optimized)        0.952     0.886     1.254     1050
dibujar 200 Text, todos sucios (always)      2.185     1.972     3.185      458
dibujar 200 Text, todos sucios, sin presentar    27.951    26.855    31.077       36
dibujar 1000 Text, nada sucio (optimized)     0.801     0.722     1.148     1248
dibujar 1000 Text, 1 sucio (optimized)       5.015     4.110    10.531      199
dibujar 1000 Text, todos sucios (always)     9.201     8.442    13.491      109
dibujar 1000 Text, todos sucios, sin presentar   168.856   153.731   263.008        6
medir 100 cadenas con font.size()           21.592    18.838    32.665       46
medir 100 cadenas con font.render()         30.562    29.578    31.853       33

### Button

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 Button                             14.537    14.473    15.241       69
dibujar 10 Button, nada sucio                0.194     0.166     0.328     5148
dibujar 10 Button, todos sucios              0.453     0.396     0.756     2207
hover on/off de 10 Button                    0.012     0.009     0.011    85648
crear 50 Button                             73.909    73.760    77.053       14
dibujar 50 Button, nada sucio                0.230     0.210     0.322     4356
dibujar 50 Button, todos sucios              1.410     1.315     1.778      709
hover on/off de 50 Button                    0.042     0.041     0.045    24025
crear 200 Button                           334.638   304.521   461.275        3
dibujar 200 Button, nada sucio               0.472     0.334     1.184     2118
dibujar 200 Button, todos sucios             5.840     4.416    11.418      171
hover on/off de 200 Button                   0.171     0.175     0.204     5860
hover de 1 Button (solo cambio de estado)     0.001     0.001     0.002   706714
dibujar 1 Button tras hover                  0.182     0.158     0.299     5485

### Input

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 1 Input                                5.408     5.194     7.137      185
dibujar 1 Input, always (re-render por frame)     0.238     0.193     0.450     4199
dibujar 1 Input, always, sin presentar       0.226     0.192     0.344     4426
update de 1 Input (dt=1/60)                  0.001     0.001     0.001  1390821
crear 10 Input                              67.136    58.213   132.540       15
dibujar 10 Input, always (re-render por frame)     0.565     0.495     0.862     1769
dibujar 10 Input, always, sin presentar      0.528     0.477     0.733     1893
update de 10 Input (dt=1/60)                 0.003     0.003     0.003   310078
crear 50 Input                             327.902   305.957   452.774        3
dibujar 50 Input, always (re-render por frame)     2.271     1.880     4.449      440
dibujar 50 Input, always, sin presentar      1.856     1.783     2.329      539
update de 50 Input (dt=1/60)                 0.012     0.012     0.012    84157
escribir 1 letra (add_letter)                0.121     0.113     0.177     8294
escribir 20 letras seguidas                  2.079     1.787     2.295      481
borrar 20 letras seguidas                    1.886     1.795     2.285      530
dibujar 1 Input (always)                     0.221     0.198     0.345     4530

### List

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear List con 10 elementos                  4.019     3.971     4.526      249
dibujar List(10), sin cambios                0.176     0.158     0.272     5674
dibujar List(10), sucia (blit de lo visible)     0.639     0.595     0.836     1564
scroll List(10) (on_wheel -15)               0.241     0.225     0.326     4157
select List(10)                              0.381     0.235     0.466     2625
append a List(10) + regenerar alto           0.563     0.516     0.763     1777
crear List con 100 elementos                 6.212     6.151     7.103      161
dibujar List(100), sin cambios               0.190     0.161     0.287     5270
dibujar List(100), sucia (blit de lo visible)     1.378     1.022     2.919      726
scroll List(100) (on_wheel -15)              0.801     0.564     1.924     1249
select List(100)                             0.811     0.619     1.639     1234
append a List(100) + regenerar alto          0.672     0.582     1.014     1489
crear List con 1000 elementos               11.035    10.349    26.563       91
dibujar List(1000), sin cambios              0.290     0.200     0.599     3446
dibujar List(1000), sucia (blit de lo visible)     1.442     1.098     3.092      693
scroll List(1000) (on_wheel -15)             1.376     0.594     2.979      727
select List(1000)                            0.941     0.649     2.906     1062
append a List(1000) + regenerar alto         0.955     0.632     3.325     1047
update List(1000) con smoothscroll (dt=1/60)     0.004     0.004     0.004   253711
scroll + draw List(1000) smoothscroll        1.433     1.127     2.779      698
píxeles de List(1000) (sin objetos)        0.0 MiB

### Bloque

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear Bloque con 10 hijos                   13.672    13.443    18.492       73
dibujar Bloque(10), sin scroll               0.911     0.853     1.317     1098
dibujar Bloque(10) forzado (always)          0.922     0.836     1.403     1084
scroll + update + draw Bloque(10)            0.876     0.826     1.105     1141
move_objs de Bloque(10) (tras scroll)        0.026     0.025     0.026    39059
crear Bloque con 50 hijos                   71.993    67.812    84.798       14
dibujar Bloque(50), sin scroll               1.001     0.954     1.245      999
dibujar Bloque(50) forzado (always)          1.034     0.947     1.503      967
scroll + update + draw Bloque(50)            1.509     1.323     2.498      663
move_objs de Bloque(50) (tras scroll)        0.167     0.101     0.259     5984
crear Bloque con 100 hijos                 150.023   151.581   166.173        7
dibujar Bloque(100), sin scroll              1.167     1.055     1.786      857
dibujar Bloque(100) forzado (always)         1.118     1.014     1.613      894
scroll + update + draw Bloque(100)           1.878     1.761     2.684      532
move_objs de Bloque(100) (tras scroll)       0.213     0.195     0.297     4685

### Image

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear Image 800x600 sin escalar              0.016     0.016     0.018    61387
crear Image 800x600 → 400x300                0.256     0.237     0.292     3910
crear Image 800x600 → 400x300 girada 30°     0.981     0.777     1.754     1020
Image grande: size = (400, 300)              0.001     0.001     0.001   928505
Image grande: alternar size 400x300 / 300x400     0.778     0.326     0.774     1285
Image icono 64x64: alternar size 32x32 / 48x48     0.013     0.012     0.013    77074
Image grande: alternar angle 45° / 0°        2.196     1.560     5.204      455
Image icono: alternar angle 45° / 0°         0.017     0.018     0.030    57185
animar ángulo de imagen grande (un frame)     0.795     0.761     1.211     1257
animar ángulo de icono (un frame)            0.027     0.029     0.031    36551
dibujar 100 Image (nada sucio)               0.260     0.237     0.382     3841
dibujar 100 Image (todos sucios)             0.656     0.602     0.833     1524
dibujar Image 800x600 (nada sucio)           0.174     0.153     0.248     5737
dibujar Image 800x600 (sucia)                0.449     0.408     0.636     2225

### Figuras

**No se pudo ejecutar:** `RuntimeError: figuras rotas por name mangling (BUG-36): 'PoligonoRegular' object has no attribute '_PoligonoRegular__pos'`


### Particles

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
crear 10 partículas                          0.074     0.073     0.082    13532
update 10 partículas (dt=1/60)               0.019     0.019     0.020    51351
draw 10 partículas                           0.196     0.182     0.255     5090
update + draw 10 partículas                  0.224     0.206     0.319     4456
crear 100 partículas                         0.749     0.695     1.010     1335
update 100 partículas (dt=1/60)              0.173     0.165     0.215     5786
draw 100 partículas                          0.404     0.371     0.586     2477
update + draw 100 partículas                 0.584     0.549     0.827     1713
crear 1000 partículas                        7.419     7.115     8.664      135
update 1000 partículas (dt=1/60)             1.783     1.675     2.300      561
draw 1000 partículas                         2.405     2.246     3.116      416
update + draw 1000 partículas                3.913     3.941     4.994      256

### App (bucle completo)

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
escena mixta 10 widgets, nada sucio          0.297     0.275     0.445     3369
escena mixta 10 widgets, 1 sucio             0.330     0.300     0.459     3031
escena mixta 10 widgets, always              0.534     0.481     0.708     1872
escena mixta 50 widgets, nada sucio          0.929     0.836     1.162     1076
escena mixta 50 widgets, 1 sucio             0.992     0.893     1.407     1008
escena mixta 50 widgets, always              2.246     2.100     2.876      445
escena mixta 200 widgets, nada sucio         6.600     6.346     8.055      152
escena mixta 200 widgets, 1 sucio            7.228     6.985     9.273      138
escena mixta 200 widgets, always             9.270     9.170    10.490      108
escena 200 sin Input: Base.collide por frame 200 cuenta
escena 200 sin Input, nada sucio             0.457     0.429     0.592     2190
escena 200 con Input: Base.collide por frame 10100 cuenta
escena 200 con Input, nada sucio             6.525     6.338     7.525      153
frame limpio con 1 000 objetos               0.781     0.746     1.053     1281
frame limpio con 1 000 objetos, sin fill     0.625     0.578     0.885     1601
frame limpio con 10 000 objetos              6.301     6.156     7.218      159
frame limpio con 10 000 objetos, sin fill     6.241     6.081     7.625      160
frame limpio con 100 000 objetos            67.755    67.520    71.717       15
frame limpio con 100 000 objetos, sin fill    67.373    66.878    74.268       15
rejilla 200 Text: mover 1, optimized         0.608     0.541     0.920     1646
rejilla 200 Text: mover 1, always            1.668     1.550     2.212      600
rejilla 1000 Text: mover 1, optimized        1.847     1.662     2.707      541
rejilla 1000 Text: mover 1, always           7.696     7.625     8.705      130
update_general con 10 widgets                0.048     0.044     0.070    20824
update_general con 50 widgets                0.230     0.205     0.333     4345
update_general con 200 widgets               0.967     0.836     1.680     1034

### Memoria por widget

benchmark                                    media   mediana       p95      fps
--------------------------------------------------------------------------------
Fuente suelta: pag.font.Font(None, 16)   46.6 KiB/widget
Text 16px (font=None)                    76.0 KiB/widget
Text 16px (font=Font compartida)         8.7 KiB/widget
Text 16px (font=ruta .ttf)               92.5 KiB/widget
Text párrafo 200 palabras                502.3 KiB/widget
Button 16px (font=None)                  78.0 KiB/widget
Input 16px (font=None)                   209.6 KiB/widget
List: por elemento                       0.2 KiB/widget
Bloque: por hijo                         77.2 KiB/widget
Image: por imagen (surface compartida)   0.8 KiB/widget
Image: por imagen escalada 64→32         5.3 KiB/widget
Particles: por partícula (radio 4)       0.6 KiB/widget
Spark: por chispa                        0.2 KiB/widget

---

Reproducir: `python benchmarks/run_all.py` (desde `site-packages`).
Un solo banco: `python benchmarks/bench_text.py`.
El perfil de 30 frames queda en `benchmarks/bench_app.prof`:
`python -m pstats benchmarks/bench_app.prof` → `sort tottime` → `stats 20`.
