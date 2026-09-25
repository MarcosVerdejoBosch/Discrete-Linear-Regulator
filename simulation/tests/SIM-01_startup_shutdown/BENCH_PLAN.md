# SIM-01 - Correspondencia con el banco real

## Accesorio de conmutacion preparado

Esquema KiCad/PDF, lista de compra, conexion y programa ESP32 disponibles en
[SIM01_InputSwitch](../../../hardware/bench/SIM01_InputSwitch/README.md).
Usa IRF4905 y BC547B, control GPIO25 de un ESP32 clasico, fuente mantenida en 8 V.
La propuesta esta revisada por conexiones; faltan compilacion ESP32 y prueba fisica.
Medir el frente de entrada real antes de compararlo con el switch ideal de SIM-01.

## Pregunta que responde

Comprobar el orden referencia -> enable -> salida, observar el pulso previo a habilitacion y la descarga despues de desconectar la entrada. Comparar ambos modos con la misma calibracion que SIM-02. No es una prueba de regulacion a plena carga ni una medida de capacidad termica, ni caracteriza el arranque a todas las tensiones.

## Condiciones nominales candidatas

Fuente de 8 V; carga resistiva de 50 ohm en 5 V y 33 ohm en 3.3 V (aproximadamente 100 mA). Conexion a 5 ms, desconexion a 55 ms, reconexion a 85 ms; registro hasta 140 ms. Transicion del control del switch de 1 us, Ron 10 mohm, Roff 1 Gohm y Vh negativo para transicion suave. La duracion real de Vin en la placa debe medirse: 1 us de control no impone una rampa lineal de Vin.

Las potencias nominales de carga son Vout^2/R: 0.50 W y 0.33 W. Como propuesta practica, resistencias de al menos 1 W permiten margen respecto de esos valores nominales, sujeto a sus condiciones de montaje y especificaciones. Registrar sus resistencias reales. El transistor de paso disipa aproximadamente 0.3 W / 0.47 W por la carga a 8 V (estimacion (Vin-Vout)*Iout, sin consumo auxiliar). No confundir esa estimacion con medicion de temperatura.

## Conexion propuesta

Fuente + -> interruptor serie -> entrada + de placa; fuente - -> retorno de placa. Resistencia entre salida y retorno. No agregar camino de descarga de la fuente a la placa al abrir el interruptor.

- Primera captura: entrada despues del interruptor y salida; disparo por flanco de entrada.
- Segunda captura: salida del circuito Start Up y salida del regulador, conservando referencia temporal de entrada si hay un tercer canal o disparo externo.
- Con cuatro canales, observar entrada, salida, Start Up y enable. Referencia UVLO/OVLO puede requerir otra captura con las mismas condiciones.
- Identificar en KiCad los pads/puntos reales antes de conectar sondas; los nombres LTspice no son instrucciones de pinout.
- Todas las masas de sondas comunes se conectan al retorno de la placa. No conectar una masa de osciloscopio a un nodo alto. Confirmar referencia a tierra del equipo disponible.

Un interruptor manual sirve para una primera comprobacion funcional, pero sus rebotes impiden asumir el flanco limpio de la simulacion. Para comparar formas de onda, registrar Vin real y reproducir despues ese estimulo en LTspice, o usar un interruptor electronico caracterizado. Apagar el boton de salida de la fuente puede introducir su propia rampa o descarga activa: no asumir que equivale a abrir el circuito.

## Capturas y criterios

1. Encendido: incluir unos ms antes de conectar y al menos 35 ms posteriores. Registrar niveles finales y orden de las seÃƒÂ±ales.
2. Detalle inicial: ventana de -20 a 200 us respecto de conexion; verificar si existe pulso en Vout y su relacion con VCTRL.
3. Apagado: guardar al menos 30 ms completos aunque la figura principal muestre solo los primeros 10 ms. Esto permite medir la cola de descarga y revisar la reconexion.
4. Reconexion: conservar registro completo. El estado residual de capacitores puede diferir del primer encendido; no asumir arranque desde cero.
5. Medir tiempo a 98% de la salida nominal despues de enable. Para enable se usa 3.5 V como convencion temporal, no como especificacion del umbral logico de transistores. Para la referencia se usa 2.45 V. Descarga: primer cruce por debajo de 50 mV; revisar ruido y posibles recruces antes de interpretarlo.

No calibrar nuevamente entre encendido y reconexion. No adoptar picos de corriente ideales como requisito del banco. La ESR de C11 y la impedancia de fuente/cables no estan completamente modeladas; el pulso y el frente se contrastaran usando condiciones reales. El osciloscopio debe permitir ver tanto la secuencia de decenas de ms como el detalle de cientos de us, con ajustes registrados y sondas adecuadas.

