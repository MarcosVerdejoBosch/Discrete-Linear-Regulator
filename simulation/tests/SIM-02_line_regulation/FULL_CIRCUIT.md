# SIM-02: validación con circuito completo

## Archivos y ejecución

- Base inalterada: `simulation/ltspice/SIM-01_startup_shutdown_5V.asc`.
- Piloto: `SIM-02_full_line_5V_pilot.asc`, 8 V, carga 5 ohm.
- Barrido: `SIM-02_full_line_5V.asc`, fuente de 6 a 11 V en pasos de 1 V.
- Se conservan todos los bloques, valores y modelos del esquema base salvo la carga y el estímulo de alimentación. No se fuerza enable ni se elimina la secuencia de arranque.
- Cada punto ejecuta un transitorio independiente de 80 ms; el switch conecta a 5 ms y queda cerrado. Temperatura 27 C, paso máximo 2 us, sin compresión de datos.
- Promedio entre 70 y 80 ms. Comparar con 60--70 ms y comprobar rizado y enable antes de aceptar cada punto.
- El parámetro VINTEST corresponde a la fuente anterior al switch. V(vbat) mide el nodo posterior y también se conserva; no confundir ambos con el nodo VIN, utilizado por otra fuente del esquema.

Comando local usado: `LTspice.exe -b -Run <ruta absoluta al .asc>`.
La instalación está en AppData/Local/Programs/ADI/LTspice. La ejecución iniciada no necesita acciones del usuario.

## Piloto completado

El log informa finalización en 55.505 s. Ventana 70--80 ms:

- Vout promedio: 5.06159 V.
- Vout mínimo/máximo: 5.06148 / 5.06176 V.
- Enable mínimo: 7.22585 V.
- Corriente de carga promedio: 1.01232 A.

Son resultados nuevos de simulación, no mediciones de hardware. No equivalen aún a una validación térmica o de tolerancias.

## Trazabilidad y límites

`results/full_circuit/preparation.json` registra base y cambios. El análisis del barrido requiere un log terminado y seis tramos completos; genera métricas y preserva esquema, netlist, log, raw y hashes.

La netlist resuelve una segunda inclusión de `phil_fet.lib` desde la carpeta original `Escritorio/Regulador`, además de las bibliotecas locales. LTspice advierte definiciones duplicadas de algunos modelos. Conservar este hecho al comparar resultados; resolver portabilidad en una revisión separada, sin modificar silenciosamente modelos durante el ensayo.

Se verificó que ambas copias de phil_fet.lib son idénticas: SHA-256
`98b9f890eb0732e8fa1b127fb16ec31cedebda98a072b65832a301e58cb5c1cf`.

El modo 3.3 V todavía no se ensayó con este banco. Debe prepararse usando el estado correcto del selector, sin confundir la fuente V5 (nodo VIN) con el selector de salida.

## Incidencia numérica del barrido

La primera ejecución con modified trap y paso máximo 2 us completó 6, 7, 8 y 9 V.
A 10 V quedó avanzando extremadamente despacio cerca de t=30.0944 ms durante
el arranque. Se detuvo ese proceso y se conservó íntegro en
`results/full_circuit/partial_modified_trap/`. No hay resultado final de 10 ni 11 V
en esa ejecución y no corresponde calcular una pendiente 6--11 V con ella.

Se preparó `SIM-02_full_line_5V_gear_check.asc`: mismo circuito, método Gear,
paso máximo 1 us, puntos 8, 10 y 11 V. El punto 8 V permite comparar ambos
métodos. No mezclar resultados de métodos distintos sin registrar y revisar
la diferencia. El análisis de cada ejecución distingue pasos completos y
estado global, aun cuando haya un archivo raw parcial.

Gear terminó el punto de 8 V con 5.061594581 V medios, frente a 5.061594535 V
con modified trap. También avanzó muy lentamente durante el arranque a 10 V;
se detuvo y preservó en partial_gear/.

## Resultado de cambios de línea

SIM-02_full_line_5V_changes.asc arranca a 8 V, cambia a 10 V entre 80 y
80.1 ms, y a 11 V entre 120 y 120.1 ms. Termina a 160 ms. Método modified
trap, paso máximo 2 us, mismo circuito y carga. Se analizan 70--80,
110--120 y 150--160 ms y se comparan con los 10 ms anteriores.

Terminó correctamente: enable activo y Vout medio de 5.061594517 V a 8 V,
5.061899620 V a 10 V y 5.062023010 V a 11 V.

combine_full_results.py combina los puntos completos de 6--9 V del primer
ensayo con 10--11 V del ensayo de cambios de línea. Conserva la historia de
cada punto; la coincidencia a 8 V es mejor que 1 uV. Pendiente entre extremos:
+0.176193 mV/V. No es un barrido DC ni un barrido completo de arranques
independientes. El informe y la figura indican este alcance.

Pendientes: modo 3.3 V completo y arranque directo a 10 V. Los resultados
históricos del banco DC reducido se conservan por separado.
