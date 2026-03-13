from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"], responses={404: {"message": "No encontrado"}}) 

class Products(BaseModel):
    name: str
    category: str

products_list = [
    Products(name="Laptop", category="Electronics"),
    Products(name="Mouse", category="Electronics"),
    Products(name="Keyboard", category="Electronics"),
    Products(name="Apple", category="Food"),
    Products(name="Bread", category="Food"),
    Products(name="Milk", category="Food"),
    Products(name="Shampoo", category="Personal Care"),
    Products(name="Soap", category="Personal Care"),
    Products(name="Toothpaste", category="Personal Care"),
]

#funcion para buscar producto por name
def search_products(name: str):
    products = filter(lambda product: product.name == name, products_list)
    try:
        return list(products)[0]
    except IndexError:
        return {"error": "Producto no encontrado"}

@router.get("/")
async def products():
    return products_list

@router.get("/{name}")
async def products(name: str):
    return search_products(name)


@router.post("/", response_model=Products, status_code=201) 
async def create_users(products: Products):
    if type(search_products) == Products:
                raise HTTPException(status_code=400, detail="El Producto ya existe")
    products_list.append(products)
    return products
    




    