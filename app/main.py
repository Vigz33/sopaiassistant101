import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from routers import root

app = FastAPI(openapi_url=None)
Instrumentator().instrument(app).expose(app)
app.include_router(root.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
