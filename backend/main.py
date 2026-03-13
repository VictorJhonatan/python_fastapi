#slecciona entorno virtual CTRL + SHIFT + P
# dale interprete de python
#selecciona interpretepath --> C:\Users\victo\Documents\python_fastapi\backend\venv\Scripts\python.exe
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from routers import users_json
from routers import products, basic_auth_users, jwt_auth_users, argon2_auth_users, argon2_auth_users_intermediate, users_db


app = FastAPI()

#routers
app.include_router(users_json.router)
app.include_router(products.router)
app.include_router(basic_auth_users.router)
app.include_router(jwt_auth_users.router)
app.include_router(argon2_auth_users.router)
app.include_router(argon2_auth_users_intermediate.router)
app.include_router(users_db.router)

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int

users_list = [
    User(id=1, name="Jose", email="jose123@example.com", age=30),
    User(id=2, name="James", email="james123@example.com", age=25),
    User(id=3, name="Maria", email="maria@example.com", age=28)
]

#funcion para buscar usuario por id
def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except IndexError:
        return {"error": "Usuario no encontrado"}

@app.get("/url")
async def url():
    return {"url": "hhtmjfdsljljldksfjks"}

#query
@app.get("/users")
async def users(id: int):
    return search_user(id) 

@app.post("/users", status_code=201)
async def create_user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    users_list.append(user)
    return user

@app.put("/users")
async def update_user(user: User):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            return user
        
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/users")
async def delete_user(id: int):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            return {"message": "Usuario eliminado"}
        
    raise HTTPException(status_code=404, detail="Usuario no encontrado")