from fastapi import Depends, FastAPI, HTTPException, Request, Response, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine
from sqladmin import Admin

import crud_utils, models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

admin = Admin(app, engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    import ipdb;
    ipdb.set_trace()
    username = crud_utils.get_user_by_username(db=db, username=user.username)
    if username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    return crud_utils.create_user(db=db, user=user)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(db: Session = Depends(get_db), username: str = Depends()):
    db: Session
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        user_dict = user.username
        return user.username


def fake_decode_token(db, token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(db, token)
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    hashed_password = form_data.password + "notreallyhashed"
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/users_all/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               current_user: schemas.User = Depends(get_current_active_user)):
    users = crud_utils.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/tweet_grp/")
def create_tweet_grp(user: schemas.TweetGroup, db: Session = Depends(get_db),
                     current_user: schemas.User = Depends(get_current_active_user)):
    tweet_grp = crud_utils.create_tweet(db=db, current_user=current_user, tweet=user)
    if tweet_grp:
        return crud_utils.create_members(tweet_grp, db=db, tweet=user)


@app.post('/tweet')
def create_chats(tweet: schemas.ChatsCreate, current_user: schemas.User = Depends(get_current_active_user),
                 db: Session = Depends(get_db)):
    return crud_utils.create_chats(db=db, current_user=current_user, tweet=tweet)


@app.get("/tweet/public_tweet/")
def read_users(id: int = None, like: schemas.Likes = None, db: Session = Depends(get_db),
               current_user: schemas.User = Depends(get_current_active_user)):
    tweets = crud_utils.get_public_tweets(db=db, id=id, like=like, current_user=current_user)
    return tweets


@app.get("/private_tweet/")
def read_users(id: int = None, like: schemas.Likes = None, db: Session = Depends(get_db),
               current_user: schemas.User = Depends(get_current_active_user)):
    tweets = crud_utils.get_private_tweets(db=db, id=id, like=like, current_user=current_user)
    return tweets


@app.post("/comments/{tweet_id}/")
def comments(comment: schemas.Comments, current_user: schemas.User = Depends(get_current_active_user),
             db: Session = Depends(get_db),
             ):
    comments = crud_utils.create_comments(db=db, current_user=current_user, comments=comment)
    return comments


@app.post("/sub_comments/{tweet_id}{comment_id}/")
def sub_comments(comment: schemas.SubComment, current_user: schemas.User = Depends(get_current_active_user),
                 db: Session = Depends(get_db)):
    comments = crud_utils.create_sub_comments(db=db, current_user=current_user, comments=comment)
    return comments
