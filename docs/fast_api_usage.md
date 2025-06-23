## Requirements
- **Python >= 3.10**
- You have to register at [supabase](https://supabase.com/)
- You have to create:
    - **DB**
    - **Tables and its columns**
- To connect to **supabase** via **python**, you must save:
    - [Supabase URL](https://supabase.com/dashboard/project/jlabkatixtriusapedam/settings/api)
    - [Supabase API public key](https://supabase.com/dashboard/project/jlabkatixtriusapedam/settings/api-keys)

## Installation and setup the project
First of all you need to install the main dependencies:
```python
pip install supadantic fastapi uvicorn
```
Let's create the new module called `main.py`. Inside this module you have to define `SUPABASE_URL` and `SUPABASE_KEY` **env variables**, e.g:
```python
import os

os.environ['SUPABASE_URL'] = 'YOUR_SUPABASE_URL'
os.environ['SUPABASE_KEY'] = 'YOUR_API_PUBLIC_KEY'
```

## Usage supadantic with FastAPI
I have already created two tables in **supabase**:
- **`author`**
- **`book`**
The tables have a 1:N relationship (one `author` can have several `book`).
Here is the full example of FastAPI application integrated with supadantic models:
```python
import os
from typing import Any

from supadantic.models import BaseSBModel
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import Response
import uvicorn


os.environ['SUPABASE_URL'] = 'YOUR_SUPABASE_URL'
os.environ['SUPABASE_KEY'] = 'YOUR_API_PUBLIC_KEY'

app = FastAPI()

# define supadantic models
class Author(BaseSBModel):
    name: str
    surname: str
    age: int
    biography: str = ""
    country: str = ""

class Book(BaseSBModel):
    name: str
    genre: str
    count_pages: int | None = None
    author_id: int

# define pydantic schemas
class CreateAuthor(BaseModel):
    name: str
    surname: str
    age: int

class UpdateAuthor(BaseModel):
    name: str | None = None
    surname: str | None = None
    age: int | None = None
    biography: str | None = None
    country: str | None = None

class CreateBook(BaseModel):
    name: str
    genre: str
    author_id: int

class UpdateBook(BaseModel):
    name: str | None = None
    genre: str | None = None
    count_pages: int | None = None

# define crud functions
def create_author(
    author: CreateAuthor
) -> Author:
    new_author = Author.objects.create(**author.model_dump())
    return new_author

def update_author(
    id: int,
    data: dict[str, Any]
) -> None:
    author = Author.objects.filter(id=id)
    if not author.exists():
        raise BaseSBModel.DoesNotExist
    author.update(**data)

def get_author(
    id: int
) -> Author:
    return Author.objects.get(id=id)

def get_author_books(
    id: int
) -> list[Book]:
    books = Book.objects.filter(author_id=id)
    return list(books)

def delete_author(
    id: int
) -> None:
    author = Author.objects.get(id=id)
    author.delete()

def create_book(
    book: CreateBook
) -> Book:
    new_book = Book.objects.create(**book.model_dump())
    return new_book

def update_book(
    id: int,
    data: dict[str, Any]
) -> None:
    book = Book.objects.filter(id=id)
    if not book.exists():
        raise BaseSBModel.DoesNotExist
    book.update(**data)

def get_book(
    id: int
) -> Book:
    return Book.objects.get(id=id)

def delete_book(
    id: int
) -> None:
    book = Book.objects.get(id=id)
    book.delete()

# define endpoints
@app.get("/authors/{id}")
def get_author_by_id(
    id: int
):
    try:
        user = get_author(id=id)
        return user
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@app.get("/authors/author_books/{id}")
def get_author_books_by_id(
    id: int
):
    try:
        author = get_author(id)
        books = get_author_books(id=id)
        return {
            "author": author,
            "books": books
        }
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@app.post("/authors/new/")
def create_new_author(
    data: CreateAuthor
):
    user = create_author(data)
    return user

@app.delete("/authors/{id}")
def delete_author_by_id(
    id: int
):
    try:
        delete_author(id)
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@app.patch("/authors/{id}")
def update_author_by_id(
    id: int,
    data: UpdateAuthor
):
    try:
        updated_data = data.model_dump(exclude_unset=True)
        update_author(
            id,
            updated_data
        )
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@app.get("/books/{id}")
def get_book_by_id(
    id: int
):
    try:
        book = get_book(id=id)
        return book
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@app.post("/books/new/")
def create_new_book(
    data: CreateBook
):
    book = create_book(data)
    return book

@app.delete("/books/{id}")
def delete_book_by_id(
    id: int
):
    try:
        delete_book(id)
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@app.patch("/books/{id}")
def update_book_by_id(
    id: int,
    data: UpdateBook
):
    try:
        updated_data = data.model_dump(exclude_unset=True)
        update_book(
            id,
            updated_data
        )
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="localhost",
        port=8000,
        reload=True
    )
```

## Testing in supadantic via `CacheClient`
In `conftest.py` define the following **fixtures**:
```python
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from supadantic.clients.cache import CacheClient
from supadantic.models import BaseSBModel

from main.py import app
from main.py import Author


@pytest.fixture
def client():
    test_app = FastAPI()
    test_app.include_router(app)
    return TestClient(test_app)

@pytest.fixture(scope="session", autouse=True)
def mock_model():
    with patch.object(BaseSBModel, "db_client", return_value=CacheClient):
        yield

@pytest.fixture(scope="function", autouse=True)
def clear_cache():
    yield
    Author.objects.all().delete()
```

Now create `test_crud.py` module with following code:
```python
from typing import TYPE_CHECKING

from main.py import CreateAuthor
from main.py import create_author, get_author, update_author, delete_author
from main.py import Author

if TYPE_CHECKING:
    from supadantic.clients.cache import CacheClient


def create_author_data():
        return CreateAuthor(
            name="Alex",
            surname="Pozh",
            age=99
        )

def test_create_author(mock_model: "CacheClient"):
    data = create_author_data()
    created_author = create_author(data)
    assert created_author.name == data.name
    assert created_author.surname == data.surname
    assert created_author.age == data.age
    assert created_author.biography == ""
    assert created_author.country == ""

def test_delete_author(mock_model: "CacheClient"):
    data = create_author_data()
    created_author = create_author(data)
    assert created_author.name == data.name

    delete_author(created_author.id)
    assert Author.objects.filter(id=created_author.id).exists() is False

def test_get_author(mock_model: "CacheClient"):
    data = create_author_data()
    created_author = create_author(data)
    user = get_author(created_author.id)
    assert user == created_author

def test_update_author(mock_model: "CacheClient"):
    data = create_author_data()
    created_author = create_author(data)

    updated_fields = {
        "name": "Qwerty",
        "age": 123
    }
    update_author(
        id=created_author.id,
        data=updated_fields
    )
    author = get_author(id=created_author.id)

    assert author.name == "Qwerty"
    assert author.age == 123
```

Create `test_api.py` module with following code:
```python
from typing import TYPE_CHECKING

from main.py import CreateAuthor, CreateBook
from main.py import create_author, create_book

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_get_author_not_found(client: "TestClient"):
    response = client.get("/authors/1")
    assert response.status_code == 404
    assert response.json() == {
                                "detail": "Not Found"
                            }

def test_get_author(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created = create_author(data)

    response = client.get(f"/authors/{created.id}")
    body = response.json()

    assert response.status_code == 200
    assert body["id"] == created.id
    assert body["name"] == "Alex"
    assert body["surname"] == "Pozh"
    assert body["biography"] == ""
    assert body["country"] == ""

def test_delete_author(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created = create_author(data)

    response = client.delete(f"/authors/{created.id}")
    assert response.status_code == 204

def test_delete_author_not_found(client: "TestClient"):
    response = client.delete(f"/authors/123")
    assert response.status_code == 404
    assert response.json() == {
                                "detail": "Not Found"
                            }

def test_post_author(client: "TestClient"):
    response = client.post(
        "/authors/new/",
        json={
            "name": "Qwerty",
            "surname": "Werty",
            "age": 109
        }
    )
    body = response.json()
    assert response.status_code == 200
    assert body["name"] == "Qwerty"
    assert body["surname"] == "Werty"
    assert body["age"] == 109

def test_patch_author(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created = create_author(data)

    patch_response = client.patch(
        f"/authors/{created.id}",
        json={
            "name": "Qwerty",
            "surname": "Werty",
            "age": 109
        }
    )
    assert patch_response.status_code == 204

    get_response = client.get(f"/authors/{created.id}")
    body = get_response.json()

    assert get_response.status_code == 200
    assert body["id"] == created.id
    assert body["name"] == "Qwerty"
    assert body["surname"] == "Werty"
    assert body["age"] == 109

def test_get_author_books(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    book1 = CreateBook(
            name="Alola",
            genre="poem",
            author_id=created_author.id
        )
    created_book = create_book(book1)

    response = client.get(
        f"/authors/author_books/{created_author.id}"
    )
    body = response.json()

    assert response.status_code == 200
    assert body["author"] == created_author.model_dump()
    assert body["books"][0] == created_book.model_dump()
```
