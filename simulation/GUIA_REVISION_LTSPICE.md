# Guía de revisión visual de LTspice

La revisión pendiente es tu comprobación visual de los archivos corregidos. Ya se ejecutaron y analizaron las 16 pruebas principales. Esta tabla describe resultados simulados nominales, no límites garantizados de la placa.

## 1. Revisar primero: las 16 entradas del selector

En la carpeta del escritorio ya preparada, abrir **ELEGIR_SIMULACION.cmd**. El número coincide con esta tabla y el programa elige el solver. Esperar a que finalice; algunos casos tardan varios minutos. No hace falta repetir la preparación.

| Nº | Archivo .asc | Solver | Duración simulada | Qué deberías observar | Revisado |
|---:|---|---|---|---|---|
| 1 | `SIM-01_calibrated_startup_5V.asc` | Normal | 140 ms | Conexión a 5 ms, desconexión a 55 ms y reconexión a 85 ms. V(out) llega a 5 V después del retardo, cae al desconectar y vuelve a regular. Hay un pulso previo al enable de aproximadamente 0,86 V. | ☐ |
| 2 | `SIM-01_calibrated_startup_33V.asc` | Alternate | 140 ms | La misma secuencia, con salida asentada en 3,3 V y pulso previo al enable de aproximadamente 0,84 V. | ☐ |
| 3 | `SIM-02_calibrated_line_5V.asc` | Normal | 320 ms | Al variar la fuente entre 6 y 11 V, las medias de V(out) quedan aproximadamente entre 4,99959 y 5,00039 V. Pequeña ondulación superpuesta; no confundirla con la variación de la media. | ☐ |
| 4 | `SIM-02_calibrated_line_33V.asc` | Normal | 320 ms | Con fuente de 6 a 11 V, las medias de V(out) quedan aproximadamente entre 3,29918 y 3,30077 V. | ☐ |
| 5 | `SIM-03_calibrated_load_5V.asc` | Normal | 280 ms | Carga de aproximadamente 1 → 0,1 → 0,25 → 0,5 → 0,75 → 1 A. La salida permanece alrededor de 5 V; la media a 1 A es unos 15 µV menor que a 0,1 A. Hay ondulación y transitorios entre mesetas. | ☐ |
| 6 | `SIM-03_calibrated_load_33V.asc` | Normal | 280 ms | La misma secuencia de cargas, manteniendo aproximadamente 3,3 V. Las diferencias de las medias son menores que 1 µV; no esperar una recta perfectamente horizontal ni atribuir precisión física a esa cifra. | ☐ |
| 7 | `SIM-04_calibrated_input_33V.asc` | Alternate | 122 ms | Al bajar la fuente, salida inicialmente en 3,3 V y posterior apagado por el circuito de enable. Cruce por 98% de salida nominal alrededor de 5,823 V en la fuente. Este resultado es un límite por protección, no dropout intrínseco. | ☐ |
| 8 | `SIM-05_calibrated_idle_5V.asc` | Normal | 120 ms | Salida cerca de 5 V con carga externa de 1 MΩ. La media de -I(VBAT) es aproximadamente 56,9 mA: consumo total del circuito, incluidas las etapas auxiliares. | ☐ |
| 9 | `SIM-05_calibrated_idle_33V.asc` | Alternate | 120 ms | Salida cerca de 3,3 V con carga externa de 1 MΩ. La media de -I(VBAT) es aproximadamente 56,0 mA. | ☐ |
| 10 | `SIM-06_calibrated_transient_5V.asc` | Normal | 160 ms | Aumento de carga a 80 ms: caída momentánea de unos 172 mV. Reducción a 120 ms: sobreimpulso de unos 363 mV. La salida vuelve a 5 V; entrada final a la banda ±1% en unos 7,42 / 6,02 µs. | ☐ |
| 11 | `SIM-06_calibrated_transient_33V.asc` | Alternate | 160 ms | Aumento de carga a 80 ms: caída momentánea de unos 165 mV. Reducción a 120 ms: sobreimpulso de unos 361 mV. Retorno a 3,3 V; entrada final a la banda ±1% en unos 7,40 / 14,80 µs. | ☐ |
| 12 | `SIM-07_calibrated_protection_5V.asc` | Normal | 264 ms | Apagado y recuperación ante subtensión y sobretensión, con umbrales diferentes al subir y bajar. En V(vee): UVLO ≈5,495 / 5,859 V; OVLO ≈11,003 / 10,135 V. Los eventos de V(ttl) no tienen por qué coincidir exactamente con los del comparador. | ☐ |
| 13 | `SIM-08_calibrated_limit_5V.asc` | Normal | 210 ms | Sobrecarga: V(out) baja a unos 3,713 V e I(Rload) se limita a unos 1,485 A. Corto simulado de 50 mΩ: media ≈1,474 A y salida ≈73,7 mV. Hay un pico breve de corriente; al retirar la falla vuelve a 5 V. | ☐ |
| 14 | `SIM-08_calibrated_limit_33V.asc` | Alternate | 210 ms | Sobrecarga: V(out) baja a unos 2,418 V e I(Rload) se limita a unos 1,465 A. Corto de 50 mΩ: media ≈1,474 A y salida ≈73,7 mV. Al retirar la falla vuelve a 3,3 V. | ☐ |
| 15 | `SIM-09_loop_5V.asc` | Alternate | Barrido AC | Diagrama de ganancia y fase del lazo. Cruce por 0 dB ≈558 kHz, margen de fase ≈52,5° y margen de ganancia ≈17,3 dB. Mantener la expresión de Tian y el orden de los dos pasos. | ☐ |
| 16 | `SIM-09_loop_33V.asc` | Alternate | Barrido AC | Cruce por 0 dB ≈530 kHz, margen de fase ≈52,0° y margen de ganancia ≈17,8 dB. Es un análisis alrededor del punto de operación guardado, no una curva de arranque. | ☐ |

