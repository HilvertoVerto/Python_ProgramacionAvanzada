"""
Controlador principal del juego de adivinanza de personajes
"""
from typing import Optional, Dict, Any
from ml.predictor import PersonajePredictor
from ml.game_session import GameSession
from persistence.database import DatabaseManager


class GameController:
    """Controlador principal que coordina todos los componentes del juego"""

    def __init__(self):
        """Inicializa el controlador y todos sus componentes"""
        self.db = DatabaseManager()
        self.predictor = PersonajePredictor()
        self.sesion: Optional[GameSession] = None
        self.jugando = True

    def iniciar(self):
        """Inicia el juego"""
        self._mostrar_bienvenida()
        self._verificar_base_datos()
        self._menu_principal()

    def _mostrar_bienvenida(self):
        """Muestra el mensaje de bienvenida"""
        print("\n" + "=" * 70)
        print("JUEGO DE ADIVINANZA DE PERSONAJES CON MACHINE LEARNING")
        print("=" * 70)
        print("\nPiensa en un personaje y responde mis preguntas.")
        print("Intentare adivinar en quien estas pensando!")

    def _verificar_base_datos(self):
        """Verifica y sincroniza la base de datos con el JSON"""
        total_personajes = self.db.contar_personajes()

        if total_personajes == 0:
            print("\n[INFO] Cargando personajes iniciales...")
            resultado = self.db.importar_desde_json("data/personajes.json")
            print(f"[OK] Importados {resultado['importados']} personajes")
        else:
            print(f"\n[INFO] Base de datos lista con {total_personajes} personajes")

    def _menu_principal(self):
        """Muestra el menú principal del juego"""
        while self.jugando:
            print("\n" + "-" * 70)
            print("MENU PRINCIPAL")
            print("-" * 70)
            print("1. Jugar")
            print("2. Ver estadisticas")
            print("3. Listar personajes")
            print("4. Salir")

            opcion = input("\nSelecciona una opcion: ").strip()

            if opcion == "1":
                self._jugar_partida()
            elif opcion == "2":
                self._mostrar_estadisticas()
            elif opcion == "3":
                self._listar_personajes()
            elif opcion == "4":
                self._salir()
            else:
                print("[ERROR] Opcion invalida")

    def _jugar_partida(self):
        """Ejecuta una partida completa del juego"""
        print("\n" + "=" * 70)
        print("NUEVA PARTIDA")
        print("=" * 70)

        # Crear nueva sesión
        self.sesion = GameSession(self.predictor)

        # Variables para registrar la partida
        personaje_objetivo_nombre = None
        preguntas_realizadas = []

        print("\nPiensa en un personaje de los que conozco...")
        input("Presiona Enter cuando estes listo...")

        while True:
            # Verificar si debería intentar adivinar
            if self.sesion.puede_intentar_adivinar():
                resultado_adivinanza, nombre_adivinado = self._intentar_adivinanza()

                if resultado_adivinanza == "correcto":
                    # Guardar el nombre del personaje adivinado
                    personaje_objetivo_nombre = nombre_adivinado

                    # Registrar partida exitosa
                    if personaje_objetivo_nombre:
                        personaje = self.db.obtener_personaje_por_nombre(personaje_objetivo_nombre)
                        if personaje:
                            self._registrar_partida(
                                personaje['id'],
                                True,
                                self.sesion.intentos_adivinanza,
                                preguntas_realizadas
                            )
                    break
                elif resultado_adivinanza == "limite_alcanzado":
                    # Se alcanzó el límite de intentos
                    personaje_objetivo_nombre = self._manejar_limite_intentos()
                    if personaje_objetivo_nombre:
                        personaje = self.db.obtener_personaje_por_nombre(personaje_objetivo_nombre)
                        if personaje:
                            self._registrar_partida(
                                personaje['id'],
                                False,
                                self.sesion.intentos_adivinanza,
                                preguntas_realizadas
                            )
                    break
                elif resultado_adivinanza == "continuar":
                    # Adivinanza incorrecta, continuar preguntando
                    pass

            # Obtener siguiente pregunta
            pregunta_data = self.sesion.obtener_siguiente_pregunta()

            if pregunta_data is None:
                print("\n[INFO] No hay mas preguntas disponibles")
                print("No pude adivinar el personaje.")
                break

            # Hacer la pregunta binaria
            caracteristica = pregunta_data['caracteristica']
            valor = pregunta_data['valor']
            pregunta = pregunta_data['pregunta']

            print(f"\n{pregunta}?")
            print("Responde: s/n")

            respuesta_str = input("Tu respuesta: ").strip().lower()

            # Validar respuesta - aceptar múltiples formatos
            if respuesta_str in ['0', 'no', 'n']:
                respuesta_binaria = False
            elif respuesta_str in ['1', 'si', 'sí', 's']:
                respuesta_binaria = True
            else:
                print("[ERROR] Respuesta invalida. Debe ser: 0/1, si/no, s/n")
                continue

            # Registrar pregunta
            preguntas_realizadas.append({
                'caracteristica': caracteristica,
                'valor': valor,
                'respuesta': respuesta_binaria
            })

            # Procesar respuesta
            self.sesion.procesar_respuesta(caracteristica, valor, respuesta_binaria)

        print("\n" + "=" * 70)

    def _intentar_adivinanza(self) -> tuple:
        """
        Intenta adivinar el personaje

        Returns:
            Tupla (resultado, nombre_personaje)
            resultado: 'correcto', 'incorrecto', 'limite_alcanzado', 'continuar'
            nombre_personaje: Nombre del personaje adivinado (o None)
        """
        print("\n" + "-" * 70)
        print("MOMENTO DE ADIVINAR")
        print("-" * 70)

        prediccion = self.sesion.intentar_adivinanza()

        if not prediccion:
            print("\n[ERROR] No se pudo hacer una prediccion")
            return ("continuar", None)

        print(f"\nCreo que estas pensando en: {prediccion['nombre']}")
        respuesta = input("Es correcto? (s/n): ").strip().lower()

        if respuesta == 's':
            print("\n[OK] Adivine correctamente!")
            return ("correcto", prediccion['nombre'])
        else:
            print(f"\n[INFO] Intento {self.sesion.intentos_adivinanza} de 3")

            if self.sesion.puede_agregar_personaje():
                return ("limite_alcanzado", None)
            else:
                print("Continuare preguntando...")
                return ("continuar", None)

    def _manejar_limite_intentos(self) -> Optional[str]:
        """
        Maneja el caso cuando se alcanza el límite de intentos
        Permite al usuario agregar un nuevo personaje

        Returns:
            Nombre del personaje pensado, o None
        """
        print("\n" + "=" * 70)
        print("LIMITE DE INTENTOS ALCANZADO")
        print("=" * 70)
        print("\nNo pude adivinar el personaje despues de 3 intentos.")

        agregar = input("\nQuieres agregar el personaje al sistema? (s/n): ").strip().lower()

        if agregar != 's':
            print("\n[INFO] No se agrego ningun personaje")
            return None

        # Solicitar información del nuevo personaje
        print("\n" + "-" * 70)
        print("AGREGAR NUEVO PERSONAJE")
        print("-" * 70)

        nombre = input("\nNombre del personaje: ").strip()

        if not nombre:
            print("[ERROR] El nombre no puede estar vacio")
            return None

        # Verificar si ya existe
        existente = self.db.obtener_personaje_por_nombre(nombre)
        if existente:
            print(f"[ERROR] El personaje '{nombre}' ya existe en la base de datos")
            return nombre

        # Obtener características del personaje basándose en las preguntas realizadas
        caracteristicas = {}

        print("\nAhora necesito las caracteristicas del personaje.")
        print("Responde basandote en las preguntas que hice:")

        # Obtener todas las características disponibles
        todas_caracteristicas = self.predictor.obtener_caracteristicas()

        for caracteristica, valores_posibles in todas_caracteristicas.items():
            pregunta_formateada = caracteristica.replace('_', ' ')
            print(f"\n{pregunta_formateada}?")
            print(f"Opciones: {', '.join(valores_posibles)}")

            valor = input("Valor: ").strip().lower()

            if valor:
                caracteristicas[caracteristica] = valor

        # Guardar en la base de datos
        try:
            personaje_id = self.db.agregar_personaje(nombre, caracteristicas)
            print(f"\n[OK] Personaje '{nombre}' agregado exitosamente (ID: {personaje_id})")

            # Exportar a JSON para mantener sincronización
            self.db.exportar_a_json("data/personajes.json")

            # Recargar predictor para incluir el nuevo personaje
            self.predictor.cargar_datos()
            print("[INFO] Sistema actualizado con el nuevo personaje")

            return nombre

        except Exception as e:
            print(f"[ERROR] No se pudo agregar el personaje: {e}")
            return None

    def _registrar_partida(
        self,
        personaje_id: int,
        adivinado: bool,
        intentos: int,
        preguntas: list
    ):
        """Registra una partida en la base de datos"""
        try:
            partida_id = self.db.registrar_partida(personaje_id, adivinado, intentos)

            for orden, pregunta in enumerate(preguntas, 1):
                caracteristica = pregunta['caracteristica']
                valor = pregunta['valor']
                respuesta = "si" if pregunta['respuesta'] else "no"

                self.db.registrar_pregunta_partida(
                    partida_id,
                    f"{caracteristica}:{valor}",
                    valor,
                    respuesta,
                    orden
                )

        except Exception as e:
            print(f"[ERROR] No se pudo registrar la partida: {e}")

    def _mostrar_estadisticas(self):
        """Muestra las estadísticas del juego"""
        print("\n" + "=" * 70)
        print("ESTADISTICAS DEL JUEGO")
        print("=" * 70)

        stats = self.db.obtener_estadisticas()

        print(f"\nTotal de personajes: {stats['total_personajes']}")
        print(f"Total de partidas jugadas: {stats['total_partidas']}")
        print(f"Partidas ganadas: {stats['partidas_ganadas']}")
        print(f"Tasa de exito: {stats['tasa_exito']:.2f}%")
        print(f"Promedio de intentos: {stats['promedio_intentos']}")
        print(f"Personaje mas jugado: {stats['personaje_mas_jugado']}")

    def _listar_personajes(self):
        """Lista todos los personajes en la base de datos"""
        print("\n" + "=" * 70)
        print("PERSONAJES EN LA BASE DE DATOS")
        print("=" * 70)

        personajes = self.db.obtener_todos_personajes()

        for i, p in enumerate(personajes, 1):
            print(f"\n{i}. {p['nombre']}")
            print(f"   Caracteristicas:")
            for clave, valor in p['caracteristicas'].items():
                print(f"     - {clave.replace('_', ' ')}: {valor}")

    def _salir(self):
        """Cierra el juego"""
        print("\n[INFO] Gracias por jugar!")
        print("Hasta pronto!\n")
        self.db.cerrar()
        self.jugando = False

    def __del__(self):
        """Asegura que la base de datos se cierre al destruir el objeto"""
        if hasattr(self, 'db'):
            self.db.cerrar()