## Pendiente antes de ejecutar en placa

Confirmar fuente, resistencia/carga disponible, osciloscopio, tipo de interruptor y puntos accesibles en PCB. No se necesita medir aun para revisar y aprobar este escenario nominal; la comparacion fisica quedara identificada como una validacion posterior.

## Adaptacion al equipo confirmado por Marco

Marco dispone de OWON VDS1022 de dos canales, fuente regulable y resistencias. Los valores/potencias exactos y el sistema de desconexion aun deben registrarse.

La documentacion de OWON especifica 25 MHz, hasta 100 MS/s, memoria de 5K puntos y conversion de 8 bits para VDS1022(I). La memoria requiere separar vista general y detalle: no se conserva la resolucion maxima de muestreo al abarcar decenas de ms. Referencia: https://www.owon.com.hk/products_owon_vds_series_pc_oscilloscope y manual https://files.owon.com.cn/probook/VDS_Series_User_Manual.pdf . El VDS1022 no debe confundirse con la variante VDS1022I de USB aislado; no asumir entradas diferencialmente aisladas.

Ajustes iniciales propuestos, adaptables al rango real observado; escalas de tension referidas a la punta de la sonda:

| Captura | CH1 | CH2 | Base de tiempo inicial | Disparo |
|---|---|---|---|---|
| Arranque general | Entrada despues del switch, 2 V/div | Salida, 1 V/div | 5 ms/div | Single, CH1 ascendente, cerca de 4 V |
| Detalle del pulso | Entrada, 2 V/div | Salida, 0.5 V/div | 20 us/div | Single, CH1 ascendente, cerca de 4 V |
| Polarizacion inicial | VCTRL, 0.5 V/div | Salida, 0.5 V/div | 20 us/div | CH1 ascendente; registrar nivel, no equiparar este origen a Vin |
| Descarga general | Entrada, 2 V/div | Salida, 1 V/div | 1 ms/div | Single, CH1 descendente; ajustar nivel a la caida observada |
| Cola de descarga | Entrada, 2 V/div | VCTRL, 1 V/div | 5 ms/div | Single, CH1 descendente |

Usar acoplamiento DC, sondas compensadas y el mismo factor configurado en sonda/software; conservar pretrigger. Registrar frecuencia de muestreo y cantidad de puntos reales indicadas por el programa. Con 5K puntos en 50 ms, el intervalo medio seria 10 us: suficiente para secuencia general, insuficiente para resolver todo frente rapido. En 200 us el intervalo ideal seria 40 ns, sujeto a los modos del software.

El cruce de 50 mV no se puede cuantificar de forma fiable con una escala vertical que cubra toda la salida y un convertidor de 8 bits. Si interesa medirlo, agregar una captura de la cola con menor escala (p. ej. 50--100 mV/div), revisar offset/ruido y anotar incertidumbre; de otro modo reportar una descarga cualitativa, sin copiar el tiempo simulado como dato medido.

Guardar los datos numericos que permita exportar el software, junto con capturas de pantalla y ajustes. No mezclar capturas de encendidos diferentes como si fueran simultaneas. Conservar CH1=entrada como referencia cuando se comparen retardos absolutos; la captura VCTRL/Vout describe la relacion entre esas dos seÃ±ales.

## Puntos verificados en la copia de KiCad

Fuente: hardware/kicad/Regulador.kicad_pcb. Verificar visualmente la correspondencia con la placa ensamblada antes de conectar; son designadores KiCad, no LTspice.

| Senal | Punto de PCB | Red en KiCad |
|---|---|---|
| Entrada de placa | TP_VCC, pad 1; INPUT, pad 1 | VCC |
| Salida | TP_OUT, pad 1 | OUT |
| Retorno | TP_GND (hay dos footprints con ese nombre), pad 1 | GND |
| Salida Start Up | C11, pad 1; tambien C12, pad 1 | VCTRL |
| Enable logico | R20, pad 2; tambien R99, pad 2 | TTL |
| Referencia principal | TP_VREF, pad 1 | VREF |

Hallazgo importante: el punto rotulado TP_TTL esta conectado a Net-(D1-K), al otro lado de R20 respecto de la red TTL. No medirlo y etiquetar esa curva como V(TTL) sin distinguir ambos nodos. R20 pad 1 comparte la red de TP_TTL; R20 pad 2 pertenece a TTL. TP_VREF corresponde a la referencia principal, no a la referencia auxiliar UVLO/OVLO.

La primera prueba puede realizarse con TP_VCC y TP_OUT, usando TP_GND como retorno. El interruptor externo debe estar antes de INPUT para que TP_VCC observe la entrada realmente aplicada a la placa.
