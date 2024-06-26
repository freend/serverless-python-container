from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from mangum import Mangum

from api.order import router as order_router

app = FastAPI()
api_router = APIRouter()

api_router.include_router(order_router)
app.include_router(api_router)

# Sample CORS Setting
origins = [
    "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return { "Hello" : "World v1" }


handler = Mangum(app)