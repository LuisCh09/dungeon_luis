from dungeon_generator.mapa import mapa
from dungeon_generator.player import explorador
from dungeon_generator.content import tesoro, monstruo
from pathlib import Path

try:
    from dungeon_generator.save import guardar_partida, cargar_partida
    HAS_SERIALIZACION = True
except Exception:
    guardar_partida = None
    cargar_partida = None
    HAS_SERIALIZACION = False


def mostrar_mapa_simple(m, exp=None):
    print("\nmapa completo:")
    print("  ", end="")
    for x in range(m.ancho):
        print(f" {x} ", end="")
    print()
    
    for y in range(m.alto):
        print(f"{y} ", end="")
        for x in range(m.ancho):
            if exp and (x, y) == exp.posicion_actual:
                print(" @ ", end="")
            elif (x, y) in m.habitaciones:
                hab = m.habitaciones[(x, y)]
                if hab.inicial:
                    print(" S ", end="")
                elif hab.contenido:
                    tipo = hab.contenido.tipo
                    if tipo == "monstruo":
                        print(" M ", end="")
                    elif tipo == "jefe":
                        print(" J ", end="")
                    elif tipo == "tesoro":
                        print(" T ", end="")
                    elif tipo == "evento":
                        print(" E ", end="")
                    else:
                        print(" . ", end="")
                else:
                    print(" . ", end="")
            else:
                print(" # ", end="")
        print()
    print("\nleyenda: @ = explorador | S = inicio | M = monstruo | J = jefe")
    print("         T = tesoro | E = evento | . = vacio | # = sin habitacion\n")


def mostrar_estadisticas(m):
    stats = m.obtener_estadisticas_mapa()
    print("estadisticas del mapa:")
    print(f"  total habitaciones: {stats['Total de habitaciones']}")
    print(f"  vacias: {stats['vacios']}")
    print(f"  tesoros: {stats['tesoros']}")
    print(f"  monstruos: {stats['monstruos']}")
    print(f"  jefes: {stats['jefes']}")
    print(f"  eventos: {stats['eventos']}")
    print(f"  promedio conexiones: {stats['promedio_conexiones']}")
    return stats


def contenido_str(hab):
    c = hab.contenido
    if c is None:
        return "vacia"
    tipo = getattr(c, "tipo", "desconocido")
    desc = getattr(c, "descripcion", None)
    if desc:
        return f"{tipo} - {desc}"
    return tipo


def demo():
    print("=== demo generador de dungeons ===\n")
    
    m = mapa(8, 6, seed=42)
    m.generar_estructura(12)
    resumen = m.colocar_contenido(seed=42)
    print("resumen colocar contenido:", resumen)

    mostrar_mapa_simple(m)
    mostrar_estadisticas(m)

    coord_tesoro = None
    coord_mon = None
    for coord, hab in m.habitaciones.items():
        if hab.contenido is not None:
            tipo = getattr(hab.contenido, "tipo", None)
            if tipo == "tesoro" and coord_tesoro is None:
                coord_tesoro = coord
            if tipo == "monstruo" and coord_mon is None:
                coord_mon = coord
        if coord_tesoro and coord_mon:
            break

    exp = explorador(m)
    print("\n--- estado inicial ---")
    print(f"posicion: {exp.posicion_actual}")
    print(f"vida: {exp.vida}")
    print(f"ataque: {exp.calcular_ataque()}")
    print(f"inventario: {len(exp.inventario)} items")

    if coord_tesoro:
        print("\n--- probando tesoro ---")
        exp.posicion_actual = coord_tesoro
        print(f"moviendo a: {exp.posicion_actual}")
        salida = exp.explorar_habitacion()
        print(salida)
        print(f"inventario: {[o.nombre for o in exp.inventario]}")
        print(f"habitacion ahora: {contenido_str(m.habitaciones[coord_tesoro])}")
        mostrar_mapa_simple(m, exp)

    if coord_mon:
        print("\n--- probando combate ---")
        exp.posicion_actual = coord_mon
        print(f"moviendo a: {exp.posicion_actual}")
        salida = exp.explorar_habitacion()
        print(salida)
        print(f"vida: {exp.vida}")
        print(f"habitacion ahora: {contenido_str(m.habitaciones[coord_mon])}")
        mostrar_mapa_simple(m, exp)

    save_file = "prueba.json"
    if HAS_SERIALIZACION:
        try:
            guardar_partida(m, exp, save_file)
            print(f"\npartida guardada en '{save_file}'")
        except Exception as e:
            print("error guardando partida:", e)
    else:
        print("\nmodulo de serializacion no disponible")

    if HAS_SERIALIZACION:
        try:
            mapa2, exp2 = cargar_partida(save_file)
            print("\n--- partida cargada correctamente ---")
            mostrar_mapa_simple(mapa2, exp2)
            print(f"posicion cargada: {exp2.posicion_actual}")
            print(f"vida cargada: {exp2.vida}")
            print(f"items cargados: {len(exp2.inventario)}")
            mostrar_estadisticas(mapa2)
        except Exception as e:
            print("error cargando partida:", e)

    if HAS_SERIALIZACION:
        try:
            p = Path(save_file)
            if p.exists():
                p.unlink()
        except Exception:
            pass

    print("\ndemo finalizada")


if __name__ == "__main__":
    demo()
