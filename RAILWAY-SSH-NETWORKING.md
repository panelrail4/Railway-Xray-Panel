# Railway XPanel 1.0.9 — SSH networking

## Important Railway limitation

This project deliberately keeps **two SSH access paths**:

1. **Native SSH over Railway TCP Proxy** — real `ssh user@host -p PORT`.
2. **Public-domain HTTP/HTTPS path** — reserved for an HTTP/WebSocket tunnel only; it is **not** a native SSH socket.

Railway Public Networking domains expose HTTP/HTTPS. A custom domain can be mapped to an internal target port, but the external connection is still HTTP/HTTPS and Railway terminates TLS. It cannot turn `https://example.com:2233` into a raw SSH listener.

Railway TCP Proxy is the correct native-SSH mechanism. Railway assigns the external proxy port; the application cannot force that external port to `2233`.

Therefore the project does **not** falsely advertise `ssh -p 2233 public-domain` as a native connection. Doing so would fail at the Railway edge.

## Native SSH path

The container SSH daemon listens on:

```text
0.0.0.0:2222
```

Create Railway → Service → Settings → Networking → TCP Proxy and select internal port `2222`.

Railway will provide something like:

```text
xxxxx.proxy.rlwy.net:12345
```

Connect:

```bash
ssh -p 12345 root@xxxxx.proxy.rlwy.net
```

or:

```bash
ssh -p 12345 railway@xxxxx.proxy.rlwy.net
```

The external port `12345` is an example only; Railway chooses it.

## Custom domain for the TCP Proxy

Railway supports a custom hostname in front of a TCP Proxy using a DNS CNAME, but the Railway-provided TCP proxy port must still be used. Cloudflare proxying must be disabled (DNS only) for this raw TCP path.

Example conceptual DNS:

```text
ssh.example.com CNAME xxxxx.proxy.rlwy.net
```

Then:

```bash
ssh -p 12345 root@ssh.example.com
```

The port remains Railway's assigned TCP proxy port.

## About port 2233

`2233` is retained as an **internal optional SSH/tunnel port setting** for compatibility and future deployment patterns, but it is not claimed to be a public Railway raw-TCP port.

If you set:

```text
SSH_PORT=2233
```

then the SSH daemon listens internally on `2233`. You would then create the Railway TCP Proxy against internal port `2233`; Railway will still assign the external TCP proxy port.

For the safest default, leave:

```text
SSH_PORT=2222
```

## Why the public-domain TLS method works for XHTTP but not SSH

Your working XHTTP setup is HTTP-based. Railway receives HTTPS for the public domain, terminates TLS, and forwards HTTP to the container. Xray can therefore receive the HTTP request after the edge and still work with the client's TLS/SNI semantics.

SSH is a raw TCP protocol. It does not speak HTTP and cannot be placed directly behind Railway's HTTP public domain.
