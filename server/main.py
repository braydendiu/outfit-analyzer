from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.services.image_processor import EnhancedImageProcessor

import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

image_processor = EnhancedImageProcessor()

@app.get("/")
async def root():
    return {"message": "Fashion Trend Analyzer API"}

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    gender: str = Form(default="women")  # Add gender parameter with default value
):
    try:
        logger.info(f"Received image: {file.filename}")
        logger.info(f"Content type: {file.content_type}")
        logger.info(f"Selected gender: {gender}")
        
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Pass gender to analyze method
        result = await image_processor.analyze(file, gender)
        logger.info("Analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)