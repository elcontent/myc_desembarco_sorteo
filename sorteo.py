import random, json, sys, os, argparse
from datetime import datetime
from tabulate import tabulate
from numpy.random import choice as np_choice
import numpy as np

# 🚨 CONSTANTES DE PENALIZACIÓN
PENALIZACION_DESEMBARCO_ANTERIOR = 0.1      # -90% si desembarcó antes
PENALIZACION_CUOTA_REDUCIDA = 0.25          # -75% si no es completa
EXCLUSION_POR_INFRACCION = True             # Si cometió infracción, fuera
BONIFICACION_IMPLICACION = 1.25             # +25% de peso si está implicado

def calcular_peso(persona):
    if EXCLUSION_POR_INFRACCION and persona.get("infraccion", False):
        return 0.0
    peso = 1.0
    if persona.get("desembarco_anterior", False):
        peso *= PENALIZACION_DESEMBARCO_ANTERIOR
    cuota = persona.get("tipo_cuota", "").strip().lower()
    cuota_normalizada = cuota.replace("í", "i")
    if cuota_normalizada not in ("completa", "si"):
      peso *= PENALIZACION_CUOTA_REDUCIDA
    if persona.get("implicacion", False):
        peso *= BONIFICACION_IMPLICACION
    return max(peso, 0.01)

def sorteo_plazas(personas, semilla=42):
    random.seed(semilla)
    np.random.seed(semilla)

    personas_filtradas = [p for p in personas if not (EXCLUSION_POR_INFRACCION and p.get("infraccion", False))]
    if not personas_filtradas:
        raise ValueError("Todos fueron excluidos.")

    personas_con_pesos = [
        {**p, "peso": calcular_peso(p)}
        for p in personas_filtradas
    ]

    total_peso = sum(p["peso"] for p in personas_con_pesos)
    if total_peso == 0:
        raise ValueError("Todos los pesos se anularon.")

    pesos_normalizados = np.array([p["peso"] for p in personas_con_pesos])
    pesos_normalizados = pesos_normalizados / pesos_normalizados.sum()

    indices = np_choice(
        len(personas_con_pesos),
        size=len(personas_con_pesos),
        replace=False,
        p=pesos_normalizados
    )
    ordenados = [personas_con_pesos[i] for i in indices]

    return ordenados, personas_filtradas

def exportar_resultados_txt(nombre_archivo, semilla, max_plazas, seleccionados, excluidos, suplentes):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(f"SORTEO DESEMBARCO - {ahora}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Semilla usada: {semilla}\n")
        f.write(f"Número de plazas disponibles: {max_plazas}\n")
        f.write(f"Total seleccionados: {len(seleccionados)}\n")
        f.write(f"Total suplentes: {len(suplentes)}\n")
        f.write(f"Total excluidos: {len(excluidos)}\n")
        f.write("=" * 80 + "\n\n")

        def tabla_participantes(participantes):
            tabla = []
            for p in participantes:
                observaciones = []
                if p.get("desembarco_anterior", False):
                    observaciones.append("Penalizado por participación anterior")
                cuota = p.get("tipo_cuota", "").strip().lower().replace("í", "i")
                if cuota not in ("completa", "si"):
                    observaciones.append("Penalizado por cuota reducida")
                if p.get("implicacion", False):
                    observaciones.append("Bonificado por implicación")
                tabla.append([
                    p["id"],
                    p["nombre"],
                    p["apellidos"],
                    p.get("tipo_cuota", ""),
                    f"{p.get('peso', 1):.2f}",
                    "Sí" if p.get("desembarco_anterior") else "No",
                    "Sí" if p.get("implicacion") else "No",
                    "; ".join(observaciones) if observaciones else "Sin penalizaciones"
                ])
            return tabulate(tabla, headers=["ID", "Nombre", "Apellidos", "Cuota", "Peso", "Desembarcó", "Implicado", "Observaciones"], tablefmt="grid")

        f.write("🎯 SELECCIONADOS:\n")
        f.write(tabla_participantes(seleccionados))
        f.write("\n\n")

        f.write("🪑 SUPLENTES:\n")
        f.write(tabla_participantes(suplentes))
        f.write("\n\n")

        f.write("⛔ EXCLUIDOS POR INFRACCIÓN:\n")
        if excluidos:
            tabla_exc = [
                [p["id"], p["nombre"], p["apellidos"], p.get("tipo_cuota", "")]
                for p in excluidos
            ]
            f.write(tabulate(tabla_exc, headers=["ID", "Nombre", "Apellidos", "Cuota"], tablefmt="grid"))
        else:
            f.write("Ninguno.\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Fin del informe.\n")

