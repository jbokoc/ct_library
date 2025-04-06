# Library

## Description

This humble server can manage authors book and leases. Although it's missing fundamental features like authentication, it serves as a good starting point for a library management system.
I'm fully aware that using this setup (framework, db, ...) vary far from ideal as even simple tasks will require a lot of code. Anyway I wanted to try out (not for first time) FastAPI whit DI container and SQLAlchemy.

## Usage

To run the server, you need to have Python3.12+. To install the dependencies, run:

```bash
poetry install
```

Before first run, you need to create the database. You can do this by running:

```bash
poetry run alembic upgrade head
```

To run the server, use:

```bash
poetry run python ct_library/main.py
```

## Future steps

- [ ] Authentication
- [ ] Better error handling
- [ ] Generic CRUD management for simple models to reduce boilerplate code

## Improvements

Maybe, just maybe would be wort it to convert the project to native async, however, in my experince it adds a lot of complexity and the performance gain is not that significant.
