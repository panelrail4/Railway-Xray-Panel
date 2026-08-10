import io
import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.subscription import Subscription
from ..models.user import User
from ..models.inbound import Inbound
from ..security import require_admin
from ..api.subscriptions import make_uri

router = APIRouter(prefix='/api/qr', tags=['qr'])


def _png(text: str):
    img = qrcode.make(text)
    buf = io.BytesIO(); img.save(buf, format='PNG')
    return Response(buf.getvalue(), media_type='image/png')


@router.get('/link')
def qr_link(user_id: int, inbound_id: int, variant: str = 'edge-tls', db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.get(User, user_id); inbound = db.get(Inbound, inbound_id)
    if not user or not inbound: raise HTTPException(404, 'User or inbound not found')
    return _png(make_uri(user, inbound, variant))


@router.get('/subscription/{token}')
def qr_subscription(token: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    sub = db.query(Subscription).filter(Subscription.token == token).first()
    if not sub: raise HTTPException(404, 'Subscription not found')
    user = db.get(User, sub.user_id)
    if not user: raise HTTPException(404, 'User not found')
    # A subscription QR is represented by its first compatible link; clients
    # that support subscription URLs should use the text URL instead.
    from ..api.subscriptions import active_links
    links = active_links(user, db)
    return _png(links[0])
