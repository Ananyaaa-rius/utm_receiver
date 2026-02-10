from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
from .db import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    logger.info("Database connected and utm_clicks table ready")
    yield
    # Shutdown
    await db.disconnect()

app = FastAPI(
    title="UTM Tracking API",
    description="Minimal FastAPI backend for UTM parameter logging",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok"}

@app.get("/track")
async def track_utm(request: Request):
    try:
        # Extract utm_* parameters
        utm_params = {k: v for k, v in request.query_params.items() if k.startswith('utm_')}
        
        # Log when /track is hit with captured parameters
        logger.info(f"UTM tracking request - IP: {request.client.host}, Parameters: {utm_params}")
        
        # Store in database
        try:
            # Debug log before database insert
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent", "")
            referrer = request.headers.get("referer", "")
            logging.debug(f"About to insert - utm_params: {utm_params}, ip_address: {ip_address}, user_agent: {user_agent}, referrer: {referrer}")
            
            await db.insert_click(
                utm_params, 
                ip_address, 
                user_agent, 
                referrer
            )
            logger.info("UTM click successfully logged to database")
        except Exception as db_error:
            logging.error(f"Database insert failed: {type(db_error).__name__}: {db_error}")
            # Return error HTML immediately
            error_html = """<!DOCTYPE html>
<html>
<head>
    <title>UTM Receiver - Error</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
        .error { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <h1>📊 UTM Receiver</h1>
    <p class="error">Failed to log UTM parameters. Please try again later.</p>
</body>
</html>"""
            return HTMLResponse(content=error_html, status_code=500)
        
        # Build HTML list items
        utm_html_items = []
        if utm_params:
            for key, value in utm_params.items():
                utm_html_items.append("<li>• {0}: {1}</li>".format(key, value))
        else:
            utm_html_items.append("<li>• No UTM parameters detected</li>")
        
        utm_html_list = "\n            ".join(utm_html_items)
        
        # HTML template
        html_template = """<!DOCTYPE html>
<html>
<head>
    <title>UTM Receiver</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .description {{
            color: #666;
            text-align: center;
            margin-bottom: 30px;
        }}
        .success {{
            color: #28a745;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }}
        .parameters {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
            margin-bottom: 20px;
        }}
        .parameters h3 {{
            margin-top: 0;
            color: #333;
        }}
        .parameters ul {{
            list-style-type: none;
            padding: 0;
        }}
        .parameters li {{
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .parameters li:last-child {{
            border-bottom: none;
        }}
        .footer {{
            text-align: center;
            color: #999;
            font-style: italic;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <h1>📊 UTM Receiver</h1>
    
    <p class="description">
        This link is used to track marketing campaigns.
    </p>
    
    <p class="success">
        Your visit has been recorded successfully.
    </p>
    
    <div class="parameters">
        <h3>Captured parameters:</h3>
        <ul>
            {0}
        </ul>
    </div>
    
    <p class="footer">
        You may now close this page.
    </p>
</body>
</html>"""
        
        return HTMLResponse(content=html_template.format(utm_html_list))
        
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"Unexpected error in /track: {type(e).__name__}: {e}")
        
        # Return friendly error page
        error_html = """<!DOCTYPE html>
<html>
<head>
    <title>UTM Receiver - Error</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
        .error { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <h1>📊 UTM Receiver</h1>
    <p class="error">Failed to log UTM parameters. Please try again later.</p>
</body>
</html>"""
        return HTMLResponse(content=error_html, status_code=500)

if __name__ == "__main__":
    import uvicorn
    # Development server only - use uvicorn command in production
    uvicorn.run("server.src.main:app", host="0.0.0.0", port=8000, reload=True)
