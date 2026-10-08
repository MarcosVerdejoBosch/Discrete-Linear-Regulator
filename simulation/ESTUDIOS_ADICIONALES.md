# Estudios adicionales: carga, capacitor externo y baja tensión

Las 16 entradas del selector principal se mantienen. El usuario comunicó que todas ejecutaron correctamente. Estos estudios complementarios tienen comprobación automática de ejecución; quedan disponibles para su revisión visual y no representan mediciones físicas.

## Abrir y ejecutar

En la carpeta preparada de LTspice, ejecutar **ELEGIR_ESTUDIO_ADICIONAL.cmd**, elegir el caso y esperar a que termine. El selector aplica el solver correspondiente y abre las curvas. También se puede abrir el `.asc` y pulsar Run: seleccionar antes **Alternate** para SIM-09 o **Normal** para los dos diagnósticos SIM-04. El perfil `.plt` debe permanecer junto al esquema.

Para una descarga nueva del repositorio, ejecutar primero `PREPARAR_LTSPICE.cmd`, igual que para los casos principales. Los modelos externos requieren la preparación descrita en `EXTERNAL_MODELS.md`.

## SIM-09: comparación de Bode

Los nombres `SIM-09_external_<modo>_<corriente>_<capacitancia>_R<resistencia>.asc` identifican todas las condiciones: 5 V o 3,3 V; 100 mA o 1 A; capacitor externo ausente, 1, 10 o 47 µF con 0,1 Ω serie. Se incluye además 10 µF con 1 Ω para sensibilidad a ESR. Son 20 casos.

**CLOAD sigue siendo el capacitor de la placa, de 1 µF con 1 Ω en serie. No se reemplazó.** El capacitor externo se llama **CEXT** y forma otra rama entre OUT y masa, con **REXT** en serie. REXT representa una resistencia serie efectiva asumida; no es una medición ni otra resistencia que sea obligatorio soldar. La ESR real deberá verificarse con el componente elegido.

Cada esquema conserva las dos inyecciones de `LG_single` y la expresión de retorno del caso original. El punto de operación DC se recalcula con la nueva carga; las polarizaciones auxiliares se mantienen fijas como en el SIM-09 principal. Este análisis linealiza alrededor de ese punto de operación: no simula el arranque del circuito auxiliar. La carga es resistiva, ajustada para obtener aproximadamente la corriente indicada en regulación.

| Modo | Carga | Sin C externo: PM / GM | CEXT = 10 µF, REXT = 0,1 Ω: PM / GM |
|---|---:|---:|---:|
| 5 V | 100 mA | 57,3° / 18,3 dB | 72,8° / 35,3 dB |
| 5 V | 1 A | 52,5° / 17,3 dB | 81,6° / 32,8 dB |
| 3,3 V | 100 mA | 53,8° / 18,4 dB | 65,1° / 35,3 dB |
| 3,3 V | 1 A | 52,0° / 17,7 dB | 71,5° / 32,9 dB |

PM: margen de fase; GM: margen de ganancia. A 1 A, agregar solamente 1 µF con 0,1 Ω reduce PM a 41,0° / 37,3° (5 V / 3,3 V). Por eso no se concluye que cualquier capacitor mejore la estabilidad. Con 10 µF y 0,1 Ω aumenta el margen, pero el cruce de ganancia baja a aproximadamente 111 / 128 kHz. Con 1 Ω, ese mismo capacitor da PM de 67,9° / 65,2° a 1 A. No se han barrido tolerancias ni temperatura.

Figuras: `docs/figures/SIM-09_load_comparison_*.pdf` y `SIM-09_external_capacitance_*.pdf`. Datos y márgenes completos: `tests/SIM-09_loop_stability/results/external/`. Se interpolan cruces sobre frecuencia logarítmica, sin suavizado, con 500 puntos/década. `analyze_external.py CARPETA_LTSPICE` reconstruye los CSV y métricas a partir de RAW completos; `plot_external.py` reconstruye las cuatro figuras. Requieren Python, NumPy y Matplotlib.

## SIM-04: UVLO anulado solamente como diagnóstico

