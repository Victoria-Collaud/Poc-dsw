"""
API REST de Gestión de Libros
================================
Este archivo demuestra:
1. Implementación de una API REST (endpoints, métodos HTTP, recursos)
2. Generación automática de OpenAPI Specification
3. Documentación interactiva con Swagger UI
4. Validación automática de datos
5. Generación de clientes a partir de la especificación

Tecnologías: Python + FastAPI + Pydantic + Swagger UI
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import uuid

# ================================================================
# 1. CONFIGURACIÓN DE LA APLICACIÓN
# ================================================================

app = FastAPI(
    title="API de Gestión de Libros",
    description="""
    ## 📚 API REST para gestión de una biblioteca personal

    Esta API permite:
    - **Gestionar libros**: CRUD completo (Crear, Leer, Actualizar, Eliminar)
    - **Filtrar y buscar**: por autor, género, año
    - **Gestionar préstamos**: registrar préstamos y devoluciones

    ### Características técnicas:
    - Arquitectura RESTful
    - Documentación automática con OpenAPI 3.0
    - Validación de datos con Pydantic
    - Autenticación básica (API Key)
    """,
    version="2.0.0",
    contact={
        "name": "Tu Nombre",
        "email": "tu@email.com",
        "url": "https://tusitio.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc (alternativa)
    openapi_url="/openapi.json" # Especificación OpenAPI en JSON
)

# ================================================================
# 2. MODELOS DE DATOS (Schemas con Pydantic)
# ================================================================

class Book(BaseModel):
    """Modelo de un libro"""
    id: str = Field(..., description="Identificador único del libro (UUID)")
    title: str = Field(..., min_length=1, max_length=200, description="Título del libro")
    author: str = Field(..., min_length=1, max_length=100, description="Autor del libro")
    isbn: str = Field(..., min_length=10, max_length=13, description="Código ISBN del libro")
    genre: str = Field(..., description="Género literario")
    year: int = Field(..., ge=1000, le=datetime.now().year, description="Año de publicación")
    available: bool = Field(default=True, description="Disponibilidad para préstamo")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de registro")
    
    @validator('isbn')
    def validate_isbn(cls, v):
        """Validación básica del ISBN"""
        # Limpiar guiones y espacios
        v = v.replace('-', '').replace(' ', '')
        if len(v) not in [10, 13]:
            raise ValueError('El ISBN debe tener 10 o 13 dígitos')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Cien años de soledad",
                "author": "Gabriel García Márquez",
                "isbn": "9788437604947",
                "genre": "Realismo mágico",
                "year": 1967,
                "available": True
            }
        }

class BookCreate(BaseModel):
    """Modelo para crear un libro (sin id y campos autogenerados)"""
    title: str = Field(..., min_length=1, max_length=200, description="Título del libro")
    author: str = Field(..., min_length=1, max_length=100, description="Autor del libro")
    isbn: str = Field(..., min_length=10, max_length=13, description="Código ISBN")
    genre: str = Field(..., description="Género literario")
    year: int = Field(..., ge=1000, le=datetime.now().year, description="Año de publicación")
    
    @validator('isbn')
    def validate_isbn(cls, v):
        v = v.replace('-', '').replace(' ', '')
        if len(v) not in [10, 13]:
            raise ValueError('El ISBN debe tener 10 o 13 dígitos')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "El amor en los tiempos del cólera",
                "author": "Gabriel García Márquez",
                "isbn": "9788437616483",
                "genre": "Novela romántica",
                "year": 1985
            }
        }

class BookUpdate(BaseModel):
    """Modelo para actualizar parcialmente un libro (todos los campos opcionales)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    genre: Optional[str] = None
    year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    available: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Cien años de soledad (Edición especial)",
                "year": 2022,
                "available": True
            }
        }

class Loan(BaseModel):
    """Modelo para un préstamo de libro"""
    book_id: str = Field(..., description="ID del libro prestado")
    user_name: str = Field(..., min_length=1, max_length=100, description="Nombre del usuario")
    loan_date: datetime = Field(default_factory=datetime.now, description="Fecha de préstamo")
    return_date: Optional[datetime] = Field(None, description="Fecha de devolución")
    
    class Config:
        json_schema_extra = {
            "example": {
                "book_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_name": "María Pérez",
                "loan_date": "2026-07-27T10:00:00",
                "return_date": None
            }
        }

class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    detail: str = Field(..., description="Descripción del error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Libro no encontrado",
                "timestamp": "2026-07-27T12:00:00"
            }
        }

