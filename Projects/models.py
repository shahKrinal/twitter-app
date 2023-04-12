from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text, Enum, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users_tab"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    group = relationship("Tweet", uselist=False, back_populates="user")
    member = relationship("TweetMembers", back_populates="members")
    tweets = relationship("Tweets", back_populates="user")
    like = relationship("Like", back_populates="user")
    comments = relationship("Comments", back_populates="user")


class Tweet(Base):
    __tablename__ = "tweet1"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users_tab.id"), nullable=True)
    user = relationship("User", back_populates="group")
    grp_members = relationship("TweetMembers", back_populates="grp")


class TweetMembers(Base):
    __tablename__ = "members_data"
    id = Column(Integer, primary_key=True, index=True)
    members = relationship("User", back_populates="member")
    grp = relationship("Tweet", back_populates="grp_members")
    user_id = Column(Integer, ForeignKey("users_tab.id"), nullable=True)
    grp_id = Column(Integer, ForeignKey("tweet1.id"), nullable=True)


class Tweets(Base):
    __tablename__ = "tweet"
    id = Column(Integer, primary_key=True, index=True)
    access = Column(Enum("public", "private", name="access_type"))
    chats = Column(Text)
    user_id = Column(Integer, ForeignKey("users_tab.id"), nullable=True)
    user = relationship("User", back_populates="tweets")
    likes = relationship("Like", back_populates="tweet")
    comments = relationship("Comments", back_populates="tweet")


class Like(Base):
    __tablename__ = "like"
    id = Column(Integer, primary_key=True, index=True)
    tweet = relationship("Tweets", back_populates="likes")
    tweet_id = Column(Integer, ForeignKey("tweet.id"), nullable=True)
    user = relationship("User", back_populates="like")
    user_id = Column(Integer, ForeignKey("users_tab.id"), nullable=True)
    count = Column(Integer)


class Comments(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, index=True)
    tweet = relationship("Tweets", back_populates="comments")
    tweet_id = Column(Integer, ForeignKey("tweet.id"), nullable=True)
    user = relationship("User", back_populates="comments")
    user_id = Column(Integer, ForeignKey("users_tab.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("comment.id"))
    parent = relationship('Comments', remote_side=[id])
    comment = Column(Text)
