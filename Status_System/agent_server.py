from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import platform
import time
import subprocess
import asyncio

app = FastAPI(title="Camera Monitoring Agent")


CAMERA_IPS = {
    "F1":"192.168.3.55", 
    "F2":"192.168.3.33",
}

# Store camera statuses (Online/Offline and Timestamp)
camera_status = {}

monitoring = False  # Flag to control if monitoring is active
monitoring_task = None  # Background task for monitoring

def ping_camera(ip: str) -> bool:
    """
    Ping the provided IP address to check if it's online.
    Returns True if online, otherwise False.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = f"ping {param} 1 {ip}"
    return os.system(command) == 0

async def monitor_cameras():
    """
    Periodically check the status of cameras by pinging their IPs
    every 2 seconds, and update the camera status with the timestamp.
    """
    global camera_status, monitoring
    while monitoring:
        new_status = {}
        for name, ip in CAMERA_IPS.items():
            online = await asyncio.to_thread(ping_camera, ip)
            new_status[name] = {
                "ip": ip,
                "status": "Online" if online else "Offline",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        camera_status = new_status
        await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    """
    Automatically start monitoring when the server starts.
    """
    global monitoring, monitoring_task
    if not monitoring:
        monitoring = True
        monitoring_task = asyncio.create_task(monitor_cameras())

@app.on_event("shutdown")
async def shutdown_event():
    """
    Stop monitoring when the server shuts down.
    """
    global monitoring, monitoring_task
    monitoring = False
    if monitoring_task:
        monitoring_task.cancel()

@app.get("/status")
async def get_status():
    """
    Endpoint to get the current camera statuses.
    This will return a JSON response with the status of each camera.
    """
    return JSONResponse(content=camera_status)

# To run the server
# python -m uvicorn agent_server:app --host 0.0.0.0 --port 8001
