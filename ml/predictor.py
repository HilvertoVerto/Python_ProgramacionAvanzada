"""
Módulo de Machine Learning para predicción de personajes
Extrae características dinámicamente del JSON (Open/Closed Principle)
"""
import json
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter


class PersonajePredictor:
    """Predictor de personajes basado en características extraídas dinámicamente"""

    def __init__(self, json_path: str = "data/personajes.json"):
        """
        Inicializa el predictor cargando datos del JSON

        Args:
            json_path: Ruta al archivo JSON con personajes
        """
        self.json_path = json_path
        self.personajes: List[Dict[str, Any]] = []
        self.caracteristicas_disponibles: Dict[str, Set[str]] = {}
        self.cargar_datos()

    def cargar_datos(self):
        """Carga los personajes desde el JSON"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.personajes = data.get('personajes', [])
        self._extraer_caracteristicas()

    def _extraer_caracteristicas(self):
        """
        Extrae dinámicamente todas las características únicas de los personajes
        Respeta el principio Open/Closed: no hay características hardcodeadas
        """
        self.caracteristicas_disponibles = {}

        for personaje in self.personajes:
            caracteristicas = personaje.get('caracteristicas', {})

            for clave, valor in caracteristicas.items():
                # Ignorar edad y características numéricas para el momento
                if isinstance(valor, (int, float)):
                    continue

                if clave not in self.caracteristicas_disponibles:
                    self.caracteristicas_disponibles[clave] = set()

                # Convertir a string y normalizar
                valor_str = str(valor).lower().strip()
                self.caracteristicas_disponibles[clave].add(valor_str)

    def obtener_caracteristicas(self) -> Dict[str, List[str]]:
        """
        Obtiene todas las características disponibles

        Returns:
            Diccionario con características y sus posibles valores
        """
        return {
            clave: sorted(list(valores))
            for clave, valores in self.caracteristicas_disponibles.items()
        }

    def calcular_entropia(self, personajes_candidatos: List[Dict[str, Any]]) -> float:
        """
        Calcula la entropía de un conjunto de personajes

        Args:
            personajes_candidatos: Lista de personajes candidatos

        Returns:
            Valor de entropía
        """
        if not personajes_candidatos:
            return 0.0

        total = len(personajes_candidatos)
        contador = Counter(p['nombre'] for p in personajes_candidatos)

        entropia = 0.0
        for count in contador.values():
            if count > 0:
                probabilidad = count / total
                entropia -= probabilidad * math.log2(probabilidad)

        return entropia

    def calcular_ganancia_informacion(
        self,
        personajes_candidatos: List[Dict[str, Any]],
        caracteristica: str
    ) -> float:
        """
        Calcula la ganancia de información al hacer una pregunta sobre una característica

        Args:
            personajes_candidatos: Lista de personajes candidatos actuales
            caracteristica: Característica a evaluar

        Returns:
            Ganancia de información
        """
        if not personajes_candidatos:
            return 0.0

        entropia_inicial = self.calcular_entropia(personajes_candidatos)

        # Agrupar personajes por valor de la característica
        grupos: Dict[str, List[Dict[str, Any]]] = {}

        for personaje in personajes_candidatos:
            valor = personaje.get('caracteristicas', {}).get(caracteristica)

            if valor is None:
                continue

            valor_str = str(valor).lower().strip()

            if valor_str not in grupos:
                grupos[valor_str] = []

            grupos[valor_str].append(personaje)

        # Calcular entropía ponderada después de la división
        total = len(personajes_candidatos)
        entropia_ponderada = 0.0

        for grupo in grupos.values():
            peso = len(grupo) / total
            entropia_ponderada += peso * self.calcular_entropia(grupo)

        # Ganancia de información
        ganancia = entropia_inicial - entropia_ponderada

        return ganancia

    def seleccionar_mejor_pregunta(
        self,
        personajes_candidatos: List[Dict[str, Any]],
        caracteristicas_preguntadas: Set[str]
    ) -> Optional[str]:
        """
        Selecciona la mejor pregunta basándose en ganancia de información

        Args:
            personajes_candidatos: Personajes que aún son candidatos
            caracteristicas_preguntadas: Características ya preguntadas

        Returns:
            Nombre de la característica a preguntar, o None si no hay más
        """
        if not personajes_candidatos:
            return None

        mejor_caracteristica = None
        mejor_ganancia = -1.0

        # Evaluar todas las características disponibles
        for caracteristica in self.caracteristicas_disponibles.keys():
            # Saltar si ya fue preguntada
            if caracteristica in caracteristicas_preguntadas:
                continue

            ganancia = self.calcular_ganancia_informacion(
                personajes_candidatos,
                caracteristica
            )

            if ganancia > mejor_ganancia:
                mejor_ganancia = ganancia
                mejor_caracteristica = caracteristica

        return mejor_caracteristica

    def calcular_ganancia_binaria(
        self,
        personajes_candidatos: List[Dict[str, Any]],
        caracteristica: str,
        valor: str
    ) -> float:
        """
        Calcula la ganancia de información de una pregunta binaria

        Args:
            personajes_candidatos: Lista de personajes candidatos
            caracteristica: Característica a preguntar
            valor: Valor específico a preguntar

        Returns:
            Ganancia de información
        """
        if not personajes_candidatos:
            return 0.0

        entropia_inicial = self.calcular_entropia(personajes_candidatos)

        # Dividir en dos grupos: los que tienen el valor y los que no
        grupo_si = []
        grupo_no = []

        for personaje in personajes_candidatos:
            valor_personaje = personaje.get('caracteristicas', {}).get(caracteristica)

            if valor_personaje is None:
                grupo_no.append(personaje)
                continue

            valor_personaje_str = str(valor_personaje).lower().strip()

            if valor_personaje_str == valor.lower().strip():
                grupo_si.append(personaje)
            else:
                grupo_no.append(personaje)

        # Calcular entropía ponderada
        total = len(personajes_candidatos)
        entropia_ponderada = 0.0

        if grupo_si:
            peso_si = len(grupo_si) / total
            entropia_ponderada += peso_si * self.calcular_entropia(grupo_si)

        if grupo_no:
            peso_no = len(grupo_no) / total
            entropia_ponderada += peso_no * self.calcular_entropia(grupo_no)

        return entropia_inicial - entropia_ponderada

    def seleccionar_mejor_pregunta_binaria(
        self,
        personajes_candidatos: List[Dict[str, Any]],
        preguntas_realizadas: Set[Tuple[str, str]]
    ) -> Optional[Tuple[str, str]]:
        """
        Selecciona la mejor pregunta binaria basándose en ganancia de información

        Args:
            personajes_candidatos: Personajes que aún son candidatos
            preguntas_realizadas: Set de tuplas (caracteristica, valor) ya preguntadas

        Returns:
            Tupla (caracteristica, valor) para la mejor pregunta binaria, o None
        """
        if not personajes_candidatos:
            return None

        mejor_pregunta = None
        mejor_ganancia = -1.0

        # Evaluar todas las combinaciones posibles de característica-valor
        for caracteristica in self.caracteristicas_disponibles.keys():
            # Obtener valores posibles para esta característica en los candidatos actuales
            valores = self.obtener_valores_posibles(caracteristica, personajes_candidatos)

            for valor in valores:
                # Saltar si esta pregunta ya fue realizada
                if (caracteristica, valor) in preguntas_realizadas:
                    continue

                ganancia = self.calcular_ganancia_binaria(
                    personajes_candidatos,
                    caracteristica,
                    valor
                )

                if ganancia > mejor_ganancia:
                    mejor_ganancia = ganancia
                    mejor_pregunta = (caracteristica, valor)

        return mejor_pregunta

    def filtrar_personajes(
        self,
        personajes_candidatos: List[Dict[str, Any]],
        caracteristica: str,
        valor_usuario: str
    ) -> List[Dict[str, Any]]:
        """
        Filtra personajes según la respuesta del usuario

        Args:
            personajes_candidatos: Lista de personajes candidatos
            caracteristica: Característica preguntada
            valor_usuario: Respuesta del usuario

        Returns:
            Lista filtrada de personajes
        """
        valor_usuario = valor_usuario.lower().strip()

        personajes_filtrados = []

        for personaje in personajes_candidatos:
            valor_personaje = personaje.get('caracteristicas', {}).get(caracteristica)

            if valor_personaje is None:
                continue

            valor_personaje_str = str(valor_personaje).lower().strip()

            if valor_personaje_str == valor_usuario:
                personajes_filtrados.append(personaje)

        return personajes_filtrados

    def filtrar_personajes_binario(
        self,
        personajes_candidatos: List[Dict[str, Any]],
        caracteristica: str,
        valor: str,
        respuesta_binaria: bool
    ) -> List[Dict[str, Any]]:
        """
        Filtra personajes según una respuesta binaria (sí/no)

        Args:
            personajes_candidatos: Lista de personajes candidatos
            caracteristica: Característica preguntada
            valor: Valor específico preguntado
            respuesta_binaria: True para sí, False para no

        Returns:
            Lista filtrada de personajes

        Note:
            Los personajes que no tienen la característica se tratan como
            si no tuvieran ese valor específico (respuesta "no").
        """
        valor = valor.lower().strip()
        personajes_filtrados = []

        for personaje in personajes_candidatos:
            caracteristicas = personaje.get('caracteristicas', {})
            valor_personaje = caracteristicas.get(caracteristica)

            # Manejo explícito de valores None o características faltantes
            if valor_personaje is None:
                # Si no tiene la característica, se interpreta como "no tiene ese valor"
                # Solo se incluye si la respuesta del usuario fue "no"
                if not respuesta_binaria:
                    personajes_filtrados.append(personaje)
                continue

            # Convertir a string y normalizar
            valor_personaje_str = str(valor_personaje).lower().strip()
            tiene_valor = (valor_personaje_str == valor)

            # Incluir el personaje si:
            # - respuesta es "sí" y el personaje tiene el valor, O
            # - respuesta es "no" y el personaje NO tiene el valor
            if tiene_valor == respuesta_binaria:
                personajes_filtrados.append(personaje)

        return personajes_filtrados

    def obtener_valores_posibles(
        self,
        caracteristica: str,
        personajes_candidatos: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Obtiene los valores posibles para una característica

        Args:
            caracteristica: Nombre de la característica
            personajes_candidatos: Lista opcional de personajes a considerar

        Returns:
            Lista de valores posibles
        """
        if personajes_candidatos is None:
            personajes_candidatos = self.personajes

        valores = set()

        for personaje in personajes_candidatos:
            valor = personaje.get('caracteristicas', {}).get(caracteristica)

            if valor is not None and not isinstance(valor, (int, float)):
                valores.add(str(valor).lower().strip())

        return sorted(list(valores))

    def hacer_prediccion(
        self,
        personajes_candidatos: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Hace una predicción del personaje más probable

        Args:
            personajes_candidatos: Lista de personajes candidatos

        Returns:
            Personaje predicho o None
        """
        if not personajes_candidatos:
            return None

        if len(personajes_candidatos) == 1:
            return personajes_candidatos[0]

        # Si hay múltiples candidatos, devolver el primero
        # (en el futuro se puede usar probabilidades)
        return personajes_candidatos[0]

    def obtener_confianza(
        self,
        personajes_candidatos: List[Dict[str, Any]]
    ) -> float:
        """
        Calcula el nivel de confianza de la predicción actual

        Args:
            personajes_candidatos: Lista de personajes candidatos

        Returns:
            Confianza entre 0 y 1
        """
        if not personajes_candidatos:
            return 0.0

        total_personajes = len(self.personajes)
        candidatos = len(personajes_candidatos)

        # Confianza inversamente proporcional al número de candidatos
        if candidatos == 1:
            return 1.0

        return 1.0 - (candidatos / total_personajes)

    def reiniciar(self):
        """Reinicia el predictor para un nuevo juego"""
        # No hay estado que reiniciar en esta versión
        pass
