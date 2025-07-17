# Nginx Configuration

This folder contains example Nginx configuration snippets for serving the site and the server status API.

* `rcfg_site.conf` – full server block that serves the static files from `/var/www/rcfg_site` and includes the API configuration.
* `rcfg_status.conf` – location block used by `rcfg_site.conf` to proxy `/api/status/` requests to the FastAPI service running on `127.0.0.1:5000`.

Copy `rcfg_site.conf` to your Nginx `sites-available` directory and enable it with a symlink in `sites-enabled`. After reloading Nginx, the website and status API will be accessible on `http://rcfg.xyz/`.
