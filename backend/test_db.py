
from db.client import  users  # importas la users ya creada

# al insertar → BD se crea sola
"""users.insert_one(
    {"username": "Marior", 
     "email": "mario@test.com"})
print("✅ Usuario insertado - BD testing creada!")
"""

"""
## Resultado es el mismo en ambas:
```
Cluster1
  └── testing        ← BD creada
        └── users    ← colección creada
        """


"""
Filas son horizontales ↔️
        nombre    |   email           |  edad
        ──────────────────────────────────────
fila 1: Victor    | victor@test.com   |  25       ← horizontal
fila 2: Maria     | maria@test.com    |  30       ← horizontal
fila 3: Juan      | juan@test.com     |  22       ← horizontal

"""

"""
Columnas son verticales ↕️
        nombre    |   email           |  edad
        ──────────────────────────────────────
        Victor    | victor@test.com   |  25
        Maria     | maria@test.com    |  30
        Juan      | juan@test.com     |  22
           ↕️            ↕️               ↕️
        columna      columna          columna
        """

"""
En MongoDB es lo mismo:
Fila horizontal    →  Documento  { "nombre": "Victor", "email": "...", "edad": 25 }
Columna vertical   →  Campo      "nombre", "email", "edad"

"""