# ================================================================
# 3. BASE DE DATOS EN MEMORIA (SIMULADA)
# ================================================================

books_db = {}  # Diccionario {id: Book}
loans_db = []  # Lista de préstamos activos

# Datos iniciales para demostración
initial_books = [
    Book(
        id=str(uuid.uuid4()),
        title="Cien años de soledad",
        author="Gabriel García Márquez",
        isbn="9788437604947",
        genre="Realismo mágico",
        year=1967,
        available=True
    ),
    Book(
        id=str(uuid.uuid4()),
        title="El Principito",
        author="Antoine de Saint-Exupéry",
        isbn="9788423987443",
        genre="Novela corta",
        year=1943,
        available=True
    ),
    Book(
        id=str(uuid.uuid4()),
        title="1984",
        author="George Orwell",
        isbn="9788499890944",
        genre="Ciencia ficción",
        year=1949,
        available=False
    )
]

for book in initial_books:
    books_db[book.id] = book

# ================================================================
# 4. ENDPOINTS REST
# ================================================================

# ---------- OPERACIONES CON LIBROS ----------

@app.get(
    "/books",
    response_model=List[Book],
    summary="Obtener todos los libros",
    description="Retorna la lista completa de libros registrados. Permite filtrar por autor, género y disponibilidad.",
    tags=["Libros"]
)
async def get_books(
    author: Optional[str] = Query(None, description="Filtrar por autor (coincidencia parcial)"),
    genre: Optional[str] = Query(None, description="Filtrar por género (coincidencia exacta)"),
    available: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    limit: int = Query(100, ge=1, le=500, description="Límite de resultados")
):
    """GET /books - Obtiene todos los libros con filtros opcionales"""
    result = list(books_db.values())
    
    # Aplicar filtros
    if author:
        result = [b for b in result if author.lower() in b.author.lower()]
    if genre:
        result = [b for b in result if b.genre.lower() == genre.lower()]
    if available is not None:
        result = [b for b in result if b.available == available]
    
    return result[:limit]

@app.get(
    "/books/{book_id}",
    response_model=Book,
    summary="Obtener libro por ID",
    description="Retorna los detalles de un libro específico",
    tags=["Libros"],
    responses={
        404: {"model": ErrorResponse, "description": "Libro no encontrado"}
    }
)
async def get_book(book_id: str):
    """GET /books/{id} - Obtiene un libro específico por su ID"""
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return book

@app.post(
    "/books",
    response_model=Book,
    status_code=201,
    summary="Crear un nuevo libro",
    description="Registra un nuevo libro en la biblioteca",
    tags=["Libros"],
    responses={
        201: {"description": "Libro creado exitosamente"},
        400: {"description": "Datos inválidos (ISBN duplicado o formato incorrecto)"}
    }
)
async def create_book(book: BookCreate):
    """POST /books - Crea un nuevo libro"""
    # Verificar ISBN duplicado
    for existing_book in books_db.values():
        if existing_book.isbn == book.isbn:
            raise HTTPException(
                status_code=400, 
                detail=f"Ya existe un libro con el ISBN {book.isbn}"
            )
    
    # Crear nuevo libro
    new_book = Book(
        id=str(uuid.uuid4()),
        **book.dict(),
        available=True
    )
    books_db[new_book.id] = new_book
    return new_book

@app.put(
    "/books/{book_id}",
    response_model=Book,
    summary="Actualizar un libro",
    description="Actualiza todos los campos de un libro existente",
    tags=["Libros"],
    responses={
        404: {"model": ErrorResponse, "description": "Libro no encontrado"}
    }
)
async def update_book(book_id: str, updated_data: BookCreate):
    """PUT /books/{id} - Actualiza completamente un libro"""
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Actualizar campos manteniendo id, available y created_at
    updated_book = Book(
        id=book.id,
        **updated_data.dict(),
        available=book.available,
        created_at=book.created_at
    )
    books_db[book_id] = updated_book
    return updated_book

@app.patch(
    "/books/{book_id}",
    response_model=Book,
    summary="Actualizar parcialmente un libro",
    description="Actualiza solo los campos proporcionados de un libro",
    tags=["Libros"],
    responses={
        404: {"model": ErrorResponse, "description": "Libro no encontrado"}
    }
)
async def patch_book(book_id: str, updated_data: BookUpdate):
    """PATCH /books/{id} - Actualiza parcialmente un libro"""
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Actualizar solo los campos proporcionados
    update_dict = updated_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(book, key, value)
    
    books_db[book_id] = book
    return book

