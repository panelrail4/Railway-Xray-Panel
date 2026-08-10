#!/bin/sh
set -eu

mkdir -p /data/xray /data/xray/backups /data/ssh /run/sshd /var/run/nginx
chmod 700 /data/ssh || true

# ---------------- SSH bootstrap ----------------
SSH_PORT="${SSH_PORT:-2222}"
SSH_USER="${SSH_USER:-railway}"

case "$SSH_PORT" in
  ''|*[!0-9]*) echo "Invalid SSH_PORT: $SSH_PORT" >&2; exit 1 ;;
esac
case "$SSH_USER" in
  root|[!a-zA-Z_][a-zA-Z0-9_-]*) echo "Invalid SSH_USER: $SSH_USER" >&2; exit 1 ;;
esac

# Passwords should normally be supplied as Railway service variables.
# If omitted, generate strong one-time credentials and persist them on the
# attached volume so the container remains usable without a manual bootstrap.
generate_password() {
  openssl rand -base64 24 | tr -d '/+=\n' | cut -c1-24
}

ROOT_PASSWORD="${SSH_ROOT_PASSWORD:-}"
USER_PASSWORD="${SSH_USER_PASSWORD:-}"
if [ -z "$ROOT_PASSWORD" ]; then ROOT_PASSWORD="$(generate_password)"; fi
if [ -z "$USER_PASSWORD" ]; then USER_PASSWORD="$(generate_password)"; fi

printf '%s\n' "root:${ROOT_PASSWORD}" > /data/ssh/generated_credentials.txt
printf '%s\n' "${SSH_USER}:${USER_PASSWORD}" >> /data/ssh/generated_credentials.txt
chmod 600 /data/ssh/generated_credentials.txt

# Ensure host keys exist on every fresh deployment.
ssh-keygen -A >/dev/null 2>&1 || true

# Root access is explicitly enabled because this container is intended as an
# administrative Ubuntu 24.04 environment. Prefer SSH keys for production.
echo "root:${ROOT_PASSWORD}" | chpasswd

if ! id "$SSH_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$SSH_USER"
fi
echo "${SSH_USER}:${USER_PASSWORD}" | chpasswd
usermod -aG sudo "$SSH_USER" || true

cat > /etc/ssh/sshd_config.d/99-xpanel.conf <<CFG
Port ${SSH_PORT}
ListenAddress 0.0.0.0
PermitRootLogin yes
PasswordAuthentication yes
KbdInteractiveAuthentication no
UsePAM no
PubkeyAuthentication yes
X11Forwarding no
AllowTcpForwarding yes
GatewayPorts no
ClientAliveInterval 60
ClientAliveCountMax 3
CFG

/usr/sbin/sshd -t
/usr/sbin/sshd

echo "[xpanel] Ubuntu 24.04 SSH listening on 0.0.0.0:${SSH_PORT}"
echo "[xpanel] Native external SSH requires Railway TCP Proxy; Railway assigns the external proxy port."
if [ -z "${SSH_ROOT_PASSWORD:-}" ] || [ -z "${SSH_USER_PASSWORD:-}" ]; then
  echo "[xpanel] Generated SSH credentials are stored in /data/ssh/generated_credentials.txt"
fi

# ---------------- Application ----------------
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips="*" &
APP_PID=$!

cleanup() {
  kill "$APP_PID" 2>/dev/null || true
  kill "${NGINX_PID:-0}" 2>/dev/null || true
  nginx -s quit 2>/dev/null || true
  /usr/sbin/sshd -t 2>/dev/null || true
}
trap cleanup INT TERM EXIT

i=0
until curl -fsS http://127.0.0.1:8000/api/health >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -ge 90 ]; then echo "FastAPI did not become ready" >&2; exit 1; fi
  sleep 1
done

# Nginx owns Railway's single public HTTP port and dispatches transport paths
# to private Xray listeners while forwarding /api and the panel to FastAPI.
nginx -g 'daemon off;' &
NGINX_PID=$!
wait "$NGINX_PID"
