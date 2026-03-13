from pydantic import BaseModel 


#Entidad de modelo con la que trabajamos a nivel de clases desde fastApi
class User(BaseModel): 
    id: str | None = None #puede que el campo sea opcional, no nos llegue
    username: str
    email: str


"""Lo que hago es insertar un usuario y email, no le paso el id porque es usuario nuevo
y en mongodn es tipo str, es mejor crea id mas largos"""