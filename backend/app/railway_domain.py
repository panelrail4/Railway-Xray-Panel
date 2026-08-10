"""Railway public-domain bootstrap.

Railway does not create a service domain merely because an application is
running. The Railway Public API can create the *.up.railway.app domain via
serviceDomainCreate. This module uses that API only when a Railway API token
is explicitly available; otherwise it safely uses Railway's injected
RAILWAY_PUBLIC_DOMAIN value when a domain has already been assigned.
"""
import json
import os
import urllib.request
from pathlib import Path

DOMAIN_FILE = Path('/data/railway_public_domain')
GRAPHQL_URL = 'https://backboard.railway.com/graphql/v2'


def get_public_domain() -> str:
    for key in ('RAILWAY_PUBLIC_DOMAIN', 'PUBLIC_HOST'):
        value = (os.getenv(key) or '').strip()
        if value:
            return value.removeprefix('https://').removeprefix('http://').rstrip('/')
    try:
        value = DOMAIN_FILE.read_text(encoding='utf-8').strip()
        if value:
            return value
    except OSError:
        pass
    return ''


def _api_token() -> str:
    return (os.getenv('RAILWAY_API_TOKEN') or os.getenv('RAILWAY_TOKEN') or '').strip()


def ensure_public_domain() -> str:
    """Return the public domain, creating a Railway-provided domain if needed.

    No domain value is hard-coded. The API requires a user/project token for
    infrastructure mutations; without one, this function does not pretend it
    can provision a domain and simply returns the currently available value.
    """
    existing = get_public_domain()
    if existing:
        return existing

    token = _api_token()
    service_id = (os.getenv('RAILWAY_SERVICE_ID') or '').strip()
    environment_id = (os.getenv('RAILWAY_ENVIRONMENT_ID') or '').strip()
    if not token or not service_id or not environment_id:
        return ''

    query = '''mutation serviceDomainCreate($input: ServiceDomainCreateInput!) {
      serviceDomainCreate(input: $input) { id domain targetPort }
    }'''
    payload = json.dumps({
        'query': query,
        'variables': {'input': {
            'serviceId': service_id,
            'environmentId': environment_id,
        }}
    }).encode('utf-8')
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Railway-XPanel/1.0.10',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = json.loads(response.read().decode('utf-8'))
        data = body.get('data', {}).get('serviceDomainCreate') or {}
        domain = (data.get('domain') or '').strip()
        if domain:
            DOMAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
            DOMAIN_FILE.write_text(domain, encoding='utf-8')
            os.environ['RAILWAY_PUBLIC_DOMAIN'] = domain
            return domain
    except Exception as exc:
        print(f'[railway-domain] automatic domain provisioning failed: {exc}', flush=True)
    return ''
