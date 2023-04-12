from pydantic import BaseModel
from enum import Enum
from typing import List, Text, Optional


class UserBase(BaseModel):
    username: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool


class TweetGroup(BaseModel):
    name: str
    users: List[str]

    # class Config:
    #     orm_mode = True


class TweetBase(TweetGroup):
    id: int


class ChatsCreate(BaseModel):
    chats: Text
    access: str


class Chat(ChatsCreate):
    id: int


class Likes(str, Enum):
    like = "like"
    unlike = 'unlike'


class LikeInfo(BaseModel):
    id: int
    likes: Likes


class Comments(BaseModel):
    id: int
    comment: Optional[Text] = None


class SubComment(BaseModel):
    tweet_id: int
    comment_id: int
    comment: Optional[Text] = None
