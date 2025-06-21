
## Usage `supadantic` with `FastAPI`

#### Installing dependencies
```bash
pip install supadantic

pip install fastapi

pip install uvicorn
```

#### Define entry point for FastAPI project
Create `main.py` in the root of your project:
```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="localhost",
        port=8000,
        reload=True
    )
```

#### Create supadantic model
Now let's create supadantic model. This is done very quickly and comfortable. Create `models/` folder with `user.py` inside:
```python
from supadantic.models import BaseSBModel
from pydantic import EmailStr

class User(BaseSBModel):
    # id field already defined in BaseSBModel class
    name: str
    email: EmailStr
    age: int
    created_at: str # support for datetime/date types are coming soon
    is_active: bool

    @classmethod
    def _get_table_name(cls) -> str:
        return 'db_user'
```

#### Create pydantic schemas
It's good way to declare pydantic schemas which we will use in endpoints to validate data. Let's create `schemas/` folder and `user.py` inside:
```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class GetUser(BaseModel):
    id: int
    name: str
    email: str
    age: int
    is_active: bool
    created_at: datetime

class CreateUser(BaseModel):
    name: str
    email: str
    age: int

class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None
```

#### Create CRUD
Now i'm gonna show you how easy it is to make CRUD operations for pudantic models. We can create new folder `crud/` with `user.py` inside:
```python
from datetime import datetime, timezone
from typing import Any
from models.user import User

from supadantic.models import BaseSBModel
from schemas.user import GetUser, CreateUser, UpdateUser

def create_user(
    user: CreateUser
) -> GetUser:
    current_time = datetime.now(timezone.utc)
    new_user = User.objects.create(**user.model_dump(), is_active=True, created_at=current_time.isoformat())
    return GetUser(**new_user.model_dump())

def update_user(
    id: int,
    data: dict[str, Any]
) -> None:
    user = User.objects.filter(id=id)
    if user.count() == 0:
        raise BaseSBModel.DoesNotExist
    user.update(**data)

def get_user(
    id: int
) -> GetUser:
    return GetUser(**User.objects.get(id=id).model_dump())

def delete_user(
    id: int
) -> None:
    user = User.objects.get(id=id)
    user.delete()
```

#### Create endpoints
It's time to define our endpoints. Create `api/` folder with `user.py` inside:
```python
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import Response
from supadantic.models import BaseSBModel
from pydantic import ValidationError

from crud.user import create_user, delete_user, get_user, update_user
from schemas.user import CreateUser, UpdateUser

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/{id}")
def get_user_by_id(
    id: int
):
    try:
        user = get_user(id=id)
        return user
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@router.post("/new/")
def create_new_user(
    data: CreateUser
):
    try:
        user = create_user(data)
        return user
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.errors()
        )

@router.delete("/{id}")
def delete_user_by_id(
    id: int
):
    try:
        delete_user(id)
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    except BaseSBModel.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

@router.patch("/{id}")
def update_user_by_id(
    id: int,
    data: UpdateUser
):
    try:
        updated_data = data.model_dump(exclude_unset=True)
        update_user(
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
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.errors()
        )
```

Don't forget to **include router in main.py**:
```python
from api.user import router as user_router

app.include_router(user_router)
```
