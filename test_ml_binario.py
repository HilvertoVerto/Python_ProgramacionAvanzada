#!/usr/bin/env python3
"""
Script de prueba para el sistema de ML con preguntas binarias
"""
from ml.predictor import PersonajePredictor
from ml.game_session import GameSession


def mostrar_linea(caracter="=", longitud=70):
    """Imprime una línea separadora"""
    print(caracter * longitud)


def main():
    mostrar_linea()
    print("PRUEBA DEL SISTEMA ML CON PREGUNTAS BINARIAS")
    mostrar_linea()

    # Inicializar predictor
    print("\n1. Inicializando predictor...")
    predictor = PersonajePredictor()
    print(f"   [OK] Cargados {len(predictor.personajes)} personajes")

    # Crear sesión de juego
    print("\n2. Simulacion de una partida con preguntas binarias")
    mostrar_linea("-")

    sesion = GameSession(predictor)

    print(f"\n   Candidatos iniciales: {', '.join(sesion.obtener_candidatos_actuales())}")

    # Simulación: el usuario piensa en "Vegeta"
    personaje_pensado = "Vegeta"
    print(f"\n   [Simulacion: Usuario piensa en '{personaje_pensado}']")

    turno = 1
    max_turnos = 20

    while turno <= max_turnos:
        print(f"\n   --- Turno {turno} ---")

        # Verificar si debería intentar adivinar
        if sesion.puede_intentar_adivinar():
            print("\n   El sistema tiene suficiente confianza para adivinar...")
            prediccion = sesion.intentar_adivinanza()

            if prediccion:
                print(f"   Prediccion: {prediccion['nombre']}")

                if prediccion['nombre'] == personaje_pensado:
                    print("   [OK] Adivino correctamente!")
                    break
                else:
                    print(f"   [ERROR] Incorrecto (intentos: {sesion.intentos_adivinanza}/3)")

                    if sesion.puede_agregar_personaje():
                        print("\n   [ADVERTENCIA] Se alcanzo el limite de 3 intentos fallidos")
                        break
            else:
                print("   No se pudo hacer una prediccion")
                break

        # Obtener siguiente pregunta binaria
        pregunta_data = sesion.obtener_siguiente_pregunta()

        if pregunta_data is None:
            print("   No hay mas preguntas disponibles")
            break

        caracteristica = pregunta_data['caracteristica']
        valor = pregunta_data['valor']
        pregunta = pregunta_data['pregunta']

        print(f"\n   {pregunta}?")
        print("   0 = No | 1 = Si")

        # Simular respuesta del usuario basándose en el personaje pensado
        personaje_obj = next(
            (p for p in predictor.personajes if p['nombre'] == personaje_pensado),
            None
        )

        if personaje_obj:
            valor_real = personaje_obj['caracteristicas'].get(caracteristica)

            if valor_real is None:
                respuesta_binaria = False
            else:
                valor_real_str = str(valor_real).lower().strip()
                valor_pregunta_str = valor.lower().strip()
                respuesta_binaria = (valor_real_str == valor_pregunta_str)

            respuesta_str = "1" if respuesta_binaria else "0"
            print(f"   Respuesta del usuario: {respuesta_str} ({'Si' if respuesta_binaria else 'No'})")

            # Procesar respuesta
            sesion.procesar_respuesta(caracteristica, valor, respuesta_binaria)

            # Mostrar progreso
            candidatos = sesion.obtener_candidatos_actuales()
            confianza = sesion.obtener_confianza()

            print(f"   Candidatos restantes ({len(candidatos)}): {', '.join(candidatos)}")
            print(f"   Confianza: {confianza:.2%}")

        turno += 1

    # Mostrar estadísticas
    print("\n" + "=" * 70)
    print("3. Estadisticas de la sesion:")
    mostrar_linea("-")

    stats = sesion.obtener_estadisticas_sesion()
    print(f"   Preguntas realizadas: {stats['preguntas_realizadas']}")
    print(f"   Intentos de adivinanza: {stats['intentos_adivinanza']}")
    print(f"   Confianza final: {stats['confianza']:.2%}")
    print(f"   Candidatos finales: {stats['candidatos_restantes']}")

    mostrar_linea()
    print("PRUEBA COMPLETADA EXITOSAMENTE")
    mostrar_linea()


if __name__ == "__main__":
    main()
