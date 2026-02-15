# Motor-de-deteccion-de-fallas

Motor de reglas configurable para el analisis de comportamiento inusual en sistemas que procesen datos constantes.

## Incluye

- Generacion de eventos de alertas.

- Reglas configurables.

- Ventanas deslizantes de datos.

- Dashboard en locahost.

- Modelo de Machine learning con algoritmo Random Forest. 

## Uso

1. Conectar a maquina procesadora de datos.
2. Iniciar dashboard.

## Casos de uso

1. Maquinaria Industrial.
2. Sensores en tiempo real.
3. Plantas de generacion Electrica.
4. Analisis preventivo.
5. Monitoreo en general.

## Tecnologias utilizadas

Scikit-Learn: Modelo de ML con algoritmo random forest y entrenado con datos previos del comportamiento del sistema.

Pandas: Para el manejo de dataframes y lectura de datos.

StreamLit: Para deploy del dashboard en el localhost y visualizacion de estadisticas en tiempo real.

FastAPI: Comunicacion dividida del sistema para fortalecer su flexibilidad a la hora de expandirlo.

PyTest: Para el testeo de la aplicacion antes de ejecutarla.
 
