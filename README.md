# Sorteo del Desembarco (Moros y Cristianos de La Vila Joiosa)

## 🏴‍☠️ Descripción

El Sorteo del Desembarco es un acto que realizamos en la Penya el Tabik cada año para repartir las plazas asignadas a la Penya para el Desembarco. 

## ⚙️ Datos técnicos

Tenemos un script desarrollado en Python que se encarga de realizar el sorteo. Este script utiliza la librería `random` para seleccionar aleatoriamente a los participantes. Así mismo, destaca que el sorteo se realiza de manera ponderada, es decir, que cada participante tiene una probabilidad distinta en función de valores como si desembarcó el año anterior, si es un colaborador activo, etc. 

La entrada de datos del script es un fichero JSON que contiene la lista de participantes y sus respectivos variables de ponderación. El script genera un fichero TXT con el resultado del sorteo.

Por último, el sorteo será reproducible, por lo que cuando termine la ejecución del script, nos dirá la semilla utilizada para el sorteo. De esta manera, si se quiere repetir el sorteo con los mismos participantes y ponderaciones, se podrá hacer utilizando la misma semilla y el mismo fichero de entrada.

## Excel2JSON

Para facilitar la creación del fichero JSON de entrada, puedes utilizar el script `excel2json.py` que convierte un fichero Excel con la lista de participantes a formato JSON. Este script asume que el fichero Excel tiene las siguientes columnas:
- `id`: Identificador del participante.
- `nombre`: Nombre del participante.
- `apellidos`: Apellidos del participante.
- `tipo cuota`: Tipo de cuota del participante (completa o reducida).
- `edad`: Edad del participante.

Puedes ejecutar el script `excel2json.py` de la siguiente manera:

```bash
python3 excel2json.py nombre_excel.xlsx nombre_hoja
```

## 🧾 Ejecución del script _sorteo.py_

Asegúrate de tener Python instalado y las dependencias requeridas (`tabulate`, etc.).  
Puedes instalar los requisitos con:

```bash
pip install -r requirements.txt
```

## 📂 Entrada

El script `sorteo.py` espera un fichero JSON con la siguiente estructura:

```json
{
  "participantes": [
    {
      "id": 1,
      "nombre": "Nombre del participante",
      "apellidos": "Apellidos del participante",
      "desembarco_anterior": true,
      "infraccion": false,
      "tipo_cuota": "completa"
    },
    ...
  ]
}
```

## 🚀 Comandos de _sorteo.py_

El script `sorteo.py` se ejecuta desde la línea de comandos y acepta los siguientes parámetros:

### 🎯 Ejecutar sorteo

```bash
python sorteo.py participantes.json NUM_PLAZAS
```

Opcionalmente, puedes especificar una semilla para reproducibilidad:

```bash
python sorteo.py participantes.json NUM_PLAZAS --semilla 12345
```

Esto generará por pantalla una tabla con los seleccionados y excluidos (si los hay) y además guardará un fichero .txt con los resultados en el mismo directorio. En caso de no especificar la semilla, se generará una aleatoria.

### 📊 Ver probabilidades sin ejecutar el sorteo

```bash
python sorteo.py participantes.json NUM_PLAZAS --probabilidades
```

Esto mostrará en consola una tabla con el peso y la probabilidad de cada participante válido (los que no están excluidos por infracción).

### 🧪 Ejemplo real

```bash
python sorteo.py participantes_example.json 5 --semilla 33
```

Salida esperada: 

```plaintext
🎯 Seleccionados (5):
╒══════╤══════════╤═════════════╤══════════╤════════╤══════════════╤═════════════╕
│   ID │ Nombre   │ Apellidos   │ Cuota    │   Peso │ Desembarcó   │ Implicado   │
╞══════╪══════════╪═════════════╪══════════╪════════╪══════════════╪═════════════╡
│    6 │ Frank    │ Davis       │ completa │   0.75 │ Sí           │ Sí          │
├──────┼──────────┼─────────────┼──────────┼────────┼──────────────┼─────────────┤
│    8 │ Henry    │ Martinez    │ sí       │   1    │ No           │ No          │
├──────┼──────────┼─────────────┼──────────┼────────┼──────────────┼─────────────┤
│    9 │ Isabel   │ Rodriguez   │ completa │   0.75 │ Sí           │ Sí          │
├──────┼──────────┼─────────────┼──────────┼────────┼──────────────┼─────────────┤
│    3 │ Charlie  │ Williams    │ sí       │   1.5  │ No           │ Sí          │
├──────┼──────────┼─────────────┼──────────┼────────┼──────────────┼─────────────┤
│    8 │ Henry    │ Martinez    │ sí       │   1    │ No           │ No          │
╘══════╧══════════╧═════════════╧══════════╧════════╧══════════════╧═════════════╛

⛔ Excluidos por infracción (1):
╒══════╤══════════╤═════════════╤══════════╕
│   ID │ Nombre   │ Apellidos   │ Cuota    │
╞══════╪══════════╪═════════════╪══════════╡
│    5 │ Eve      │ Miller      │ reducida │
╘══════╧══════════╧═════════════╧══════════╛

📁 Resultados exportados a 'sorteo_resultado_20250721_032338.txt'
```

En el caso de querer ver las probabilidades sin ejecutar el sorteo, la salida sería:

```plaintext
📊 Listado de Probabilidades:
==================================================
╒══════╤══════════╤═════════════╤════════╤════════════════╕
│   ID │ Nombre   │ Apellidos   │   Peso │ Probabilidad   │
╞══════╪══════════╪═════════════╪════════╪════════════════╡
│    1 │ Alice    │ Johnson     │   1.5  │ 20.13%         │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│    3 │ Charlie  │ Williams    │   1.5  │ 20.13%         │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│    8 │ Henry    │ Martinez    │   1    │ 13.42%         │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│   10 │ Jack     │ Lee         │   1    │ 13.42%         │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│    6 │ Frank    │ Davis       │   0.75 │ 10.07%         │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│    9 │ Isabel   │ Rodriguez   │   0.75 │ 10.07%         │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│    4 │ Diana    │ Brown       │   0.5  │ 6.71%          │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│    7 │ Grace    │ Garcia      │   0.3  │ 4.03%          │
├──────┼──────────┼─────────────┼────────┼────────────────┤
│    2 │ Bob      │ Smith       │   0.15 │ 2.01%          │
╘══════╧══════════╧═════════════╧════════╧════════════════╛
==================================================
```


## 👤 Autor

El script ha sido desarrollado por **Jordi Sellés Enríquez** como parte de la Directiva de la Penya el Tabik.
