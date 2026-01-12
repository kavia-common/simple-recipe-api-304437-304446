from typing import List

from fastapi import APIRouter, HTTPException, status

from src.api import db
from src.api.models import RecipeCreate, RecipeOut, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _row_to_recipe_out(row: dict) -> RecipeOut:
    """Convert DB row dict into RecipeOut."""
    return RecipeOut(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        ingredients=row["ingredients"],
        instructions=row["instructions"],
    )


@router.get(
    "",
    response_model=List[RecipeOut],
    summary="List recipes",
    description="Returns all recipes ordered by id descending.",
    operation_id="list_recipes",
)
def list_recipes() -> List[RecipeOut]:
    """List all recipes."""
    rows = db.fetch_all(
        """
        SELECT id, title, description, ingredients, instructions
        FROM recipes
        ORDER BY id DESC
        """
    )
    return [_row_to_recipe_out(r) for r in rows]


@router.post(
    "",
    response_model=RecipeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recipe",
    description="Creates a recipe and returns the created record.",
    operation_id="create_recipe",
)
def create_recipe(payload: RecipeCreate) -> RecipeOut:
    """Create a new recipe."""
    row = db.execute_returning_one(
        """
        INSERT INTO recipes (title, description, ingredients, instructions)
        VALUES (%s, %s, %s, %s)
        RETURNING id, title, description, ingredients, instructions
        """,
        (payload.title, payload.description, payload.ingredients, payload.instructions),
    )
    return _row_to_recipe_out(row)


@router.get(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Get recipe by id",
    description="Fetch a single recipe by its id.",
    operation_id="get_recipe",
)
def get_recipe(recipe_id: int) -> RecipeOut:
    """Get a recipe by id."""
    row = db.fetch_one(
        """
        SELECT id, title, description, ingredients, instructions
        FROM recipes
        WHERE id = %s
        """,
        (recipe_id,),
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return _row_to_recipe_out(row)


@router.put(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Update recipe",
    description="Replaces the recipe fields for the given id and returns the updated record.",
    operation_id="update_recipe",
)
def update_recipe(recipe_id: int, payload: RecipeUpdate) -> RecipeOut:
    """Update a recipe by id."""
    row = db.execute_returning_one(
        """
        UPDATE recipes
        SET title = %s,
            description = %s,
            ingredients = %s,
            instructions = %s
        WHERE id = %s
        RETURNING id, title, description, ingredients, instructions
        """,
        (
            payload.title,
            payload.description,
            payload.ingredients,
            payload.instructions,
            recipe_id,
        ),
    )
    # If id doesn't exist, RETURNING yields 0 rows; db layer raises.
    # Convert that into a 404 for API correctness.
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return _row_to_recipe_out(row)


@router.delete(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Delete recipe",
    description="Deletes a recipe by id and returns the deleted record.",
    operation_id="delete_recipe",
)
def delete_recipe(recipe_id: int) -> RecipeOut:
    """Delete a recipe by id."""
    try:
        row = db.execute_returning_one(
            """
            DELETE FROM recipes
            WHERE id = %s
            RETURNING id, title, description, ingredients, instructions
            """,
            (recipe_id,),
        )
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return _row_to_recipe_out(row)
