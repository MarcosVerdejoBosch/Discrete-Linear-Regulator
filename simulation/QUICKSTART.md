# Ejecutar las simulaciones

## Tres pasos en Windows

1. Descargar el ZIP de la rama de revision y **extraerlo**. Tener LTspice instalado.
2. Doble clic en **PREPARAR_LTSPICE.cmd**, en la raiz. Seleccionar la carpeta con los modelos del proyecto (tambien sirve una carpeta `Simulaciones` ya preparada). Se comprueba que esten todos y se crea `LTspice-local` sin modificar los originales.
3. En `LTspice-local`, abrir **SIM-09_loop_5V.asc** o **SIM-09_loop_33V.asc** y pulsar **Run**, usando solver **Alternate**. Cada esquema ejecuta las dos inyecciones y su archivo `.plt` muestra magnitud y fase automaticamente.

Para evitar configurar el solver manualmente, usar **PROBAR_SIM09_5V.cmd** o **PROBAR_SIM09_33V.cmd**: ejecutan con Alternate y abren el resultado al terminar. No requieren Python. SIM-01 tiene sus propios `PROBAR_SIM01_*.cmd`, con solver Normal.

No separar el `.asc`, `.bias`, `.plt`, los modelos ni `LG_single.asc`/`.asy`. Conservar el orden `.step param lg list -1 1`: la expresion usa `@1` y `@2`. Si quedo abierto un grafico con ajustes antiguos, usar **Plot Settings > Reload Plot Settings (Espacio)**.

## Modelos externos: una preparacion inicial necesaria

El ZIP incluye los circuitos, ajustes de curvas y resultados publicados. Las bibliotecas externas y la sonda jerarquica no estan redistribuidas: su procedencia y permisos siguen pendientes de revision. Una instalacion nueva de LTspice, por si sola, no aporta todos estos archivos. Ver [lista de dependencias](EXTERNAL_MODELS.md). Si falta alguno, el asistente indica cual y no crea una preparacion incompleta.

El asistente no descarga programas ni modelos. Solo copia dependencias locales. `LTspice-local` esta excluida de Git para no publicar accidentalmente esas bibliotecas. Si ya existe, se conserva; usar otra carpeta para una nueva revision.

Instalacion de LTspice en otra ubicacion: definir `LTSPICE_EXE` antes de usar los lanzadores SIM-09. Para preparar sin dialogo o indicar otra biblioteca:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File simulation/prepare_windows.ps1 -Models "D:\Modelos" -LtspiceLib "D:\LTspice\lib" -Destination "D:\Prueba nueva"
```

## Que muestra SIM-09

Retorno del lazo principal por doble inyeccion de Tian, alrededor de un punto de operacion estacionario guardado. Aproximadamente 1 A, 27 C, capacitor de salida 1 uF con resistencia serie externa de 1 ohm; polarizaciones auxiliares fijas.

| Salida | Margen de fase | Margen de ganancia |
|---|---:|---:|
| 5 V | 52.51 grados | 17.28 dB |
| 3.3 V | 51.98 grados | 17.75 dB |

Estos resultados describen la simulacion nominal; no son mediciones de la placa ni validacion de todos los lazos auxiliares. Cambiar la topologia requiere revisar o regenerar el `.bias`.

Las figuras con referencias punteadas estan en [interactive_review](tests/SIM-09_loop_stability/interactive_review). Los cuatro CIR historicos con inyecciones separadas se conservan para trazabilidad; **para la revision interactiva usar los dos ASC indicados arriba**.

## Figuras para el informe (opcional)

Para regenerar los graficos de Python en la carpeta preparada, instalar Python 3, NumPy y Matplotlib y ejecutar `python probar_sim09.py --open`. Si ya corrio ambos circuitos, usar `python probar_sim09.py --plot-only --open`. Esto es opcional: LTspice muestra las curvas sin Python.

SIM-02 a SIM-08 y sus condiciones se encuentran en el [indice](README.md). Sus resultados anteriores estan documentados; esta actualizacion verifica nuevamente SIM-09 y no afirma haber repetido todos los estudios. Componentes reales, informe y resultados siguen sujetos a revision.
