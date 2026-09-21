# SIM-01: calibrated startup / shutdown

Current candidate: [calibrated scenarios and results](CALIBRATED_STARTUP.md). Both modes completed at 8 V, 50/33 ohm, with the SIM-02 calibration. [Hardware bench plan](BENCH_PLAN.md) adapted to the OWON VDS1022. Complete 140 ms refinement check passed with 1 us maximum step and explicit trtol=1; user approval before freezing remains pending. The bench plan now links the P-MOS switch schematic and ESP32 program.

# Historical SIM-01: startup_shutdown

## Estado

Revisado parcialmente; falta sensibilidad a ESR e impedancia de fuente.

## Fuentes

- [SIM-01_startup_shutdown_5V.asc](../../ltspice/SIM-01_startup_shutdown_5V.asc): copia identificada del escenario, sin cambios eléctricos.

## Condiciones y resultados

8 V de fuente; carga de 50 ohm; modo nominal 5 V; 27 °C. Control del switch: conexión a 5 ms, apertura a 55 ms, reconexión a 85 ms. Duración 140 ms, paso máximo 1 us. Modelo SWLOAD: Ron=10m, Roff=1e9, Vt=2.5, Vh=-0.2.

Resultados del switch: Vout estable 5.0616 V; habilitación 23.818 ms desde conexión; pulso inicial 0.854 V, reencendido 1.164 V; caída por debajo de 50 mV: OUT 0.393 ms y VCTRL 12.472 ms desde apertura. Son resultados de simulación, no mediciones.

`results/source_voltage_fall/` corresponde al ensayo anterior, fuente forzada a cero. `results/input_switch/` corresponde a desconexión por switch. No mezclar ambos. Sus PDF son figuras de revisión. El archivo signals.txt conserva la exportación del usuario; no se ejecutó de nuevo LTspice desde esta copia.

## Figura del informe

[SIM-01_startup_shutdown_5V.pdf](../../../docs/figures/SIM-01_startup_shutdown_5V.pdf), incluida en `Electrical Characteristics / Startup and Shutdown Behavior`.

- Panel (a): V(vbat), V(vctrl), V(comp), V(ttl) y V(out), de 2 a 40 ms. Origen local: conexión a 5 ms; incluye 3 ms anteriores.
- Figura independiente `SIM-01_initial_transient_5V.pdf`: V(vctrl) y V(out), de 4.98 a 5.2 ms, con origen local en la conexión e incluyendo 0.02 ms anteriores. Incluida en el informe.
- Panel (b): V(vbat), V(vctrl) y V(out), de 54 a 65 ms. Origen local: apertura a 55 ms; incluye 1 ms anterior. Los tiempos de cruce por 50 mV se obtienen del registro completo, no de esta ventana acotada.
- V(vbat) se presenta como Input after switch: es el nodo aguas abajo del switch, no la fuente ideal antes del switch. Se representa su tensión exportada real, sin imponer una caída artificial a cero.
- Etiquetas: V(vctrl) = Startup-circuit output (alimentación a la salida del arranque); V(comp) = UVLO/OVLO reference (referencia de U8); V(out) = Output; V(ttl) = Enable.
- Habilitación: cruce ascendente de V(ttl) por 3.5 V. Referencia: cruce por 2.45 V. Descarga: primer cruce descendente por 50 mV.
- La figura muestra el primer encendido y apagado; la reconexión a 85 ms permanece en los datos y no está representada.

## Verificación sencilla en LTspice

1. Abrir `simulation/ltspice/SIM-01_startup_shutdown_5V.asc` desde este proyecto.
2. Ejecutar Run. Si falta un símbolo o modelo, consultar `simulation/DEPENDENCIES.md` antes de reemplazar componentes.
3. Agregar las señales indicadas arriba y comprobar las mismas ventanas de tiempo. LTspice muestra tiempos absolutos; la figura resta 5 ms o 55 ms.
4. Comparar secuencia, pulso inicial y tiempos de descarga con estos resultados. Conservar cualquier ensayo modificado como una variante, sin sobrescribir esta referencia.

La figura se regenera con `regenerate-figures.cmd` desde la raíz del proyecto. Usa NumPy y Matplotlib, con estilo compartido y versiones registradas; ver `simulation/plotting/README.md`. Genera PDF, SVG y PNG desde la exportación preservada, sin ejecutar LTspice.

Pendiente: explicar/medir transición inicial, ESR e impedancia de fuente; unificar ajustes con tablas DC y revisar modelo del MOSFET de entrada.
