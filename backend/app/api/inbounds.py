import json, os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.inbound import Inbound
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
    try:
        validate_combination(data.transport, data.security)
    except ValueError as e:
        raise HTTPException(422, str(e))

    # The Railway HTTP edge owns $PORT. Xray listeners therefore use private
    # ports; Nginx dispatches the HTTP transport by path.
    requested_port = data.listen_port
    if not (os.getenv('RAILWAY_TCP_PROXY_DOMAIN') and os.getenv('RAILWAY_TCP_PROXY_PORT')):
        if requested_port < 10000:
            requested_port = 10000
    used = {p for (p,) in db.query(Inbound.listen_port).filter(Inbound.enabled.is_(True)).all()}
    while requested_port in used:
        requested_port += 1

    path = data.path
    defaults = {'xhttp': '/xhttp', 'websocket': '/ws', 'grpc': '/grpc', 'httpupgrade': '/upgrade'}
    if data.transport in defaults and not path:
        path = defaults[data.transport]
    if path and not path.startswith('/'):
        path = '/' + path

    i = Inbound(
        name=data.name.strip(), protocol=data.protocol,
        transport=data.transport, security=data.security,
        listen_port=requested_port, path=path, flow=data.flow,
        settings_json=json.dumps(data.settings or {}),
    )
    db.add(i); db.commit(); db.refresh(i)
    try:
        result = rebuild_and_restart(db)
        if result.get('status') == 'error':
            db.delete(i); db.commit(); rebuild_and_restart(db)
            raise HTTPException(422, result.get('error'))
        write_nginx_config(db)
    except HTTPException:
        raise
    except Exception as e:
        db.delete(i); db.commit(); rebuild_and_restart(db)
        raise HTTPException(500, str(e))
    return i

@router.delete('/{inbound_id}')
def delete_inbound(inbound_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    i = db.get(Inbound, inbound_id)
    if not i: raise HTTPException(404, 'Inbound not found')
    db.delete(i); db.commit()
    result = rebuild_and_restart(db)
    write_nginx_config(db)
    return {'deleted': True, 'xray': result}
