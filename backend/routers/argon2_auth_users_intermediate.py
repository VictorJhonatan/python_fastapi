#argon2_auth_users_intermediate
"""
JWT Auth con FastAPI — Versión mejorada
=======================================
Mejoras aplicadas vs versión original:
  - pyjwt        en lugar de python-jose  (más mantenido, oficial)
  - pwdlib[argon2] en lugar de bcrypt     (Argon2id: ganador PHC 2015)
  - Argon2Hasher explícito               (parámetros tuneable)
  - datetime.now(timezone.utc)           (evita DeprecationWarning Python 3.12+)
  - Manejo de errores más detallado
  - Comentarios explicativos en cada sección

Instalación:
    pip install fastapi "uvicorn[standard]" pyjwt "pwdlib[argon2]"
"""
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt                                      # pip install pyjwt
from jwt.exceptions import InvalidTokenError    # reemplaza JWTError de python-jose y sirve excepción que salta si el token es inválido/expirado
from pwdlib import PasswordHash                 # pip install "pwdlib[argon2]" verificar contraseñas con Argon2
from pwdlib.hashers.argon2 import Argon2Hasher
from datetime import datetime, timedelta, timezone # calcular la expiración del token


# ── Configuración ────────────────────────────────────────────────────────────
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  #producción 30min  SECRET = os.getenv("JWT_SECRET")

#En producción guarda esto en una variable de entorno (.env)
# SECRET = os.getenv("JWT_SECRET")
SECRET = "be574619c9a15b1e65580155d8a79ec67606d837bd3c77795eb8e8cc122e07ba"

