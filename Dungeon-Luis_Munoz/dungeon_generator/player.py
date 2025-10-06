from __future__ import annotations
from typing import Tuple, List, Optional, Dict
from collections import deque
from .mapa import mapa
from .room import habitacion
from .content import tesoro, monstruo, jefe, evento
import random

class explorador:
    def __init__(self, m: mapa, posicion: Optional[Tuple[int,int]] = None, vida: int = 5, ataque_base: int = 1):
        self.mapa = m
        if posicion is None:
            inicial = m.habitacion_inicial
            if inicial is None:
                raise ValueError("el mapa no tiene habitacion inicial definida")
            self.posicion_actual = tuple(inicial.pos)
        else:
            self.posicion_actual = tuple(posicion)
        self.vida = int(vida)
        self.ataque_base = int(ataque_base)
        self.inventario: List = []
        self.equipado: Dict[str, Optional[object]] = {}  
        self.buffs: List[dict] = []  

    @property
    def esta_vivo(self) -> bool:
        return self.vida > 0

    def recibir_dano(self, cantidad: int):
        cantidad = int(cantidad)
        self.vida = max(0, self.vida - cantidad)

    def calcular_ataque(self) -> int:
        # calcula ataque total incluyendo equipamiento y buffs
        total = int(self.ataque_base)
        for obj in (self.equipado or {}).values():
            if obj:
                eff = getattr(obj, "efecto", {}) or {}
                total += int(eff.get("ataque", 0))
        for b in (self.buffs or []):
            total += int(b.get("ataque", 0))
        return max(1, total)

    def equipar(self, objeto) -> str:
        # equipa un objeto en el slot correspondiente
        if getattr(objeto, "categoria", "") != "equipable":
            return "ese objeto no es equipable"
        eff = getattr(objeto, "efecto", {}) or {}
        slot = eff.get("slot", "ring")
        prev = self.equipado.get(slot)
        self.equipado[slot] = objeto
        if objeto in self.inventario:
            self.inventario.remove(objeto)
        if prev:
            self.inventario.append(prev)
            return f"has equipado {objeto.nombre}, {prev.nombre} devuelto al inventario"
        return f"has equipado {objeto.nombre} en slot {slot}"

    def usar(self, objeto) -> str:
        # usa un objeto consumible del inventario
        if objeto not in self.inventario:
            return "no tienes ese objeto"
        if getattr(objeto, "categoria", "") != "consumible":
            return "ese objeto no es consumible"
        eff = getattr(objeto, "efecto", {}) or {}
        modo = eff.get("modo", "permanente")
        
        if "ataque" in eff:
            val = int(eff.get("ataque", 0))
            if modo == "permanente":
                self.ataque_base += val
                self.inventario.remove(objeto)
                return f"has usado {objeto.nombre}, ataque base +{val}"
            elif modo == "temporal_habitaciones":
                dur = int(eff.get("habitaciones", 1))
                self.buffs.append({"ataque": val, "restante_habitaciones": dur})
                self.inventario.remove(objeto)
                return f"has usado {objeto.nombre}, +{val} ataque por {dur} habitaciones"
       
        if eff.get("tipo") == "curar":
            amt = int(eff.get("valor", 1))
            self.vida += amt
            self.inventario.remove(objeto)
            return f"has usado {objeto.nombre} y recuperas {amt} pv"
      
        self.inventario.remove(objeto)
        return f"has usado {objeto.nombre}"

    def obtener_habitaciones_adyacentes(self) -> List[str]:
        hab = self.mapa.habitaciones.get(tuple(self.posicion_actual))
        if not hab:
            return []
        return list(hab.conexiones.keys())

    def mover(self, direccion: str) -> bool:
        # mueve el explorador en una direccion si hay conexion
        hab = self.mapa.habitaciones.get(tuple(self.posicion_actual))
        if not hab or direccion not in hab.conexiones:
            return False
        
        otra = hab.conexiones[direccion]
        self.posicion_actual = tuple(otra.pos)
        otra.visitada = True
        
        # actualiza duracion de buffs temporales
        nuevos = []
        for b in (self.buffs or []):
            b["restante_habitaciones"] -= 1
            if b["restante_habitaciones"] > 0:
                nuevos.append(b)
        self.buffs = nuevos
        return True

    def explorar_habitacion(self) -> str:
        # explora la habitacion actual e interactua con su contenido
        hab = self.mapa.habitaciones.get(tuple(self.posicion_actual))
        if not hab:
            return "no hay habitacion en tu posicion"
        if hab.visitada and hab.contenido is None:
            return "ya visitaste esta habitacion y esta vacia"
        if hab.contenido is None:
            hab.visitada = True
            return "la habitacion esta vacia"
        
        contenido = hab.contenido
        resultado = contenido.interactuar(self)
        
        # limpia contenido si fue usado
        if isinstance(contenido, (tesoro, evento)):
            hab.contenido = None
        elif isinstance(contenido, (monstruo, jefe)):
            if getattr(contenido, "vida", 1) <= 0:
                hab.contenido = None
        
        hab.visitada = True
        return resultado

    def encontrar_camino(self, destino: Tuple[int,int]) -> list:
        start = tuple(self.posicion_actual)
        if start == destino:
            return []
        q = deque([start])
        prev = {start: None}
        while q:
            cur = q.popleft()
            hab = self.mapa.habitaciones[cur]
            for dir_name, otra in hab.conexiones.items():
                coord = tuple(otra.pos)
                if coord not in prev:
                    prev[coord] = (cur, dir_name)
                    if coord == destino:
                        path = []
                        node = coord
                        while prev[node] is not None:
                            pcoord, pdirection = prev[node]
                            path.append((pdirection, node))
                            node = pcoord
                        path.reverse()
                        return path
                    q.append(coord)
        return []

    def mover_hasta(self, destino: Tuple[int,int]) -> bool:
        # mueve el explorador hasta el destino explorando en el camino
        path = self.encontrar_camino(destino)
        if not path:
            return False
        
        for direccion, coord in path:
            if not self.esta_vivo or not self.mover(direccion):
                return False
            hab = self.mapa.habitaciones.get(tuple(self.posicion_actual))
            if hab and hab.contenido is not None:
                print(self.explorar_habitacion())
                if not self.esta_vivo:
                    return False
        return True

    def __repr__(self):
        return f"explorador(pos={self.posicion_actual}, vida={self.vida}, ataque={self.calcular_ataque()}, items={len(self.inventario)})"
