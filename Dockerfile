# syntax=docker/dockerfile:1

# ---------- Frontend build ----------
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build -- --config ./vite.config.mjs

# ---------- Ubuntu 24.04 runtime ----------
FROM ubuntu:24.04 AS app
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Ubuntu 24.04 is the actual runtime OS. The image intentionally includes
# common administration/networking/build tools so the service can be used as
# a general-purpose Ubuntu container through SSH in addition to XPanel/Xray.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       wget \
       unzip \
       zip \
       nginx \
       openssh-server \
       sudo \
       git \
       nano \
       vim-tiny \
       less \
       jq \
       procps \
       iproute2 \
       iputils-ping \
       dnsutils \
       net-tools \
       traceroute \
       tcpdump \
       lsof \
       psmisc \
       htop \
       rsync \
       socat \
       netcat-openbsd \
       openssl \
       build-essential \
       python3 \
       python3-dev \
       python3-pip \
       python3-venv \
       python3-setuptools \
       python3-wheel \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd /var/run/nginx

ARG XRAY_VERSION=26.6.27
RUN curl -fsSL \
    "https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VERSION}/Xray-linux-64.zip" \
    -o /tmp/xray.zip \
    && unzip -o /tmp/xray.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/xray \
    && rm -f /tmp/xray.zip

# Keep Python dependencies isolated from Ubuntu's externally-managed Python.
COPY requirements.txt ./
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
ENV PATH="/opt/venv/bin:${PATH}"

COPY backend ./backend
COPY --from=frontend /frontend/dist ./backend/app/static
COPY entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

RUN mkdir -p /data/xray /data/ssh /data/backups /var/log/ssh \
    && chmod 700 /data/ssh

# SSH is deliberately separate from Railway's HTTP PORT. Create a Railway
# TCP Proxy targeting SSH_PORT (default 2222) if external SSH is required.
ENV XRAY_PATH=/usr/local/bin/xray \
    XRAY_CONFIG=/data/xray/config.json \
    PYTHONUNBUFFERED=1 \
    SSH_PORT=2222 \
    SSH_USER=railway

EXPOSE 8080 2222

CMD ["./entrypoint.sh"]
