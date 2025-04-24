from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

# Dictionary mapping agent names to their URLs
agent_servers = {
    "F1": "http://192.168.3.55:8001",
    "F2": "http://192.168.40.72:8001",
    
}

app = FastAPI(title="Master Server - Camera Monitoring")

# Set up Jinja2 template rendering
templates = Jinja2Templates(directory="templates")

# Startup event: Initialize an AsyncClient for reuse
@app.on_event("startup")
async def startup_event():
    app.state.client = httpx.AsyncClient()

# Shutdown event: Properly close the AsyncClient
@app.on_event("shutdown")
async def shutdown_event():
    await app.state.client.aclose()

# Home endpoint to render the HTML page
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint that gets the status from each agent server
@app.get("/status")
@app.get("/status")
async def request_status():
    results = {}
    client: httpx.AsyncClient = app.state.client

    for agent_name, url in agent_servers.items():
        try:
            # Query the /status endpoint on the agent server
            response = await client.get(f"{url}/status", timeout=5.0)
            response.raise_for_status()  # Raise an error for non-2xx status codes
            agent_data = response.json()

            # Flatten the agent response (no need to repeat the agent name as a key)
            for camera_name, camera_data in agent_data.items():
                results[camera_name] = camera_data

        except httpx.RequestError as exc:
            # In case of network issues or unreachable server, log the error but don't show in response
            results[agent_name] = {"status": "Offline", "error": f"Network error: {str(exc)}"}
        except httpx.HTTPStatusError as exc:
            # Handle specific HTTP errors (like 404, 503, etc.)
            results[agent_name] = {"status": "Offline", "error": f"HTTP error: {exc.response.status_code}"}
        except httpx.TimeoutException:
            # Handle timeout issues separately
            results[agent_name] = {"status": "Offline", "error": "Request timed out"}

    return JSONResponse(content=results)





#python -m uvicorn master_server:app --host 0.0.0.0 --port 8000 --reload


#web
#http://192.168.40.72:8000

#cd to file