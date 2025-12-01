#!/usr/bin/env python3
"""
Script de prueba para el sistema de Machine Learning
Demuestra cómo se extraen las preguntas dinámicamente del JSON
"""
from ml.predictor import PersonajePredictor
from ml.game_session import GameSession


def mostrar_linea(caracter="=", longitud=70):
    """Imprime una línea separadora"""
    print(caracter * longitud)


def main():
    mostrar_linea()
    print("PRUEBA DEL SISTEMA DE MACHINE LEARNING")
    mostrar_linea()

    # Inicializar predictor
    print("\n1. Inicializando predictor...")
    predictor = PersonajePredictor()
    print(f"   [OK] Cargados {len(predictor.personajes)} personajes")

    # Mostrar características extraídas dinámicamente
    print("\n2. Características extraídas dinámicamente del JSON:")
    print("   (Respetando el principio Open/Closed)")
    mostrar_linea("-")

    caracteristicas = predictor.obtener_caracteristicas()
    for i, (caracteristica, valores) in enumerate(caracteristicas.items(), 1):
        print(f"\n   {i}. {caracteristica.replace('_', ' ').title()}")
        print(f"      Valores posibles: {', '.join(valores)}")

    # Crear sesión de juego
    print("\n" + "=" * 70)
    print("3. Simulación de una partida")
    mostrar_linea("-")

    sesion = GameSession(predictor)

    print(f"\n   Candidatos iniciales: {', '.join(sesion.obtener_candidatos_actuales())}")

    # Simulación: el usuario piensa en "Yuri"
    personaje_pensado = "Yuri"
    print(f"\n   [Simulación: Usuario piensa en '{personaje_pensado}']")

    turno = 1
    while True:
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
                        print("   El sistema permitiria agregar un nuevo personaje")
                        break
            else:
                print("   No se pudo hacer una predicción")
                break

        # Obtener siguiente pregunta
        pregunta_data = sesion.obtener_siguiente_pregunta()

        if pregunta_data is None:
            print("   No hay más preguntas disponibles")
            break

        caracteristica = pregunta_data['caracteristica']
        pregunta = pregunta_data['pregunta']
        opciones = pregunta_data['opciones']

        print(f"\n   {pregunta}?")
        print(f"   Opciones: {', '.join(opciones)}")

        # Simular respuesta del usuario basándose en el personaje pensado
        personaje_obj = next(
            (p for p in predictor.personajes if p['nombre'] == personaje_pensado),
            None
        )

        if personaje_obj:
            respuesta = str(
                personaje_obj['caracteristicas'].get(caracteristica, '')
            ).lower().strip()
            print(f"   Respuesta del usuario: {respuesta}")

            # Procesar respuesta
            sesion.procesar_respuesta(caracteristica, respuesta)

            # Mostrar candidatos restantes
            candidatos = sesion.obtener_candidatos_actuales()
            print(f"   Candidatos restantes ({len(candidatos)}): {', '.join(candidatos)}")

            # Mostrar confianza
            confianza = sesion.obtener_confianza()
            print(f"   Confianza: {confianza:.2%}")

        turno += 1

        if turno > 20:  # Límite de seguridad
            print("\n   Límite de turnos alcanzado")
            break

    # Mostrar estadísticas
    print("\n" + "=" * 70)
    print("4. Estadísticas de la sesión:")
    mostrar_linea("-")

    stats = sesion.obtener_estadisticas_sesion()
    print(f"   Preguntas realizadas: {stats['preguntas_realizadas']}")
    print(f"   Intentos de adivinanza: {stats['intentos_adivinanza']}")
    print(f"   Confianza final: {stats['confianza']:.2%}")

    # Demostrar búsqueda por característica
    print("\n" + "=" * 70)
    print("5. Demostración de búsqueda por característica:")
    mostrar_linea("-")

    print("\n   Búsqueda: color_ojos = 'morado'")
    resultados = predictor.filtrar_personajes(
        predictor.personajes,
        'color_ojos',
        'morado'
    )
    print(f"   Encontrados: {', '.join([p['nombre'] for p in resultados])}")

    print("\n   Búsqueda: personalidad = 'carismática'")
    resultados = predictor.filtrar_personajes(
        predictor.personajes,
        'personalidad',
        'carismática'
    )
    print(f"   Encontrados: {', '.join([p['nombre'] for p in resultados])}")

    # Calcular ganancia de información
    print("\n" + "=" * 70)
    print("6. Análisis de ganancia de información:")
    mostrar_linea("-")

    print("\n   Calculando qué pregunta proporciona más información...")
    for caracteristica in list(caracteristicas.keys())[:5]:
        ganancia = predictor.calcular_ganancia_informacion(
            predictor.personajes,
            caracteristica
        )
        print(f"   {caracteristica.replace('_', ' ').title():30} → Ganancia: {ganancia:.4f}")

    mostrar_linea()
    print("PRUEBA COMPLETADA EXITOSAMENTE")
    mostrar_linea()


if __name__ == "__main__":
    main()
