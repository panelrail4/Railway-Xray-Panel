# Automatic Railway Public Domain

Railway-provided domains are not automatically created for every service. This
project therefore does two things:

1. If Railway has already assigned `RAILWAY_PUBLIC_DOMAIN`, the panel uses it
   automatically. No domain value needs to be entered in XPanel.
2. If no domain exists, XPanel can call Railway's official GraphQL API
   `serviceDomainCreate` during startup and create a `*.up.railway.app` domain.

For (2), Railway's API requires an authenticated token. Set only this secret:

`RAILWAY_API_TOKEN=<your Railway API token>`

The service and environment IDs are read automatically from Railway's injected
`RAILWAY_SERVICE_ID` and `RAILWAY_ENVIRONMENT_ID` variables. No public-domain
value is entered manually.

This limitation is imposed by Railway's platform: the running container cannot
create infrastructure resources without an authenticated API request. The
official API documents `serviceDomainCreate` for creating a Railway-provided
service domain.


## v1.1.0 behavior
For HTTP transports, generated links always use `RAILWAY_PUBLIC_DOMAIN` on port 443. `RAILWAY_TCP_PROXY_DOMAIN/PORT` is intentionally not selected for XHTTP, WS, gRPC or HTTPUpgrade because those links rely on Railway HTTPS edge termination.
