import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
import uvicorn
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr

load_dotenv()
url: str = os.getenv("supabase_url") 
key: str = os.getenv("supabase_key") 

if not url or not key:
    raise RuntimeError("Faltan las credenciales de Supabase. Define SUPABASE_URL/SUPABASE_KEY en las variables de entorno.")

supabase: Client = create_client(url, key)
app = FastAPI(title="API de Contactos con Supabase")

class Contacto(BaseModel):
    nombre: str 
    apellidos: str = None
    correo: str
    numero_de_telefono: int = None
    fecha_nacimiento: str = None


@app.get("/")
def read_root():
    return {"mensaje": "La API de Contactos funciona correctamente"}

# Obtener todos los contactos
@app.get("/contactos")
def get_all_contactos():
    response = supabase.table("Contacto").select("*").execute()
    return {"contactos": response.data}

@app.get("/contacto/{contacto_id}")
def read_contacto(contacto_id: int):
    response = supabase.table("Contacto").select("*").eq("id", contacto_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
        
    return {"contacto": response.data[0]}

@app.post("/contacto/")
def create_contacto(contacto: Contacto):
    new_data = contacto.model_dump()
    
    result = supabase.table("Contacto").insert(new_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=400, detail="Error al crear el contacto")
        
    return {"mensaje": "Contacto creado exitosamente", "contacto": result.data}

@app.delete("/contacto/{contacto_id}")
def delete_contacto(contacto_id: int):
    result = supabase.table("Contacto").delete().eq("id", contacto_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="No se pudo eliminar: contacto no encontrado")
        
    return {"mensaje": f"Contacto {contacto_id} eliminado correctamente"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)