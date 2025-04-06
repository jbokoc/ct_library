import os
import sys
from pathlib import Path

current_folder = Path(__file__).resolve().parent
sys.path.append(os.path.join(current_folder, "../"))

import uvicorn

from ct_library.api import router
from ct_library.exceptions import register_exception_handlers  # noqa: F401, F403:q


def app_factory():
    """
    Factory function to create a FastAPI app instance.
    :return: A FastAPI app instance.
    """
    from ct_library.container import Container  # noqa: F401, F403

    di_container = Container()

    app = di_container.app()
    app.include_router(router)
    register_exception_handlers(app)
    return app


if __name__ == "__main__":
    uvicorn.run(app_factory, host="0.0.0.0", port=8000)
