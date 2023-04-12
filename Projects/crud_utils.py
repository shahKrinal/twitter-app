from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(username=user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_tweet(db: Session, current_user: schemas.User, tweet: schemas.TweetGroup):
    obj = db.query(models.User).filter(models.User.username == current_user).first()
    if obj.group:
        return obj.group
    tweet_grp = models.Tweet(name=tweet.name, user=obj)
    db.add(tweet_grp)
    db.commit()
    db.refresh(tweet_grp)
    return tweet_grp


def create_members(tweet_grp, db: Session, tweet: schemas.TweetGroup):
    import ipdb;
    ipdb.set_trace()
    member_list = []
    for member in tweet.users:
        member_obj = db.query(models.User).filter(models.User.username == member).first()
        if member_obj:
            obj = db.query(models.TweetMembers).filter(models.TweetMembers.members == member_obj,
                                                       models.TweetMembers.grp == tweet_grp).first()
            if not obj:
                grp_obj = models.TweetMembers(members=member_obj, grp=tweet_grp)
                db.add(grp_obj)
                db.commit()
                db.refresh(grp_obj)
                member_list.append(grp_obj)
            else:
                member_list.append(obj)
        else:
            return None
    return member_list


def create_chats(db: Session, current_user: schemas.User, tweet: schemas.ChatsCreate):
    user = db.query(models.User).filter(models.User.username == current_user).first()
    tweet_obj = models.Tweets(chats=tweet.chats, access=tweet.access, user=user)
    db.add(tweet_obj)
    db.commit()
    db.refresh(tweet_obj)
    return tweet_obj


def get_public_tweets(db: Session, id: int, like: schemas.Likes, current_user: schemas.User):
    if like:
        tweet_obj = db.query(models.Tweets).filter(models.Tweets.id == id).first()
        user = db.query(models.User).filter(models.User.username == current_user).first()
        like_obj = db.query(models.Like).filter(models.Like.tweet == tweet_obj, models.Like.user == user).first()
        if like_obj:
            if like == 'like':
                if like_obj.count == 0:
                    like_obj.count += 1
                    db.commit()
            else:
                like_obj.count -= 1
                db.commit()
        else:
            like = models.Like(tweet=tweet_obj, user=user, count=1)
            db.add(like)
            db.commit()
            db.refresh(like)
    public_tweets = db.query(models.Tweets).filter(models.Tweets.access == 'public')
    tweets = []
    for tweet in public_tweets:
        like_objects = db.query(models.Like).filter(models.Like.tweet == tweet)
        count = 0
        for likes in like_objects:
            if likes.count:
                count += 1
        tweets.append({'tweet': tweet, 'like': count})

    return tweets


def get_private_tweets(db: Session, current_user: schemas.User, id: int, like: schemas.Likes):
    if like:
        tweet_obj = db.query(models.Tweets).filter(models.Tweets.id == id).first()
        user = db.query(models.User).filter(models.User.username == current_user).first()
        like_obj = db.query(models.Like).filter(models.Like.tweet == tweet_obj, models.Like.user == user).first()
        if like_obj:
            if like == 'like':
                if like_obj.count == 0:
                    like_obj.count += 1
                    db.commit()
            else:
                like_obj.count -= 1
                db.commit()
        else:
            like = models.Like(tweet=tweet_obj, user=user, count=1)
            db.add(like)
            db.commit()
            db.refresh(like)
    tweets = db.query(models.Tweets).filter(models.Tweets.access == 'private')
    obj1 = db.query(models.User).filter(models.User.username == current_user).first()
    tweet_list = []
    for tweet in tweets:
        tweets = []
        like_objects = db.query(models.Like).filter(models.Like.tweet == tweet)
        count = 0
        for likes in like_objects:
            if likes.count:
                count += 1
        tweets.append({'likes': count})

        user = tweet.user
        grp = user.group.grp_members
        for member in grp:
            if member.members == obj1:
                tweet_list.append(
                    {'tweet_id': tweet.id, 'grp_name': user.group.name, 'chats': tweet.chats,
                     'user': tweet.user.username, 'likes': tweets})
        if current_user == user.username:
            tweet_list.append(
                {'grp_name': user.group.name, 'chats': tweet.chats, 'user': tweet.user.username, 'likes': likes})
    return tweet_list


def create_comments(db: Session, current_user: schemas.User, comments: schemas.Comments):
    if comments.id:
        tweet_obj = db.query(models.Tweets).filter(models.Tweets.id == comments.id).first()
        if comments.comment:
            user = db.query(models.User).filter(models.User.username == current_user).first()
            comment_obj = models.Comments(tweet=tweet_obj, user=user, comment=comments.comment)
            db.add(comment_obj)
            db.commit()
            db.refresh(comment_obj)
        comments = db.query(models.Comments).filter(models.Comments.tweet == tweet_obj)
        return comments.all()


def create_sub_comments(db: Session, current_user: schemas.User, comments: schemas.SubComment):
    if comments:
        tweet_obj = db.query(models.Tweets).filter(models.Tweets.id == comments.tweet_id).first()
        comment_obj = db.query(models.Tweets).filter(models.Comments.id == comments.comment_id).first()
        user = db.query(models.User).filter(models.User.username == current_user).first()
        comment = models.Comments(tweet=tweet_obj, user=user, comment=comments.comment,parent =comment_obj)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
