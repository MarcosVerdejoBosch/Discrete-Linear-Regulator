# SIM-04: carga pulsada y descanso térmico del driver

## Pregunta comprobada

Marco propone un ESP32 para conectar/desconectar la carga, compartiendo el
montaje con regulación de carga. Se conserva R21=10 Ω / ¼ W. La prueba comprueba
si retirar la carga externa reduce la potencia de Q3 y R21 cerca del dropout.

## Condiciones y archivos

- Modo 5 V; circuito completo y calibración conservados.
- RV10=100 kΩ, RV12=47 kΩ; R21 permanece en 10 Ω.
- Modelos eléctricos a 27 °C, sin autocalentamiento.
- Arranque a 8 V; control a 5,10 V; después, fuente constante de 4,94 V.
- Carga conmutada idealmente entre 50 Ω y 1 MΩ mediante una tabla de
  conductancia. No se ha modelado todavía el MOSFET físico ni el ESP32.
- Flancos de conductancia de 10 µs; pulsos de 150–160 y 180–190 ms.
  Son tiempos de diagnóstico, no una frecuencia ni duración aprobada para banco.
- Duración total 210 ms, paso máximo 2 µs, solver Normal y `trtol=1`.
- Medias sobre 4,96 ms, dejando 20 µs de guarda respecto de los límites
  de las ventanas nominales para excluir la conmutación de las medias DC.

El escenario principal es `SIM-04_pulsed_load_5V.asc`. Su generación y hashes
están en `results/pulsed_load/preparation.json`. `pulsed_load.py analyze`
exige finalización y archiva ASC, netlist, log, RAW, CSV y métricas.

## Resultado de conmutar solamente la carga

La corrida completó el intervalo solicitado. A 4,94 V de fuente, la corriente
externa cambia entre aproximadamente 98 mA y 5 µA, pero Q3 mantiene unos
352 mW. R21 disipa aproximadamente 214 mW durante la carga y 217 mW durante
el intervalo sin carga. El promedio de Q3 sobre cada ciclo completo es
aproximadamente 352 mW: no se obtiene descanso térmico para ese transistor.

La salida se asienta cerca de 4,895 V con carga y 4,922 V sin ella. Retirar
la carga no restablece los 5 V programados; la corriente de base del transistor
de paso permanece alrededor de 146–147 mA. Por eso el duty cycle de la carga
no representa el duty cycle de la disipación del driver.

El control a 5,10 V sí mantiene Vout alrededor de 4,999 V; Q3 disipa unos
26 mW con carga y 17 mW sin carga. La objeción corresponde a la condición
de dropout ensayada, no al uso general de un ESP32 para conmutar la carga.

[Figura de diagnóstico](results/pulsed_load/pulsed_load_driver.pdf) ·
[Datos y hashes](results/pulsed_load/metrics.json)

## Alternativa: carga conmutada y bloqueo externo del drive

El escenario `SIM-04_pulsed_load_inhibit_5V.asc` añade solamente un camino
externo que tira TTL a GND durante el intervalo sin carga. Se representa
idealmente con 0,1 Ω cuando actúa y 1 GΩ cuando se libera. No fuerza TTL alto:
UVLO, OVLO y el retardo conservan la posibilidad de impedir la habilitación.

La tabla siguiente es una especificación funcional para el futuro circuito
de interfaz, no un permiso para conectar TTL directamente al GPIO:

| Estado | Carga externa | Bloqueo externo de TTL | Control del pass |
|---|---|---|---|
| Descanso | Desconectada | Activo | Deshabilitado |
| Medición | Conectada | Liberado | Permitido solo si las protecciones lo habilitan |
| ESP32 arrancando o sin control | Desconectada | Debe quedar activo por hardware | Deshabilitado |

La interfaz real debe respetar los niveles de tensión y tener un estado seguro
durante el arranque del ESP32. El circuito de prueba se conecta a la red TTL
identificada en KiCad; no confundirla automáticamente con el punto TP_TTL,
que está al otro lado de R20 según la revisión previa de conectividad.

