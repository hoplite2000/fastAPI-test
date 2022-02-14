from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuth, OAuthError


from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

test_router = FastAPI(
    title = "test",
    description = "test",
    docs_url = "/api",
    openapi_url = "/openapi.json"
)

test_router.add_middleware(SessionMiddleware, secret_key='!secret')
user = None
config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@test_router.get(
    path = "/",
    include_in_schema = False
)
async def homepage(request: Request):
    global user
    user = request.session.get('user')
    print(user)
    if not user:
        return RedirectResponse(url = "/login")
    return RedirectResponse(url="/api")

@test_router.get(
    path = "/login",
    include_in_schema = False
)
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)

@test_router.route('/auth')
async def auth(request: Request):
    print(request)
    try:
        token = await oauth.google.authorize_access_token(request)
        parse_user = await oauth.google.parse_id_token(request, token)
        print(parse_user)
    except OAuthError as error:
        print("error")
        return {"Msg": error}
    user = parse_user.get('email')
    if user:
        request.session['user'] = user
    return RedirectResponse(url='/api')

@test_router.get(
    path = "/api/hello",
    tags = ["Test"]
)
def get_common():
    print(user)
    return {"Welcome msg": "Hello world"}

@test_router.get(
    path = "/api/hello/{id}",
    tags = ["Test"]
)
def get_common(id):
    if user == id:
        return {"Welcome msg": f"Hello world {id}"}
    else:
        return {"Msg": "Access denied"}
