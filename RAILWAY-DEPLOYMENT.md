# Railway Deployment — XPanel 1.0.7

## Variables

Recommended:

```text
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
SECRET_KEY=<long-random-secret>
PUBLIC_HOST=<your-service>.up.railway.app
RAILWAY_EDGE_TLS=true
XRAY_START_ON_BOOT=true
```

`PUBLIC_HOST` مهم است چون پنل از آن برای ساخت SNI و لینک‌های VLESS استفاده می‌کند.

## Port model

Railway یک public HTTP port به Service می‌دهد. داخل کانتینر:

- `$PORT` → Nginx
- `127.0.0.1:8000` → FastAPI panel
- `127.0.0.1:10000+` → Xray inbounds

Nginx بر اساس path، ترافیک را به inbound مربوط می‌فرستد.

## First test

اول فقط این inbound را بساز:

```text
Protocol: VLESS
Transport: XHTTP
Security: TLS (Railway Edge)
Path: /xhttp
```

بعد User بساز و از صفحه Users لینک `Railway TLS` را بردار.

در v2rayNG باید TLS روشن باشد و SNI برابر Public Domain باشد.

اگر XHTTP همین نسخه کار کرد، سپس WS را تست کن. gRPC را بعد از آن تست کن.

## SSH networking note (v1.0.9)

Native SSH requires Railway TCP Proxy. A Railway public HTTP/HTTPS domain cannot expose raw SSH on an arbitrary external port such as 2233. If you want `2233`, set `SSH_PORT=2233` as the internal listening port and create the TCP Proxy for that internal port; Railway still chooses the external proxy port.

A custom hostname may CNAME to the Railway TCP proxy hostname, but the Railway-assigned proxy port remains required.
