from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import os
import random
from . import utils

router = APIRouter()


async def broadcast_message(message: str):
    disconnected = []
    for conn in list(utils.active_connections):
        try:
            await conn.send_text(message)
        except WebSocketDisconnect:
            disconnected.append(conn)
    for conn in disconnected:
        try:
            utils.active_connections.remove(conn)
        except ValueError:
            pass


async def broadcast_random_sound():
    sound_files = []
    try:
        sound_files = [f for f in os.listdir(utils.SOUNDS_DIR) if f.endswith(('.wav', '.mp3'))]
    except Exception:
        pass
    if sound_files and utils.active_connections:
        sound_file = random.choice(sound_files)
        sound_url = f"/static/sounds/{sound_file}"
        await broadcast_message(sound_url)


# Bind utils.broadcast_message to this implementation
utils.broadcast_message = broadcast_message


@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    utils.active_connections.append(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                # expect json with mode
                import json
                payload = json.loads(data)
                mode = payload.get('mode')
                if mode == 1:
                    await broadcast_message('doorbell')
                elif mode == 2:
                    sound_file = payload.get('sound_file')
                    if sound_file:
                        await broadcast_message(f"/static/sounds/{sound_file}")
                elif mode == 3:
                    # open door
                    if utils:
                        from .arduino import SER
                        if SER:
                            SER.write(b'OPEN_DOOR\n')
                elif mode == 4:
                    from .arduino import SER
                    if SER:
                        SER.write(b'OPEN_GARAGE\n')
            except WebSocketDisconnect:
                break
    finally:
        try:
            utils.active_connections.remove(websocket)
        except ValueError:
            pass


@router.websocket('/voice_ws')
async def voice_websocket(websocket: WebSocket):
    await websocket.accept()
    utils.voice_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            for conn in list(utils.voice_connections):
                if conn != websocket:
                    await conn.send_bytes(data)
    except WebSocketDisconnect:
        pass
    finally:
        try:
            utils.voice_connections.remove(websocket)
        except ValueError:
            pass
