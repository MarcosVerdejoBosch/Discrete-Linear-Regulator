# SIM-04 — Revisión térmica del driver

## Restricción confirmada — 20 de septiembre de 2026

Marco confirma **R21 = 10 Ω, ¼ W**, y exige mantener ese valor.
La variante de 100 Ω queda descartada como propuesta de implementación;
sus resultados se conservan únicamente como comparación histórica.
El trabajo de banco continúa con el circuito original y su revisión térmica.

## Resultado y decisión

**La revisión sí era necesaria: no queda justificado un ensayo continuo de
dropout con R21=10 Ω bajo las condiciones térmicas de referencia evaluadas.**
Esto no prueba sobretemperatura en la placa real: falta conocer su resistencia
térmica efectiva y el componente instalado.

Ambas corridas finalizaron: 163 ms para el circuito original y 179 ms para la
variante. Medias de los últimos 5 ms de cada meseta de 15 ms:

| Fuente (V) | Q3, R21=10 Ω (mW) | R21=10 Ω (mW) | Q3, R21=100 Ω (mW) | R21=100 Ω (mW) |
|---:|---:|---:|---:|---:|
| 8.00 | 33.2 | 0.0 | 32.8 | 0.1 |
| 5.10 | 26.0 | 0.1 | 24.8 | 0.6 |
| 5.00 | 352.0 | 230.7 | 44.7 | 27.6 |
| 4.95 | 353.4 | 216.7 | 44.8 | 26.0 |
| 4.94 | 351.8 | 213.9 | 44.6 | 25.7 |

El máximo de Q3 entre las mesetas originales es 353.4 mW. A 35 °C,
los dos montajes de referencia darían aproximadamente 212 °C (500 K/W)
o 163 °C (362 K/W), por encima del máximo absoluto. Para sostener
ese punto a Tj ≤100 °C haría falta RθJA ≤184 K/W, valor no demostrado
por la copia de PCB. Estas son comprobaciones de margen, no temperaturas medidas.

R21 original llega a 230.7 mW: 92.3% de los 250 mW nominales confirmados.
Quedan unos 19 mW de diferencia respecto del rating nominal, antes de considerar
derating, tolerancias y condiciones reales. Se mantiene la pieza de ¼ W.
La comprobación de R21 no resuelve por sí sola la disipación de Q3.

Con R21=100 Ω, Q3 queda como máximo en 44.8 mW entre las mesetas y R21 en
27.6 mW. El cálculo de Q3 a 35 °C y 500 K/W da aproximadamente 57 °C.
Se mantiene la referencia alrededor de 2,474 V y enable supera 0,90 VEE.
La diferencia entre mitades de ventana es menor que 0,002 mV y la ondulación
de salida menor que 0,45 mV. No aparece deriva de salida en esas ventanas.

La variante cruza una pérdida de 100 mV entre 4,95 y 5,00 V de fuente.
A 4,95 V entrega 4,89752 V, frente a 4,90461 V del original. Por eso no
se puede presentar el dropout de esta variante como si fuera el original.

Picos numéricos de potencia de Q3 a lo largo de estas corridas: 404.2 mW
(original) y 52.9 mW (100 Ω). Se conservan para inspección;
no constituyen una validación de ratings pulsados ni de todos los transitorios.

### Próximo paso de banco

El siguiente paso es estudiar una entrada de dos niveles con duración controlada
que permita observar dropout conservando R21=10 Ω / ¼ W. La alternativa
de 100 Ω queda fuera del plan, y no corresponde validar su adopción permanente.

Para **medir el circuito original**, conservar R21=10 Ω y preparar un ensayo
de entrada de dos niveles con tiempo controlado, o demostrar térmicamente
el montaje. No usar por ahora el barrido manual con esperas de varios segundos
dentro de dropout. La sección de pulsos explica por qué no basta SIM-01.

[Comparación gráfica](results/driver_thermal/driver_power_comparison.pdf) ·
[Datos completos y hashes](results/driver_thermal/metrics.json)

## Alcance y método

Se revisa el modo 5 V, carga 50 Ω, RV10=100 kΩ y RV12=47 kΩ.
Los resultados corresponden a modelos eléctricos nominales a 27 °C.
La temperatura de unión se estima por separado: no hay realimentación
electrotérmica, tolerancias ni medición térmica de la placa.

Q3 en KiCad corresponde a Q14 en LTspice, y R21 a R15.
Se repitió el ensayo con mesetas guardando las corrientes de terminales,
sin cambiar el circuito. La potencia instantánea absorbida por Q3 es:

`P_Q3 = (Vc − Ve) Ic + (Vb − Ve) Ib`.

Las corrientes llevan el signo de LTspice, positivo hacia el terminal.
El colector está a GND. Se calcula la media temporal de esa potencia,
no el producto de tensiones y corrientes medias. Para R21 se usa
`P_R21 = R21 × I_R21²`. Esto reemplaza la estimación previa que omitía
las contribuciones de polarización y base del driver.

## Referencia térmica y criterio de evaluación

