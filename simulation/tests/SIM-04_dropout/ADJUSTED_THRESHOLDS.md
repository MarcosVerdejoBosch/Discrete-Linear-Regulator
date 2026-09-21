# SIM-04: exploración con umbrales ajustados

Variante separada del ensayo de entrada mínima con umbrales originales.
No se modificaron los esquemas originales ni se anularon protecciones.
La revisión personal de Marco y la implementación física siguen pendientes.

## Ajustes y condiciones

| Elemento en la placa | Equivalente LTspice | Valor original simulado | Variante | Máximo confirmado por Marco |
|---|---|---:|---:|---:|
| RV10, ajuste UVLO | R70 | 75 kΩ | 100 kΩ | 100 kΩ |
| RV12, umbral previo al retardo | R65 | 15 kΩ | 47 kΩ | 50 kΩ |

La correspondencia se comprobó contra la conectividad exportada del esquema
KiCad. RV12 cambia la entrada necesaria para iniciar/mantener la secuencia;
no es el ajuste de la constante de tiempo del retardo. Se conservan la
calibración de salida, las resistencias fijas, RV11 y las demás protecciones.

- Circuito completo, modelos nominales a 27 °C, sin modelo de autocalentamiento.
- Cargas de 50 Ω en 5 V y 33 Ω en 3,3 V: aproximadamente 100 mA cuando regula;
  la corriente disminuye al caer Vout, porque la carga es resistiva.
- Arranque a 8 V durante 80 ms, descenso a 2,8 V a −0,1 V/ms, final a 142 ms.
- Solver Normal, `trtol=1`, paso máximo 2 µs, compresión deshabilitada.
- Criterio exploratorio: salida 100 mV por debajo de su media inicial.
  No confundirlo con el criterio anterior de 98% nominal, particularmente en 3,3 V.

## Resultado de la rampa

Ambas corridas completaron 142 ms. En 5 V, la salida alcanza el criterio de
100 mV a 110,550 ms: entrada de placa VBAT ≈4,942 V, Vout ≈4,900 V y
VCTRL ≈4,929 V. La referencia principal cambia aproximadamente −0,172 mV
respecto de su media inicial. Enable y permiso de retardo siguen activos;
la primera conmutación de UVLO aparece después, a 112,032 ms.

En 3,3 V, UVLO conmuta primero, a 112,082 ms, con VBAT ≈4,790 V.
El criterio de pérdida de 100 mV se alcanza después del apagado. Por tanto,
**el recorrido real de estos dos potenciómetros permite explorar la pérdida
de regulación en 5 V, pero todavía no permite medir dropout en 3,3 V**.
No se presume que ambas configuraciones tengan igual margen de entrada.

La rampa también muestra conmutaciones repetidas de UVLO/enable cerca del
apagado con estos ajustes extremos. No se recortaron ni ocultaron en la
[figura de diagnóstico](results/adjusted/SIM-04_adjusted.pdf).
Esta variante no valida la histéresis ajustada como configuración final de la placa.

## Qué diferencia de tensión se está calculando

- VBAT − Vout: margen entre entrada de placa y salida, incluyendo los caminos
  de polaridad/startup, transistor de paso y resistencia de sensado.
- VCTRL − Vout: margen de la etapa reguladora, incluyendo la resistencia de sensado.
- VCTRL − N008: tensión emisor-colector del TIP42C, sin la resistencia de sensado.

En el cruce de la rampa resultan aproximadamente 42,1, 28,9 y 19,0 mV,
respectivamente. Son resultados del modelo bajo este criterio y esta carga;
no especificaciones garantizadas ni mediciones de hardware.

## Comprobación con entrada fija

La corrida adicional de 5 V completó 163 ms. Después del arranque se mantuvo
cada entrada durante 15 ms; se promediaron los últimos 5 ms. Enable permaneció
por encima de 0,90 veces VEE en todas las ventanas. La referencia principal
se mantuvo alrededor de 2,47365 V en las cuatro mesetas de baja entrada.

| Fuente (V) | Entrada de placa (V) | Vout (V) | Caída de Vout (mV) | Magnitud de corriente de base TIP42C (mA) |
|---:|---:|---:|---:|---:|
| 5.10 | 5.09860 | 4.99934 | 0.68 | 2.3 |
| 5.00 | 4.99700 | 4.95432 | 45.70 | 151.8 |
| 4.95 | 4.94705 | 4.90461 | 95.41 | 147.1 |
| 4.94 | 4.93706 | 4.89467 | 105.35 | 146.2 |