### Cómo comparar las curvas

- SIM-02 y SIM-03: los valores indicados son **medias asentadas**, no mínimos/máximos de la ondulación instantánea. Las vistas iniciales amplían la tensión de salida.
- SIM-06: el perfil abre el escalón a 80 ms. Para ver el de 120 ms, usar Zoom to Fit y ampliar esa zona. No comparar un pico con una media.
- SIM-07: los umbrales de comparador se refieren a V(vee), la alimentación local de las protecciones. SIM-04 nominal cita la fuente antes del switch. Son nodos y criterios distintos.
- SIM-09: mantener juntos ASC, PLT, BIAS y la sonda LG_single. Las dos inyecciones pertenecen a una sola ejecución de cada ASC.
- Guardar el resultado como “revisado” si la corrida termina y reproduce la secuencia esperada. Si falla o difiere, anotar archivo, mensaje y zona de la curva. No modificar componentes para igualar la tabla.

## 2. Seis estudios complementarios completados

No están en el selector principal. Su revisión es opcional para comprobar los detalles de dropout y del banco pulsado. Si se abren manualmente, usar el solver indicado; algunos necesitan agregar las señales a la ventana o consultar las figuras calculadas de potencia.

| Archivo .asc | Solver | Señales principales | Qué deberías observar |
|---|---|---|---|
| `SIM-04_adjusted_5V.asc` | Normal | V(out), V(vbat), V(ttl), V(1) | Rampa de 8 a 4 V, final a 120 ms. Pérdida de 100 mV antes de UVLO: V(out)≈4,900 V con entrada de placa≈4,947 V. Cerca del apagado aparecen conmutaciones repetidas; esta variante extrema no valida una histéresis definitiva. |
| `SIM-04_adjusted_33V.asc` | Alternate | V(out), V(vbat), V(ttl), V(1) | Rampa de 8 a 4 V, final a 120 ms. UVLO actúa primero, alrededor de 4,793 V en la entrada de placa, mientras la salida aún está cerca de 3,3 V. No permite extraer dropout intrínseco en este modo. |
| `SIM-04_adjusted_settled_5V.asc` | Normal | V(out), V(n034), V(ttl) | Mesetas de fuente 8 / 5,10 / 5,00 / 4,95 / 4,94 V. Salidas medias aproximadas: 5,000 / 4,999 / 4,950 / 4,900 / 4,890 V, con enable activo. Final a 163 ms. |
| `SIM-04_driver_thermal_5V.asc` | Normal | V(out), -Ib(Q26); resultados calculados de potencia | Mismas mesetas, final a 163 ms. A 4,95 V de fuente: corriente de base del transistor de paso≈147 mA, Q3≈353 mW y R21≈215 mW. Potencia calculada a partir de tensiones y corrientes; no se simula temperatura real de la placa. |
| `SIM-04_pulsed_load_5V.asc` | Normal | V(out), I(Rload), -Ib(Q26) | Final a 210 ms. En la zona de baja entrada, la carga se conecta y desconecta pero la corriente de base sigue cerca de 147 mA; Q3 continúa disipando alrededor de 0,35 W. Retirar solo la carga no produce reposo térmico. |
| `SIM-04_pulsed_load_inhibit_5V.asc` | Normal | V(out), I(Rload), -Ib(Q26), V(ttl) | Final a 210 ms. Al inhibir también el drive entre pulsos, la salida y la corriente de base caen; las potencias disminuyen en reposo. Persisten picos breves de conmutación. Es un ensayo eléctrico de la idea, no la implementación física del ESP32. |

