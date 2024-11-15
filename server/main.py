from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .services.image_processor import EnhancedImageProcessor 
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://outfit-analyzer.onrender.com", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
image_processor = EnhancedImageProcessor()

@app.get("/")
async def root():
    return {"message": "Fashion Trend Analyzer API"}

@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        logger.info(f"Received image: {file.filename}")
        
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        result = await image_processor.analyze(file)
        logger.info("Analysis completed successfully")
        logger.info(f"Result: {result}")  # Add this line for debugging
        return result
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)