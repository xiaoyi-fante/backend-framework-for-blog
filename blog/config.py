schema = 'mysql+pymysql'
username = 'root'
password = 'asdf1234'
host = '127.0.0.1'
port = 3306
database = 'blog'
params = 'charset=utf8'

SQLURL = '{}://{}:{}@{}:{}/{}?{}'.format(
    schema, username, password, host, port, database, params
)

SQLDEBUG = True

WSIP = '127.0.0.1'
WSPORT = 9000

AUTH_SECRET = 'WWW.magedu.CoM'
AUTH_EXPIRE = 8 * 60 * 60