router = APIRouter(prefix="/argon2_auth_users_intermediate", tags=["argon2_auth_users_intermediate"], responses={404: {"message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="jwt_auth_users/login")


# ── Argon2id con pwdlib ──────────────────────────────────────────────────────
# Argon2Hasher usa Argon2id por defecto (variante más recomendada).
# Parámetros ajustables según tu servidor:
#   time_cost   → iteraciones CPU        (default: 3)
#   memory_cost → RAM en KiB             (default: 65536 = 64 MB)
#   parallelism → hilos paralelos        (default: 4)
#
# Más memory_cost = más difícil de atacar con GPUs (ventaja clave vs bcrypt)
pwd_hasher = PasswordHash([Argon2Hasher(
    time_cost=3,
    memory_cost=65536, # para atacar por fuerza bruta necesitas 64MB por intento, lo que hace inviable usar GPUs (que tienen poca RAM por núcleo). Bcrypt no tiene esto.
    parallelism=4,
)])


# ── Modelos ──────────────────────────────────────────────────────────────────
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserInDB(User):
    password: str

class UserUpdate(BaseModel):
    """Modelo específico para actualización (no expone el campo password)."""
    full_name: str
    email: str
    disabled: bool


# ── Base de datos simulada ───────────────────────────────────────────────────
# En producción los hashes ya vendrían almacenados desde el registro del usuario.
# Aquí se generan al iniciar la app solo para el ejemplo.
user_db = {
    "victor": {
        "username": "victor",
        "full_name": "Victor Robles",
        "email": "victor@victor.com",
        "disabled": False,
        "password": pwd_hasher.hash("12345"),
    },
    "analu": {
        "username": "ana",
        "full_name": "Ana García",
        "email": "ana@ana.com",
        "disabled": True,
        "password": pwd_hasher.hash("897452"),
    },
    "luis": {
        "username": "luis",
        "full_name": "Luis Martínez",
        "email": "luis@luis.com",
        "disabled": False,
        "password": pwd_hasher.hash("5674844"),
    },
}


# ── Helpers ──────────────────────────────────────────────────────────────────
def search_user(username: str) -> UserInDB | None:
    """Retorna el usuario CON contraseña (solo para verificación interna)."""
    if username in user_db:
        return UserInDB(**user_db[username])
    return None

def search_users(username: str) -> User | None:
    """Retorna el usuario SIN contraseña (para respuestas públicas)."""
    if username in user_db:
        return User(**user_db[username])
    return None

#nucleo de seguridad
# ── Dependencias JWT ─────────────────────────────────────────────────────────
async def auth_user(token: str = Depends(oauth2)) -> User:
    """Valida el token JWT y retorna el usuario asociado."""
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise exception
    except InvalidTokenError:   # cubre token expirado, firma inválida, etc.
        raise exception

    user = search_users(username)
    if user is None:
        raise exception
    return user


async def current_user(user: User = Depends(auth_user)) -> User:
    """Verifica que el usuario autenticado esté activo."""
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )
    return user


# ── Rutas ────────────────────────────────────────────────────────────────────
@router.post("/login", summary="Obtener token de acceso")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica al usuario y devuelve un JWT Bearer token.
    """
    if form.username not in user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es correcto",
        )

    user = search_user(form.username)

    # ✅ Verificación Argon2 — compara texto plano con hash almacenado
    if not pwd_hasher.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña incorrecta",
        )

    # ✅ timezone-aware datetime (evita DeprecationWarning en Python 3.12+)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": user.username, "exp": expire},
        SECRET,
        algorithm=ALGORITHM,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User, summary="Usuario autenticado actual")
async def me(user: User = Depends(current_user)):
    """Devuelve los datos del usuario que tiene sesión activa."""
    return user


@router.put("/users/put/{username}", response_model=dict, summary="Actualizar datos del usuario",)
async def put_users(
    username: str,
    user_data: UserUpdate,                   # ← modelo separado, más limpio
    current: User = Depends(current_user),   # solo usuarios autenticados
):
    """
    Actualiza full_name, email y disabled del usuario autenticado.
    Un usuario solo puede modificar su propio perfil.
    """
    if username != current.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este usuario",
        )

    if username not in user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # Actualiza solo los campos permitidos (la contraseña no se toca aquí)
    user_db[username]["full_name"] = user_data.full_name
    user_db[username]["email"]     = user_data.email
    user_db[username]["disabled"]  = user_data.disabled

    return {"message": "Usuario actualizado", "user": user_data}


@router.delete("/users/{username}", summary="Eliminar usuario")
async def delete_user(
    username: str,
    current: User = Depends(current_user),
):
    """
    Elimina al usuario autenticado.
    Un usuario solo puede eliminarse a sí mismo.
    """
    if username != current.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este usuario",
        )

    if username not in user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    del user_db[username]
    return {"message": f"Usuario '{username}' eliminado correctamente"}


"""
### 🔄 Flujo completo resumido
```
1. POST /login  →  usuario + contraseña  →  recibe JWT token
2. GET /me      →  Header: Bearer <token>  →  FastAPI valida → devuelve datos
3. PUT /put     →  Bearer <token> + JSON body  →  actualiza
4. DELETE       →  Bearer <token>  →  elimina
"""


"""
1️⃣ Framework → 2️⃣ Protocolo → 3️⃣ Token → 4️⃣ Seguridad de contraseñas

Entonces quedaría:

FastAPI → OAuth2 → JWT → Argon2"""


"""-------------------------------
Orden real en una API
Argon2 (hash de contraseña)
Propósito:
proteger la contraseña en la base de datos

Si hackean la DB → no ven la contraseña real.
-------------------------------------------
OAuth2 (protocolo de autenticación)
OAuth2PasswordBearer

Esto define cómo el cliente enviará el token.
------------------------------------------
JWT (token de autenticación) codifica y descodifica

Después del login exitoso se genera el JWT.

1️⃣Usuario se registra
   password → Argon2 → hash guardado en DB

2️⃣ Usuario hace login
   password → Argon2 verify

3️⃣ Si es correcto
   se genera JWT

4️⃣ Cliente guarda JWT

5️⃣ Cada request
   Authorization: Bearer JWT

6️⃣ FastAPI usa OAuth2 dependency
   para extraer el token

7️⃣ JWT se valida
   → usuario autenticado
"""