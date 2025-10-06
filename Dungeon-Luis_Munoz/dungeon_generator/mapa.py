from __future__ import annotations
import random
from typing import Dict, Tuple, List, Optional
from .room import habitacion
from collections import deque
import math
from .content import tesoro, monstruo, jefe, evento, contenido_from_dict
from .items import objeto

def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

class mapa:
    def __init__(self, ancho: int, alto: int, seed: Optional[int] = None):
        if ancho <= 0 or alto <= 0:
            raise ValueError("ancho y alto deben ser positivos")
        self.ancho = ancho
        self.alto = alto
        self.habitaciones: Dict[Tuple[int, int], habitacion] = {}
        self.habitacion_inicial: Optional[habitacion] = None
        self._next_id = 0
        if seed is not None:
            random.seed(seed)

    def _coords_en_borde(self) -> List[Tuple[int, int]]:
        bordes = []
        for x in range(self.ancho):
            bordes.append((x, 0))
            bordes.append((x, self.alto - 1))
        for y in range(self.alto):
            bordes.append((0, y))
            bordes.append((self.ancho - 1, y))
        return list(dict.fromkeys(bordes))

    def generar_estructura(self, n_habitaciones: int):
        # genera habitaciones conectadas usando algoritmo recursivo
        self._validar_parametros(n_habitaciones)
        self._inicializar_mapa()
        self._crear_habitacion_inicial()
        self._expandir_mapa(n_habitaciones)
        self._verificar_mapa()
    
    def _validar_parametros(self, n: int):
        if n <= 0:
            raise ValueError("n_habitaciones debe ser >= 1")
        if n > self.ancho * self.alto:
            raise ValueError("demasiadas habitaciones para el tamano del mapa")
    
    def _inicializar_mapa(self):
        self.habitaciones.clear()
        self._next_id = 0
    
    def _crear_habitacion_inicial(self):
        bordes = self._coords_en_borde()
        coord = random.choice(bordes)
        self.habitacion_inicial = habitacion(self._next_id, coord, inicial=True)
        self.habitaciones[coord] = self.habitacion_inicial
        self._next_id += 1
    
    def _expandir_mapa(self, objetivo: int):
        # usa cola para expansion por niveles
        deltas = {"norte": (0, -1), "sur": (0, 1), "este": (1, 0), "oeste": (-1, 0)}
        cola = [self.habitacion_inicial]
        
        while self._next_id < objetivo and cola:
            actual = random.choice(cola)
            expandio = False
            
            # intenta agregar vecino
            vecinos = self._obtener_vecinos_libres(actual, deltas)
            if vecinos:
                dir_name, coord = random.choice(vecinos)
                nueva = self._crear_y_conectar(actual, dir_name, coord)
                cola.append(nueva)
                expandio = True
                
                # conexiones extras
                if random.random() < 0.3:
                    self._conectar_vecinos_existentes(nueva, deltas)
            
            if not expandio:
                cola.remove(actual)
    
    def _obtener_vecinos_libres(self, hab: habitacion, deltas: dict) -> List:
        vecinos = []
        for dir_name, (dx, dy) in deltas.items():
            nx, ny = hab.pos[0] + dx, hab.pos[1] + dy
            coord = (nx, ny)
            if self._coord_valida(coord) and coord not in self.habitaciones:
                vecinos.append((dir_name, coord))
        return vecinos
    
    def _coord_valida(self, coord: Tuple[int, int]) -> bool:
        return 0 <= coord[0] < self.ancho and 0 <= coord[1] < self.alto
    
    def _crear_y_conectar(self, origen: habitacion, direccion: str, coord: Tuple[int, int]) -> habitacion:
        nueva = habitacion(self._next_id, coord)
        self._next_id += 1
        origen.conectar(direccion, nueva)
        self.habitaciones[coord] = nueva
        return nueva
    
    def _conectar_vecinos_existentes(self, hab: habitacion, deltas: dict):
        for dir_name, (dx, dy) in deltas.items():
            coord = (hab.pos[0] + dx, hab.pos[1] + dy)
            if coord in self.habitaciones:
                vecino = self.habitaciones[coord]
                if vecino.pos != hab.pos and dir_name not in hab.conexiones:
                    try:
                        hab.conectar(dir_name, vecino)
                    except:
                        pass
    
    def _verificar_mapa(self):
        if len(self.habitaciones) == 0:
            raise RuntimeError("no se pudieron colocar todas las habitaciones")
        if not self.es_todo_accesible():
            raise RuntimeError("mapa generado no es accesible")



    def es_todo_accesible(self) -> bool:
        # verifica que todas las habitaciones sean accesibles desde el inicio
        if not self.habitacion_inicial:
            return False
        
        visitados = set([self.habitacion_inicial.pos])
        pendientes = [self.habitacion_inicial]
        
        while pendientes:
            actual = pendientes.pop()
            for vecino in actual.conexiones.values():
                if vecino.pos not in visitados:
                    visitados.add(vecino.pos)
                    pendientes.append(vecino)
        
        return len(visitados) == len(self.habitaciones)

    def imprimir_ascii(self) -> str:
        # representacion ascii del mapa
        grid = [["  " for _ in range(self.ancho)] for _ in range(self.alto)]
        for (x, y), hab in self.habitaciones.items():
            mark = f"{hab.id:02d}"
            if hab.inicial:
                mark = "S "
            grid[y][x] = mark

        lines = []
        for y in range(self.alto):
            lines.append(" ".join(grid[y]))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        # serializa el mapa a diccionario
        return {
            "ancho": self.ancho,
            "alto": self.alto,
            "habitaciones": [hab.to_dict() for hab in self.habitaciones.values()],
            "inicio": list(self.habitacion_inicial.pos) if self.habitacion_inicial else None
        }

    @staticmethod
    def from_dict(d: dict) -> "mapa":
        # reconstruye mapa desde diccionario
        m = mapa(d["ancho"], d["alto"])
        for h in d["habitaciones"]:
            hab = habitacion.from_dict(h)
            m.habitaciones[tuple(hab.pos)] = hab
            m._next_id = max(m._next_id, hab.id + 1)
        for h in d["habitaciones"]:
            coord = tuple(h["pos"])
            hab_obj = m.habitaciones[coord]
            for dir_, coord_other in h.get("conexiones", {}).items():
                coord_other_t = tuple(coord_other)
                if coord_other_t in m.habitaciones:
                    otra = m.habitaciones[coord_other_t]
                    if dir_ not in hab_obj.conexiones:
                        hab_obj.conectar(dir_, otra)
        inicio_coord = d.get("inicio")
        if inicio_coord:
            m.habitacion_inicial = m.habitaciones[tuple(inicio_coord)]
        return m

    def __repr__(self):
        return f"mapa({self.ancho}x{self.alto}, habitaciones={len(self.habitaciones)})"
    
    def colocar_contenido(self, seed: Optional[int] = None) -> dict:
        # distribuye contenido usando generadores y comprehensions
        if seed is not None:
            random.seed(seed)

        if len(self.habitaciones) <= 1:
            return self._stats_vacios()
        
        inicio = tuple(self.habitacion_inicial.pos)
        disponibles = [c for c in self.habitaciones.keys() if c != inicio]
        random.shuffle(disponibles)
        
        stats = self._distribuir_contenido(disponibles, inicio)
        return stats
    
    def _stats_vacios(self) -> dict:
        return {"jefes": 0, "monstruos": 0, "tesoros": 0, "eventos": 0}
    
    def _calcular_cantidades(self, total: int) -> dict:
        return {
            "jefes": 1,
            "monstruos": max(1, int(total * 0.25)),
            "tesoros": max(1, int(total * 0.20)),
            "eventos": max(0, int(total * 0.08))
        }
    
    def _distribuir_contenido(self, coords: List, origen: Tuple[int, int]) -> dict:
        cantidades = self._calcular_cantidades(len(coords))
        stats = {k: 0 for k in cantidades.keys()}
        idx = 0
        
        # genera contenido por tipo
        generadores = {
            "jefes": self._generar_jefe,
            "monstruos": self._generar_monstruo,
            "tesoros": self._generar_tesoro,
            "eventos": self._generar_evento
        }
        
        for tipo, cantidad in cantidades.items():
            for _ in range(cantidad):
                if idx >= len(coords):
                    break
                coord = coords[idx]
                distancia = manhattan(coord, origen)
                contenido = generadores[tipo](distancia)
                self.habitaciones[coord].contenido = contenido
                stats[tipo] += 1
                idx += 1
        
        return stats
    
    def _generar_jefe(self, dist: int) -> jefe:
        return jefe(
            f"jefe nivel {dist}",
            vida=8 + dist,
            ataque=3 + dist // 3,
            recompensa_especial=objeto(f"tesoro jefe", valor=50 + dist * 5, 
                                      descripcion="recompensa de jefe")
        )
    
    def _generar_monstruo(self, dist: int) -> monstruo:
        return monstruo(
            f"monstruo nivel {dist}",
            vida=5 + dist // 2,
            ataque=1 + dist // 4
        )
    
    def _generar_tesoro(self, dist: int) -> tesoro:
        obj = objeto(f"gema nivel {dist}", valor=10 + dist * 2, descripcion="tesoro")
        return tesoro(obj)
    
    def _generar_evento(self, dist: int) -> evento:
        tipos = {
            "trampa": lambda: evento("trampa", "una trampa", {"tipo": "trampa", "valor": 2}),
            "fuente": lambda: evento("fuente", "restaura vida", {"tipo": "curar", "valor": 2}),
            "portal": lambda: evento("portal", "teletransportador", {"tipo": "portal"})
        }
        tipo = random.choice(list(tipos.keys()))
        return tipos[tipo]()
    def obtener_estadisticas_mapa(self) -> dict:
        # retorna estadisticas del mapa: total habitaciones, tipos de contenido
        # y promedio de conexiones
        total = len(self.habitaciones)
        conteos = {"vacios": 0, "tesoros": 0, "monstruos": 0, "jefes": 0, "eventos": 0}
        suma_conex = 0
        for hab in self.habitaciones.values():
            suma_conex += len(hab.conexiones)
            if hab.contenido is None:
                conteos["vacios"] += 1
            else:
                t = getattr(hab.contenido, "tipo", None)
                if t == "tesoro":
                    conteos["tesoros"] += 1
                elif t == "monstruo":
                    conteos["monstruos"] += 1
                elif t == "jefe":
                    conteos["jefes"] += 1
                elif t == "evento":
                    conteos["eventos"] += 1
                else:
                    conteos["vacios"] += 1
        promedio = (suma_conex / total) if total > 0 else 0.0
        resumen = {"Total de habitaciones": total, **conteos, "promedio_conexiones": round(promedio, 2)}
        return resumen