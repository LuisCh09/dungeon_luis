from dungeon_generator.mapa import mapa
from dungeon_generator.player import explorador

try:
    from dungeon_generator.display import visualizador
    HAS_VISUALIZADOR = True
except Exception:
    visualizador = None
    HAS_VISUALIZADOR = False


def mostrar_minimapa_simple(mapa, exp):
    # muestra minimapa ascii simple sin colores
    vista_radio = 3
    ex, ey = exp.posicion_actual
    
    print("\nmapa local:")
    for y in range(ey - vista_radio, ey + vista_radio + 1):
        linea = ""
        for x in range(ex - vista_radio, ex + vista_radio + 1):
            if (x, y) == (ex, ey):
                linea += " @ "  # explorador
            elif (x, y) in mapa.habitaciones:
                hab = mapa.habitaciones[(x, y)]
                if hab.contenido:
                    tipo = hab.contenido.tipo
                    if tipo == "monstruo":
                        linea += " M "
                    elif tipo == "jefe":
                        linea += " J "
                    elif tipo == "tesoro":
                        linea += " T "
                    elif tipo == "evento":
                        linea += " E "
                    else:
                        linea += " . "
                else:
                    linea += " . " if hab.visitada else " ? "
            else:
                linea += " # "
        print(linea)


def mostrar_mapa_completo_simple(mapa, exp):
    # muestra mapa completo ascii simple
    print("\nmapa completo:")
    print("  ", end="")
    for x in range(mapa.ancho):
        print(f" {x} ", end="")
    print()
    
    for y in range(mapa.alto):
        print(f"{y} ", end="")
        for x in range(mapa.ancho):
            if (x, y) == exp.posicion_actual:
                print(" @ ", end="")
            elif (x, y) in mapa.habitaciones:
                hab = mapa.habitaciones[(x, y)]
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
    print("\nleyenda: @ = tu | S = inicio | M = monstruo | J = jefe | T = tesoro")
    print("         E = evento | . = vacio | ? = no visitado | # = sin habitacion\n")


def juego_interactivo():
    # crea el mapa y explorador
    print("=== generador de dungeons ===\n")
    m = mapa(8, 6, seed=None)  # sin seed para mapas aleatorios
    m.generar_estructura(15)
    resumen = m.colocar_contenido()
    
    exp = explorador(m)
    
    print(f"mapa generado: {resumen}")
    print(f"posicion inicial: {exp.posicion_actual}\n")
    
    # loop principal
    jugando = True
    while jugando and exp.esta_vivo:
        # muestra estado simple
        print("\n" + "="*60)
        mostrar_minimapa_simple(m, exp)
        print(f"\nposicion: ({exp.posicion_actual[0]}, {exp.posicion_actual[1]})")
        print(f"vida: {exp.vida}")
        if exp.inventario:
            print(f"inventario: {', '.join([o.nombre for o in exp.inventario])}")
        else:
            print("inventario: vacio")
        
        # muestra habitacion actual
        hab = m.habitaciones.get(exp.posicion_actual)
        if hab:
            if hab.contenido:
                print(f"\ncontenido: {hab.contenido.tipo}")
            else:
                print("\nhabitacion vacia")
        
        # muestra direcciones disponibles
        direcciones = exp.obtener_habitaciones_adyacentes()
        print(f"\ndirecciones disponibles: {', '.join(direcciones)}")
        
        # pide comando
        print("\ncomandos: n/s/e/o (mover), explorar, inventario, mapa, salir")
        comando = input("> ").strip().lower()
        
        # procesa comando
        if comando in ['salir', 'quit', 'q']:
            jugando = False
            print("\nsaliendo del juego...")
        
        elif comando in ['n', 'norte']:
            if exp.mover('norte'):
                print("te mueves al norte")
            else:
                print("no puedes ir al norte")
        
        elif comando in ['s', 'sur']:
            if exp.mover('sur'):
                print("te mueves al sur")
            else:
                print("no puedes ir al sur")
        
        elif comando in ['e', 'este']:
            if exp.mover('este'):
                print("te mueves al este")
            else:
                print("no puedes ir al este")
        
        elif comando in ['o', 'oeste']:
            if exp.mover('oeste'):
                print("te mueves al oeste")
            else:
                print("no puedes ir al oeste")
        
        elif comando in ['explorar', 'x']:
            resultado = exp.explorar_habitacion()
            print(f"\n{resultado}")
            if not exp.esta_vivo:
                print("\n*** has muerto ***")
                jugando = False
        
        elif comando in ['inventario', 'i', 'inv']:
            if exp.inventario:
                print("\ninventario:")
                for i, obj in enumerate(exp.inventario):
                    print(f"  {i+1}. {obj.nombre} (valor: {obj.valor})")
            else:
                print("\ninventario vacio")
        
        elif comando in ['mapa', 'm']:
            mostrar_mapa_completo_simple(m, exp)
        
        elif comando in ['ayuda', 'h', 'help', '?']:
            print("\ncomandos:")
            print("  n/norte, s/sur, e/este, o/oeste - movimiento")
            print("  explorar/x - explorar habitacion")
            print("  inventario/i - ver items")
            print("  mapa/m - ver mapa completo")
            print("  ayuda/h - esta ayuda")
            print("  salir/q - salir")
        
        else:
            print(f"comando desconocido: {comando}")
            print("escribe 'ayuda' para ver comandos disponibles")
    
    # fin del juego
    print("\n" + "="*60)
    print("=== fin del juego ===")
    if exp.esta_vivo:
        print(f"sobreviviste con {exp.vida} puntos de vida")
    else:
        print("has muerto en el dungeon")
    print(f"items recogidos: {len(exp.inventario)}")
    valor_total = sum(obj.valor for obj in exp.inventario)
    print(f"valor total: {valor_total}")
    print("="*60)


if __name__ == "__main__":
    juego_interactivo()
