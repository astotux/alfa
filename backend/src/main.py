from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import api_router
from database import engine
from models import Base
from another_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from auth.dependencies import get_jwt_config

app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

Base.metadata.create_all(bind=engine)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(api_router)

@app.get("/api/test")
def test():
    return {"message": "Backend работает!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