El arranque a 8 V establece los permisos de protección antes de bajar la
entrada. No se presupone que la placa pueda arrancar directamente a 4,94 V.
La variante ideal conmuta carga y bloqueo simultáneamente; el orden real,
los retardos de interfaz y las transiciones deben comprobarse al diseñarla.

Se procesa con `pulsed_load.py analyze inhibit`. Su archivo de preparación,
condiciones y resultados corresponden a `results/pulsed_load_inhibit/`.

## Resultado del bloqueo externo

La segunda corrida también completó 210 ms. El bloqueo externo sí establece
un estado de baja disipación durante el intervalo sin carga:

| Estado a 4,94 V de fuente | Q3 (mW) | R21 (mW) | Vout (V) |
|---|---:|---:|---:|
| Carga activa, drive permitido | 351.82 | 213.929 | 4.89467 |
| Carga retirada, drive bloqueado | 8.54 | 0.000 | 0.02527 |

La referencia principal permanece alrededor de 2,47364 V. La salida durante
el pulso reproduce la meseta de 4,89467 V obtenida con la carga continua.
En ambos pulsos, entra y permanece dentro de ±1 mV de su media final después
de aproximadamente 40 µs desde la orden. Este tiempo pertenece al modelo y
al actuador ideal; no es una especificación del banco físico.

Con los 10 ms activos y 20 ms de descanso empleados como diagnóstico, la
potencia media de Q3 baja a 123,13 mW y la de R21 a 71,39 mW. La energía de
Q3 por ciclo de 30 ms es 3,69 mJ, frente a 10,55 mJ con carga pulsada sola.
La reducción del promedio no valida por sí sola el ciclo de trabajo térmico:
hay que comprobar temperatura de pico, repetición, interfaz y componente real.

Al incluir los flancos de apagado, aparecen picos numéricos de 417 mW
en Q3 y 299 mW en R21. El último supera brevemente su rating continuo
de 250 mW; hay que evaluar la capacidad de pulso de la pieza real y la
secuencia de desconexión. No se ocultan estos flancos ni se consideran
validados por las medias de las mesetas.

El sumidero ideal de TTL presenta un pico numérico de aproximadamente 37 mA.
No se debe trasladar ese nodo directamente a un GPIO. La corriente y los
retardos se verificarán de nuevo con una interfaz real y su limitación de corriente.

[Figura con bloqueo externo](results/pulsed_load_inhibit/pulsed_load_driver.pdf) ·
[Datos, ventanas y hashes](results/pulsed_load_inhibit/metrics.json)

### Decisión para continuar

Usar el ESP32 y la carga conmutada compartidos, añadiendo un bloqueo externo
de enable para el modo de prueba de dropout. En regulación de carga, ese
bloqueo se mantiene liberado para que el regulador permanezca habilitado.
R21 sigue siendo 10 Ω / ¼ W y las protecciones conservan prioridad.

El siguiente entregable es el esquema de la interfaz ESP32/carga/bloqueo,
incluyendo estado de arranque seguro y secuencia de control. Las duraciones
ensayadas siguen siendo diagnósticas, no instrucciones para energizar la placa.

## Alcance del resultado para el banco

Conmutar solo la carga queda descartado como medio de descanso térmico en
esta condición de dropout. El montaje sigue siendo útil para regulación de
carga y respuesta transitoria con una entrada que mantenga regulación.

Antes de ejecutar la alternativa física se requiere comprobar la interfaz,
establecer los tiempos de medición y evaluar el régimen térmico pulsado.
Un promedio de potencia menor no equivale por sí solo a una temperatura de
unión validada. Fabricante de Q3 y comportamiento térmico de la placa real
siguen pendientes. El protocolo de lectura de los pulsos con el osciloscopio
tampoco se sustituye por una lectura DC ordinaria del multímetro.
