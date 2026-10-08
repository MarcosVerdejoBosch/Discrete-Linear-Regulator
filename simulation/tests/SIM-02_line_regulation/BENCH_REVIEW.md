# Revisión del banco SIM-02

## Alcance confirmado

Se revisaron los esquemas guardados y los resultados DC originales. Ambos bancos
contienen 122 instancias de componentes; SIM-01 contiene 212. No son el mismo
esquema con una directiva de análisis diferente.

- Los bancos DC carecen del switch SWLOAD de SIM-01 y del LTC1044 U10.
- Incluyen una fuente controlada E1 de ganancia -1.84, ausente en SIM-01.
- La instancia R33 vale 14k en ambos bancos DC y 14.5k en SIM-01.
- RLOAD vale 5 ohm / 3.3 ohm; SIM-01 usa 50 ohm.
- Hay componentes ausentes y designadores reutilizados: una comparación por
  nombre no demuestra equivalencia funcional ni identifica por sí sola la causa
  de la diferencia de tensión de salida.

El inventario comparado está en results/component_comparison.txt. Esta revisión
no demuestra equivalencia de conectividad ni de modelos con la placa fabricada.
La diferencia de salida entre SIM-01 y SIM-02 no debe atribuirse únicamente a
calibración sin una revisión eléctrica adicional.

## Qué respalda el informe

Los raw reproducen los resultados de los logs: magnitud de pendiente entre
6 y 11 V de 1.113129 y 1.136017 mV/V. La pendiente tiene signo negativo.
El informe identifica estos resultados como correspondientes a bancos DC
reducidos y conserva pendiente la validación con el circuito completo actual.

Se retiró de la columna Typ la media aritmética de extremos: no era una
medición a tensión nominal ni un valor típico estadístico. La exactitud se
expresa como error absoluto máximo observado, no como un intervalo garantizado ±.

## Siguiente validación

Preparar una variante del esquema completo con alimentación aplicada y habilitación
normal. Barrer 6--11 V, inicialmente con las mismas cargas resistivas y temperatura.
Si las funciones de arranque impiden un punto DC representativo, usar escalones
de entrada y medir después de asentamiento, verificando enable y referencias.
Registrar cualquier simplificación explícita. No reemplazar estos datos históricos
ni la tabla sin resultados nuevos comprobados.
