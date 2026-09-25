# Ejecutar las simulaciones

[Tabla de todos los archivos ASC y resultados esperados](GUIA_REVISION_LTSPICE.md).

## Tres pasos en Windows

1. Descargar el ZIP de la rama de revision y **extraerlo**. Tener LTspice instalado.
2. Doble clic en **PREPARAR_LTSPICE.cmd**, en la raiz. Seleccionar la carpeta con los modelos del proyecto (tambien sirve una carpeta `Simulaciones` ya preparada). Se comprueba que esten todos y se crea `LTspice-local` sin modificar los originales.
3. En `LTspice-local`, doble clic en **ELEGIR_SIMULACION.cmd**, elegir el numero del ensayo y esperar. El selector aplica el solver verificado y abre las curvas al finalizar. Los resultados anteriores se conservan en `previous-runs`.

Tambien se puede abrir cada `.asc` y pulsar **Run**, usando el solver indicado en `scenario_catalog.json`. Mantener junto al esquema su archivo `.plt` para cargar las curvas automaticamente. En SIM-09, cada esquema ejecuta las dos inyecciones y muestra magnitud y fase.

Para evitar configurar el solver manualmente, usar **PROBAR_SIM09_5V.cmd** o **PROBAR_SIM09_33V.cmd**: ejecutan con Alternate y abren el resultado al terminar. No requieren Python. SIM-01 tiene sus propios `PROBAR_SIM01_*.cmd`: 5 V usa Normal y 3.3 V usa Alternate; los lanzadores lo seleccionan automaticamente.

No separar el `.asc`, `.bias`, `.plt`, los modelos ni `LG_single.asc`/`.asy`. Conservar el orden `.step param lg list -1 1`: la expresion usa `@1` y `@2`. Si quedo abierto un grafico con ajustes antiguos, usar **Plot Settings > Reload Plot Settings (Espacio)**.

## Vistas iniciales

SIM-02 y SIM-03 amplian el eje de salida para revisar los niveles asentados; algunos picos quedan fuera de esa escala. SIM-06 abre una vista ampliada del aumento de carga a 80 ms. Para ver toda la secuencia o la reduccion de carga a 120 ms, usar Zoom to Fit y ampliar el intervalo correspondiente. Los perfiles solo cambian la vista: no recortan los datos calculados.

## Modelos externos: una preparacion inicial necesaria

El ZIP incluye los circuitos, ajustes de curvas y resultados publicados. Las bibliotecas externas y la sonda jerarquica no estan redistribuidas: su procedencia y permisos siguen pendientes de revision. Una instalacion nueva de LTspice, por si sola, no aporta todos estos archivos. Ver [lista de dependencias](EXTERNAL_MODELS.md). Si falta alguno, el asistente indica cual y no crea una preparacion incompleta.

El asistente copia las dependencias locales y descarga IRF4905 desde Infineon si falta, verificando su SHA256. Requiere internet para esa descarga o el archivo previamente obtenido en la carpeta de modelos. No instala programas. Si falla la descarga, ejecutar `simulation/get_irf4905.ps1 -Destination "RUTA_A_LTspice-local"` antes de simular. `LTspice-local` esta excluida de Git para no publicar accidentalmente esas bibliotecas. Si ya existe, se conserva; usar otra carpeta para una nueva revision.

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

Las 16 entradas del selector SIM-01 a SIM-09 completaron la ejecucion local con la revision IRF4905. El [registro de revalidacion](../publication/U17_REVALIDATION_2026-09-24.md) identifica las condiciones y los controles complementarios. Componentes reales, informe y resultados siguen sujetos a la caracterizacion de banco.
