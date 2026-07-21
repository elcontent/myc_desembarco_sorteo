import copy
import unittest

from sorteo import calcular_desglose, sorteo_plazas, validar_participantes


BASE = {
    "id": 1,
    "nombre": "Ana",
    "apellidos": "Ejemplo",
    "tipo_cuota": "completa",
    "desembarco_anterior": False,
    "infraccion": False,
    "implicacion": False,
    "antiguo": False,
    "desfila": False,
    "cumplio_18_este_ano": False,
    "tirador": False,
    "comisiones": 0,
}


class TestBaremo(unittest.TestCase):
    def test_comisiones_bonifican_con_tope(self):
        persona = copy.deepcopy(BASE)
        persona["comisiones"] = 10
        self.assertAlmostEqual(calcular_desglose(persona)["peso"], 1.60)

    def test_implicacion_actual_pesa_mas_que_antiguedad(self):
        implicada = copy.deepcopy(BASE)
        implicada["implicacion"] = True
        antigua = copy.deepcopy(BASE)
        antigua["antiguo"] = True
        self.assertGreater(calcular_desglose(implicada)["peso"], calcular_desglose(antigua)["peso"])

    def test_desfilar_bonifica_un_25_por_ciento(self):
        persona = copy.deepcopy(BASE)
        persona["desfila"] = True
        self.assertAlmostEqual(calcular_desglose(persona)["peso"], 1.25)

    def test_cumplir_18_este_ano_bonifica_un_15_por_ciento(self):
        persona = copy.deepcopy(BASE)
        persona["cumplio_18_este_ano"] = True
        self.assertAlmostEqual(calcular_desglose(persona)["peso"], 1.15)

    def test_ser_tirador_bonifica_un_15_por_ciento(self):
        persona = copy.deepcopy(BASE)
        persona["tirador"] = True
        desglose = calcular_desglose(persona)
        self.assertAlmostEqual(desglose["peso"], 1.15)
        self.assertIn("Tirador ×1.15", desglose["factores"])

    def test_nuevas_bonificaciones_son_acumulables(self):
        persona = copy.deepcopy(BASE)
        persona.update({"desfila": True, "cumplio_18_este_ano": True, "tirador": True})
        self.assertAlmostEqual(calcular_desglose(persona)["peso"], 1.653125)

    def test_cuota_completa_tiene_prioridad_absoluta(self):
        completa = copy.deepcopy(BASE)
        reducida = copy.deepcopy(BASE)
        reducida.update({"id": 2, "tipo_cuota": "reducida", "comisiones": 4, "implicacion": True, "antiguo": True})
        orden, _ = sorteo_plazas([reducida, completa], 123)
        self.assertEqual(orden[0]["id"], 1)

    def test_misma_semilla_mismo_resultado(self):
        personas = []
        for identificador in range(1, 8):
            persona = copy.deepcopy(BASE)
            persona["id"] = identificador
            personas.append(persona)
        primero, _ = sorteo_plazas(personas, 2026)
        segundo, _ = sorteo_plazas(personas, 2026)
        self.assertEqual([p["id"] for p in primero], [p["id"] for p in segundo])

    def test_rechaza_ids_duplicados(self):
        with self.assertRaisesRegex(ValueError, "duplicado"):
            validar_participantes({"participantes": [BASE, copy.deepcopy(BASE)]})

    def test_normaliza_booleanos_y_cuota(self):
        persona = copy.deepcopy(BASE)
        persona.update({
            "tipo_cuota": "Nuevo Sí", "implicacion": "Sí", "antiguo": "No",
            "desfila": "Sí", "cumplio_18_este_ano": "No", "tirador": "Sí",
        })
        resultado = validar_participantes({"participantes": [persona]})[0]
        self.assertEqual(resultado["tipo_cuota"], "completa")
        self.assertTrue(resultado["implicacion"])
        self.assertFalse(resultado["antiguo"])
        self.assertTrue(resultado["desfila"])
        self.assertFalse(resultado["cumplio_18_este_ano"])
        self.assertTrue(resultado["tirador"])


if __name__ == "__main__":
    unittest.main()
