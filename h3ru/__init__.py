from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import uvicorn

from .arduino import read_from_arduino, SER, init_serial
from .camera import start_cameras, CAMERAS, gen_frames
from . import utils
from .ws import router as ws_router

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, 'templates'))

app = FastAPI()
app.include_router(ws_router)
app.mount('/static', StaticFiles(directory=os.path.join(PROJECT_ROOT, 'static')), name='static')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@app.get('/video_feed/{cam_id}')
async def video_feed(cam_id: int):
    if 0 <= cam_id < len(CAMERAS):
        return StreamingResponse(gen_frames(cam_id), media_type='multipart/x-mixed-replace; boundary=frame')
    raise HTTPException(status_code=404, detail='Invalid camera id')


@app.get('/result')
async def result():
    async with utils.lock:
        return {"result": utils.RESULT_MESSAGE}


@asynccontextmanager
async def lifespan(app_obj: FastAPI):
    # startup
    init_serial()
    # start camera capture
    start_cameras()
    # start arduino read loop (calls broadcast via ws)
    if callable(read_from_arduino):
        try:
            # read_from_arduino returns a coroutine function that accepts a callback
            import asyncio
            asyncio.create_task(read_from_arduino(utils.broadcast_message))
        except Exception:
            pass
    yield
    # shutdown


def run(host: str = '0.0.0.0', port: int = 8001, ssl_certfile: str = None, ssl_keyfile: str = None):
    uvicorn.run('h3ru:app', host=host, port=port, ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile)


app.router.lifespan_context = lifespan