def mostrar_probabilidades(personas):
    personas_validas = [p for p in personas if not (EXCLUSION_POR_INFRACCION and p.get("infraccion", False))]
    if not personas_validas:
        print("🚫 No hay participantes válidos para calcular probabilidades.")
        return

    personas_con_pesos = [
        {
            **p,
            "peso": calcular_peso(p)
        }
        for p in personas_validas
    ]

    total_peso = sum(p["peso"] for p in personas_con_pesos)
    if total_peso == 0:
        print("🚫 Todos los pesos son 0. Nadie puede participar.")
        return

    print("\n📊 Listado de Probabilidades:")
    print("=" * 50)
    tabla = []
    for p in sorted(personas_con_pesos, key=lambda x: x["peso"], reverse=True):
        prob = (p["peso"] / total_peso) * 100
        tabla.append([
            int(p["id"]),
            p["nombre"],
            p["apellidos"],
            f"{p['peso']:.2f}",
            f"{prob:.2f}%"
        ])

    headers = ["ID", "Nombre", "Apellidos", "Peso", "Probabilidad"]
    print(tabulate(tabla, headers=headers, tablefmt="fancy_grid"))
    print("=" * 50 + "\n")
    
def main():
    parser = argparse.ArgumentParser(
        description="Sorteo ponderado de plazas para el Desembarco de Moros y Cristianos de La Vila Joiosa"
    )

    parser.add_argument("archivo_json", help="Ruta al archivo JSON de participantes")
    parser.add_argument("num_plazas", type=int, help="Número máximo de plazas disponibles")
    parser.add_argument("--semilla", type=int, help="Semilla para reproducibilidad del sorteo")
    parser.add_argument("--probabilidades", action="store_true", help="Mostrar listado de probabilidades sin realizar sorteo")

    args = parser.parse_args()

    if not os.path.exists(args.archivo_json):
        print(f"No encuentro el archivo '{args.archivo_json}'.")
        sys.exit(1)

    with open(args.archivo_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        personas = data.get("participantes", [])

    if args.probabilidades:
        mostrar_probabilidades(personas)
        sys.exit(0)

    semilla = args.semilla if args.semilla is not None else datetime.now().microsecond
    if args.semilla is None:
        print(f"🔁 No se especificó semilla, usando semilla aleatoria: {semilla}")

    ordenados, participantes_validos = sorteo_plazas(personas, semilla)
    seleccionados = ordenados[:args.num_plazas]
    suplentes = ordenados[args.num_plazas:]
    excluidos = [p for p in personas if p.get("infraccion", False)]

    print(f"\n🎯 Seleccionados ({len(seleccionados)}):")
    tabla_sel = [
        [
            int(s["id"]),
            s["nombre"],
            s["apellidos"],
            s.get("tipo_cuota", ""),
            f"{s.get('peso', 1):.2f}",
            "Sí" if s.get("desembarco_anterior") else "No",
            "Sí" if s.get("implicacion") else "No"
        ]
        for s in seleccionados
    ]
    headers_sel = ["ID", "Nombre", "Apellidos", "Cuota", "Peso", "Desembarcó", "Implicado"]
    print(tabulate(tabla_sel, headers=headers_sel, tablefmt="fancy_grid"))

    print(f"\n🪑 Suplentes ({len(suplentes)}):")
    if suplentes:
        tabla_sup = [
            [
                int(s["id"]),
                s["nombre"],
                s["apellidos"],
                s.get("tipo_cuota", ""),
                f"{s.get('peso', 1):.2f}",
                "Sí" if s.get("desembarco_anterior") else "No",
                "Sí" if s.get("implicacion") else "No"
            ]
            for s in suplentes
        ]
        print(tabulate(tabla_sup, headers=headers_sel, tablefmt="fancy_grid"))
    else:
        print("Ninguno.")

    print(f"\n⛔ Excluidos por infracción ({len(excluidos)}):")
    if excluidos:
        tabla_exc = [
            [int(e["id"]), e["nombre"], e["apellidos"], e.get("tipo_cuota", "")]
            for e in excluidos
        ]
        headers_exc = ["ID", "Nombre", "Apellidos", "Cuota"]
        print(tabulate(tabla_exc, headers=headers_exc, tablefmt="fancy_grid"))
    else:
        print("Ninguno.")

    nombre_salida = f"sorteo_resultado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    exportar_resultados_txt(nombre_salida, semilla, args.num_plazas, seleccionados, excluidos, suplentes)
    print(f"\n📁 Resultados exportados a '{nombre_salida}'")

if __name__ == "__main__":
    main()