@app.delete(
    "/books/{book_id}",
    status_code=204,
    summary="Eliminar un libro",
    description="Elimina un libro de la biblioteca (si no está prestado)",
    tags=["Libros"],
    responses={
        204: {"description": "Libro eliminado exitosamente"},
        400: {"description": "El libro está prestado y no puede eliminarse"},
        404: {"model": ErrorResponse, "description": "Libro no encontrado"}
    }
)
async def delete_book(book_id: str):
    """DELETE /books/{id} - Elimina un libro (solo si no está prestado)"""
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Verificar si está prestado
    if not book.available:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar un libro que está prestado"
        )
    
    del books_db[book_id]
    return None

# ---------- OPERACIONES CON PRÉSTAMOS ----------

@app.post(
    "/loans",
    response_model=Loan,
    status_code=201,
    summary="Registrar un préstamo",
    description="Registra el préstamo de un libro a un usuario",
    tags=["Préstamos"],
    responses={
        201: {"description": "Préstamo registrado exitosamente"},
        400: {"description": "El libro no está disponible"},
        404: {"model": ErrorResponse, "description": "Libro no encontrado"}
    }
)
async def create_loan(loan: Loan):
    """POST /loans - Registra un nuevo préstamo"""
    # Verificar que el libro existe
    book = books_db.get(loan.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Verificar disponibilidad
    if not book.available:
        raise HTTPException(status_code=400, detail="El libro no está disponible")
    
    # Marcar libro como no disponible
    book.available = False
    books_db[book.id] = book
    
    # Registrar préstamo
    loans_db.append(loan)
    return loan

@app.post(
    "/loans/{book_id}/return",
    response_model=Book,
    summary="Devolver un libro",
    description="Registra la devolución de un libro prestado",
    tags=["Préstamos"],
    responses={
        200: {"description": "Devolución registrada exitosamente"},
        400: {"description": "El libro no está prestado"},
        404: {"model": ErrorResponse, "description": "Libro no encontrado"}
    }
)
async def return_book(book_id: str):
    """POST /loans/{id}/return - Registra la devolución de un libro"""
    book = books_db.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    if book.available:
        raise HTTPException(status_code=400, detail="El libro no está prestado")
    
    # Marcar libro como disponible
    book.available = True
    books_db[book.id] = book
    
    # Actualizar fecha de devolución en el préstamo
    for loan in loans_db:
        if loan.book_id == book_id and loan.return_date is None:
            loan.return_date = datetime.now()
            break
    
    return book

@app.get(
    "/loans/active",
    response_model=List[Loan],
    summary="Obtener préstamos activos",
    description="Retorna la lista de préstamos que no han sido devueltos",
    tags=["Préstamos"]
)
async def get_active_loans():
    """GET /loans/active - Obtiene todos los préstamos activos"""
    return [loan for loan in loans_db if loan.return_date is None]

# ---------- ENDPOINT DE ESTADÍSTICAS ----------

@app.get(
    "/stats",
    summary="Estadísticas de la biblioteca",
    description="Retorna métricas agregadas de la biblioteca",
    tags=["Estadísticas"]
)
async def get_stats():
    """GET /stats - Obtiene estadísticas de la biblioteca"""
    total_books = len(books_db)
    available_books = sum(1 for b in books_db.values() if b.available)
    active_loans = len([l for l in loans_db if l.return_date is None])
    
    # Agrupar por género
    genres = {}
    for book in books_db.values():
        genres[book.genre] = genres.get(book.genre, 0) + 1
    
    return {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": total_books - available_books,
        "active_loans": active_loans,
        "genres_distribution": genres,
        "timestamp": datetime.now()
    }

# ================================================================
# 5. EJECUCIÓN (si se corre directamente)
# ================================================================

if __name__ == "__main__":
    import uvicorn
    print("""
    ========================================
    📚 API de Gestión de Libros
    ========================================
    Servidor iniciado en: http://localhost:8000
    Documentación Swagger UI: http://localhost:8000/docs
    Documentación ReDoc: http://localhost:8000/redoc
    Especificación OpenAPI: http://localhost:8000/openapi.json
    ========================================
    
    Prueba rápida:
    > GET http://localhost:8000/books
    > POST http://localhost:8000/books
    > GET http://localhost:8000/stats
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)