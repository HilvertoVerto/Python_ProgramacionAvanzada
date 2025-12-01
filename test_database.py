#!/usr/bin/env python3
"""
Script de prueba para el módulo de persistencia
"""
from persistence.database import DatabaseManager


def main():
    print("=" * 60)
    print("PRUEBA DEL SISTEMA DE PERSISTENCIA")
    print("=" * 60)

    # Crear instancia del gestor de base de datos
    with DatabaseManager() as db:
        print("\n1. Base de datos inicializada correctamente")
        print(f"   Personajes en BD: {db.contar_personajes()}")

        # Importar personajes desde JSON
        print("\n2. Importando personajes desde JSON...")
        resultado = db.importar_desde_json("data/personajes.json")
        print(f"   Importados: {resultado['importados']}")
        print(f"   Actualizados: {resultado['actualizados']}")
        print(f"   Errores: {resultado['errores']}")
        print(f"   Total procesados: {resultado['total']}")

        # Mostrar todos los personajes
        print("\n3. Personajes en la base de datos:")
        personajes = db.obtener_todos_personajes()
        for p in personajes:
            print(f"   - {p['nombre']} (ID: {p['id']})")
            print(f"     Color pelo: {p['caracteristicas'].get('color_pelo')}")
            print(f"     Color ojos: {p['caracteristicas'].get('color_ojos')}")
            print(f"     Personalidad: {p['caracteristicas'].get('personalidad')}")

        # Probar búsqueda por característica
        print("\n4. Búsqueda de personajes con ojos verdes:")
        resultados = db.buscar_por_caracteristica('color_ojos', 'verde esmeralda')
        for r in resultados:
            print(f"   - {r['nombre']}")

        # Probar búsqueda por personalidad
        print("\n5. Búsqueda de personajes tímidos:")
        resultados = db.buscar_por_caracteristica('personalidad', 'tímida')
        for r in resultados:
            print(f"   - {r['nombre']}")

        # Exportar a JSON
        print("\n6. Exportando base de datos a JSON...")
        if db.exportar_a_json("data/personajes_backup.json"):
            print("   Exportación exitosa!")

        print("\n7. Estadísticas:")
        stats = db.obtener_estadisticas()
        print(f"   Total personajes: {stats['total_personajes']}")
        print(f"   Total partidas: {stats['total_partidas']}")

    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()
