from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXT = {'.html', '.css'}
LOG_FILE = os.path.join(BASE_DIR, 'change_log.txt')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'changeme')


def list_files():
    files = []
    for root, _, filenames in os.walk(BASE_DIR):
        for name in filenames:
            if os.path.splitext(name)[1] in ALLOWED_EXT:
                files.append(os.path.relpath(os.path.join(root, name), BASE_DIR))
    return sorted(files)


@app.middleware('http')
async def check_token(request: Request, call_next):
    token = request.headers.get('X-Admin-Token')
    if request.url.path.startswith('/admin'):
        if token != ADMIN_TOKEN:
            raise HTTPException(status_code=401, detail='Unauthorized')
    return await call_next(request)


@app.get('/admin', response_class=HTMLResponse)
async def admin_home():
    files = list_files()
    items = '\n'.join(f'<li><a href="/admin/edit?file={f}">{f}</a></li>' for f in files)
    return f"<h1>File Editor</h1><ul>{items}</ul>"


@app.get('/admin/edit', response_class=HTMLResponse)
async def edit_form(file: str):
    path = os.path.join(BASE_DIR, file)
    if not os.path.isfile(path) or os.path.splitext(path)[1] not in ALLOWED_EXT:
        raise HTTPException(status_code=404, detail='File not found')
    with open(path, 'r') as fh:
        content = fh.read()

    return (
        "<form method='post' action='/admin/edit'>"
        f"<h2>Editing {file}</h2>"
        f"<input type='hidden' name='file' value='{file}'>"
        "<textarea name='content' style='width:100%;height:80vh;'>" + content + "</textarea><br>"
        "<button type='submit'>Save</button></form>"
    )

@app.post('/admin/edit')
async def save_file(file: str = Form(...), content: str = Form(...)):
    path = os.path.join(BASE_DIR, file)
    if not os.path.isfile(path) or os.path.splitext(path)[1] not in ALLOWED_EXT:
        raise HTTPException(status_code=404, detail='File not found')
    with open(path, 'w') as fh:
        fh.write(content)
    with open(LOG_FILE, 'a') as log:
        log.write(f"{datetime.utcnow().isoformat()} - {file} updated\n")
    return RedirectResponse(url=f'/admin/edit?file={file}', status_code=303)
