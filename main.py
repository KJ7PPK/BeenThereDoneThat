from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import csv
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATA_DIR = "data"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/import-openflights")
async def import_openflights(request: Request, file: UploadFile):
    contents = await file.read()
    decoded = contents.decode("utf-8").splitlines()
    reader = csv.reader(decoded)

    # Very minimal import logic just for demonstration
    entries = []
    for row in reader:
        if len(row) > 7:
            entries.append({"from": row[2], "to": row[4], "airline": row[0], "date": row[1]})
    return templates.TemplateResponse("import_result.html", {"request": request, "entries": entries})