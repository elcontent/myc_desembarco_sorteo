import argparse
import json
import os
import re
import unicodedata

import pandas as pd


COLUMNAS_REQUERIDAS = ["id", "nombre", "apellidos", "tipo_cuota"]
CAMPOS_BOOLEANOS = [
    "desembarco_anterior", "infraccion", "implicacion", "antiguo", "desfila",
    "cumplio_18_este_ano", "tirador",
]


def normalizar_columna(columna):
    texto = unicodedata.normalize("NFKD", str(columna).strip().lower())
    texto = texto.encode("ascii", "ignore").decode()
    texto = re.sub(r"\s+", "_", texto)
    return re.sub(r"[^a-z0-9_]", "", texto)


def es_verdadero(valor, campo):
    if pd.isna(valor) or str(valor).strip() == "":
        return False
    if isinstance(valor, bool):
        return valor
    texto = normalizar_columna(valor)
    if texto in {"si", "s", "true", "1", "x"}:
        return True
    if texto in {"no", "n", "false", "0"}:
        return False
    raise ValueError(f"Valor no reconocido en '{campo}': {valor}")


def valor_json(valor):
    if pd.isna(valor):
        return ""
    return valor.item() if hasattr(valor, "item") else valor


def excel2json(ruta_excel, nombre_hoja, fila_encabezado, ruta_salida="participantes.json"):
    if not os.path.isfile(ruta_excel):
        raise ValueError(f"No se encuentra el archivo: {ruta_excel}")

    try:
        df = pd.read_excel(ruta_excel, sheet_name=nombre_hoja, header=fila_encabezado, engine="openpyxl")
    except ValueError as error:
        raise ValueError(f"No se pudo leer la hoja '{nombre_hoja}': {error}") from error

    df.columns = [normalizar_columna(c) for c in df.columns]
    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas obligatorias: {', '.join(faltantes)}")
    if "edad" not in df.columns and "18" not in df.columns:
        raise ValueError("Debe existir la columna 'edad' o la columna '18'.")

    df = df[df["id"].notna() & (df["id"].astype(str).str.strip() != "")].copy()
    if "edad" in df.columns:
        edades = pd.to_numeric(df["edad"], errors="coerce")
        df = df[edades >= 18].copy()
        print("✅ Mayores de edad filtrados mediante la columna 'edad'.")
    else:
        mascara = df["18"].apply(lambda valor: es_verdadero(valor, "18"))
        df = df[mascara].copy()
        print("✅ Mayores de edad filtrados mediante la columna '18'.")

    participantes = []
    for _, fila in df.iterrows():
        persona = {campo: valor_json(fila[campo]) for campo in COLUMNAS_REQUERIDAS}
        for campo in CAMPOS_BOOLEANOS:
            persona[campo] = es_verdadero(fila[campo], campo) if campo in df.columns else False
        comisiones = valor_json(fila["comisiones"]) if "comisiones" in df.columns else 0
        if comisiones == "":
            comisiones = 0
        try:
            comisiones_float = float(comisiones)
        except (TypeError, ValueError):
            raise ValueError(f"Número de comisiones no válido para ID {persona['id']}.") from None
        if not comisiones_float.is_integer() or comisiones_float < 0:
            raise ValueError(f"Las comisiones deben ser un entero positivo para ID {persona['id']}.")
        persona["comisiones"] = int(comisiones_float)
        participantes.append(persona)

    if not participantes:
        raise ValueError("No se encontraron participantes mayores de edad.")
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump({"participantes": participantes}, archivo, indent=2, ensure_ascii=False, allow_nan=False)
    print(f"🎉 JSON generado en '{ruta_salida}' con {len(participantes)} participantes.")


def main():
    parser = argparse.ArgumentParser(description="Convierte el censo Excel en el JSON del sorteo")
    parser.add_argument("archivo_excel")
    parser.add_argument("nombre_hoja")
    parser.add_argument("fila_encabezado", type=int, help="Número de fila en Excel, empezando por 1")
    parser.add_argument("--salida", default="participantes.json")
    args = parser.parse_args()
    if args.fila_encabezado < 1:
        parser.error("La fila de encabezado debe ser 1 o superior.")
    try:
        excel2json(args.archivo_excel, args.nombre_hoja, args.fila_encabezado - 1, args.salida)
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
