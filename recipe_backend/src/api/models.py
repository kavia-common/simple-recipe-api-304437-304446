from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    """Shared fields for recipe payloads."""
    title: str = Field(..., min_length=1, max_length=200, description="Recipe title.")
    description: str = Field(
        ..., min_length=1, max_length=2000, description="Short description of the recipe."
    )
    ingredients: str = Field(
        ...,
        min_length=1,
        description="Ingredients list (free-form text).",
    )
    instructions: str = Field(
        ...,
        min_length=1,
        description="Cooking steps/instructions (free-form text).",
    )


class RecipeCreate(RecipeBase):
    """Payload to create a recipe."""
    pass


class RecipeUpdate(RecipeBase):
    """Payload to update a recipe (full replacement for MVP simplicity)."""
    pass


class RecipeOut(RecipeBase):
    """Recipe representation returned by API."""
    id: int = Field(..., description="Recipe primary key.")
