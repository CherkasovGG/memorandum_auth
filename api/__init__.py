from api.user import user_router
from api.auth import auth_router


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def init_cors(api: FastAPI) -> None:
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_routers(api: FastAPI) -> None:
    api.include_router(user_router)
    api.include_router(auth_router)


def create_api() -> FastAPI:
    api = FastAPI(
        title="Auth Service",
        description="Hide API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    init_routers(api=api)
    init_cors(api=api)

    return api


api = create_api()


@api.get("/")
async def hello():
    return {"message": "Hello, world!"}
