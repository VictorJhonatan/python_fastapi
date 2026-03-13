from fastapi import Depends, APIRouter, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta

router = APIRouter(prefix="/jwt_auth_users", tags=["jwt_auth_users"], responses={404: {"message": "No encontrado"}}) 

oauth2 = OAuth2PasswordBearer(tokenUrl="jwt_auth_users/login")

ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 1

SECRET = "3530c50dba6bec2a5378eee6c7c00f287582b5279153b2dfaced2f54221e64f4"

class User(BaseModel):
    username: str
    full_name : str
    email: str
    disabled: bool

class UserInDB(User):
    password: str

user_db = {

    "victor": {
        "username": "victor",
        "full_name": "Victor Robles",
        "email": "victor@victor.com",
        "disabled": False, 
        "password": "$2a$12$JElUWHY3N3x.sWwfA2rQoe5ojfI4iOBCT/Q7sN6/ciL/VjKLCd4P2" # 12345
    },

    "analu": {
        "username": "ana",
        "full_name": "Ana García",
        "email": "ana@ana.com",
        "disabled": True,
        "password": "$2a$12$Bsm.FcCFK3FVr1V9a5W54.mAZnpS1ItOa32gFpF7e/JHgGKa5R0Na" #897452
    },

    "luis": {
        "username": "luis",
        "full_name": "Luis Martínez",
        "email": "luis@luis.com",
        "disabled": False,
        "password": "$2a$12$P8Yb2Pbi4wqFBBzZgwEtheJYXS.mMtEo/sKPYsDRKlMljQOBrMG22" #5674844
    }
}

def search_user(username: str):
    if username in user_db:
        return UserInDB(**user_db[username]) 
    
#fun sin la contraseña
def search_users(username: str):
    if username in user_db:
        return User(**user_db[username])

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
    

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    users_db = user_db.get(form.username)
    if not users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    user = search_user(form.username)

    if not bcrypt.checkpw(form.password.encode("utf-8"), user.password.encode("utf-8")): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña incorrecta")
    
    acces_token = {"sub": user.username, 
                   "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)} 
    
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
OAuth2 define el flujo → el usuario manda usuario y contraseña al endpoint /login

JWT es el token que se devuelve → firmado con tu SECRET y verificado con bcrypt

Cada endpoint protegido con Depends(current_user) exige ese token válido
"""

""" JWT (JSON Web Token)
Es un token (cadena de texto cifrada) 
que se genera cuando el usuario inicia 
sesión. Contiene información del usuario 
y tiene una fecha de expiración. 
En tu código se ve aquí:

acces_token = {"sub": user.username, 
               "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}

return {"access_token": jwt.encode(acces_token, SECRET, algorithm=ALGORITHM)}"""

""" OAuth2:
Es un protocolo/estándar que define 
cómo debe fluir la autenticación. 
No es una librería sino un conjunto 
de reglas. En tu código lo usas con:

oauth2 = OAuth2PasswordBearer(tokenUrl="jwt_auth_users/login")
"""


# LINK DE ENCRIPTAMIENTO DE CONTRASEÑAS: https://bcrypt-generator.com/
