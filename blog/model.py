from sqlalchemy import Column,Integer,String,BigInteger,DateTime
from sqlalchemy import UniqueConstraint,ForeignKey,create_engine,PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT,TINYINT
from . import config

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False)
    email = Column(String(64), nullable=False, unique=True)
    password = Column(String(128), nullable=False)

    def __repr__(self):
        return "<User ({}, {})>".format(self.id, self.name)

class Post(Base):
    __tablename__ = "post"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False)
    postdate = Column(DateTime, nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    hits = Column(BigInteger, nullable=False, default=0, index=True) # 这个点击量这块，或者类似频繁写入的数据，并且是非关键数据，推荐放到redis中，然后每隔一段时间同步到数据库对应的字段上，从而减轻数据库的压力

    author = relationship('User')
    content = relationship('Content', userlist=False)

    def __repr__(self):
        return "<Post ({}, {})>".format(self.id, self.title)


class Content(Base):
    __tablename__ = 'content'

    id = Column(BigInteger, ForeignKey('post.id'), primary_key=True)
    content = Column(LONGTEXT, nullable=False)

    def __repr__(self):
        return "<Content ({}, {})>".format(self.id, self.content[:20])

class Dig(Base):
    __tablename__ = 'dig'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    post_id = Column(BigInteger, ForeignKey('post.id'), nullable=False)
    state = Column(TINYINT, nullable=False, default=0, comment="0 bury;1 dig")
    pubdate = Column(DateTime, nullable=False)

    user = relationship('user')
    __table_args__ = (UniqueConstraint('user_id', 'post_id'),)

class Tag(Base):
    __tablename__ = "tag"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tag = Column(String(16), nullable=False, unique=True)

class Post_tag(Base):
    __tablename__ = "post_tag"

    post_id = Column(BigInteger, ForeignKey('post.id'), nullable=False)
    tag_id = Column(BigInteger, ForeignKey('tag.id'), nullable=False)

    __table_args__ = (PrimaryKeyConstraint('post_id','tag_id'),)

    post = relationship('Post')
    tag = relationship('Tag')



engine = create_engine(config.SQLURL, echo=config.SQLDEBUG)

def createalltables():
    Base.metadata.create_all(engine)

def dropalltables():
    Base.metadata.drop_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