## 3. Doce archivos históricos o diagnósticos: no repetir ahora

No tienen un criterio de aprobación nuevo en esta revisión. Se conservan como antecedentes y algunos sirven de base a los scripts.

| Archivo .asc | Propósito y estado |
|---|---|
| `SIM-01_check_step_33V.asc` | Control adicional de resolución del arranque. No se considera revalidado con el IRF4905; usar SIM-01_calibrated_startup para la revisión actual. |
| `SIM-01_check_step_5V.asc` | Control adicional de resolución del arranque. No se considera revalidado con el IRF4905; usar SIM-01_calibrated_startup para la revisión actual. |
| `SIM-02_cal_01_33V.asc` | Etapa de calibración y archivo base de generación. Su propósito era ajustar el divisor; usar los casos calibrated_line y calibrated_load para revisar los resultados actuales. |
| `SIM-02_cal_01_5V.asc` | Etapa de calibración y archivo base de generación. Su propósito era ajustar el divisor; usar los casos calibrated_line y calibrated_load para revisar los resultados actuales. |
| `SIM-02_cal_02_33V.asc` | Etapa de calibración y archivo base de generación. Su propósito era ajustar el divisor; usar los casos calibrated_line y calibrated_load para revisar los resultados actuales. |
| `SIM-02_cal_02_5V.asc` | Etapa de calibración y archivo base de generación. Su propósito era ajustar el divisor; usar los casos calibrated_line y calibrated_load para revisar los resultados actuales. |
| `SIM-02_full_line_33V_changes.asc` | Exploración previa de regulación de línea. Conservada por trazabilidad; sustituida para esta revisión por SIM-02_calibrated_line del modo correspondiente. |
| `SIM-02_full_line_33V_pilot.asc` | Exploración previa de regulación de línea. Conservada por trazabilidad; sustituida para esta revisión por SIM-02_calibrated_line del modo correspondiente. |
| `SIM-02_full_line_5V_changes.asc` | Exploración previa de regulación de línea. Conservada por trazabilidad; sustituida para esta revisión por SIM-02_calibrated_line del modo correspondiente. |
| `SIM-03_load_stepcheck_33V.asc` | Control adicional de 1 µs que no completó la revalidación. No hace falta ejecutarlo para aceptar el alcance de medias asentadas con 2 µs. |
| `SIM-03_load_stepcheck_5V.asc` | Control adicional de 1 µs que no completó la revalidación. No hace falta ejecutarlo para aceptar el alcance de medias asentadas con 2 µs. |
| `SIM-04_driver_R100_5V.asc` | Alternativa histórica con R21=100 Ω. No representa la placa: el valor implementado sigue siendo 10 Ω / ¼ W. |

## 4. Archivo de soporte local

| Archivo .asc | Qué esperar |
|---|---|
| `LG_single.asc` | Subcircuito de la sonda de ganancia de lazo. No es un ensayo independiente ni una salida de 5/3,3 V; lo utilizan los otros esquemas. Conservarlo junto a su símbolo. |

## 5. Dos esquemas de comparación del cambio de U17

Estos archivos están en `simulation/tests/SIM-01_startup_shutdown/u17_review/`, fuera del conjunto preparado para abrir desde el selector.

| Archivo .asc | Propósito y estado |
|---|---|
| `IRF4905_5V.asc` | Comparación del arranque al cambiar U17. Antecedente de la revalidación; para revisar la versión vigente ejecutar SIM-01_calibrated_startup_5V.asc. |
| `IRF4905_33V.asc` | Comparación equivalente en 3,3 V. Para revisar la versión vigente ejecutar SIM-01_calibrated_startup_33V.asc. |

**Inventario:** 36 archivos ASC en el repositorio (34 escenarios en `simulation/ltspice` y dos comparaciones en `simulation/tests`). La carpeta preparada contiene los 34 escenarios y LG_single.asc: 35 archivos. Los controles full-tone de SIM-09 usan archivos CIR y no forman parte de esta lista.

Después de tu revisión de las pruebas principales, podemos fijar esta versión de simulación como referencia para las mediciones físicas, conservando los alcances y diagnósticos documentados.
