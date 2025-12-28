# TeX Tailor - Server Setup Guide

Quick guide to deploy TeX Tailor on an always-on server for LAN access.

## Prerequisites
- Docker installed on server
- Git access to repository
- Server on same LAN as client devices

## Setup Steps

1. **Clone repository to server**
   ```bash
   git clone https://github.com/cjordan223/auto-tailor-v2.git tex-tailor
   cd tex-tailor
   ```

2. **Build Docker image**
   ```bash
   docker build -t tex-tailor-local .
   ```

3. **Run container**
   ```bash
   docker run -d \
     --name tex-tailor \
     -p 3500:3001 \
     --restart unless-stopped \
     tex-tailor-local
   ```

4. **Access from any LAN device**
   - Open browser: `http://<server-ip>:3500`
   - Example: `http://192.168.1.100:3500`

## Management Commands

```bash
# View logs
docker logs tex-tailor

# Stop container
docker stop tex-tailor

# Start container
docker start tex-tailor

# Restart container
docker restart tex-tailor

# Remove container
docker rm -f tex-tailor

# Rebuild after code changes
docker build -t tex-tailor-local . && docker restart tex-tailor
```

## Optional: Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  tex-tailor:
    build: .
    ports:
      - "3500:3001"
    restart: unless-stopped
```

Run: `docker-compose up -d`

## Troubleshooting

- Check container status: `docker ps -a`
- View logs: `docker logs tex-tailor`
- Check port: `netstat -an | grep 3500`
