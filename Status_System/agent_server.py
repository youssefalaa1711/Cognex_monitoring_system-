from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import platform
import time
import asyncio

app = FastAPI(title="Camera Monitoring Agent")

CAMERA_IPS = {
    "F1": "192.168.40.72",  # Example for F1
    "F2": "192.168.40.73",  # Example for F2
}

camera_status = {}  # Store status of each camera by name
monitoring = False  # Flag to control if monitoring is active
monitoring_task = None  # Background task for monitoring

def ping_camera(ip: str) -> bool:
    """
    Synchronously ping the provided IP address.
    Returns True if the ping is successful (camera is online), otherwise False.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = f"ping {param} 1 {ip}"
    return os.system(command) == 0

async def monitor_cameras():
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

@app.post("/start")
async def start_monitoring():
    global monitoring, monitoring_task
    if not monitoring:
        monitoring = True
        monitoring_task = asyncio.create_task(monitor_cameras())
        return {"message": "Monitoring started."}
    return {"message": "Monitoring already running."}

@app.post("/stop")
async def stop_monitoring():
    global monitoring, monitoring_task
    monitoring = False
    if monitoring_task:
        monitoring_task.cancel()
    return {"message": "Monitoring stopped."}

@app.get("/status")
async def get_status():
    return JSONResponse(content=camera_status)



#to run
#python -m uvicorn agent_server:app --host 0.0.0.0 --port 8001


#web
#http://192.168.40.72:8001
