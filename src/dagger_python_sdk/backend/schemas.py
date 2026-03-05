from datetime import datetime

from pydantic import Field, EmailStr, BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    user_id: int  # TODO: TEMP for now


class PostResponse(PostBase):
    """Provides field not provided by the client."""

    # Tells pydantic to read data from objects with attributes
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
