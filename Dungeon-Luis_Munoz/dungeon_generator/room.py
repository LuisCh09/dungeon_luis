from __future__ import annotations
from typing import Dict, Optional, Tuple, List
from .content import contenido_habitacion  


class habitacion:
    # direcciones opuestas como constante de clase
    DIRECCIONES = {"norte": "sur", "sur": "norte", "este": "oeste", "oeste": "este"}
    
    def __init__(self, id: int, pos: Tuple[int, int], inicial: bool = False):
        self.id: int = id
        self.pos: Tuple[int, int] = (int(pos[0]), int(pos[1]))
        self.inicial: bool = inicial
        self.contenido: Optional[contenido_habitacion] = None
        self._conexiones: Dict[str, "habitacion"] = {}
        self.visitada: bool = False
    
    @property
    def conexiones(self) -> Dict[str, "habitacion"]:
        return self._conexiones

    @property
    def x(self) -> int:
        return self.pos[0]

    @property
    def y(self) -> int:
        return self.pos[1]

    def conectar(self, direccion: str, otra: "habitacion"):
        # conecta dos habitaciones bidireccionalmente
        if direccion not in self.DIRECCIONES:
            raise ValueError(f"direccion invalida: {direccion}")
        self._conexiones[direccion] = otra
        otra._conexiones[self.DIRECCIONES[direccion]] = self

    def desconectar(self, direccion: str):
        # desconecta dos habitaciones
        if direccion in self._conexiones:
            otra = self._conexiones.pop(direccion)
            opp = self.DIRECCIONES[direccion]
            if opp in otra._conexiones and otra._conexiones[opp] is self:
                otra._conexiones.pop(opp)
    
    def vecinos_disponibles(self) -> List[str]:
        # retorna lista de direcciones con conexiones
        return list(self._conexiones.keys())

    def posiciones_vecinas(self) -> Dict[str, Tuple[int, int]]:
        x, y = self.pos
        return {
            "norte": (x, y - 1),
            "sur": (x, y + 1),
            "este": (x + 1, y),
            "oeste": (x - 1, y),
        }

    def to_dict(self) -> dict:
        conexiones_coords = {dir_: [hab.x, hab.y] for dir_, hab in self._conexiones.items()}
        contenido_dict = self.contenido.to_dict() if self.contenido is not None else None
        return {
            "id": self.id,
            "pos": [self.x, self.y],
            "inicial": self.inicial,
            "visitada": self.visitada,
            "conexiones": conexiones_coords,
            "contenido": contenido_dict
        }

    @staticmethod
    def from_dict(d: dict) -> "habitacion":
        pos = tuple(d["pos"])
        hab = habitacion(d["id"], pos, d.get("inicial", False))
        hab.visitada = d.get("visitada", False)
        return hab

    def __repr__(self):
        return f"habitacion(id={self.id}, pos=({self.x},{self.y}), inicial={self.inicial})"
