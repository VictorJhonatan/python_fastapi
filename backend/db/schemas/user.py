#dentro de esuqemas trabajamos con operaciones para trabajar con modelos y como se trata estos modelos en BD

"""VAMOS A TRANSFORMAR LO QUE VIENE DE LA DB ---- ROUTER DE USERS_DB DEL POST
 EST ES JSON ---> db_client.local.users.find_one({"_id": id}) ---> representamos al User del modelo

TRANSFORMO LA DB A MODELO DEL USER
 """ 
def user_schema(user) -> dict: #user viene de la db
    return {
        "id": str(user["_id"]), # convierte (_id) ObjectId → str y renombra _id → id
        "username": user["username"],
        "email": user["email"]
    }

def users_schema(users) -> list:
    return [user_schema(user) for user in users]