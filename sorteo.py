import argparse
import hashlib
import json
import math
import os
import random
import secrets
import sys
import unicodedata
from datetime import datetime

try:
    from tabulate import tabulate
except ImportError:  # Permite validar y ejecutar el núcleo sin el formato enriquecido.
    def tabulate(filas, headers=(), tablefmt=None):
        contenido = [headers, *filas] if headers else list(filas)
        return "\n".join("\t".join(str(valor) for valor in fila) for fila in contenido)


VERSION = "2.0.0"

# Baremo 2026. La cuota completa determina el bloque de prioridad; estos
# multiplicadores ordenan de forma ponderada a las personas dentro de su bloque.
PENALIZACION_DESEMBARCO_ANTERIOR = 0.55
BONIFICACION_IMPLICACION = 1.30
BONIFICACION_ANTIGUEDAD = 1.20
BONIFICACION_POR_COMISION = 0.15
MAX_COMISIONES_BONIFICADAS = 4
SIMULACIONES_PROBABILIDAD = 20_000

CUOTAS_COMPLETAS = {"completa", "si", "nueva si", "nuevo si"}
CUOTAS_REDUCIDAS = {"reducida", "incompleta", "no", "media"}


def normalizar_texto(valor):
    texto = str(valor).strip().lower()
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def normalizar_booleano(valor, campo):
    if isinstance(valor, bool):
        return valor
    if valor is None or valor == "":
        return False
    if isinstance(valor, (int, float)) and valor in (0, 1):
        return bool(valor)
    texto = normalizar_texto(valor)
    if texto in {"si", "s", "true", "1", "x"}:
        return True
    if texto in {"no", "n", "false", "0"}:
        return False
    raise ValueError(f"El campo '{campo}' debe contener Sí/No o true/false.")


def normalizar_cuota(valor):
    cuota = normalizar_texto(valor)
    if cuota in CUOTAS_COMPLETAS:
        return "completa"
    if cuota in CUOTAS_REDUCIDAS:
        return "reducida"
    raise ValueError(
        f"Tipo de cuota desconocido: '{valor}'. Usa completa/sí/nuevo sí o reducida/no."
    )


def validar_participantes(datos):
    if not isinstance(datos, dict) or not isinstance(datos.get("participantes"), list):
        raise ValueError("El JSON debe contener una lista llamada 'participantes'.")
    if not datos["participantes"]:
        raise ValueError("La lista de participantes está vacía.")

    ids = set()
    participantes = []
    for posicion, original in enumerate(datos["participantes"], start=1):
        if not isinstance(original, dict):
            raise ValueError(f"El participante {posicion} no es un objeto válido.")

        persona = dict(original)
        identificador = persona.get("id")
        if identificador is None or str(identificador).strip() == "":
            raise ValueError(f"Falta el ID del participante {posicion}.")
        clave_id = str(identificador).strip()
        if clave_id in ids:
            raise ValueError(f"El ID '{clave_id}' está duplicado.")
        ids.add(clave_id)

        for campo in ("nombre", "apellidos"):
            if not str(persona.get(campo, "")).strip():
                raise ValueError(f"Falta '{campo}' en el participante con ID {clave_id}.")
            persona[campo] = str(persona[campo]).strip()

        persona["id"] = identificador
        persona["tipo_cuota"] = normalizar_cuota(persona.get("tipo_cuota", ""))
        for campo in ("desembarco_anterior", "infraccion", "implicacion", "antiguo"):
            persona[campo] = normalizar_booleano(persona.get(campo, False), campo)

        comisiones = persona.get("comisiones", 0)
        try:
            comisiones_num = int(comisiones)
        except (TypeError, ValueError):
            raise ValueError(
                f"'comisiones' debe ser un entero para el participante con ID {clave_id}."
            ) from None
        if isinstance(comisiones, float) and not comisiones.is_integer():
            raise ValueError(f"'comisiones' no puede tener decimales para el ID {clave_id}.")
        if comisiones_num < 0:
            raise ValueError(f"'comisiones' no puede ser negativo para el ID {clave_id}.")
        persona["comisiones"] = comisiones_num
        participantes.append(persona)

    return participantes


