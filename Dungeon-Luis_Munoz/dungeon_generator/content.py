from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import random
from .items import objeto


class contenido_habitacion(ABC):
    @property
    @abstractmethod
    def descripcion(self) -> str:
        ...

    @property
    @abstractmethod
    def tipo(self) -> str:
        ...

    @abstractmethod
    def interactuar(self, explorador) -> str:
        ...

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        ...

    @staticmethod
    @abstractmethod
    def from_dict(d: Dict[str, Any]) -> "contenido_habitacion":
        ...

class tesoro(contenido_habitacion):
    def __init__(self, recompensa: objeto):
        self.recompensa = recompensa

    @property
    def descripcion(self) -> str:
        return f"un tesoro: {self.recompensa.nombre} valor {self.recompensa.valor}"

    @property
    def tipo(self) -> str:
        return "tesoro"

    def interactuar(self, explorador) -> str:
        explorador.inventario.append(self.recompensa)
        return f"recogiste: {self.recompensa.nombre} valor {self.recompensa.valor}"

    def to_dict(self) -> Dict[str, Any]:
        return {"tipo": self.tipo, "recompensa": self.recompensa.to_dict()}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "tesoro":
        obj = objeto.from_dict(d["recompensa"])
        return tesoro(obj)


class monstruo(contenido_habitacion):
    def __init__(self, nombre: str, vida: int, ataque: int):
        self.nombre = nombre
        self.vida = int(vida)
        self.ataque = int(ataque)

    @property
    def descripcion(self) -> str:
        return f"monstruo {self.nombre} vida {self.vida} atq {self.ataque}"

    @property
    def tipo(self) -> str:
        return "monstruo"

    def interactuar(self, explorador) -> str:
        log = []
        vida_enemigo = self.vida
        vida_jugador = explorador.vida
        turno = random.choice([0, 1])
        log.append(f"comienza combate contra {self.nombre} vida: {vida_enemigo}")
        
        while vida_enemigo > 0 and vida_jugador > 0:
            if turno == 0:
                danio = random.randint(1, 2)
                vida_enemigo -= danio
                log.append(f"atacas y haces {danio} de dano enemigo {max(0, vida_enemigo)} pv")
                turno = 1
            else:
                danio = random.randint(1, self.ataque)
                vida_jugador -= danio
                explorador.recibir_dano(danio)
                log.append(f"{self.nombre} te golpea por {danio} tus pv {max(0, vida_jugador)}")
                turno = 0

        self.vida = max(0, vida_enemigo)
        if self.vida <= 0 and explorador.vida > 0:
            log.append(f"derrotaste a {self.nombre}")
        elif explorador.vida <= 0:
            log.append("fuiste derrotado")
        return "\n".join(log)

    def to_dict(self) -> Dict[str, Any]:
        return {"tipo": self.tipo, "nombre": self.nombre, "vida": self.vida, "ataque": self.ataque}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "monstruo":
        return monstruo(d["nombre"], int(d["vida"]), int(d["ataque"]))


class jefe(monstruo):
    def __init__(self, nombre: str, vida: int, ataque: int, recompensa_especial: objeto):
        super().__init__(nombre, vida, ataque)
        self.recompensa_especial = recompensa_especial

    @property
    def tipo(self) -> str:
        return "jefe"

    def interactuar(self, explorador) -> str:
        log = []
        vida_jugador = explorador.vida
        vida_enemigo = self.vida
        turno = 0 if random.random() < 0.35 else 1
        log.append(f"enfrentas al jefe {self.nombre} vida: {vida_enemigo}")
        
        while vida_enemigo > 0 and vida_jugador > 0:
            if turno == 0:
                danio = random.randint(1, 2 + int(self.ataque/2))
                vida_enemigo -= danio
                log.append(f"atacas y haces {danio} de dano enemigo {max(0, vida_enemigo)} pv")
                turno = 1
            else:
                danio = random.randint(1, self.ataque)
                vida_jugador -= danio
                explorador.recibir_dano(danio)
                log.append(f"{self.nombre} te golpea por {danio} tus pv {max(0, vida_jugador)}")
                turno = 0

        self.vida = max(0, vida_enemigo)
        if self.vida <= 0 and explorador.vida > 0:
            explorador.inventario.append(self.recompensa_especial)
            log.append(f"derrotaste al jefe {self.nombre} y obtienes {self.recompensa_especial.nombre}")
        elif explorador.vida <= 0:
            log.append("fuiste derrotado por el jefe")
        return "\n".join(log)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"recompensa_especial": self.recompensa_especial.to_dict()})
        base["tipo"] = self.tipo
        return base

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "jefe":
        recompensa = objeto.from_dict(d["recompensa_especial"])
        return jefe(d["nombre"], int(d["vida"]), int(d["ataque"]), recompensa)

class evento(contenido_habitacion):
    def __init__(self, nombre: str, descripcion: str, efecto: Dict[str, Any]):
        self.nombre = nombre
        self._descripcion = descripcion
        self.efecto = efecto  

    @property
    def descripcion(self) -> str:
        return f"{self.nombre}: {self._descripcion}"

    @property
    def tipo(self) -> str:
        return "evento"

    def interactuar(self, explorador) -> str:
        tipo_efecto = self.efecto.get("tipo")
        if tipo_efecto == "curar":
            amount = int(self.efecto.get("valor", 1))
            explorador.vida += amount
            return f"fuente: recuperas {amount} pv"
        elif tipo_efecto == "trampa":
            amount = int(self.efecto.get("valor", 1))
            explorador.recibir_dano(amount)
            return f"trampa: recibes {amount} de dano"
        elif tipo_efecto == "portal":
            return "portal: te teletransportas a otra habitacion"
        elif tipo_efecto == "buff":
            return f"bonificacion temporal: {self.efecto.get('detalle', '')}"
        return "evento misterioso"

    def to_dict(self) -> Dict[str, Any]:
        return {"tipo": self.tipo, "nombre": self.nombre, "descripcion": self._descripcion, "efecto": self.efecto}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "evento":
        return evento(d["nombre"], d.get("descripcion", ""), d.get("efecto", {}))


def contenido_from_dict(d: Dict[str, Any]) -> contenido_habitacion:
    tipo = d.get("tipo")
    if tipo == "tesoro":
        return tesoro.from_dict(d)
    elif tipo == "monstruo":
        return monstruo.from_dict(d)
    elif tipo == "jefe":
        return jefe.from_dict(d)
    elif tipo == "evento":
        return evento.from_dict(d)
    raise ValueError(f"tipo de contenido desconocido: {tipo}")
