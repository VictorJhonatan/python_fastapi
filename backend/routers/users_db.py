from fastapi import APIRouter, HTTPException, status
from db.models.user import User
from db.schemas.user import user_schema, users_schema
from db.client import db_client
from bson import ObjectId


users_list = [ ]

router = APIRouter(prefix="/userdb", 
                   tags=["userdb"], 
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

@router.get("/{id}")
async def users(id: str):
    return search_user("_id", ObjectId(id))

@router.get("/") 
async def usuario(id: str):
    return search_user("_id", ObjectId(id))


@router.post("/",response_model=User, status_code=status.HTTP_201_CREATED) 
async def users(user: User):


    if type(search_user("email", user.email)) == User:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe")

    user_dict = dict(user)
    del user_dict["id"] #borramos id para que lo genere mongodb

    # 1. Insertas en MongoDB → te devuelve el _id generado
    #Creamos nuestrp esquema users y creacion DB y el id que se inserto 
    id = db_client.users.insert_one(user_dict).inserted_id #insert_one insertar un registro, y many(muchos)

    # 2. Buscas el documento recién creado
    #find_one-->buscaremos el id, y el id que buscara la que retorna la base de datos variable id
    documento_mongo = db_client.users.find_one({"_id": id}) #nombre de clave la db unica por defecto es _id asi crea mongoDB
    #find_one-->buscaremos el id en Json, y el id que buscara la que retorna la base de datos variable id
    # → { "_id": ObjectId("64abc..."), "username": "luis", ... }

    # 3. El esquema lo traduce a un dict compatible con Pydantic
    new_user = user_schema(documento_mongo)
    # → { "id": "64abc...", "username": "luis", ... }

    return User(**new_user)


@router.put("/", response_model=User)
async def update_user(user: User):
     
    user_dict = dict(user)
    del user_dict["id"]

    try:
        db_client.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)

    except:
        return {"error": "No se actulizo tu usuario"}

    return search_user("_id", ObjectId(user.id))
    

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str):

    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)}) 

    if not found:
        return {"error": "No se elimino el usuario"}


def search_user(field: str, key): #busqueda es field, key es la clave
    try:
        user = user_schema(db_client.users.find_one({field : key}))
        return User(**user)
    
    except:
        return {"error": "Usuario no encontrado"}



