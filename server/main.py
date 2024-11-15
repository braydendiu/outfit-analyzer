from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.image_processor import EnhancedImageProcessor
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Updated CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for testing
    allow_credentials=False,  # Change to False since we're allowing all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

image_processor = EnhancedImageProcessor()

@app.get("/")
async def root():
    return {"message": "Fashion Trend Analyzer API"}

@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        logger.info(f"Received image: {file.filename}")
        logger.info(f"Content type: {file.content_type}")
        
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        result = await image_processor.analyze(file)
        logger.info("Analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"error": str(e)}  # Return error as JSON