# Revisión pendiente del usuario

Las 16 entradas principales ya fueron confirmadas por Marco. La revisión visual del informe está pospuesta. Esta lista cubre solamente los estudios adicionales.

Abrir **ELEGIR_ESTUDIO_ADICIONAL.cmd** en la carpeta Simulaciones. El selector aplica el solver. Si se abre directamente el ASC, usar Alternate para los Bode. Cada Run calcula las dos inyecciones y muestra un Bode para una condición. El comentario del esquema identifica el archivo de la otra carga.

Para empezar con la comparación principal: casos **1, 6, 3, 8** (5 V sin CEXT / con 10 µF), y **11, 16, 13, 18** (equivalentes de 3,3 V). Después pueden revisarse 1 µF, 47 µF y la variante de 10 µF / 1 Ω. Todos conservan la rama de placa de 1 µF + 1 Ω.

| Opción | Archivo ASC (sin extensión) | PM esperado | GM esperado |
|---|---|---:|---:|
| 1 | `SIM-09_external_5V_100mA_0u_R0` | 57.3° | 18.3 dB |
| 2 | `SIM-09_external_5V_100mA_1u_R0p1` | 46.7° | 15.6 dB |
| 3 | `SIM-09_external_5V_100mA_10u_R0p1` | 72.8° | 35.3 dB |
| 4 | `SIM-09_external_5V_100mA_47u_R0p1` | 77.5° | 36.3 dB |
| 5 | `SIM-09_external_5V_100mA_10u_R1` | 77.1° | 22.9 dB |
| 6 | `SIM-09_external_5V_1A_0u_R0` | 52.5° | 17.3 dB |
| 7 | `SIM-09_external_5V_1A_1u_R0p1` | 41.0° | 14.9 dB |
| 8 | `SIM-09_external_5V_1A_10u_R0p1` | 81.6° | 32.8 dB |
| 9 | `SIM-09_external_5V_1A_47u_R0p1` | 99.8° | 33.6 dB |
| 10 | `SIM-09_external_5V_1A_10u_R1` | 67.9° | 21.1 dB |
| 11 | `SIM-09_external_33V_100mA_0u_R0` | 53.8° | 18.4 dB |
| 12 | `SIM-09_external_33V_100mA_1u_R0p1` | 39.2° | 15.0 dB |
| 13 | `SIM-09_external_33V_100mA_10u_R0p1` | 65.1° | 35.3 dB |
| 14 | `SIM-09_external_33V_100mA_47u_R0p1` | 85.1° | 36.3 dB |
| 15 | `SIM-09_external_33V_100mA_10u_R1` | 70.6° | 22.9 dB |
| 16 | `SIM-09_external_33V_1A_0u_R0` | 52.0° | 17.8 dB |
| 17 | `SIM-09_external_33V_1A_1u_R0p1` | 37.3° | 14.9 dB |
| 18 | `SIM-09_external_33V_1A_10u_R0p1` | 71.5° | 32.9 dB |
| 19 | `SIM-09_external_33V_1A_47u_R0p1` | 103.2° | 33.6 dB |
| 20 | `SIM-09_external_33V_1A_10u_R1` | 65.2° | 21.4 dB |

Los valores son referencias numéricas redondeadas de las corridas documentadas, no tolerancias de aceptación del hardware. Los perfiles PLT muestran la expresión del lazo; las tablas y superposiciones de las figuras se calculan aparte a partir de los CSV.

## Dropout: validar el cambio de umbrales

**Opciones 23 y 24:** `SIM-04_adjusted_5V.asc` y `SIM-04_adjusted_33V.asc`. UVLO sigue conectado. RV10 = 100 kΩ y RV12 = 47 kΩ; los valores nominales de las 16 pruebas principales no cambian. Las curvas preseleccionadas muestran entrada/salida y señales de permiso.

- 5 V, Normal: fuente 8 → 4 V; 100 mV de pérdida de salida cerca de 4,947 V de entrada, antes de que actúe UVLO.
- 3,3 V, Alternate: UVLO actúa primero, cerca de 4,793 V. Este caso confirma el límite de protección; no obtiene dropout intrínseco.
- Opciones 21 y 22: diagnósticos con permiso UVLO anulado. Son otros ensayos y no reemplazan la validación del cambio de umbral.

Dejar constancia al cerrar: casos ejecutados, si completaron y cualquier diferencia observada. No marcar los estudios adicionales como aceptados hasta recibir esa confirmación.
