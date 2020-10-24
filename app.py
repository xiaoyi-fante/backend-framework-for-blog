from blog import config
from fanteweb import FanteWeb
from blog.handler.post import post_router
from blog.handler.user import user_router

if __name__ == '__main__':
    application = FanteWeb()

    # 路由注册
    application.register(user_router)
    application.register(post_router)

    from wsgiref import simple_server
    server = simple_server.make_server(config.WSIP, config.WSPORT, application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()