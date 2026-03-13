from fastapi import Depends, APIRouter, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt # pyjwt # InvalidTokenError
from pwdlib import PasswordHash
from datetime import datetime, timedelta

#PasswordHash.recommended()  GENERICO
pwd_context = PasswordHash.recommended() 
#este  PasswordHash([Argon2Hasher()]) puedes tunear time_cost, memory_cost, parallelism
#control total sobre los parámetros de Argon2.


#Usas preflix Mantiene tu estructura original
router = APIRouter(prefix="/argon2_auth_users", tags=["argon2_auth_users"], responses={404: {"message": "No encontrado"}}) 

oauth2 = OAuth2PasswordBearer(tokenUrl="argon2_auth_users/login")

ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 5

SECRET = "3530c50dba6bec2a5378eee6c7c00f287582b5279153b2dfaced2f54221e64f4"

class User(BaseModel):
    username: str
    full_name : str
    email: str
    disabled: bool

class UserInDB(User):
    password: str

# ── Base de datos simulada ───────────────────────────────────────────────────
# Hashes generados con:  pwd_hasher.hash("1234")  (Argon2id)
user_db = {

    "victor": {
        "username": "victor",
        "full_name": "Victor Robles",
        "email": "victor@victor.com",
        "disabled": False, 
        "password": pwd_context.hash("12345")
    },

    "analu": {
        "username": "ana",
        "full_name": "Ana García",
        "email": "ana@ana.com",
        "disabled": True,
        "password": pwd_context.hash("897452")
    },

    "luis": {
        "username": "luis",
        "full_name": "Luis Martínez",
        "email": "luis@luis.com",
        "disabled": False,
        "password": pwd_context.hash("5674844")
    }
}

# ── Helpers ──────────────────────────────────────────────────────────────────
def search_user(username: str):
    if username in user_db:
        return UserInDB(**user_db[username]) 
    
#fun sin la contraseña
def search_users(username: str):
    if username in user_db:
        return User(**user_db[username])

# ── Dependencias JWT ─────────────────────────────────────────────────────────
async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="credenciales  de autenticación inválidas", 
            headers={"WWW-Authenticate": "Bearer"})
    
    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub") 
        if username is None:
            raise exception
    
    except JWTError:
        raise exception
    
    return search_users(username)

async def current_user(user: User = Depends(auth_user)): 
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return user
    
# ── Rutas ────────────────────────────────────────────────────────────────────
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    users_db = user_db.get(form.username)
    if not users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    user = search_user(form.username)

    if not pwd_context.verify(form.password, user.password): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña incorrecta")
    
    acces_token = {"sub": user.username, 
                   "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)} 
    #datetime.utcnow() Deprecado en Python 3.12+
    #MEJOR: datetime.now(timezone.utc) Correcto y moderno
    
    return {"access_token": jwt.encode(acces_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user


@router.put("/users/put/{username}")
async def putusers(username: str, user: User, current: User = Depends(current_user)): # current --> Solo usuarios autenticados puedan usar este endpoint.
    
    if username != current.username:  
        raise HTTPException(status_code=403, detail="Usuario incorrecto")
    
    if username not in user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_db[username]["full_name"] = user.full_name
    user_db[username]["email"] = user.email
    user_db[username]["disabled"] = user.disabled
    return {"message": "Usuario actualizado", "user": user}

@router.delete("/users/{username}")
async def delete_user(username: str, current: User = Depends(current_user)):

    if username != current.username: 
        raise HTTPException(status_code=403, detail="Usuario incorrecto")

    if username not in user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    del user_db[username]

    return {"message": "Usuario eliminado"}


"""
Argon2 ganó la Password Hashing 
Competition en 2015. Sus ventajas 
principales son que puede usar
 memoria RAM además de CPU 
 (lo que lo hace resistente a 
 ataques con hardware especializado 
 como GPUs/ASICs), tiene tres variantes 
 (Argon2i, Argon2d, Argon2id — la recomendada), 
 y permite configurar memoria, iteraciones 
 y paralelismo por separado."""