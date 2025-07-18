# Sorteo del Desembarco (Moros y Cristianos de La Vila Joiosa)

## 🏴‍☠️ Descripción

El Sorteo del Desembarco es un acto que realizamos en la Penya el Tabik cada año para repartir las plazas asignadas a la Penya para el Desembarco. 

## ⚙️ Datos técnicos

Tenemos un script desarrollado en Python que se encarga de realizar el sorteo. Este script utiliza la librería `random` para seleccionar aleatoriamente a los participantes. Así mismo, destaca que el sorteo se realiza de manera ponderada, es decir, que cada participante tiene una probabilidad distinta en función de valores como si desembarcó el año anterior, si es un colaborador activo, etc. 

La entrada de datos del script es un fichero JSON que contiene la lista de participantes y sus respectivos variables de ponderación. El script genera un fichero TXT con el resultado del sorteo.

Por último, el sorteo será reproducible, por lo que cuando termine la ejecución del script, nos dirá la semilla utilizada para el sorteo. De esta manera, si se quiere repetir el sorteo con los mismos participantes y ponderaciones, se podrá hacer utilizando la misma semilla y el mismo fichero de entrada.

## ▶️ Ejecución

Para ejecutar el script, asegúrate de tener Python instalado en tu sistema. Luego, sigue estos pasos:

1. Clona el repositorio o descarga el script `sorteo.py`.
2. Prepara un fichero JSON con la lista de participantes y sus ponderaciones. Un ejemplo de este fichero podría ser:
    ```json
    {
      "participantes": [
        {
            "id": 1,
            "nombre": "Ana",
            "apellidos": "Pérez",
            "desembarco_anterior": true,
            "infraccion": false,
            "tipo_cuota": "completa"
        },
        {
            "id": 2,
            "nombre": "Luis",
            "apellidos": "Gómez",
            "desembarco_anterior": false,
            "infraccion": true,
            "tipo_cuota": "reducida"
        }
      ]
    }
    ```
3. Ejecuta el script desde la línea de comandos:
    ```bash
    python3 sorteo.py participantes.json NUM_PLAZAS [SEMILLA]
    ```
4. El resultado del sorteo se guardará en un fichero `sorteo_resultado_20250718_130242.txt` en el mismo directorio donde se ejecutó el script.
5. Revisa el fichero `sorteo_resultado_20250718_130242.txt` para ver los participantes seleccionados y la semilla utilizada.

## 👤 Autor

El script ha sido desarrollado por **Jordi Sellés Enríquez** como parte de la Directiva de la Penya el Tabik.
