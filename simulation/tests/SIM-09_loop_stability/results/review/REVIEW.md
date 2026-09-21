# SIM-09: revision tecnica, 2026-09-20

## Conclusion y alcance

Los resultados nominales se reproducen: 5 V, 557.712 kHz, 52.508 grados,
17.278 dB; 3.3 V, 530.473 kHz, 51.979 grados, 17.752 dB.
Son margenes del lazo de regulacion sondeado, a ~1 A, 27 C, COUT=1 uF y
ESR=1 ohm. No constituyen una demostracion de estabilidad de todos los
lazos internos, del doblador conmutado ni de todo el rango de cargas.
La revision personal de Marco y la verificacion fisica siguen pendientes.

## Polarizacion y topologia

La polarizacion DC se conserva; AC linealiza alrededor del punto de trabajo.
Las fuentes auxiliares ideales fijan tambien sus impedancias incrementales.
Esto excluye acoplamientos de alimentacion/referencia, no solo el offset DC.
Las fuentes proceden de medias 70--80 ms del circuito completo SIM-08.
Los dos ensayos de inyeccion tienen identicos valores OP guardados, en todos
los nodos y corrientes disponibles. La salida del arranque aislado y el OP
AC difieren menos de 0.24 uV. El log AC muestra que LTspice recalcula el OP
mediante pseudo-transitorio: .loadbias es una ayuda de inicializacion, no
una imposicion inmutable del estado instantaneo guardado.

La sonda esta entre FB y N033. El capacitor OUT--FB permanece del lado del
divisor; la compensacion local del VAS permanece cerrada. No hay un unico
corte que demuestre por si solo estabilidad de todos esos lazos locales.
El camino de limite se conserva, pero no esta limitando: su entrada de
sensado es ~1.00 V frente a ~1.485 V de umbral; D4 esta polarizado en inversa.
El modelo incluye corriente de fuga inversa (~31.7 uA), no una apertura ideal.

## Evidencia revisada y controles nuevos

- SHA256 de archivos nominales y tonos coincidentes con archivos activos.
- Margenes nominales recalculados desde las dos inyecciones RAW.
- Caso analitico T=100/(1+s*0.001): error relativo maximo ~5.01e-14.
- Ocho corridas nuevas completas: barrido de 2000 puntos/decada y sonda
  invertida, dos inyecciones por modo. Los originales no se modificaron.
- Barrido denso: cambio maximo de cruce 3.009 Hz, margen de fase <0.00007
  grados, margen de ganancia <0.000161 dB. Mismo OP que el original.
- Sonda invertida: diferencia relativa de T <1.77e-8 en el barrido;
  diferencia de salida OP <0.104 uV. No altera las cifras del informe.
- Una interseccion con 0 dB y una con -180 grados en ambos modos.
- Se reviso visualmente la figura existente; se conserva sin cambios.

preparation.json identifica variantes y hashes fuente; numerical_checks.json
registra resultados y hashes de CIR/LOG/RAW/OP archivados en esta carpeta.
archive_audit.json registra OP, caso analitico y ajustes de tonos.
Para repetir variantes, ejecutar los ocho SIM-09_review_*.cir desde
simulation/ltspice (usan las mismas bibliotecas y archivos .bias nominales).
La extraccion emplea loop() y margins() de analyze_loop.py con cada prefijo
SIM-09_review_dense_<modo> y SIM-09_review_reverse_<modo>.

## Comparacion con circuito completo

Los tonos de 500 uV se comparan con la misma relacion de retorno por tension
del banco AC. No se comparan directamente con la doble inyeccion de Tian.
Con los ultimos 80 ciclos se reproducen los limites publicados: 0.06 dB y
1.2 grados. Al ajustar 20/40/60/80 ciclos, las diferencias observadas estan
entre -0.06549 y -0.02251 dB, y entre 0.83385 y 1.34457 grados.
Por tanto, 0.06 dB/1.2 grados identifica el ajuste concreto de 80 ciclos;
no es una cota independiente de la ventana ni una incertidumbre estadistica.
El residuo incluye senales no explicadas por el tono y no debe ocultarse.
Faltan barrido de amplitud y comparacion de tonos en mas frecuencias para
extender esta comprobacion. No se ejecutaron nuevos tonos en esta revision.

## Siguiente comprobacion relevante

Antes de ampliar la conclusion, estudiar cargas bajas (0.1 A y casi vacio)
y sensibilidad a COUT/ESR. Mantener cada variante identificada y comprobar
su OP; no reutilizar sin verificar las polarizaciones de 1 A. Para el banco,
confirmar capacitor real y ESR, y comenzar por respuesta transitoria. El
ESP32 se definira al implementar, sin introducir ahora otro circuito.

## Fuentes consultadas

Tian et al., 2001, ecuacion 30 y limitaciones de lazo unico/multiples lazos:
https://kenkundert.com/docs/cd2001-01.pdf
Implementacion de doble inyeccion, simetria y limitaciones AC:
https://sites.google.com/site/frankwiedmann/loopgain