def calcular_desglose(persona):
    if persona["infraccion"]:
        return {"peso": 0.0, "factores": ["Exclusión por infracción"]}

    peso = 1.0
    factores = ["Base 1,00"]
    if persona["desembarco_anterior"]:
        peso *= PENALIZACION_DESEMBARCO_ANTERIOR
        factores.append(f"Rotación ×{PENALIZACION_DESEMBARCO_ANTERIOR:.2f}")
    if persona["implicacion"]:
        peso *= BONIFICACION_IMPLICACION
        factores.append(f"Implicación ×{BONIFICACION_IMPLICACION:.2f}")
    if persona["antiguo"]:
        peso *= BONIFICACION_ANTIGUEDAD
        factores.append(f"Antigüedad ×{BONIFICACION_ANTIGUEDAD:.2f}")

    comisiones_bonificadas = min(persona["comisiones"], MAX_COMISIONES_BONIFICADAS)
    factor_comisiones = 1 + BONIFICACION_POR_COMISION * comisiones_bonificadas
    if comisiones_bonificadas:
        peso *= factor_comisiones
        factores.append(
            f"{persona['comisiones']} comisión(es) ×{factor_comisiones:.2f}"
            + (" (tope aplicado)" if persona["comisiones"] > MAX_COMISIONES_BONIFICADAS else "")
        )
    return {"peso": round(peso, 8), "factores": factores}


def preparar_participantes(personas):
    preparados = []
    excluidos = []
    for persona in personas:
        desglose = calcular_desglose(persona)
        preparada = {**persona, **desglose}
        (excluidos if persona["infraccion"] else preparados).append(preparada)
    return preparados, excluidos


def orden_ponderado(personas, rng):
    # Carrera exponencial: produce un orden ponderado sin reemplazo y permite
    # conservar una lista completa de suplentes.
    claves = []
    for persona in personas:
        u = max(rng.random(), sys.float_info.min)
        clave = -math.log(u) / persona["peso"]
        claves.append((clave, str(persona["id"]), persona))
    return [persona for _, _, persona in sorted(claves, key=lambda x: (x[0], x[1]))]


def sorteo_plazas(personas, semilla):
    preparados, excluidos = preparar_participantes(personas)
    if not preparados:
        raise ValueError("Todas las personas han sido excluidas.")

    rng = random.Random(semilla)
    completas = [p for p in preparados if p["tipo_cuota"] == "completa"]
    reducidas = [p for p in preparados if p["tipo_cuota"] == "reducida"]
    ordenados = orden_ponderado(completas, rng) + orden_ponderado(reducidas, rng)
    return ordenados, excluidos


def estimar_probabilidades(personas, num_plazas, simulaciones=SIMULACIONES_PROBABILIDAD):
    preparados, _ = preparar_participantes(personas)
    conteos = {str(p["id"]): 0 for p in preparados}
    for semilla in range(simulaciones):
        rng = random.Random(semilla)
        completas = [p for p in preparados if p["tipo_cuota"] == "completa"]
        reducidas = [p for p in preparados if p["tipo_cuota"] == "reducida"]
        orden = orden_ponderado(completas, rng) + orden_ponderado(reducidas, rng)
        for persona in orden[:num_plazas]:
            conteos[str(persona["id"])] += 1
    return {clave: 100 * valor / simulaciones for clave, valor in conteos.items()}


def filas_participantes(participantes, probabilidades=None):
    filas = []
    for p in participantes:
        fila = [
            p["id"], p["nombre"], p["apellidos"], p["tipo_cuota"],
            p["comisiones"], f"{p['peso']:.3f}",
            "Sí" if p["desembarco_anterior"] else "No",
            "Sí" if p["implicacion"] else "No",
            "Sí" if p["antiguo"] else "No",
        ]
        if probabilidades is not None:
            fila.append(f"{probabilidades[str(p['id'])]:.2f}%")
        filas.append(fila)
    return filas


def mostrar_probabilidades(personas, num_plazas, simulaciones):
    preparados, excluidos = preparar_participantes(personas)
    probabilidades = estimar_probabilidades(personas, num_plazas, simulaciones)
    headers = ["ID", "Nombre", "Apellidos", "Cuota", "Comisiones", "Peso", "Salió antes", "Implicado", "Antiguo", "Prob. plaza"]
    print(f"\n📊 Probabilidad estimada de obtener una de las {num_plazas} plazas")
    print(f"Simulación determinista de {simulaciones:,} sorteos. La cuota completa tiene prioridad.")
    print(tabulate(filas_participantes(preparados, probabilidades), headers=headers, tablefmt="fancy_grid"))
    if excluidos:
        print(f"\n⛔ Personas excluidas: {len(excluidos)}")


def hash_archivo(ruta):
    digest = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(65536), b""):
            digest.update(bloque)
    return digest.hexdigest()


def configuracion_baremo():
    return {
        "prioridad": ["cuota completa", "cuota reducida"],
        "penalizacion_desembarco_anterior": PENALIZACION_DESEMBARCO_ANTERIOR,
        "bonificacion_implicacion": BONIFICACION_IMPLICACION,
        "bonificacion_antiguedad": BONIFICACION_ANTIGUEDAD,
        "bonificacion_por_comision": BONIFICACION_POR_COMISION,
        "max_comisiones_bonificadas": MAX_COMISIONES_BONIFICADAS,
    }


