## Requirements
- **Python >= 3.10**
- You have to create in your supabase project:
    - **DB**
    - **Tables and its columns**
- Take the key that suits you best. For this example we recommend using `service_role`, but it is not suitable for production. You can read more [here](https://supabase.com/docs/guides/api/api-keys).

## Installation and setup the project
First of all you need to install the main dependencies:
```python
pip install supadantic fastapi uvicorn
```
Then add`SUPABASE_URL` and `SUPABASE_KEY` **env variables** to `.env`.

## Usage supadantic with FastAPI
Let’s define `book` and `author` tables in **supabase** like that:
![DB Schema](img/db_schema.png)
The tables have a 1:N relationship (one `author` can have several `book`).
Here is the full example of FastAPI application integrated with supadantic models:
```python
from supadantic.models import BaseSBModel
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import Response
import uvicorn

app = FastAPI()

# Define supadantic models
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


# Define pydantic schemas
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


# Define endpoints
@router.get("/")
def authors_list():
    try:
        return list(Author.objects.all())
    except Author.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found."
        )


@router.get("/{id}/")
def retrieve_author(id: int):
    try:
        return Author.objects.get(id=id)
    except Author.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found."
        )


@router.post("/")
def create_author(author: CreateAuthor):
    return Author.objects.create(**author.model_dump())


@router.delete("/{id}/")
def delete_author(id: int):
    try:
        Author.objects.get(id=id).delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Author.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found."
        )


@router.patch("/{id}/")
def update_author(id: int, data: UpdateAuthor):
    updated_data = data.model_dump(exclude_unset=True)
    author = Author.objects.filter(id=id)

    if not author.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Author not found."
        )
    author.update(**updated_data)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{id}/books/")
def author_book_list(id: int):
    books = Book.objects.filter(author_id=id)
    return list(books)


@router.get("/{id}/books/{book_id}/")
def retrieve_book(id: int, book_id: int):
    try:
        return Book.objects.get(id=book_id, author_id=id)
    except Book.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
        )


@router.post("/{id}/books/")
def create_book(id: int, book: CreateBook):
    new_book = Book.objects.create(**book.model_dump(), author_id=id)
    return new_book


@router.patch("/{id}/books/{book_id}/")
def update_book(id: int, book_id: int, data: UpdateBook):
    updated_data = data.model_dump(exclude_unset=True)
    book = Book.objects.filter(id=book_id, author_id=id)
    if not book.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    book.update(**updated_data)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{id}/books/{book_id}/")
def delete_book(id: int, book_id: int):
    try:
        Book.objects.get(id=book_id, author_id=id).delete()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Book.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
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

Then create `test_api.py` module with following code:
```python
from typing import TYPE_CHECKING

from main import create_author
from main import CreateAuthor

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


# Tests for author endpoints
def test_get_authors(client: "TestClient"):
    author1 = CreateAuthor(name="Alex", surname="Pozh", age=99)
    author2 = CreateAuthor(
        name="Qwerty", surname="Qwerty", age=199, country="New Zeland"
    )
    create_author(author1)
    create_author(author2)

    response = client.get("/authors/")
    body = response.json()

    assert response.status_code == 200
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["name"] == "Alex"
    assert body[0]["surname"] == "Pozh"
    assert body[0]["age"] == 99
    assert body[0]["country"] == ""
    assert body[0]["biography"] == ""


def test_get_author_not_found(client: "TestClient"):
    response = client.get("/authors/1/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found."}


def test_get_author(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created = create_author(data)

    response = client.get(f"/authors/{created.id}/")
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

    response = client.delete(f"/authors/{created.id}/")
    assert response.status_code == 204


def test_delete_author_not_found(client: "TestClient"):
    response = client.delete(f"/authors/123/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Author not found."}


def test_post_author(client: "TestClient"):
    response = client.post(
        "/authors/",
        json={
            "name": "Qwerty",
            "surname": "Werty",
            "age": 109,
            "biography": "The coolest writer of all time.",
            "country": "New Zeland",
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["name"] == "Qwerty"
    assert body["surname"] == "Werty"
    assert body["age"] == 109
    assert body["biography"] == "The coolest writer of all time."
    assert body["country"] == "New Zeland"


def test_patch_author(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created = create_author(data)

    patch_response = client.patch(
        f"/authors/{created.id}/",
        json={"name": "Qwerty", "surname": "Werty", "age": 109},
    )
    assert patch_response.status_code == 204

    get_response = client.get(f"/authors/{created.id}/")
    body = get_response.json()

    assert get_response.status_code == 200
    assert body["id"] == created.id
    assert body["name"] == "Qwerty"
    assert body["surname"] == "Werty"
    assert body["age"] == 109


# Tests for author's book endpoints
def test_get_author_books(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    response = client.get(f"/authors/{created_author.id}/books/")
    body = response.json()

    assert response.status_code == 200
    assert isinstance(body, list)
    assert len(body) == 0


def test_get_author_book_not_found(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    response = client.get(f"/authors/{created_author.id}/books/1/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found."}


def test_get_author_book(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    post_response = client.post(
        f"/authors/{created_author.id}/books/",
        json={"name": "Qwerty", "genre": "Poema", "count_pages": 14},
    )
    book = post_response.json()

    response = client.get(f"/authors/{created_author.id}/books/{book['id']}/")
    body = response.json()

    assert response.status_code == 200
    assert body["name"] == "Qwerty"
    assert body["genre"] == "Poema"
    assert body["count_pages"] == 14


def test_post_author_books(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    response = client.post(
        f"/authors/{created_author.id}/books/",
        json={"name": "Qwerty", "genre": "Poema", "count_pages": 14},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["name"] == "Qwerty"
    assert body["genre"] == "Poema"
    assert body["count_pages"] == 14


def test_patch_author_book(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    post_response = client.post(
        f"/authors/{created_author.id}/books/",
        json={"name": "Qwerty", "genre": "Poema", "count_pages": 14},
    )
    book = post_response.json()

    patch_response = client.patch(
        f"/authors/{created_author.id}/books/{book['id']}/",
        json={"name": "Alola", "genre": "fair tale"},
    )
    assert patch_response.status_code == 204

    get_response = client.get(f"/authors/{created_author.id}/books/{book['id']}/")
    body = get_response.json()

    assert get_response.status_code == 200
    assert body["name"] == "Alola"
    assert body["genre"] == "fair tale"
    assert body["count_pages"] == 14


def test_delete_author_book(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    post_response = client.post(
        f"/authors/{created_author.id}/books/",
        json={"name": "Qwerty", "genre": "Poema", "count_pages": 14},
    )
    book = post_response.json()

    response = client.delete(f"/authors/{created_author.id}/books/{book['id']}/")
    assert response.status_code == 204


def test_delete_author_book_not_found(client: "TestClient"):
    data = CreateAuthor(name="Alex", surname="Pozh", age=99)
    created_author = create_author(data)

    response = client.delete(f"/authors/{created_author.id}/books/203/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}
```
