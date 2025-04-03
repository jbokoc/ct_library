from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def app_factory():
    """
    Factory function to create a FastAPI app instance.
    :return: A FastAPI app instance.
    """
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    # app.on_event("startup").append(models.create_db_and_tables)

    return app


if __name__ == "__main__":
    uvicorn.run(app_factory, host="0.0.0.0", port=8000)
