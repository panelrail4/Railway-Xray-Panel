import os
from pathlib import Path
from sqlalchemy.orm import Session
from ..models import Inbound

NGINX_CONF = Path('/etc/nginx/conf.d/default.conf')


def _path(value: str | None, default: str) -> str:
    p = (value or default).strip()
    if not p.startswith('/'):
        p = '/' + p
    return p.rstrip('/') or '/'


def _common(location: str, upstream: int, kind: str) -> str:
    # Railway terminates public TLS before traffic reaches the container.
    # Xray therefore listens in cleartext; the client still uses TLS/SNI.
    lines = [
        f'location ^~ {location} {{',
        '    proxy_http_version 1.1;',
        '    proxy_set_header Host $host;',
        '    proxy_set_header X-Real-IP $remote_addr;',
        '    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '    proxy_set_header X-Forwarded-Proto https;',
        '    proxy_connect_timeout 10s;',
        '    proxy_read_timeout 3600s;',
        '    proxy_send_timeout 3600s;',
        '    client_body_timeout 3600s;',
        '    proxy_buffering off;',
        '    proxy_request_buffering off;',
        '    proxy_pass_request_headers on;',
    ]
    if kind in ('websocket', 'httpupgrade'):
        lines += [
            '    proxy_set_header Upgrade $http_upgrade;',
            '    proxy_set_header Connection "upgrade";',
        ]
    else:
        # XHTTP is HTTP-based and must not be forced into WebSocket upgrade mode.
        lines += [
            '    proxy_set_header Connection "";',
        ]
    lines += [f'    proxy_pass http://127.0.0.1:{int(upstream)};','}']
    return '\n'.join(lines)


def _grpc(location: str, upstream: int) -> str:
    # Kept as a dedicated grpc_pass route. Whether Railway preserves HTTP/2
    # to the container is platform-dependent; the panel labels this transport
    # accordingly instead of pretending it is universally supported.
    return '\n'.join([
        f'location ^~ {location} {{',
        '    grpc_read_timeout 3600s;',
        '    grpc_send_timeout 3600s;',
        '    grpc_set_header X-Real-IP $remote_addr;',
        '    grpc_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '    grpc_set_header X-Forwarded-Proto https;',
        f'    grpc_pass grpc://127.0.0.1:{int(upstream)};',
        '}',
    ])


def write_nginx_config(db: Session):
    # Always run the HTTP reverse proxy on Railway's externally exposed port.
    # This is the key difference from the old one-file XHTTP deployment: the
    # panel remains reachable while transport inbounds live on private ports.
    port = os.getenv('PORT', '8080')
    rows = db.query(Inbound).filter(Inbound.enabled.is_(True)).all()
    locations: list[str] = []
    seen: set[str] = set()

    for i in rows:
        transport = (i.transport or '').lower()
        if transport == 'xhttp':
            p = _path(i.path, '/xhttp')
            block = _common(p, i.listen_port, 'xhttp')
        elif transport == 'websocket':
            p = _path(i.path, '/ws')
            block = _common(p, i.listen_port, 'websocket')
        elif transport == 'httpupgrade':
            p = _path(i.path, '/upgrade')
            block = _common(p, i.listen_port, 'httpupgrade')
        elif transport == 'grpc':
            p = _path(i.path, '/grpc')
            block = _grpc(p, i.listen_port)
        else:
            continue
        if p in seen:
            continue
        seen.add(p)
        locations.append(block)

    lines = [
        'server {',
        f'    listen 0.0.0.0:{port} default_server;',
        '    server_name _;',
        '    client_max_body_size 0;',
        '    proxy_intercept_errors off;',
        '',
    ]
    lines += locations
    lines += [
        '',
        '    # Panel/API. Transport paths above take precedence.',
        '    location / {',
        '        proxy_http_version 1.1;',
        '        proxy_set_header Host $host;',
        '        proxy_set_header X-Real-IP $remote_addr;',
        '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '        proxy_set_header X-Forwarded-Proto https;',
        '        proxy_pass http://127.0.0.1:8000;',
        '    }',
        '}',
        '',
    ]
    NGINX_CONF.parent.mkdir(parents=True, exist_ok=True)
    NGINX_CONF.write_text('\n'.join(lines), encoding='utf-8')
    return True
