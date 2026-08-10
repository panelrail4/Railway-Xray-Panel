import base64, os, secrets, json
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from ..models.subscription import Subscription
from ..models.user import User
from ..models.inbound import Inbound
from ..security import require_admin
from ..database import get_db
from ..railway_domain import get_public_domain, resolve_public_domain

router = APIRouter(tags=['subscriptions'])


def endpoint(inbound: Inbound, request=None):
    """Return the correct public endpoint for the selected transport.

    Railway HTTP Public Networking is the compatibility path for XHTTP/WS/
    gRPC/HTTPUpgrade: the client connects with TLS/SNI to the Railway domain,
    Railway terminates HTTPS, and Nginx forwards clear HTTP to Xray. A raw TCP
    Proxy is used only for transports that actually need raw TCP (for example
    REALITY or a direct TCP/TLS inbound).
    """
    transport = (inbound.transport or '').lower()
    tcp_domain = os.getenv('RAILWAY_TCP_PROXY_DOMAIN')
    tcp_port = os.getenv('RAILWAY_TCP_PROXY_PORT')
    public = resolve_public_domain(request)

    if transport in ('xhttp', 'websocket', 'grpc', 'httpupgrade'):
        if public:
            return public, 443, 'railway'
        raise HTTPException(409, 'Railway Public Domain is not available yet.')

    if tcp_domain and tcp_port:
        return tcp_domain, int(tcp_port), 'tcp'
    if public:
        return public, 443, 'railway'
    raise HTTPException(409, 'No public endpoint is available.')


def _client_security(inbound: Inbound) -> str:
    # `security` is the security requested by the client. On Railway edge TLS,
    # the server-side Xray transport is deliberately `none` because Railway
    # already terminates HTTPS before the container.
    return (inbound.security or 'none').lower()


def make_uri(user: User, inbound: Inbound, variant: str = 'default', request=None):
    host, port, kind = endpoint(inbound, request)
    security = _client_security(inbound)

    if security == 'reality' and kind != 'tcp':
        raise HTTPException(409, 'REALITY requires a direct TCP endpoint/TCP Proxy; Railway HTTP ingress cannot carry REALITY.')

    params = {'encryption': 'none', 'type': inbound.transport}
    custom = {}
    try:
        custom = json.loads(inbound.settings_json or '{}')
    except Exception:
        pass

    if inbound.transport == 'grpc':
        params['serviceName'] = inbound.path or 'grpc'
    elif inbound.transport in ('xhttp', 'websocket', 'httpupgrade'):
        params['path'] = inbound.path or {
            'xhttp': '/xhttp', 'websocket': '/ws', 'httpupgrade': '/upgrade'
        }[inbound.transport]
    
    if inbound.transport == 'xhttp':
        xset = custom.get('xhttpSettings') or {}
        params['mode'] = xset.get('mode', 'auto')

    if security == 'reality':
        from ..xray.reality import reality_parameters
        rp = custom.get('realitySettings') or reality_parameters()
        server_names = rp.get('serverNames') or [rp.get('serverName', 'www.microsoft.com')]
        params.update({
            'security': 'reality',
            'sni': server_names[0],
            'fp': 'chrome',
            'pbk': rp.get('password') or rp.get('publicKey', ''),
            'sid': (rp.get('shortIds') or [rp.get('shortId', '')])[0],
        })
    elif security == 'tls':
        params.update({
            'security': 'tls',
            'sni': resolve_public_domain(request) or host,
            'fp': 'chrome',
        })
    else:
        params['security'] = 'none'
        if variant == 'plain-http' and kind == 'railway':
            port = 80

    # The old working deployment used TLS as a client-side switch while Xray
    # itself listened without TLS. `variant=edge-tls` explicitly preserves that
    # proven behavior.
    label = f'{user.username}-{inbound.name}'
    if variant == 'edge-tls' and kind == 'railway':
        params['security'] = 'tls'
        params['sni'] = resolve_public_domain(request) or host
        params['fp'] = 'chrome'
        port = 443
        label += '-TLS'

    query = '&'.join(f'{k}={quote(str(v), safe="")}' for k, v in params.items())
    return f'vless://{user.uuid}@{host}:{port}?{query}#{quote(label)}'


def active_links(user: User, db: Session, request=None):
    inbounds = db.query(Inbound).filter(Inbound.enabled.is_(True)).order_by(Inbound.id.desc()).all()
    if not inbounds:
        raise HTTPException(409, 'No enabled inbound exists')
    links = []
    for i in inbounds:
        try:
            links.append(make_uri(user, i, 'edge-tls', request))
        except HTTPException:
            continue
    if not links:
        raise HTTPException(409, 'No enabled inbound can produce a Railway-compatible link.')
    return links


@router.post('/api/subscriptions/{user_id}')
def create_subscription(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, 'User not found')
    links = active_links(user, db, request)
    token = secrets.token_urlsafe(32)
    sub = Subscription(user_id=user.id, token=token)
    db.add(sub); db.commit()
    public = resolve_public_domain(request)
    if not public:
        raise HTTPException(409, 'Railway public domain is not available yet.')
    url = f'https://{public}/sub/{token}'
    return {'token': token, 'url': url, 'links': links, 'uri': links[0]}


@router.get('/api/users/{user_id}/links')
def user_links(user_id: int, request: Request, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, 'User not found')
    inbounds = db.query(Inbound).filter(Inbound.enabled.is_(True)).all()
    result = []
    for i in inbounds:
        variants = {}
        for variant in ('edge-tls', 'plain-http'):
            try: variants[variant] = make_uri(user, i, variant, request)
            except HTTPException as e: variants[variant] = None
        result.append({'inbound_id': i.id, 'name': i.name, 'transport': i.transport, 'variants': variants})
    return {'user': {'id': user.id, 'username': user.username, 'uuid': user.uuid}, 'links': result}


@router.get('/api/users/{user_id}/inbounds/{inbound_id}/link')
def one_link(user_id: int, inbound_id: int, request: Request, variant: str = 'edge-tls', db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.get(User, user_id); inbound = db.get(Inbound, inbound_id)
    if not user or not inbound: raise HTTPException(404, 'User or inbound not found')
    return {'uri': make_uri(user, inbound, variant, request), 'variant': variant}


@router.get('/sub/{token}', response_class=PlainTextResponse)
def subscription(token: str, request: Request, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.token == token, Subscription.enabled.is_(True)).first()
    if not sub: raise HTTPException(404, 'Subscription not found')
    user = db.get(User, sub.user_id)
    if not user or not user.enabled: raise HTTPException(404, 'User disabled')
    links = active_links(user, db, request)
    return base64.b64encode(('\n'.join(links) + '\n').encode()).decode()
