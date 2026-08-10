import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Inbound
from ..schemas.inbound import InboundCreate, InboundResponse
from ..security import require_admin
from ..xray.transports import validate_combination
from ..xray.runtime import rebuild_and_restart
from ..xray.nginx import write_nginx_config

router = APIRouter(prefix='/api/inbounds', tags=['inbounds'])

@router.get('', response_model=list[InboundResponse])
def list_inbounds(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Inbound).order_by(Inbound.id.desc()).all()

@router.post('', response_model=InboundResponse)
def create_inbound(data: InboundCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    transport = data.transport.strip().lower()
    security = data.security.strip().lower()
    protocol = data.protocol.strip().lower()

    try:
        validate_combination(transport, security)
    except ValueError as e:
        raise HTTPException(422, str(e))

    if protocol != 'vless':
        raise HTTPException(422, 'This XPanel build currently creates VLESS inbounds only.')

    defaults = {'xhttp': '/xray', 'websocket': '/ws', 'grpc': '/grpc', 'httpupgrade': '/upgrade'}
    path = (data.path or defaults.get(transport, '')).strip()
    if path and not path.startswith('/'):
        path = '/' + path

    requested_port = max(int(data.listen_port), 10000) if transport in ('xhttp','websocket','grpc','httpupgrade') else int(data.listen_port)
    used = {p for (p,) in db.query(Inbound.listen_port).filter(Inbound.enabled.is_(True)).all()}
    while requested_port in used:
        requested_port += 1

    i = Inbound(
        name=data.name.strip() or f'{transport}-{requested_port}',
        protocol=protocol,
        transport=transport,
        security=security,
        listen_host='127.0.0.1' if transport in ('xhttp','websocket','grpc','httpupgrade') else '0.0.0.0',
        listen_port=requested_port,
        path=path or None,
        flow=data.flow.strip() if data.flow and data.flow.strip() else None,
        settings_json=json.dumps(data.settings or {}),
    )
    db.add(i)
    db.commit()
    db.refresh(i)

    try:
        result = rebuild_and_restart(db)
        if result.get('status') == 'error':
            raise HTTPException(422, f"Xray configuration/start failed:\n{result.get('error') or 'unknown Xray error'}")
        try:
            write_nginx_config(db)
        except Exception as e:
            raise HTTPException(500, f"Nginx configuration failed:\n{e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Inbound creation failed:\n{e}")

    return i

@router.delete('/{inbound_id}')
def delete_inbound(inbound_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    i = db.get(Inbound, inbound_id)
    if not i:
        raise HTTPException(404, 'Inbound not found')
    db.delete(i)
    db.commit()
    result = rebuild_and_restart(db)
    try:
        write_nginx_config(db)
    except Exception as e:
        return {'deleted': True, 'xray': result, 'nginx_error': str(e)}
    return {'deleted': True, 'xray': result}
