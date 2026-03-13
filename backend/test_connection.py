"""

from pymongo import MongoClient

MONGO_URL = "mongodb+srv://datos:datos@cluster1.wuxjxzt.mongodb.net/"

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("CONECTADO EXITOSAMENTE")
except Exception as e:
    print(f"ERROR: {e}")

"""