# SIM-09: loop_stability

## Estado

Completado: analisis nominal del lazo de regulacion en ambos modos, a aproximadamente 1 A y 27 C, con polarizaciones auxiliares fijas. Curvas y margenes incluidos en el informe.

## Fuentes

- [Metodo, alcance y reproduccion](REGULATION_LOOP.md)
- [Resultados y archivos trazables](results/core/)
- [TEST_Phase_Margin.asc](../../ltspice/TEST_Phase_Margin.asc): referencia original importada; no es el escenario validado del informe.

## Condiciones y resultados

| Modo | Cruce de ganancia | Margen de fase | Margen de ganancia |
|---|---:|---:|---:|
| 5 V | 558 kHz | 52.5 grados | 17.3 dB |
| 3.3 V | 530 kHz | 52.0 grados | 17.8 dB |

Se utiliza doble inyeccion de Tian, preservando los valores de compensacion y calibracion. El banco se polariza a partir del circuito completo con fuente de 8 V; mantiene el capacitor de salida de 1 uF y ESR serie de 1 ohm. Una comprobacion puntual con el circuito completo encuentra diferencias menores que 0.06 dB y 1.2 grados en la relacion de retorno por inyeccion de tension cerca del cruce.

Estos resultados no caracterizan todo el rango de carga, temperaturas, tolerancias ni la dinamica de las fuentes auxiliares. Ver el alcance exacto y las verificaciones en REGULATION_LOOP.md antes de reutilizar las curvas.
