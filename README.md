# RCFG Website

This repository contains the source for the RCFG website and the status API service.

## Automatic Deployment

Two GitHub Actions workflows keep the site up to date:

- **Deploy to GitHub Pages** – publishes the repository contents to GitHub Pages whenever changes are pushed to the `main` branch.
- **Deploy to Web Server** – synchronises the repository with the production server via SSH on every push to `main`.

To enable server deployment, define the following secrets in the repository settings:

- `SERVER_HOST` – hostname or IP of the server.
- `SERVER_PORT` – SSH port (default `22`).
- `SERVER_USER` – SSH user used for deployment.
- `SERVER_SSH_KEY` – private key for the SSH user.

The workflow copies the repository to `/var/www/rcfg_site` and then restarts the `status_api` service and reloads Nginx.
