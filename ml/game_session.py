"""
Módulo para gestionar sesiones de juego
"""
from typing import Optional, List, Dict, Any, Set, Tuple
from ml.predictor import PersonajePredictor


class GameSession:
    """Gestiona una sesión de juego de adivinanza"""

    def __init__(self, predictor: PersonajePredictor):
        """
        Inicializa una sesión de juego

        Args:
            predictor: Instancia del predictor de personajes
        """
        self.predictor = predictor
        self.personajes_candidatos: List[Dict[str, Any]] = []
        self.preguntas_realizadas: Set[Tuple[str, str]] = set()
        self.historial_preguntas: List[Dict[str, Any]] = []
        self.intentos_adivinanza = 0
        self.max_intentos_adivinanza = 3
        self.reiniciar()

    def reiniciar(self):
        """Reinicia la sesión para un nuevo juego"""
        self.personajes_candidatos = self.predictor.personajes.copy()
        self.preguntas_realizadas.clear()
        self.historial_preguntas.clear()
        self.intentos_adivinanza = 0

    def obtener_siguiente_pregunta(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene la siguiente pregunta binaria a realizar

        Returns:
            Diccionario con la pregunta binaria, o None si no hay más preguntas
        """
        # Si ya no quedan candidatos, no hay más preguntas
        if not self.personajes_candidatos:
            return None

        # Si solo queda un candidato, intentar adivinar
        if len(self.personajes_candidatos) == 1:
            return None

        # Seleccionar la mejor pregunta binaria
        pregunta_binaria = self.predictor.seleccionar_mejor_pregunta_binaria(
            self.personajes_candidatos,
            self.preguntas_realizadas
        )

        if pregunta_binaria is None:
            return None

        caracteristica, valor = pregunta_binaria

        # Formatear la pregunta
        pregunta_formateada = self._formatear_pregunta_binaria(caracteristica, valor)

        return {
            'caracteristica': caracteristica,
            'valor': valor,
            'pregunta': pregunta_formateada
        }

    def _formatear_pregunta_binaria(self, caracteristica: str, valor: str) -> str:
        """
        Formatea una pregunta binaria

        Args:
            caracteristica: Nombre de la característica
            valor: Valor a preguntar

        Returns:
            Pregunta formateada
        """
        # Convertir snake_case a palabras separadas
        caracteristica_formateada = caracteristica.replace('_', ' ')

        return f"{caracteristica_formateada}: {valor}"

    def procesar_respuesta(self, caracteristica: str, valor: str, respuesta_binaria: bool):
        """
        Procesa la respuesta binaria del usuario a una pregunta

        Args:
            caracteristica: Característica preguntada
            valor: Valor específico preguntado
            respuesta_binaria: True para sí (1), False para no (0)
        """
        # Registrar pregunta
        self.preguntas_realizadas.add((caracteristica, valor))
        self.historial_preguntas.append({
            'caracteristica': caracteristica,
            'valor': valor,
            'respuesta': respuesta_binaria
        })

        # Filtrar personajes candidatos
        self.personajes_candidatos = self.predictor.filtrar_personajes_binario(
            self.personajes_candidatos,
            caracteristica,
            valor,
            respuesta_binaria
        )

    def intentar_adivinanza(self) -> Optional[Dict[str, Any]]:
        """
        Intenta adivinar el personaje

        Returns:
            Predicción del personaje o None si no puede predecir
        """
        self.intentos_adivinanza += 1
        return self.predictor.hacer_prediccion(self.personajes_candidatos)

    def obtener_confianza(self) -> float:
        """
        Obtiene el nivel de confianza actual

        Returns:
            Confianza entre 0 y 1
        """
        return self.predictor.obtener_confianza(self.personajes_candidatos)

    def puede_intentar_adivinar(self) -> bool:
        """
        Determina si el sistema debería intentar adivinar

        Returns:
            True si debe intentar adivinar
        """
        # Intentar adivinar si:
        # 1. Solo queda un candidato
        # 2. La confianza es alta (>0.7)
        # 3. No quedan más preguntas útiles

        if not self.personajes_candidatos:
            return False

        if len(self.personajes_candidatos) == 1:
            return True

        confianza = self.obtener_confianza()
        if confianza >= 0.7:
            return True

        # Verificar si quedan preguntas útiles
        siguiente_pregunta = self.predictor.seleccionar_mejor_pregunta_binaria(
            self.personajes_candidatos,
            self.preguntas_realizadas
        )

        if siguiente_pregunta is None:
            return True

        return False

    def puede_agregar_personaje(self) -> bool:
        """
        Determina si se debe permitir agregar un nuevo personaje
        (Después de 3 fallos consecutivos)

        Returns:
            True si se alcanzó el límite de intentos
        """
        return self.intentos_adivinanza >= self.max_intentos_adivinanza

    def obtener_estadisticas_sesion(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la sesión actual

        Returns:
            Diccionario con estadísticas
        """
        return {
            'preguntas_realizadas': len(self.historial_preguntas),
            'candidatos_restantes': len(self.personajes_candidatos),
            'intentos_adivinanza': self.intentos_adivinanza,
            'confianza': self.obtener_confianza(),
            'puede_adivinar': self.puede_intentar_adivinar(),
            'puede_agregar': self.puede_agregar_personaje()
        }

    def obtener_candidatos_actuales(self) -> List[str]:
        """
        Obtiene los nombres de los personajes candidatos actuales

        Returns:
            Lista de nombres
        """
        return [p['nombre'] for p in self.personajes_candidatos]