`SIM-04_UVLO_bypass_bounded_5V.asc` y `..._33V.asc` conectan la entrada de R87 a VEE para conceder el permiso de UVLO. El comparador sigue presente; el retardo y OVLO siguen actuando. Se mantienen los ajustes de exploración RV10 = 100 kΩ y RV12 = 47 kΩ, con cargas de 50 Ω / 33 Ω. **Los umbrales nominales de los casos principales no cambian.**

La fuente permanece en 8 V hasta 80 ms y baja a 4 V en 120 ms (5 V) o a 3,2 V en 128 ms (3,3 V). Ambas corridas completaron con Normal. Las netlists regeneradas desde los ASC se compararon con los CIR ejecutados: coinciden eléctricamente.

Una caída de salida de 100 mV respecto del nivel inicial ocurre a V(VBAT) ≈ 4,947 V / 4,028 V. En 3,3 V esto **no mide dropout intrínseco del transistor de paso**: sigue habiendo margen de entrada y las funciones auxiliares/de descarga afectan el límite de operación. Anular UVLO no elimina esas dependencias. En 5 V la corriente de base cerca de dropout alcanza aproximadamente 147 mA; se conserva la advertencia térmica del driver y R21 de 10 Ω / ¼ W del informe. No trasladar el bypass como recomendación de operación continua de la placa.

## Corriente de limitación y pico de entrada

- SIM-08, 3,3 V, media temporal entre 100 y 110 ms: **I(Rload) = 1,4655 A**, mientras **−I(R25) = 1,4815 A**. Son ramas distintas; los dos valores observados son compatibles. El informe distingue corriente de carga y corriente sensada.
- Las entradas **8 y 9 del selector principal corresponden a SIM-05**, los dos ensayos en vacío. El pico de entrada alrededor de 5 ms es ≈47,3 A. En el diagnóstico, la corriente de **C20 (10 µF del doblador)** explica casi todo el pico.
- Una sensibilidad separada con 0,25 Ω en la fuente y 0,1 Ω de ESR en C20 reduce el pico a ≈12,1 A. Son valores ilustrativos asumidos, no una predicción validada del pico real. Las capacitancias, resistencia de fuente y cableado reales deben caracterizarse para esa comparación.

Los CIR de diagnóstico, logs de finalización, métricas y huellas de los RAW se guardan en `tests/2026-10-05_review/`. Los RAW voluminosos permanecen en el archivo local; los resultados de Bode se publican como CSV. Los CIR de inrush pueden copiarse a la carpeta preparada para ejecutarlos con sus modelos; usan Normal y un intervalo corto de 5,02 ms. No reemplazan los ensayos principales.


## Cierre de revisión local — 2026-10-07

Las 16 entradas principales quedan congeladas desde la carpeta local validada por el usuario, con modelos, símbolos y perfiles. El archivo privado de respaldo no se publica en el repositorio público. Los estudios adicionales no forman parte de esa aceptación.

Los ASC de CEXT contienen una nota visible: cada Run representa una condición de carga/capacitancia, con las dos inyecciones necesarias para calcular el lazo. Para comparar 100 mA y 1 A, abrir los dos archivos indicados en la nota. Las figuras del informe combinan esos casos; no agregar otro `.step` sin adaptar la expresión que identifica las inyecciones con `@1` y `@2`.

**Dropout pendiente de revisión personal:** el selector adicional incluye al final `SIM-04_adjusted_5V.asc` (Normal) y `SIM-04_adjusted_33V.asc` (Alternate). Usan RV10 = 100 kΩ y RV12 = 47 kΩ, cargas de 50 Ω / 33 Ω, fuente de 8 a 4 V entre 80 y 120 ms. Conservan UVLO. En 5 V se espera una pérdida de salida de 100 mV cerca de 4,947 V de entrada; en 3,3 V actúa UVLO primero, cerca de 4,793 V. Por eso el segundo caso no establece dropout intrínseco. Son diferentes de los dos archivos `UVLO_bypass`, que anulan un permiso y se conservan sólo como diagnóstico.

La revisión visual de las figuras del informe queda pospuesta por decisión del usuario. Las cifras publicadas conservan sus datos y procedimientos asociados; eso no equivale a aprobación visual del informe ni a validación física.
