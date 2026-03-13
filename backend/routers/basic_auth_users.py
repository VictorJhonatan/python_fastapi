from fastapi import Depends, APIRouter, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix="/basic_auth_users", tags=["basic_auth_users"], responses={404: {"message": "No encontrado"}}) 

oauth2 = OAuth2PasswordBearer(tokenUrl="basic_auth_users/login")

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
        "password": "123456"
    },

    "analu": {
        "username": "ana",
        "full_name": "Ana García",
        "email": "ana@ana.com",
        "disabled": True,
        "password": "123456"
    },

    "luis": {
        "username": "luis",
        "full_name": "Luis Martínez",
        "email": "luis@luis.com",
        "disabled": False,
        "password": "123456"
    }
}

def search_users(username: str):
    if username in user_db:
        return User(**user_db[username])
    
def search_user(username: str):
    if username in user_db:
        return UserInDB(**user_db[username])
    
async def current_user(token: str = Depends(oauth2)):
    user = search_users(token)
    if not user:  # if user is None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="credenciales  de autenticación inválidas", 
            headers={"WWW-Authenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return user
    

@router.post("/login") 
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_dbs = user_db.get(form.username)
    if not user_dbs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    
    user = search_user(form.username)
    if not form.password == user.password: # si la contraseña no es correcta
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña incorrecta")
    
    return {"access_token": user.username, "token_type": "bearer"}

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user

@router.put("/users/put/{username}")
async def putusers(username: str, user: User, current: User = Depends(current_user)): # current --> Solo usuarios autenticados puedan usar este endpoint.
    
    if username != current.username:  # ← solo puede editarse a sí mismo
        raise HTTPException(status_code=403, detail="Usuario incorrecto")
    
    if username not in user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_db[username]["full_name"] = user.full_name
    user_db[username]["email"] = user.email
    user_db[username]["disabled"] = user.disabled
    return {"message": "Usuario actualizado", "user": user}

@router.delete("/users/{username}")
async def delete_user(username: str, current: User = Depends(current_user)):

    if username != current.username:  # ← solo puede editarse a sí mismo
        raise HTTPException(status_code=403, detail="Usuario incorrecto")

    if username not in user_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    del user_db[username]

    return {"message": "Usuario eliminado"}
