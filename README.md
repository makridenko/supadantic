# Supadantic

[![PyPI - Downloads](https://img.shields.io/pypi/dm/supadantic)](https://github.com/makridenko/supadantic)
[![GitHub License](https://img.shields.io/github/license/makridenko/supadantic)](https://github.com/makridenko/supadantic)
[![versions](https://img.shields.io/pypi/pyversions/supadantic.svg)](https://github.com/makridenko/supadantic)
[![pypi](https://img.shields.io/pypi/v/supadantic.svg)](https://pypi.python.org/pypi/supadantic)

Supadantic is a small Python library that allows you to manage [Supabase](supabase.com) tables through [Pydantic](https://github.com/pydantic/pydantic) models. It is very convenient to use in projects based on [FastAPI](https://github.com/tiangolo/fastapi), [Flask](https://github.com/pallets/flask), and so on.


## Important information
Supadantic may not have backward compatibility until version `0.1.0`. This is because the library is still experimental and is being used in several of my other projects, where requirements are still being finalized.


## Installation

Install using `pip install -U supadantic`.

Also, you need to add `SUPABASE_URL` and `SUPABASE_KEY` to your env variables.


## A Simple example

```python
from supadantic.models import BaseSBModel


class User(BaseSBModel):
    # id field already defined in BaseSBModel class
    name: str = 'John Doe'
    is_active: bool = True

    # By default table name is class name in snake_case
    # If you want to change it - you should implement _get_table_name method
    @classmethod
    def _get_table_name(cls) -> str:
        return 'db_user'

# Save user
active_user = User(name='John Snow')
active_user.save()

non_active_user = User(is_active=False)
non_active_user.save()

# Get all users
users = User.objects.all()

# Count users
users.count()

# Get first user
users.first()

# Get last user
users.last()

# Filter users
active_users = User.objects.filter(is_active=True)
# Or
active_users = User.objects.exclude(is_active=False)

# Update all active users
active_users.update(is_active=False)

# Delete all non active users
User.objects.exclude(is_active=True).delete()

# Get one user and delete
user = User.objects.get(name='John Doe')
user.delete()
```