[Nexperia, BC807 series, Rev. 8, secciones 8–9](https://assets.nexperia.com/documents/data-sheet/BC807_SER.pdf)
especifica Tj máxima de 150 °C y resistencias unión-ambiente de 500 K/W
en huella estándar y 362 K/W con 1 cm² de cobre en colector, bajo sus
condiciones de placa. Las potencias máximas a 25 °C son 250 y 345 mW.
No se ha confirmado que el componente montado sea de este fabricante.

Para comparar escenarios se adopta **35 °C de ambiente** y un objetivo
de revisión de **Tj ≤100 °C**. Son supuestos de ingeniería de esta revisión,
no requisitos originales del proyecto ni límites de la hoja de datos.

`Tj_estimada = Ta + P × RθJA`

Con 500 K/W, el objetivo permite 130 mW. El máximo absoluto a 35 °C
corresponde a 230 mW. Con 362 K/W, esos valores son aproximadamente
180 y 318 mW. Una estimación por encima de 150 °C señala que el punto
no queda justificado bajo ese montaje de referencia; no predice una
temperatura real exacta ni prueba que la placa vaya a alcanzar ese valor.

La copia KiCad sitúa Q3 en SOT-23, cara superior, colector en GND,
con pad de 1,475 × 0,6 mm. Contiene zonas de GND en varias capas.
No se convierte automáticamente esa conexión en un área térmica eficaz
ni en un valor de RθJA: el stackup fabricado y la distribución del cobre
no se han validado contra el montaje del fabricante.

## R21 y otras pérdidas

La potencia nominal confirmada de R21 es ¼ W y su resistencia es 10 Ω.
Ambas características se conservan en el banco y en el diseño.
Para decidir el margen práctico se propone trabajar por debajo del 50%
de su potencia nominal, sujeto al derating de la pieza real. Es un criterio
conservador elegido para el banco, no una regla universal del fabricante.

Reducir la corriente de carga no basta para controlar el consumo del driver:
al perder margen de entrada, el lazo puede aumentar fuertemente la corriente
de base del TIP42C. Aumentar R21 limita ese camino, pero también cambia el
drive disponible y puede modificar dropout, regulación y estabilidad.

## Variante de 100 Ω — comparación histórica descartada

Se simuló R21=100 Ω en un archivo separado, conservando las demás condiciones.
Se añadió una última meseta de 4,90 V de fuente para comprobar el margen inferior.
Esta comparación solo evalúa el banco de 5 V / 50 Ω; no valida una modificación
permanente a corriente nominal ni en todos los escenarios SIM-01…SIM-09.

El usuario decidió conservar R21=10 Ω / ¼ W. No se propone implementar
la variante de 100 Ω ni continuar su validación como cambio del proyecto.

## Alternativa pulsada para conservar el circuito original

La Fig. 2 de la hoja de datos proporciona impedancia térmica transitoria
típica. Pulsar puede reducir el calentamiento, pero una media de potencia
baja no garantiza por sí sola una temperatura de unión aceptable.
Hay que incluir potencia inicial, duración, repetición y picos eléctricos.

No se fija aún un pulso como condición física validada. El switch de encendido
de SIM-01 no equivale a un generador de dos niveles 8 V / entrada de dropout:
el regulador debe estar previamente habilitado, y su umbral de encendido puede
impedir arrancar directamente en el valor bajo. Tampoco un ajuste manual de
la fuente garantiza un pulso de duración controlada.

## Datos y estado de implementación

Los escenarios son `SIM-04_driver_thermal_5V.asc` y
`SIM-04_driver_R100_5V.asc`. `driver_thermal.py` comprueba finalización,
calcula potencias y promedios, y archiva los archivos y hashes en
`results/driver_thermal/`. Se conserva el escenario anterior sin modificar.

Solo sigue pendiente identificar el fabricante de Q3. R21 está confirmada
como 10 Ω / ¼ W y se conserva por instrucción del usuario. No se ha efectuado una medición
física, modificado la placa ni incorporado R21=100 Ω al diseño nominal.

## Preferencia de accionamiento — ESP32 y carga conmutada

Marco propone usar el ESP32 para habilitar/deshabilitar una resistencia de
carga mediante un MOSFET, compartiendo el montaje con regulación de carga.
Se mantiene R21=10 Ω / ¼ W. Esta preferencia sustituye el accionamiento de
entrada como primera opción a investigar, no constituye validación térmica.

La próxima comprobación debe comparar la potencia de Q3 y R21 durante los
intervalos con carga y sin carga (o con carga base), manteniendo activos los
circuitos auxiliares reales. Si la entrada está por debajo de la salida
programada, retirar la carga no garantiza que desaparezca el error de tensión
ni que el driver deje de suministrar corriente de base. No interpretar duty
cycle de la carga como duty cycle de la disipación de Q3 sin comprobarlo.

Antes de definir frecuencia y ancho de pulso: verificar establecimiento de
Vout, enable y referencia; potencia instantánea y energía de Q3/R21; y
recuperación durante el intervalo de descanso. Si la carga desconectada no
reduce suficientemente esa potencia, hará falta otro mecanismo de descanso
para dropout. El montaje de carga conmutada seguirá siendo útil para estudiar
regulación y respuesta a cambios de carga a una entrada con margen suficiente.
No hay un pulso físico autorizado por este documento ni valores temporales validados.

## Carga pulsada: comprobación completada

La carga pulsada sola no reduce la disipación de Q3 cerca del dropout:
permanece en ~352 mW aun retirando la carga externa. Una segunda corrida
con carga pulsada y bloqueo externo de TTL durante el descanso reduce Q3
a ~8,5 mW entre pulsos; durante la medición recupera la meseta original.
Ambas corridas completaron 210 ms. Se conserva R21=10 Ω / ¼ W.
Ver [método y resultados](PULSED_LOAD.md). La interfaz física y los tiempos
térmicamente admisibles todavía deben definirse; no repetir todavía el
pulso diagnóstico en la placa. El próximo paso es la interfaz ESP32/carga/bloqueo.
