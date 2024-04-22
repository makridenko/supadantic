# Supadantic

Supadantic is a small Python library that allows you to manage [Supabase](supabase.com) tables through [Pydantic](https://github.com/pydantic/pydantic) models. It is very convenient to use in projects based on [FastAPI](https://github.com/tiangolo/fastapi), [Flask](https://github.com/pallets/flask), and so on.


## Installation

Install using `pip install -U pydantic`.
Also, you need to add `SUPABASE_URL` and `SUPABASE_KEY` to your env variables.


## A Simple example

```python
from supadantic.models import BaseSBModel


class User(BaseSBModel):
    # id field already defined in BaseSBModel class
    name: str = 'John Doe'
    is_active: bool = True

    @classmethod
    def _get_table_name(cls) -> str:
        return 'users'

# Save user
active_user = User(name='John Snow')
active_user.save()

non_active_user = User(is_active=False)
non_active_user.save()

# Get all users
users = User.all()

# Count users
users.count()

# Get first user
users.first()

# Get last user
users.last()

# Filter users
active_users = User.filter(eq={'is_active': True})

# Update all active users
active_users.update(data={'is_active': False})

# Delete all non active users
User.filter(neq={'is_active': True}).delete()

# Get one user and delete
user = User.get(eq={'name': 'John Doe'})
user.delete()
```
