from fastapi import FastAPI


def get_app() -> FastAPI:
    from main import app
    return app
