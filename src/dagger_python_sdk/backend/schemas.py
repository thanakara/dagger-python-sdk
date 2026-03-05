from pydantic import BaseModel, ConfigDict, Field


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    """Provides field not provided by the client."""

    # Tells pydantic to read data from objects with attributes
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str
