from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes_recipes import router as recipes_router

openapi_tags = [
    {
        "name": "Health",
        "description": "Service health and readiness endpoints.",
    },
    {
        "name": "Recipes",
        "description": "CRUD endpoints for recipe management.",
    },
]

app = FastAPI(
    title="Simple Recipe API",
    description=(
        "A minimal FastAPI backend for creating, reading, updating, and deleting recipes.\n\n"
        "Database: PostgreSQL (configure via DATABASE_URL environment variable)."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Basic service health check endpoint.",
    operation_id="health_check",
)
# PUBLIC_INTERFACE
def health_check():
    """Health check endpoint returning a simple status payload."""
    return {"message": "Healthy"}


app.include_router(recipes_router)
