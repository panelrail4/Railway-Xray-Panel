# Changelog

## 1.1.0
- Reworked Railway HTTP ingress to preserve the proven XHTTP-over-Railway model from Xhttp-main: client TLS/SNI terminates at Railway Edge and Xray receives clear HTTP inside the container.
- HTTP transports (XHTTP/WS/gRPC/HTTPUpgrade) always generate Railway Public Domain links instead of incorrectly selecting the raw TCP Proxy endpoint.
- Nginx now reloads automatically after inbound changes.
- XHTTP proxying uses HTTP/1.1, disabled request/response buffering and long-lived timeouts.
- Xray HTTP transport listeners are bound privately behind Nginx; raw/TCP listeners remain available for TCP Proxy use.
- Ubuntu 24.04 remains the actual runtime image with OpenSSH, sudo and administration/networking tools.
- SSH continues to listen on the internal SSH_PORT (default 2222) and can be exposed through Railway TCP Proxy.
- Fixed startup ordering and health behavior so the panel, Xray and Nginx can coexist reliably.
- Automatic Railway domain provisioning remains supported through Railway's official GraphQL API when RAILWAY_API_TOKEN is supplied.
