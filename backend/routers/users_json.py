from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json

router = APIRouter(prefix="/users_json", tags=["users_json"], responses={404: {"message": "No encontrado"}}) 

class User(BaseModel):
    id: int
    name: str
    surname: str
    age: int
    url: str

with open("database.json", "r", encoding="utf-8") as mi_other_file:
    datos = json.load(mi_other_file)


#Buscar un usuario por su ID
def search_user(id: int):
    users = filter(lambda user: user["id"] == id, datos["users"])
    try:
        return list(users)[0]
    except IndexError:
        return {"error": "Usuario no encontrado"}


@router.get("/")
async def users(id: int):
    return search_user(id)

@router.post("/", response_model=User, status_code=201) 
async def create_users(user: User):
    for u in datos["users"]:
        if u["id"] == user.id:
            raise HTTPException(status_code=404, detail="El usuario ya existe") 
        
    datos["users"].append(user.dict()) 
    with open("database.json", "w", encoding="utf-8") as mi_other_file:
        json.dump(datos, mi_other_file, indent=4) 
    return user

@router.put("/")
async def update_users(user: User):
    for index, saved_user in enumerate(datos["users"]):
        if saved_user["id"] == user.id:
            datos["users"][index] = user.dict()
            with open("database.json", "w", encoding="utf-8") as mi_other_file:
                json.dump(datos, mi_other_file, indent=4)
            return user
    raise HTTPException(status_code=404, detail="Usuario no Actualizado")

@router.delete("/{id}")
async def delete_user(id: int):
    for index, saved_user in enumerate(datos["users"]):
        if saved_user["id"] == id:
            del datos["users"][index]
            with open("database.json", "w", encoding="utf-8") as mi_other_file:
                json.dump(datos, mi_other_file, indent=4) 
            return {"message": "Usuario Eliminado"}
    raise HTTPException(status_code=404, detail="Usuario no Actualizado")
    







