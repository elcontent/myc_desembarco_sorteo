# 🎲 Sorteo del Desembarco - Penya El Tabik

Sorteo ponderado y transparente para asignar las plazas del Desembarco en las fiestas de Moros y Cristianos de La Vila Joiosa.

## 🏴‍☠️ Descripción

El Sorteo del Desembarco es un acto que realizamos en la Penya el Tabik cada año para repartir las plazas asignadas a la Penya para el Desembarco. 

## ⚙️ Datos técnicos y funcionamiento general

Tenemos un script desarrollado en Python que se encarga de realizar el sorteo. Este script utiliza las librerías `random` y `numpy` para seleccionar aleatoriamente a los participantes, pero aplicando ponderaciones según ciertos criterios objetivos (participación previa, implicación, tipo de cuota...).

La entrada de datos del script es un fichero JSON que contiene la lista de participantes y sus respectivas variables de ponderación. El script genera un fichero TXT con el resultado del sorteo.

Por último, el sorteo será reproducible, por lo que cuando termine la ejecución del script, nos dirá la semilla utilizada para el sorteo. De esta manera, si se quiere repetir el sorteo con los mismos participantes y ponderaciones, se podrá hacer utilizando la misma semilla y el mismo fichero de entrada.

### ⚙️ Criterios de Ponderación del Sorteo

El sorteo del desembarco **no es completamente aleatorio**. Se aplica un sistema de **ponderación basado en criterios objetivos**, con el objetivo de fomentar la participación activa, la equidad y la rotación.  
A continuación se detallan las reglas aplicadas:

#### 📐 Reglas de exclusión y penalización por defecto

| Criterio                            | Efecto sobre la probabilidad | Detalles                                                       |
|-------------------------------------|-------------------------------|----------------------------------------------------------------|
| ❌ Infracción cometida              | Exclusión total              | No participa en el sorteo.                                     |
| 📉 Participó en el desembarco anterior | -90% de peso                 | Probabilidad drásticamente reducida (*peso x 0.1*).            |
| 💸 Cuota reducida o incompleta      | -75% de peso                 | Penaliza la aportación parcial (*peso x 0.25*).                |
| 🤝 Implicación activa en la organización | +25% de peso               | Reconoce el compromiso (*peso x 1.25*).                        |

> 📎 *Nota: Las penalizaciones y bonificaciones son acumulativas y se aplican sobre un peso base de 1.0.*

---

#### 📋 Ejemplo de cálculo del peso

Una persona con:
- Cuota reducida ✅  
- Participación el año anterior ✅  
- Implicación ✅  

**Peso:** `1.0 x 0.1 x 0.25 x 1.25 = 0.03125`  
(*Muy baja probabilidad, pero no imposible.*)

Una persona con:
- Cuota completa ✅  
- No desembarcó ✅  
- Implicación ✅  

**Peso:** `1.0 x 1.25 = 1.25`  
(*Más probabilidades de ser seleccionada.*)

---

#### Ajuste de pesos

Las ponderaciones se ajustan en el principio del script `sorteo.py` mediante constantes. Puedes modificar estos valores para ajustar la influencia de cada criterio en el sorteo. Estas constantes son:

```python
# 🚨 CONSTANTES DE PENALIZACIÓN
PENALIZACION_DESEMBARCO_ANTERIOR = 0.1      # -90% si desembarcó antes
PENALIZACION_CUOTA_REDUCIDA = 0.25          # -75% si no es completa
EXCLUSION_POR_INFRACCION = True             # Si cometió infracción, fuera
BONIFICACION_IMPLICACION = 1.25             # +25% de peso si está implicado
```

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

Desarrollado por [Jordi Sellés Enríquez](https://cv.elcontent.es) – Directiva de la Penya El Tabik

