import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
from datetime import datetime, date
from .crud import get_all, create
from .importers import import_openflights

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///./data/locations.db"
db = Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await db.connect()
    import sqlalchemy
    from .models import metadata
    engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    entries = await get_all(db)
    stats = {"plane":0,"total_miles":0,"hotel":0,"total_nights":0,
             "cruise":0,"drive":0,"train":0,"visited":0}
    for e in entries:
        t = e["type"]
        stats[t] = stats.get(t, 0) + 1
        if t=="plane":
            stats["total_miles"] += e["extra"].get("distance", 0)
        if t=="hotel":
            stats["total_nights"] += e["extra"].get("nights", 0)
    return templates.TemplateResponse("index.html", {
        "request": request, "entries": entries, "stats": stats
    })

# -- Flights import (unchanged) --

# -- Hotels --
@app.get("/hotels", response_class=HTMLResponse)
def form_hotels(request: Request):
    return templates.TemplateResponse("hotels.html", {"request":request})

@app.post("/hotels")
async def add_hotel(
    request: Request,
    brand: str = Form(...),
    location: str = Form(...),
    checkin: date = Form(...),
    checkout: date = Form(...)
):
    nights = (checkout - checkin).days
    payload = {
        "type":"hotel", "name":f"{brand} @ {location}",
        "description": None, "date": checkin, "end_date": checkout,
        "origin_latitude":None,"origin_longitude":None,
        "destination_latitude":None,"destination_longitude":None,
        "extra": {"brand":brand,"location":location,"nights":nights}
    }
    await create(db, **payload)
    return RedirectResponse("/", status_code=303)

# -- Cruises --
@app.get("/cruises", response_class=HTMLResponse)
def form_cruises(request: Request):
    return templates.TemplateResponse("cruises.html", {"request":request})

@app.post("/cruises")
async def add_cruise(
    request: Request,
    line: str = Form(...),
    ship: str = Form(...),
    embark: date = Form(...),
    disembark: date = Form(...),
    ports: str = Form("")  # textarea: "Port|YYYY-MM-DD"
):
    ports_list = []
    for ln in ports.splitlines():
        if "|" in ln:
            p,d = ln.split("|",1)
            try:
                dt = datetime.strptime(d.strip(), "%Y-%m-%d").date()
                ports_list.append({"port":p.strip(),"date":dt.isoformat()})
            except:
                continue
    payload = {
        "type":"cruise","name":ship,"description":line,
        "date":embark,"end_date":disembark,
        "origin_latitude":None,"origin_longitude":None,
        "destination_latitude":None,"destination_longitude":None,
        "extra": {"line":line,"ship":ship,"ports":ports_list}
    }
    await create(db, **payload)
    return RedirectResponse("/", status_code=303)

# -- Routes/Train --
@app.get("/routes", response_class=HTMLResponse)
def form_routes(request: Request):
    return templates.TemplateResponse("routes.html", {"request":request})

@app.post("/routes")
async def add_route(
    request: Request,
    mode: str = Form(...),        # "drive" or "train"
    origin: str = Form(...),
    destination: str = Form(...),
    traveled_on: date = Form(None)
):
    payload = {
        "type":mode, "name":f"{origin} → {destination}",
        "description":None, "date":traveled_on,
        "origin_latitude":None,"origin_longitude":None,
        "destination_latitude":None,"destination_longitude":None,
        "extra":{"origin":origin,"destination":destination}
    }
    await create(db, **payload)
    return RedirectResponse("/", status_code=303)

# -- Visited --
@app.get("/visited", response_class=HTMLResponse)
def form_visited(request: Request):
    return templates.TemplateResponse("visited.html", {"request":request})

@app.post("/visited")
async def add_visited(
    request: Request,
    location: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    visited_on: date = Form(None)
):
    payload = {
        "type":"visited","name":location,"description":None,
        "date":visited_on,
        "origin_latitude":lat,"origin_longitude":lon,
        "destination_latitude":None,"destination_longitude":None,
        "extra":{}
    }
    await create(db, **payload)
    return RedirectResponse("/", status_code=303)


from fastapi import UploadFile, File, Request
from .importers import import_openflights
from fastapi.responses import RedirectResponse

@app.post("/import-flights")
async def import_flights(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    count = await import_openflights(contents.decode("utf-8"), db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": f"Imported {count} flights"
    })


from fastapi import UploadFile, File, Request
from fastapi.responses import RedirectResponse
from .importers import import_openflights

# removed broken import handler
async def import_openflights_handler(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    count = await import_openflights(contents.decode("utf-8"), db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": f"Imported {count} flights"
    })

@app.post("/import-openflights")
async def import_openflights_handler(request: Request, file: UploadFile = File(...)):
    import os
    from .importers import import_openflights
    from .crud import create
    import_path = "/tmp/import.csv"
    with open(import_path, "wb") as f_out:
        f_out.write(await file.read())
    await import_openflights(import_path, db, create)
    return RedirectResponse(url="/", status_code=303)
