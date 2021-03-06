from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuth, OAuthError


from fastapi import Depends, FastAPI
from starlette.middleware.sessions import SessionMiddleware

test_router = FastAPI(
    title = "test",
    description = "test",
    docs_url = "/v1/api",
    openapi_url = "/openapi.json"
)

test_router.add_middleware(SessionMiddleware, secret_key='!secret')

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
    path = "/v1",
    include_in_schema = False
)
async def homepage(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url = "/v1/login")
    return RedirectResponse(url="/v1/api")

@test_router.get(
    path = "/v1/login",
    include_in_schema = False
)
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@test_router.route('/v1/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        parse_user = await oauth.google.parse_id_token(request, token)
    except OAuthError as error:
        print("error")
        return {"Msg": error}
    user = parse_user.get('email')
    if user:
        request.session['user'] = user
    return RedirectResponse(url='/v1/api')

@test_router.get(
    path = "/vi/api/hello",
    tags = ["Test"]
)
def get_common():
    return {"Welcome msg": "Hello world"}

@test_router.get(
    path = "/v1/api/hello/{id}",
    tags = ["Test"]
)
def get_common(id, request: Request):
    user = request.session.get('user')
    if user == id:
        return {"Welcome msg": f"Hello world {id}"}
    else:
        return {"Msg": "Access denied", "user": user}