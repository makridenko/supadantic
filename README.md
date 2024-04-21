# Supadantic

[![PyPI - Downloads](https://img.shields.io/pypi/dm/supadantic)](https://github.com/makridenko/supadantic)
[![GitHub License](https://img.shields.io/github/license/makridenko/supadantic)](https://github.com/makridenko/supadantic)
[![versions](https://img.shields.io/pypi/pyversions/supadantic.svg)](https://github.com/makridenko/supadantic)
[![pypi](https://img.shields.io/pypi/v/supadantic.svg)](https://pypi.python.org/pypi/supadantic)

Supadantic is a small Python library that allows you to manage [Supabase](supabase.com) tables through [Pydantic](https://github.com/pydantic/pydantic) models. It is very convenient to use in projects based on [FastAPI](https://github.com/tiangolo/fastapi), [Flask](https://github.com/pallets/flask), and so on.


## Installation

Install using `pip install -U pydantic`.
Also, you need to add `SUPABASE_URL` and `SUPABASE_KEY` to your env variables.


## A Simple example

```python
from supadantic import BaseDBEntity


class User(BaseDBEntity):
    # id field already defined in BaseDBEntity class
    name: str = 'John Doe'

    @classmethod
    def _get_table_name(cls) -> str:
        return 'users'

# Save user
user = User()
user.save()

another_user = User(name='Another name')
another_user.save()

# Get users
User.get_list()

# Get users with name == 'John Doe'
User.get_list(eq={'name': 'John Doe'})

# Get users with name != 'Another name'
User.get_list(neq={'name': 'Another name'})

# Get one user
user = User.get(eq={'id': 1})

# Delete this user
user.delete()

# Bulk update
User.bulk_update(ids=[1,2], data={'name': 'New name'})
```
