from fanteweb import FanteWeb
from .user import authenticate
from webob import exc
from ..util import jsonify, validate
from ..model import Post, Content, session, Dig,Tag,Post_tag
import datetime,math,re

post_router = FanteWeb.Router('/post')

@post_router.post('/')
@authenticate
def pub(ctx, request:FanteWeb.Request):
    payload = request.json


    try:
        title = payload['title']
        tags = re.split('[\s,]+', payload.get('tags', ''))
        c = payload['content']
    except Exception as e:
        raise exc.HTTPBadRequest()

    post = Post()
    post.author_id = request.user.id
    post.title = title
    post.postdate = datetime.datetime.now()
    content = Content()
    content.content = c
    post.content = content

    session.add(post)

    # 标签
    for tag in tags:
        t = session.query(Tag).filter(Tag.tag == tag).first()
        if not t:
            t = Tag()
            t.tag = tag
            session.add(t)

        pt = Post_tag()
        pt.tag = t
        pt.post = post
        session.add(pt)

    try:
        session.commit()
        return jsonify(post_id=post.id)
    except Exception as e:
        session.rollback()
        raise exc.HTTPInternalServerError()

@post_router.get('/{id:int}')
def get(ctx, request:FanteWeb.Request):
    post_id = request.vars.id

    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise exc.HTTPNotFound()

    post.hits += 1
    session.add(post)
    try:
        session.commit()
    except:
        session.rollback()

    print(post.postdate)

    # 博文详情页增加点赞功能
    bury_info, dig_info = get_digbury_info(post_id)

    # tag显示
    taglist = session.query(Post_tag).filter(Post_tag.post_id == post_id).all()
    tags = " ".join([x.tag.tag for x in taglist])

    return jsonify(post={
        'id':post_id,
        'title':post.title,
        'author': post.author.name,
        'postdate':post.postdate.timestamp(),
        'content':post.content.content
    }, diginfo=dig_info, buryinfo=bury_info, tags=tags)

# 博文详情页增加点赞功能
def get_digbury_info(post_id):
    dig_query = session.query(Dig).filter(Dig.post_id == post_id)

    digs = dig_query.filter(Dig.state == 1)
    dig_count = digs.count()
    dig_list = digs.order_by(Dig.pubdate.desc()).limit(5).all()

    buries = dig_query.filter(Dig.state == 0)
    bury_count = buries.count()
    bury_list = buries.order_by(Dig.pubdate.desc()).limit(5).all()
    dig_info = {'count': dig_count, 'digs': [{'id': x.user_id, 'name': x.user.name} for x in dig_list]}
    bury_info = {'count': bury_count, 'buries': [{'id': x.user_id, 'name': x.user.name} for x in bury_list]}

    return bury_info, dig_info


@post_router.get('/')
@post_router.get('/u/{id:int}')
@post_router.get('/t/{tag:str')
def list(ctx, request:FanteWeb.Request):
    # try:
    #     page = request.params.get('page', 1)
    #     page = int(page)
    #     if page < 1:
    #         page = 1
    # except:
    #     page=1
    page = validate(request.params, 'page', int, 1, lambda x,y: x if x>0 else y)
    # try:
    #     size = request.params.get('size', 1)
    #     size = int(size)
    #     if size < 1 or size > 100:
    #         size = 1
    # except:
    #     size=20
    size = validate(request.params, 'size', int, 20, lambda x,y: x if 0<x<101 else y)

    query = session.query(Post)

    # 通过传入用户id来过滤数据
    try:
        user_id = validate({'id':request.vars.id}, 'id', int, -1, lambda x,y:x if x>0 else y)
    except:
        user_id = -1
    if user_id > 0:
        query = query.filter(Post.author_id == user_id)

    # 按照标签查询
    try:
        tagname = validate({'tag':request.vars.tag}, 'tag', str, "", lambda x,y:x if len(x) else y)
    except:
        tagname = ""
    if tagname:
        query = query.join(Post_tag).join(Tag).filter(Tag.tag == tagname)

    count = query.count() # 总记录数

    posts = query.order_by(Post.id.desc()).limit(size).offset(size*(page-1)).all()

    # 分页pagination
    pagecount = math.ceil(count / size) # 总页数

    return jsonify(posts=[{
        'id':post.id,
        'title':post.title,
        'postdate':post.postdate.timestamp()
    } for post in posts], pagination={
        'page':page,
        'count':count,
        'pagecount':pagecount,
        'size':size
    })


# 点赞、踩
def dig_or_bury(user_id, post_id, state):
    d = Dig()
    d.post_id = user_id
    d.user_id = post_id
    d.state = state
    d.pubdate = datetime.datetime.now()
    session.add(d)
    try:
        session.commit()
        return jsonify()
    except:
        session.rollback()
        return jsonify(500)

@post_router.put('/dig/{id:int}')
@authenticate
def dig(ctx, request:FanteWeb.Request):
    return dig_or_bury(request.user.id, request.vars.id, 1)

@post_router.put('/bury/{id:int}')
@authenticate
def bury(ctx, request:FanteWeb.Request):
    return dig_or_bury(request.user.id, request.vars.id, 0)