El criterio de pérdida de 100 mV queda entre 4,94 y 4,95 V de fuente, o
aproximadamente 4,937–4,947 V en la entrada de placa. En esas dos mesetas,
VBAT − Vout es aproximadamente 42,4 mV y VCTRL − Vout, 28,9 mV.
La diferencia entre las medias de las dos mitades de cada ventana es menor
que 0,001 mV, con ondulación pico a pico menor que 0,45 mV. Esto respalda que
la caída persiste con entrada fija; no demuestra autocalentamiento ni
convergencia frente a todos los ajustes de solver y paso temporal.

La estimación de disipación de Q3 es 344–346 mW y R21 disipa 214–231 mW
en las mesetas de fuente entre 4,94 y 5,00 V. Ver
[resultados completos y hashes](results/adjusted_settled/metrics.json).

## Hallazgo para la implementación física

En ese mismo cruce, el TIP42C recibe aproximadamente **147 mA de corriente
de base** para una corriente de colector de unos 99 mA. La baja tensión
emisor-colector coincide con una fuerte sobreexcitación de base. La corriente
por la resistencia de drive R21 (R15 en LTspice, 10 Ω) es aproximadamente
147 mA: unos 215 mW en esa resistencia. No debe confundirse esta corriente
con la corriente entregada a la carga.

El esquema de la placa identifica Q3 como BC807 en SOT-23. Una estimación de
su disipación usando la tensión de emisor y la corriente del camino de drive
es del orden de **0,35 W**, sin incluir exactamente las contribuciones de los
espejos de polarización y la base. Esto requiere revisión térmica antes de
un ensayo físico sostenido, aunque la carga sea solo de 100 mA.

Como referencia, [Nexperia, BC807 series, sección 8](https://assets.nexperia.com/documents/data-sheet/BC807_SER.pdf)
indica 250 mW a 25 °C sobre huella estándar y 345 mW con 1 cm² de cobre en
colector, con reducción a mayor temperatura. No se ha confirmado el fabricante
montado ni que la placa reproduzca esas condiciones. El modelo eléctrico
de LTspice no demuestra que esta disipación sea aceptable en la placa.

El siguiente paso de implementación es revisar Q3 y la potencia admisible de
R21; no copiar automáticamente el procedimiento de lecturas lentas del ensayo
de protecciones. La medición de dropout queda pendiente de esa revisión.

## Archivos y reproducción

- `prepare_adjusted.py`: genera los dos escenarios ajustados desde las copias
  calibradas de SIM-02; no ejecutar sobre una corrida en curso.
- `analyze_adjusted.py analyze`: exige final completo, extrae eventos y archiva
  esquemas, netlists, logs, RAW y hashes en `results/adjusted/`.
- `plot_adjusted.py`: genera PDF, SVG, PNG y CSV a partir de esos resultados.
- `prepare_settled.py`: comprobación independiente con valores de entrada fijos
  para 5 V, manteniendo todos los componentes de esta variante.
- `analyze_settled.py analyze`: comprueba final completo y promedia las mesetas;
  resultados y hashes en `results/adjusted_settled/`.

La exploración preliminar con RV10=200 kΩ fue interrumpida al conocer su máximo
real. Se conserva únicamente como intento incompleto fuera de rango en
`results/adjusted_out_of_range/`; no respalda estos resultados ni el informe.

## Revisión térmica completada

La comprobación con corrientes de terminales da 352–353 mW en Q3 cerca de
dropout. No queda justificado el ensayo DC original con los montajes térmicos
de referencia. Una variante solo simulada con R21=100 Ω reduce Q3 a ~45 mW
y R21 a ~28 mW en las mesetas; no fue adoptada en la placa ni en el diseño.
Ver [revisión, supuestos y alternativas de banco](THERMAL_REVIEW.md).

**Decisión vigente (2026-09-20):** R21 se mantiene en 10 Ω / ¼ W por
instrucción de Marco. Los 100 Ω son una comparación histórica descartada;
el próximo banco conservará el circuito original. Ver THERMAL_REVIEW.md.
