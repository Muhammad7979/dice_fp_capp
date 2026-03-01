# Client Project Documentation

## 1. Project Overview

### Purpose
The client project is a Flask web app that requests random data from the server project, stores the received payload locally, verifies its SHA-256 checksum, and shows the result in a simple browser UI.

### Technologies Used
- Python 3.11
- Flask (web app and endpoints)
- Requests (HTTP call to server)
- Docker + Docker Compose
- Terraform (separate infra experiment under `terraform/`)
- GitHub Actions (build/push/deploy pipeline)
- Prometheus scrape config file (host metrics targets)

### High-Level Architecture
1. User opens client UI (`/`).
2. UI button triggers frontend fetch to client endpoint `/fetch`.
3. Client app sends `GET` to `SERVER_URL` (expected server endpoint: `/data`).
4. Client stores returned `data` in `/clientdata/received.txt`.
5. Client recomputes checksum and compares to server checksum.
6. Result is returned as JSON and shown in the page.

---

## 2. Project Structure

```text
client-repo/
├── app/
│   └── client.py
├── terraform/
│   └── main.tf
├── .github/
│   └── workflows/
│       └── main.yml
├── Dockerfile
├── docker-compose.yml
├── prometheus.yaml
└── requirements.txt
```

### Key Directories and Files
- `app/client.py`
  - Main Flask app.
  - Endpoints:
    - `GET /` -> inline HTML UI.
    - `GET /fetch` -> calls server, validates checksum, returns message JSON.
  - Requires environment variable: `SERVER_URL`.
- `Dockerfile`
  - Builds image from `python:3.11-slim`.
  - Installs Flask/Requests with pip.
  - Creates `/clientdata` directory.
  - Runs `python client.py` on port `5000`.
- `docker-compose.yml`
  - Runs `client` service mapping `5000:5000`.
  - Persists data using Docker volume `clientvol` mounted at `/clientdata`.
- `prometheus.yaml`
  - Scrape config for `node_exporter` (`localhost:9100`) and `cadvisor` (`localhost:8080`).
- `terraform/main.tf`
  - Simple AWS EC2 + permissive security group example (`0-65535/tcp` ingress).
  - Separate from app runtime.
- `.github/workflows/main.yml`
  - CI/CD pipeline for building and deploying Docker image to EC2.
  - Uses Docker Hub and SSH action.
  - Workflow name says "Server CI/CD Pipeline" even though it deploys client image.
- `requirements.txt`
  - Currently empty (dependencies are installed directly in Dockerfile).

---

## 3. Installation & Setup

### Required Software
- Python `3.11+`
- pip
- Docker + Docker Compose (for containerized run)

### Local Run (without Docker)
1. Create virtual environment:
   ```bash
   cd client-repo
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install flask requests
   ```
3. Set server URL (must point to server `/data` endpoint):
   ```bash
   export SERVER_URL="http://localhost:5000/data"
   ```
4. Start app:
   ```bash
   python app/client.py
   ```
5. Open:
   - `http://localhost:5000`

### Docker Run
```bash
cd client-repo
docker build -t dice-client .
docker run --rm -p 5000:5000 \
  -e SERVER_URL="http://<server-host>:5000/data" \
  -v clientvol:/clientdata \
  dice-client
```

### Docker Compose Run
```bash
cd client-repo
export SERVER_URL="http://<server-host>:5000/data"
docker compose up --build
```

Note: `docker-compose.yml` does not define `environment`, so you must pass `SERVER_URL` externally (shell env, `.env`, or compose override).

---

## 4. Configuration

### Environment Variables
- `SERVER_URL` (required)
  - Example: `http://10.0.1.131:5000/data`
  - App uses `os.environ["SERVER_URL"]`; if not set, startup fails with `KeyError`.

### Files/Paths
- Data directory: `/clientdata`
- Stored file: `/clientdata/received.txt`

### Monitoring Config
- `prometheus.yaml` is static and currently points to local host metrics exporters.

---

## 5. Usage

### Start the Project
- Local: `python app/client.py`
- Docker: `docker run ...`
- Compose: `docker compose up`

### Run/Test Behavior
- Open homepage and click **Fetch Data**.
- It calls `/fetch`, which returns JSON with:
  - generated data text
  - checksum
  - checksum verification status

### Client Endpoints
- `GET /`
  - Renders simple single-page UI with one button.
- `GET /fetch`
  - Calls remote server, validates checksum, returns message JSON.

### UI Components
Inline HTML in `client.py` contains:
- Header/title
- Description text
- `Fetch Data` button
- Output box shown after fetch

---

## 6. Docker / Deployment

### Dockerfile Notes
- Base: `python:3.11-slim`
- Installs system packages (`python3-pip`, `curl`, `build-essential`, etc.)
- Installs Python deps directly (`flask`, `requests`)

### Compose Notes
- Port mapping `5000:5000`
- Persistent volume `clientvol`

### CI/CD (`.github/workflows/main.yml`)
- Trigger: push to `main`
- Steps:
  - Checkout
  - Docker Hub login
  - Build image `dice_project_client_app:latest`
  - Push image
  - SSH into target EC2 and redeploy container
- Deploy command injects:
  - `SERVER_URL="http://10.0.1.131:5000/data"` (hardcoded private IP)

---

## 7. Dependencies

### Python Libraries
- `flask`: web routing and response handling
- `requests`: outbound HTTP call to server endpoint

### Python Standard Library
- `hashlib`: SHA-256 checksum calculation
- `os`: env vars and local directory creation

### Infrastructure/Tooling
- Docker / Compose: containerized runtime
- Terraform: infrastructure provisioning experiments
- GitHub Actions: CI/CD automation

---

## 8. Additional Notes

### Important Commands
- Local start:
  ```bash
  python app/client.py
  ```
- Container logs:
  ```bash
  docker logs -f client_app
  ```

### Common Pitfalls / Troubleshooting
- Missing `SERVER_URL` causes app crash at startup.
- Client and server both default to port `5000`; running both on one host needs port remap for one service.
- `requirements.txt` is empty; local installs need manual `pip install flask requests`.
- CI deploy uses hardcoded server private IP; if server IP changes, client cannot fetch data.

### Security/Operational Notes
- Terraform config in this repo uses wide-open ingress in places; restrict CIDRs/ports before production.
