class objeto:
    # representa un objeto del juego: tesoro, equipamiento o consumible
    
    def __init__(self, nombre: str, valor: int = 0, descripcion: str = "", 
                 categoria: str = "normal", efecto: dict = None):
        self._datos = {
            "nombre": nombre,
            "valor": int(valor),
            "descripcion": descripcion,
            "categoria": categoria,
            "efecto": efecto if efecto else {}
        }
    
    @property
    def nombre(self) -> str:
        return self._datos["nombre"]
    
    @property
    def valor(self) -> int:
        return self._datos["valor"]
    
    @property
    def descripcion(self) -> str:
        return self._datos["descripcion"]
    
    @property
    def categoria(self) -> str:
        return self._datos["categoria"]
    
    @property
    def efecto(self) -> dict:
        return self._datos["efecto"]

    def to_dict(self) -> dict:
        return dict(self._datos)

    @staticmethod
    def from_dict(d: dict) -> "objeto":
        return objeto(
            d.get("nombre", "obj"),
            int(d.get("valor", 0)),
            d.get("descripcion", ""),
            d.get("categoria", "normal"),
            d.get("efecto"),
        )

    def __repr__(self):
        return f"objeto({self.nombre}, valor={self.valor})"
