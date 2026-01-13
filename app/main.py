from fastapi import FastAPI
from app.routers.pods import pods_control, pods_create, pods_delete, pods_get

app = FastAPI()

app.include_router(pods_control.router)
app.include_router(pods_create.router)
app.include_router(pods_get.router)
app.include_router(pods_delete.router)
    


