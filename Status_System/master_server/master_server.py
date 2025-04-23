from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx

# Dictionary mapping agent names to their URLs
agent_servers = {
    "F1": "http://192.168.40.72:8001",
    "F2": "http://192.168.40.73:8001",
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
async def request_status():
    results = {}
    client: httpx.AsyncClient = app.state.client

    for agent_name, url in agent_servers.items():
        try:
            # Query the /status endpoint on the agent server
            response = await client.get(f"{url}/status", timeout=5.0)
            response.raise_for_status()
            results[agent_name] = response.json()
        except httpx.RequestError as exc:
            results[agent_name] = {"error": f"Request failed: {str(exc)}"}
        except httpx.HTTPStatusError as exc:
            results[agent_name] = {"error": f"HTTP error: {exc.response.status_code}"}

    return JSONResponse(content=results)




#python -m uvicorn master_server:app --host 0.0.0.0 --port 8000 --reload


#web
#http://192.168.40.72:8000

#cd to file