import json
from typing import Tuple
from .mapa import mapa
from .player import explorador
from .content import contenido_from_dict
from .items import objeto
from pathlib import Path


def guardar_partida(m: mapa, exp: explorador, archivo: str) -> None:
    # guarda el estado completo del juego en json
    # serializa inventario ignorando elementos none
    inventario_serializado = []
    for obj in exp.inventario:
        if obj is None:
            continue
        inventario_serializado.append(obj.to_dict())

    data = {
        "mapa": m.to_dict(),
        "explorador": {
            "vida": exp.vida,
            "posicion": list(exp.posicion_actual),
            "inventario": inventario_serializado
        }
    }
    p = Path(archivo)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def cargar_partida(archivo: str) -> Tuple[mapa, explorador]:
    # carga partida desde json y reconstruye mapa y explorador
    # retorna tupla (mapa, explorador)
    p = Path(archivo)
    text = p.read_text(encoding="utf-8")
    data = json.loads(text)

    mapa_dict = data["mapa"]
    m = mapa.from_dict(mapa_dict)

    for h in mapa_dict.get("habitaciones", []):
        cont = h.get("contenido")
        if cont is not None:
            coord = tuple(h["pos"])
            if coord in m.habitaciones:
                try:
                    m.habitaciones[coord].contenido = contenido_from_dict(cont)
                except Exception:
                    m.habitaciones[coord].contenido = None

    exp_data = data.get("explorador", {})
    posicion = tuple(exp_data.get("posicion", m.habitacion_inicial.pos))
    exp = explorador(m, posicion=posicion, vida=int(exp_data.get("vida", 5)))

    invent = []
    for o in exp_data.get("inventario", []):
        try:
            invent.append(objeto.from_dict(o))
        except Exception:
            continue
    exp.inventario = invent

    return m, exp
