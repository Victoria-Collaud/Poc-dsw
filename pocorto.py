"""
API REST de Usuarios - Ejemplo Simplificado
============================================
Demuestra: REST + OpenAPI en un solo archivo
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# ============================================================
# 1. CONFIGURACIÓN (FastAPI genera OpenAPI automáticamente)
# ============================================================

app = FastAPI(
    title="API de Usuarios",
    description="API REST básica para gestión de usuarios",
    version="1.0.0"
)

# ============================================================
# 2. MODELO DE DATOS
# ============================================================

class User(BaseModel):
    """Modelo de usuario"""
    id: int
    name: str
    email: str
    age: int

# ============================================================
# 3. BASE DE DATOS EN MEMORIA
# ============================================================

users_db = [
    User(id=1, name="Ana Gómez", email="ana@email.com", age=28),
    User(id=2, name="Carlos Ruiz", email="carlos@email.com", age=32)
]
next_id = 3

# ============================================================
# 4. ENDPOINTS REST (5 operaciones CRUD)
# ============================================================

@app.get("/users", response_model=List[User])
def get_users():
    """GET /users - Obtener todos los usuarios"""
    return users_db

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    """GET /users/{id} - Obtener un usuario por ID"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.post("/users", response_model=User, status_code=201)
def create_user(user: User):
    """POST /users - Crear un nuevo usuario"""
    global next_id
    # Verificar email duplicado
    for existing in users_db:
        if existing.email == user.email:
            raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Asignar ID y guardar
    user.id = next_id
    next_id += 1
    users_db.append(user)
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User):
    """PUT /users/{id} - Actualizar un usuario completo"""
    for i, existing in enumerate(users_db):
        if existing.id == user_id:
            user.id = user_id
            users_db[i] = user
            return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    """DELETE /users/{id} - Eliminar un usuario"""
    global users_db
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    users_db = [u for u in users_db if u.id != user_id]
    return None

# ============================================================
# 5. EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("\n📚 API de Usuarios")
    print("📍 http://localhost:8000")
    print("📖 Documentación: http://localhost:8000/docs")
    print("📄 OpenAPI: http://localhost:8000/openapi.json\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    