# Changelog

## 1.1.4
- Fixed FastAPI startup failure caused by Request annotations on helper functions.
- Request is now injected only into FastAPI route handlers and passed explicitly to link-generation helpers.
- QR, user-link, one-link, and subscription endpoints preserve Railway public-domain fallback resolution.

1.1.0
- Reworked Railway HTTP ingress to preserve the proven XHTTP-over-Railway model from Xhttp-main: client TLS/SNI terminates at Railway Edge and Xray receives clear HTTP inside the container.
- HTTP transports (XHTTP/WS/gRPC/HTTPUpgrade) always generate Railway Public Domain links instead of incorrectly selecting the raw TCP Proxy endpoint.
- Nginx now reloads automatically after inbound changes.
- XHTTP proxying uses HTTP/1.1, disabled request/response buffering and long-lived timeouts.
- Xray HTTP transport listeners are bound privately behind Nginx; raw/TCP listeners remain available for TCP Proxy use.
- Ubuntu 24.04 remains the actual runtime image with OpenSSH, sudo and administration/networking tools.
- SSH continues to listen on the internal SSH_PORT (default 2222) and can be exposed through Railway TCP Proxy.
- Fixed startup ordering and health behavior so the panel, Xray and Nginx can coexist reliably.
- Automatic Railway domain provisioning remains supported through Railway's official GraphQL API when RAILWAY_API_TOKEN is supplied.

## 1.1.1
- Fixed inbound creation failure when no panel users exist by adding a non-advertised bootstrap VLESS client.
- Made inbound creation normalize transport/security values and validate Nginx before restarting Xray.
- Improved rollback and surfaced exact backend errors in the Inbounds page.

## 1.1.2
- Fixed inbound creation flow and exposed exact Xray/Nginx errors.
- Restored XHTTP defaults from the working Xhttp-main template (`/xray`, mode `auto`).
- Added explicit VLESS `encryption: none` and omitted empty client flow.
- Fixed schema defaults and response listen_host.
