#gestionar conexion en mongo db

from pymongo import MongoClient

# Mantenemos tus variables tal cual

#gestionar conexion en mongo db

"""En la URL al final /net
agrega nombre de la db que quieres crear: """

#conectar db de manera LOCAL
# db_client = MongoClient().local

MONGO_URL = "mongodb+srv://datos:datos@cluster1.wuxjxzt.mongodb.net/?appName=Cluster1" 

# db_client = MongoClient(MONGO_URL).testing # opcion una sin la variable db
db_client = MongoClient(MONGO_URL).testing  # conecta al CLUSTER (servidor)

# llamamamos db opcion 2
# db = db_client["testing"] # selecciona la BD dentro del cluster


# users = db["users"] # fila(coleccion)



