#!/usr/bin/env python3
"""
Juego de adivinanza de personajes con Machine Learning
Punto de entrada principal del programa
"""
from game_controller import GameController


def main():
    """Función principal del programa"""
    controller = GameController()
    controller.iniciar()


if __name__ == "__main__":
    main()
