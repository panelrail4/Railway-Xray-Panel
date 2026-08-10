# 1.0.7

- Rebuilt around the working `Xhttp-main` Railway model: client-side TLS/SNI at Railway Edge, Xray origin without TLS.
- Corrected Xray VLESS inbound key to `settings.clients`.
- Corrected Xray transport field to `streamSettings.network`.
- Added Nginx path dispatch for XHTTP, WebSocket, HTTPUpgrade and gRPC.
- Added anti-buffering / long-timeout settings for HTTP transports.
- Added per-user, per-inbound TLS and plain variants.
- Added QR generation for individual links and subscriptions.
- Added Railway-focused UI guidance and deployment documentation.
- Pinned Xray 26.6.27 instead of using a moving `latest` URL.

## 1.0.8 — Ubuntu 24.04 + SSH administration
- Runtime image changed from `python:3.12-slim` to **Ubuntu 24.04**.
- Added OpenSSH Server with configurable SSH port (default `2222`).
- Added root SSH login and a configurable non-root sudo user.
- Added password configuration through Railway variables: `SSH_ROOT_PASSWORD`, `SSH_USER`, `SSH_USER_PASSWORD`.
- If passwords are omitted, strong credentials are generated and stored at `/data/ssh/generated_credentials.txt`.
- Added common Ubuntu administration/networking/development tools: git, curl, wget, nano, vim, jq, iproute2, ping, DNS tools, traceroute, tcpdump, lsof, htop, rsync, socat, netcat, openssl and build-essential.
- Python dependencies now run in `/opt/venv` to remain compatible with Ubuntu 24.04's externally-managed Python environment.
- Existing XPanel, Xray, Nginx, users, inbounds, subscriptions, links and QR functionality is retained.

## 1.0.9
- Preserved Ubuntu 24.04 runtime, XPanel, Xray transports, subscriptions, QR and SSH.
- Added explicit dual-path SSH networking documentation.
- Documented Railway limitation: public domains are HTTP/HTTPS and cannot provide raw SSH on external port 2233.
- Kept native SSH through Railway TCP Proxy as the primary fallback.
- Added optional `SSH_PUBLIC_LABEL_PORT=2233` as a documentation/label variable; it does not override Railway's externally assigned TCP proxy port.
