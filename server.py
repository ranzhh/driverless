#!/usr/bin/env python3
"""
FastAPI server to view driverless processing results.
Auto-reloads when output files change.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI(title="Driverless Results Viewer")

# Configuration
OUTPUT_DIR = Path("output")
DATA_DIR = Path("data")

# Store active WebSocket connections
active_connections: list[WebSocket] = []

# Store file modification times
file_mtimes = {}


def get_file_mtime(filepath: Path) -> float:
    """Get file modification time."""
    try:
        return filepath.stat().st_mtime
    except FileNotFoundError:
        return 0


def check_files_changed() -> list[str]:
    """Check if any output files have changed."""
    changed = []
    files_to_watch = [
        OUTPUT_DIR / "detected_cones.json",
        OUTPUT_DIR / "detected_cones.png",
        OUTPUT_DIR / "odometry_matches.png",
        OUTPUT_DIR / "original_image.png",
    ]

    for filepath in files_to_watch:
        current_mtime = get_file_mtime(filepath)
        previous_mtime = file_mtimes.get(str(filepath), 0)

        if current_mtime > previous_mtime:
            file_mtimes[str(filepath)] = current_mtime
            changed.append(filepath.name)

    return changed


@app.on_event("startup")
async def startup_event():
    """Initialize file modification times on startup."""
    check_files_changed()
    # Start background task to monitor files
    asyncio.create_task(monitor_files())


async def monitor_files():
    """Background task to monitor file changes and notify clients."""
    while True:
        await asyncio.sleep(1)  # Check every second
        changed = check_files_changed()

        if changed and active_connections:
            message = json.dumps({"type": "reload", "files": changed})
            # Notify all connected clients
            disconnected = []
            for connection in active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)

            # Remove disconnected clients
            for conn in disconnected:
                active_connections.remove(conn)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main viewer page."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Driverless Results Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status.connected {
            background: #4caf50;
            color: white;
        }
        
        .status.disconnected {
            background: #f44336;
            color: white;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .card img {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .timestamp {
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .json-view {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
        }
        
        .json-view pre {
            margin: 0;
            color: #333;
        }
        
        .reload-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4caf50;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            opacity: 0;
            transform: translateY(-20px);
            transition: opacity 0.3s, transform 0.3s;
            pointer-events: none;
            font-weight: bold;
        }
        
        .reload-indicator.show {
            opacity: 1;
            transform: translateY(0);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .reloading {
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏎️ Driverless Results Viewer</h1>
            <p class="subtitle">Real-time visualization of cone detection, track lines, and odometry</p>
            <span id="status" class="status disconnected">Connecting...</span>
        </header>
        
        <div class="grid">
            <!-- Cone Detection with Track Lines -->
            <div class="card">
                <h2>Step 1 & 2: Cone Detection + Track Lines</h2>
                <img id="cones-img" src="/output/detected_cones.png" alt="Detected Cones" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'600\' height=\'400\'%3E%3Crect fill=\'%23f0f0f0\' width=\'600\' height=\'400\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' fill=\'%23999\' font-size=\'20\'%3EImage not available%3C/text%3E%3C/svg%3E'">
                <p class="timestamp">Last updated: <span id="cones-time">Loading...</span></p>
            </div>
            
            <!-- Odometry Matches -->
            <div class="card">
                <h2>Step 3: Odometry Calculation</h2>
                <img id="odometry-img" src="/output/odometry_matches.png" alt="Odometry Matches" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'600\' height=\'400\'%3E%3Crect fill=\'%23f0f0f0\' width=\'600\' height=\'400\'/%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' fill=\'%23999\' font-size=\'20\'%3EImage not available%3C/text%3E%3C/svg%3E'">
                <p class="timestamp">Last updated: <span id="odometry-time">Loading...</span></p>
            </div>
        </div>
        
        <!-- Detected Cones JSON Data -->
        <div class="card">
            <h2>Detected Cones Data (JSON)</h2>
            <div class="json-view">
                <pre id="json-content">Loading...</pre>
            </div>
            <p class="timestamp">Last updated: <span id="json-time">Loading...</span></p>
        </div>
    </div>
    
    <div id="reload-indicator" class="reload-indicator">
        🔄 Reloading updated files...
    </div>
    
    <script>
        let ws;
        let reconnectAttempts = 0;
        const maxReconnectAttempts = 5;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                document.getElementById('status').textContent = 'Connected ✓';
                document.getElementById('status').className = 'status connected';
                reconnectAttempts = 0;
                loadInitialData();
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'reload') {
                    console.log('Files changed:', data.files);
                    showReloadIndicator();
                    reloadImages();
                    loadJSON();
                }
            };
            
            ws.onclose = () => {
                console.log('WebSocket disconnected');
                document.getElementById('status').textContent = 'Disconnected ✗';
                document.getElementById('status').className = 'status disconnected';
                
                // Attempt to reconnect
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`Reconnecting... (attempt ${reconnectAttempts})`);
                    setTimeout(connectWebSocket, 2000);
                }
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
        
        function showReloadIndicator() {
            const indicator = document.getElementById('reload-indicator');
            indicator.classList.add('show');
            setTimeout(() => {
                indicator.classList.remove('show');
            }, 2000);
        }
        
        function reloadImages() {
            const timestamp = new Date().getTime();
            const conesImg = document.getElementById('cones-img');
            const odometryImg = document.getElementById('odometry-img');
            
            conesImg.classList.add('reloading');
            odometryImg.classList.add('reloading');
            
            conesImg.src = `/output/detected_cones.png?t=${timestamp}`;
            odometryImg.src = `/output/odometry_matches.png?t=${timestamp}`;
            
            conesImg.onload = () => {
                conesImg.classList.remove('reloading');
                updateTimestamp('cones-time');
            };
            
            odometryImg.onload = () => {
                odometryImg.classList.remove('reloading');
                updateTimestamp('odometry-time');
            };
        }
        
        async function loadJSON() {
            try {
                const response = await fetch(`/output/detected_cones.json?t=${new Date().getTime()}`);
                const data = await response.json();
                document.getElementById('json-content').textContent = JSON.stringify(data, null, 2);
                updateTimestamp('json-time');
            } catch (error) {
                console.error('Error loading JSON:', error);
                document.getElementById('json-content').textContent = 'Error loading JSON data';
            }
        }
        
        function updateTimestamp(elementId) {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            document.getElementById(elementId).textContent = timeString;
        }
        
        function loadInitialData() {
            reloadImages();
            loadJSON();
        }
        
        // Connect when page loads
        connectWebSocket();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/output/{filename}")
async def get_output_file(filename: str):
    """Serve output files."""
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        return FileResponse(filepath)
    return {"error": "File not found"}


@app.get("/data/{filename}")
async def get_data_file(filename: str):
    """Serve input data files."""
    filepath = DATA_DIR / filename
    if filepath.exists():
        return FileResponse(filepath)
    return {"error": "File not found"}


@app.get("/api/status")
async def get_status():
    """Get current status and file information."""
    files = {
        "detected_cones_json": (OUTPUT_DIR / "detected_cones.json").exists(),
        "detected_cones_png": (OUTPUT_DIR / "detected_cones.png").exists(),
        "odometry_matches": (OUTPUT_DIR / "odometry_matches.png").exists(),
    }

    return {
        "status": "running",
        "files": files,
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import os

    import uvicorn

    # Use 0.0.0.0 in Docker, 127.0.0.1 for local development
    host = os.environ.get("SERVER_HOST", "127.0.0.1")

    print("🚀 Starting Driverless Results Viewer...")
    print("📊 View results at: http://localhost:8080")
    print("🔄 Auto-reloading enabled - changes to output files will be reflected automatically")
    uvicorn.run(app, host=host, port=8080, log_level="info")
