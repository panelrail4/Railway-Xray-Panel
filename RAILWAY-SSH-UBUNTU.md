# Ubuntu 24.04 + SSH on Railway

This version keeps the XPanel/Xray HTTP service and adds an Ubuntu 24.04 runtime with OpenSSH.

## Important Railway architecture

Railway services are containers, not conventional VPS instances. The container in this project is **Ubuntu 24.04**, so Ubuntu commands and packages are available, but kernel-level operations remain controlled by Railway.

The service uses two different internal listeners:

- `$PORT` — Railway HTTP/HTTPS Public Networking, used by XPanel and the XHTTP/WS/HTTPUpgrade/gRPC HTTP ingress paths.
- `2222` — OpenSSH inside the container, used only through Railway TCP Proxy.

Railway documents that HTTP and TCP public networking can be used together on one service. A TCP Proxy forwards a generated public `domain:port` to the selected internal port. See the official Railway TCP Proxy documentation.

## Railway configuration

After deployment:

1. Generate a Public Domain for the service. This is the domain used by XPanel and the TLS/SNI side of the transport links.
2. In **Service → Settings → Networking → TCP Proxy**, create a TCP Proxy targeting internal port **2222**.
3. Railway will give you a TCP hostname and proxy port, for example `something.proxy.rlwy.net:12345`.
4. SSH with:

```bash
ssh -p 12345 root@something.proxy.rlwy.net
```

or:

```bash
ssh -p 12345 railway@something.proxy.rlwy.net
```

Do not use the HTTP Public Domain's port for SSH.

## Passwords

Set these Railway Variables before deployment:

```text
SSH_USER=railway
SSH_ROOT_PASSWORD=<strong-root-password>
SSH_USER_PASSWORD=<strong-user-password>
SSH_PORT=2222
```

The container also supports generated credentials if the password variables are omitted. The generated credentials are stored at:

```text
/data/ssh/generated_credentials.txt
```

For persistent storage, attach a Railway Volume to `/data`. Railway documents that a Volume persists data across deployments; without a Volume, the container filesystem is ephemeral.

## Ubuntu commands

Once connected, normal user-space Ubuntu commands can be used, for example:

```bash
cat /etc/os-release
uname -a
apt update
apt install <package>
systemctl --version
ip addr
ss -lntp
curl -I https://example.com
```

### systemd caveat

This is an Ubuntu 24.04 **container**, not a full VM. `systemd` is not PID 1 in this image. Therefore commands such as `systemctl start <service>` should not be treated as if this were a traditional Ubuntu VPS. Long-running services should normally be managed by the container entrypoint/process model or added deliberately to the image.

Similarly, kernel modules, Docker-in-Docker, privileged networking and changes to the host kernel are outside the container's control.

## Security

Password-based root SSH is enabled because it was explicitly requested. Use a strong password and, preferably, add an SSH public key and disable password authentication for a production deployment.

The SSH TCP Proxy is independent of the Railway HTTP Public Domain. If a custom domain is used for TCP, Railway requires DNS-only (not Cloudflare proxy) for the TCP hostname.
