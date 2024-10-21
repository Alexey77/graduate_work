from fastapi import Depends, FastAPI


def get_app() -> FastAPI:
    from main import app
    return app


# def get_db(app: FastAPI = Depends(get_app)) -> DatabaseConnection:
#     return app.state.db
