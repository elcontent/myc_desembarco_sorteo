# 🎲 Sorteo del Desembarco — Penya El Tabik

Herramienta reproducible y auditable para asignar las plazas del Desembarco de las fiestas de Moros y Cristianos de La Vila Joiosa.

## Baremo 2026

El sistema combina **prioridad económica**, **implicación personal** y **rotación**.

### 1. Prioridad por cuota

El sorteo se divide en dos bloques independientes:

1. Personas con cuota completa (`completa`, `sí` o `nuevo sí`).
2. Personas con cuota reducida (`reducida`, `no`, `media` o `incompleta`).

Primero se adjudican plazas al bloque de cuota completa. El segundo bloque solo obtiene plaza cuando quedan vacantes después de ordenar a todas las personas del primero. Dentro de cada bloque se realiza un sorteo ponderado sin reemplazo.

Esto evita que una cuota reducida muy bonificada adelante a una cuota completa, pero conserva un orden justo de suplentes en ambos grupos.

### 2. Ponderación dentro de cada bloque

Todas las personas parten de un peso `1,00`:

| Criterio | Factor | Motivo |
|---|---:|---|
| Desembarcó el año anterior | `× 0,55` | Favorece la rotación |
| Implicación personal activa | `× 1,30` | Premia el trabajo actual en la Penya |
| Antigüedad | `× 1,20` | Reconoce la trayectoria sin hacerla decisiva |
| Desfila este año | `× 1,25` | Premia el compromiso directo con los actos de la Penya |
| Ha cumplido 18 este año | `× 1,15` | Facilita la incorporación de nuevos adultos al Desembarco |
| Es tirador/a | `× 1,15` | Reconoce una función activa y específica durante el Desembarco |
| Cada comisión | `× (1 + 0,15 × comisiones)` | Premia trabajo concreto y verificable |

La bonificación de comisiones tiene un máximo de cuatro comisiones: el factor máximo es `× 1,60`. Se evita así que acumular cargos nominales produzca una ventaja desproporcionada.

Ejemplo: una persona implicada, antigua, que desfila, presente en tres comisiones y que no desembarcó el año anterior tendrá:

```text
1,00 × 1,30 × 1,20 × 1,25 × 1,45 = 2,8275
```

Si desembarcó el año anterior:

```text
1,00 × 0,55 × 1,30 × 1,20 × 1,25 × 1,45 = 1,5551
```

Si además ha cumplido 18 años durante el año del sorteo, el peso se multiplica por `1,15`. Esta bonificación se aplica una sola vez y únicamente ese año. El campo debe reflejar que ya los ha cumplido, no que los cumplirá más adelante.

Las personas que participen como tiradoras reciben otro factor `× 1,15`. Este extra es acumulable con desfilar, cumplir 18 y los demás criterios, pero no altera la prioridad por tipo de cuota.

Las infracciones siguen suponiendo exclusión total.

## Datos de entrada

```json
{
  "participantes": [
    {
      "id": 1,
      "nombre": "Nombre",
      "apellidos": "Apellidos",
      "tipo_cuota": "completa",
      "desembarco_anterior": false,
      "infraccion": false,
      "implicacion": true,
      "antiguo": false,
      "desfila": true,
      "cumplio_18_este_ano": true,
      "tirador": true,
      "comisiones": 2
    }
  ]
}
```

El programa rechaza IDs duplicados, campos obligatorios vacíos, cuotas desconocidas, booleanos ambiguos y cantidades de comisiones negativas o decimales.

## Instalación

Requiere Python 3.10 o superior.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Conversión desde Excel

Columnas obligatorias:

- `id`
- `nombre`
- `apellidos`
- `tipo cuota`
- Una de estas dos: `edad` o `18`

Columnas opcionales: `desembarco anterior`, `infraccion`, `implicacion`, `antiguo`, `desfila`, `cumplio 18 este ano`, `tirador` y `comisiones`. Los campos opcionales ausentes toman `false` o `0`.

`cumplio 18 este ano` es un dato explícito para evitar errores con una edad calculada en una fecha concreta: debe marcarse `Sí` solo cuando la persona ya haya cumplido los 18 durante el año del sorteo.

```bash
python3 excel2json.py censo.xlsx NOMBRE_HOJA FILA_ENCABEZADO
```

Por ejemplo, si los títulos están en la fila 7:

```bash
python3 excel2json.py censo.xlsx Censo 7
```

Puede elegirse otro fichero de salida:

```bash
python3 excel2json.py censo.xlsx Censo 7 --salida participantes_2026.json
```

## Ejecutar el sorteo

```bash
python3 sorteo.py participantes.json NUM_PLAZAS
```

Con una semilla concreta:

```bash
python3 sorteo.py participantes.json 5 --semilla 20260728
```

Si no se indica semilla, se genera una aleatoria de 64 bits y se muestra al terminar. Usando el mismo JSON y la misma semilla se obtiene el mismo orden.

### Probabilidad real de obtener plaza

```bash
python3 sorteo.py participantes.json 5 --probabilidades
```

Se simulan 20.000 sorteos deterministas para estimar la probabilidad de conseguir **alguna de las plazas**, respetando la prioridad por cuota y el sorteo sin reemplazo. Ya no se presenta la probabilidad de la primera extracción como si fuera la probabilidad final.

El número de simulaciones puede modificarse:

```bash
python3 sorteo.py participantes.json 5 --probabilidades --simulaciones 50000
```

## Auditoría

Cada ejecución genera:

- Un informe legible `.txt`.
- Un registro estructurado `.json` con seleccionados, suplentes, excluidos y desglose de pesos.
- La semilla empleada.
- La versión del programa.
- La configuración exacta del baremo.
- La huella SHA-256 del fichero de entrada.
- Fecha y zona horaria de ejecución.

La huella permite demostrar que el fichero utilizado para repetir el sorteo es exactamente el mismo.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```

Las pruebas comprueban la prioridad de la cuota completa, la reproducibilidad, los límites de las comisiones, las bonificaciones por desfilar, cumplir 18 y ser tirador, la relación entre implicación y antigüedad y varias validaciones de entrada.

## Autor

Desarrollado por [Jordi Sellés Enríquez](https://cv.elcontent.es) para la Penya El Tabik.
