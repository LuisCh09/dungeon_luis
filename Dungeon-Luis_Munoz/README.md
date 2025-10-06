# generador de mapas de dungeon
*Luis Muñoz*
## descripcion
generador de dungeons procedurales con exploracion, combate y sistema de inventario.
## ejecucion
**demo automatica:**
```bash
python3 main.py
```
**juego interactivo:**
```bash
python3 juego_interactivo.py
```
### controles del juego interactivo
- `n/norte` - mover al norte
- `s/sur` - mover al sur  
- `e/este` - mover al este
- `o/oeste` - mover al oeste
- `explorar/x` - explorar habitacion actual
- `inventario/i` - ver tu inventario
- `mapa/m` - ver el mapa completo
- `ayuda/h` - ver comandos disponibles
- `salir/q` - salir del juego
## estructura
- `dungeon_generator/` - paquete principal
  - `content.py` - tipos de contenido: tesoros, monstruos, jefes, eventos
  - `player.py` - logica del jugador y movimiento
  - `room.py` - estructura de habitaciones
  - `mapa.py` - generacion procedural de mapas
  - `items.py` - sistema de objetos e items
  - `save.py` - guardado y carga de partidas
  - `display.py` - visualizacion con rich
- `main.py` - demo del juego
- `juego_interactivo.py` - juego jugable con controles


Este programa fue creado con 5 energeticas, contrareloj y muchas paginas de phyton abiertas. Disculpen si hay cosas desordenadas y que les guste mucho <3.
