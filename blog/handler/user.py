# User 操作
import pymysql
from fanteweb import FanteWeb
import jwt
import bcrypt
from webob import exc
from ..config import AUTH_EXPIRE, AUTH_SECRET
from ..util import jsonify
from ..model import session, User
import datetime

user_router = FanteWeb.Router('/user')

def gen_token(user_id):
    return jwt.encode({
        'user_id':user_id,
        'timestamp': int(datetime.datetime.now().timestamp())
    }, AUTH_SECRET, 'HS256').decode()

@user_router.post('/reg')
def reg(ctx, request:FanteWeb.Request):
    payload = request.json
    print(payload, type(payload))
    email = payload.get('email')

    query = session.query(User).filter(User.email == email).first()
    if query:
        raise exc.HTTPConflict()

    user = User()
    try:
        user.name = payload['name']
        user.email = email
        user.password = bcrypt.hashpw(payload['password'].encode(), bcrypt.gensalt())
    except Exception as e:
        print(e)
        raise exc.HTTPBadRequest()

    session.add(user)
    try:
        session.commit()

        return jsonify(user={
            'id':user.id,
            'name':user.name
        }, token=gen_token(user.id))
    except Exception as e:
        session.rollback()
        raise exc.HTTPInternalServerError()

@user_router.post('/login')
def login(ctx, request:FanteWeb.Request):
    print(request)
    print(request.json)
    payload = request.json

    # 用户email验证
    email = payload.get('email')
    user = session.query(User).filter(User.email == email).first()
    if user and bcrypt.checkpw(payload['password'].encode(), user.password.encode()):
        return jsonify(user={
            'id':user.id,
            'name':user.name
        }, token=gen_token(user.id))
    else:
        raise exc.HTTPUnauthorized()

# @user_router.reg_preinterceptor
def authenticate(handler):
    def wrapper(ctx, request:FanteWeb):
        try:
            jwtstr = request.headers.get('Jwt')
            payload = jwt.decode(jwtstr, AUTH_SECRET, algorithms=['HS256'])

            # 时间问题，过期
            if (datetime.datetime.now().timestamp() - payload.get('timestamp', 0)) > AUTH_EXPIRE:
                raise exc.HTTPUnauthorized()

            user_id = payload.get('user_id', -1)
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise exc.HTTPUnauthorized()

            request.user = user

        except Exception as e:
            raise exc.HTTPUnauthorized()
        return handler(ctx, request)
    return wrapper