def exportar_resultados(base_salida, metadatos, seleccionados, suplentes, excluidos):
    auditoria = {
        "metadatos": metadatos,
        "baremo": configuracion_baremo(),
        "seleccionados": seleccionados,
        "suplentes": suplentes,
        "excluidos": excluidos,
    }
    with open(base_salida + ".json", "w", encoding="utf-8") as archivo:
        json.dump(auditoria, archivo, indent=2, ensure_ascii=False, allow_nan=False)

    with open(base_salida + ".txt", "w", encoding="utf-8") as archivo:
        archivo.write("SORTEO DEL DESEMBARCO\n" + "=" * 100 + "\n")
        for clave, valor in metadatos.items():
            archivo.write(f"{clave}: {valor}\n")
        archivo.write("Baremo: cuota completa primero; ponderación dentro de cada bloque.\n\n")
        headers = ["ID", "Nombre", "Apellidos", "Cuota", "Comisiones", "Peso", "Salió antes", "Implicado", "Antiguo"]
        for titulo, grupo in (("SELECCIONADOS", seleccionados), ("SUPLENTES", suplentes)):
            archivo.write(f"{titulo}\n")
            archivo.write(tabulate(filas_participantes(grupo), headers=headers, tablefmt="grid") if grupo else "Ninguno")
            archivo.write("\n\n")
        archivo.write("EXCLUIDOS\n")
        if excluidos:
            archivo.write(tabulate([[p["id"], p["nombre"], p["apellidos"]] for p in excluidos], headers=["ID", "Nombre", "Apellidos"], tablefmt="grid"))
        else:
            archivo.write("Ninguno")


def main():
    parser = argparse.ArgumentParser(description="Sorteo ponderado del Desembarco de la Penya El Tabik")
    parser.add_argument("archivo_json", help="JSON de participantes")
    parser.add_argument("num_plazas", type=int, help="Número de plazas")
    parser.add_argument("--semilla", type=int, help="Semilla reproducible")
    parser.add_argument("--probabilidades", action="store_true", help="Estimar la probabilidad real de conseguir plaza")
    parser.add_argument("--simulaciones", type=int, default=SIMULACIONES_PROBABILIDAD, help="Simulaciones para --probabilidades")
    args = parser.parse_args()

    try:
        if args.num_plazas <= 0:
            raise ValueError("El número de plazas debe ser mayor que cero.")
        if args.simulaciones <= 0:
            raise ValueError("El número de simulaciones debe ser mayor que cero.")
        if not os.path.isfile(args.archivo_json):
            raise ValueError(f"No se encuentra el archivo '{args.archivo_json}'.")
        with open(args.archivo_json, "r", encoding="utf-8") as archivo:
            personas = validar_participantes(json.load(archivo))

        validos = sum(not p["infraccion"] for p in personas)
        if args.num_plazas > validos:
            print(f"⚠️ Hay {args.num_plazas} plazas y solo {validos} participantes válidos; se seleccionarán todos.")

        if args.probabilidades:
            mostrar_probabilidades(personas, args.num_plazas, args.simulaciones)
            return

        semilla = args.semilla if args.semilla is not None else secrets.randbits(64)
        ordenados, excluidos = sorteo_plazas(personas, semilla)
        seleccionados = ordenados[:args.num_plazas]
        suplentes = ordenados[args.num_plazas:]

        headers = ["ID", "Nombre", "Apellidos", "Cuota", "Comisiones", "Peso", "Salió antes", "Implicado", "Antiguo"]
        print(f"\n🎯 Seleccionados ({len(seleccionados)}):")
        print(tabulate(filas_participantes(seleccionados), headers=headers, tablefmt="fancy_grid"))
        print(f"\n🪑 Suplentes ({len(suplentes)}):")
        print(tabulate(filas_participantes(suplentes), headers=headers, tablefmt="fancy_grid") if suplentes else "Ninguno.")
        print(f"\n⛔ Excluidos ({len(excluidos)}):")
        print(", ".join(f"{p['nombre']} {p['apellidos']}" for p in excluidos) if excluidos else "Ninguno.")

        marca = datetime.now().astimezone()
        base_salida = f"sorteo_resultado_{marca.strftime('%Y%m%d_%H%M%S')}"
        metadatos = {
            "version": VERSION,
            "fecha": marca.isoformat(),
            "semilla": semilla,
            "plazas": args.num_plazas,
            "sha256_entrada": hash_archivo(args.archivo_json),
        }
        exportar_resultados(base_salida, metadatos, seleccionados, suplentes, excluidos)
        print(f"\n🔐 Semilla: {semilla}")
        print(f"📁 Auditoría exportada a '{base_salida}.txt' y '{base_salida}.json'")
    except (ValueError, json.JSONDecodeError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
