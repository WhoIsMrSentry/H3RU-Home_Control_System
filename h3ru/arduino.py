import glob
import serial
import logging
import os
from typing import Optional, Callable
from . import utils


def find_arduino_port() -> Optional[str]:
    # Prefer explicit environment variable
    env = os.environ.get('ARDUINO_PORT')
    if env:
        return env

    # Linux common patterns
    ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    if ports:
        return ports[0]

    # On Windows, user should set ARDUINO_PORT to e.g. COM3
    return None


SER = None


def init_serial(baud: int = 115200, timeout: float = 1.0):
    global SER
    try:
        port = find_arduino_port()
        if port:
            SER = serial.Serial(port, baud, timeout=timeout)
            logging.info(f"Arduino connected at {port}")
        else:
            logging.warning("Arduino port not found; running without serial")
            SER = None
    except Exception as e:
        logging.error(f"Failed to init serial: {e}")
        SER = None


async def read_from_arduino(broadcast_callback: Callable[[str], None] = None):
    """Asynchronously read lines from Arduino and optionally broadcast messages.

    `broadcast_callback` can be an async callable; we'll await if coroutine.
    """
    import asyncio, inspect
    global SER
    while True:
        if SER and getattr(SER, 'in_waiting', 0) > 0:
            try:
                line = SER.readline().decode('utf-8').strip()
                logging.info(f"Arduino message: {line}")
                if line.startswith('RESULT:'):
                    async with utils.lock:
                        utils.RESULT_MESSAGE = line.split('RESULT:')[1]
                    if broadcast_callback:
                        if inspect.iscoroutinefunction(broadcast_callback):
                            await broadcast_callback(f"Jetson: {utils.RESULT_MESSAGE}")
                        else:
                            broadcast_callback(f"Jetson: {utils.RESULT_MESSAGE}")
                if line == 'doorbell' and broadcast_callback:
                    if inspect.iscoroutinefunction(broadcast_callback):
                        await broadcast_callback('doorbell')
                    else:
                        broadcast_callback('doorbell')
            except Exception as e:
                logging.error(f"Arduino read error: {e}")
        await asyncio.sleep(0.1)
