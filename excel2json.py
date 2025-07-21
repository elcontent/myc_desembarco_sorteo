import pandas as pd
import json
import sys
import os
import unicodedata
import re

COLUMNAS_REQUERIDAS = ["id", "nombre", "apellidos", "tipo_cuota", "edad", "18"]
CAMPOS_EXTRA = {
    "desembarco_anterior": False,
    "infraccion": False,
    "implicacion": False
}

def normalizar_columna(col):
    col = str(col).strip().lower()
    col = unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8')
    col = re.sub(r'\s+', '_', col)
    col = re.sub(r'[^a-z0-9_]', '', col)
    return col

def excel_minimo_a_json(ruta_excel, nombre_hoja, fila_encabezado, ruta_salida="participantes.json"):
    if not os.path.exists(ruta_excel):
        print(f"No se encuentra el archivo: {ruta_excel}")
        sys.exit(1)

    try:
        df = pd.read_excel(
            ruta_excel,
            sheet_name=nombre_hoja,
            header=fila_encabezado,
            engine='openpyxl'
        )
    except ValueError:
        print(f"No se encontró la hoja '{nombre_hoja}' en el archivo.")
        sys.exit(1)

    # Normalizar columnas
    df.columns = [normalizar_columna(c) for c in df.columns]

    # Verificar columnas mínimas
    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        print(f"El Excel no tiene las columnas necesarias: {', '.join(faltantes)}")
        sys.exit(1)

    # Nos quedamos solo con las columnas mínimas
    df = df[COLUMNAS_REQUERIDAS]
    
    # Filtramos las filas sin ID
    original_len = len(df)
    df = df[df["id"].notna()]
    df = df[df["id"].astype(str).str.strip() != ""]
    filtrados = original_len - len(df)

    if filtrados > 0:
        print(f"⚠️ Se han ignorado {filtrados} fila(s) sin ID.")
        
    # Filtro por mayoría de edad
    columnas_disponibles = df.columns.tolist()
    if "edad" in columnas_disponibles:
        df = df[df["edad"].fillna(0).astype(float) >= 18]
        print("✅ Se ha filtrado por columna 'edad' (>= 18)")
    elif "18" in columnas_disponibles:
        df = df[df["18"].fillna(0).astype(int) == 1]
        print("✅ Se ha filtrado por columna '18' (marcado como mayor de edad)")
    else:
        print("⚠️ No se encontró columna 'edad' ni '18'. No se ha aplicado filtro de mayoría de edad.")


    # Añadir los campos extra por defecto
    for campo, valor in CAMPOS_EXTRA.items():
        df[campo] = value_default = valor

    participantes = df.to_dict(orient="records")
    data = {"participantes": participantes}

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"🎉 JSON generado correctamente en: {ruta_salida}")
    print(f"📊 Participantes procesados: {len(participantes)}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python excel_minimo_a_json.py archivo.xlsx NOMBRE_HOJA FILA_ENCABEZADO")
        sys.exit(1)

    ruta_excel = sys.argv[1]
    nombre_hoja = sys.argv[2]
    try:
        fila_encabezado = int(sys.argv[3]) - 1  # Convertir a índice 0
    except ValueError:
        print("La fila de encabezado debe ser un número entero (empezando en 0).")
        sys.exit(1)

    excel_minimo_a_json(ruta_excel, nombre_hoja, fila_encabezado)
