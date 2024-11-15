from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.image_processor import EnhancedImageProcessor
import json
import numpy as np

# JSON encoder for numpy data types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

# Initialize FastAPI app
app = FastAPI()

# CORS configuration: Replace with your actual frontend URL on Render
frontend_url = "https://outfit-analyzer-frontend.onrender.com"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the image processor service
image_processor = EnhancedImageProcessor()

# Define the API endpoint for image analysis
@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    gender: str = Form(default='women')
):
    try:
        # Perform image analysis using the uploaded file and gender
        result = await image_processor.analyze(file, gender)
        
        # Convert result to a JSON-serializable format using NumpyEncoder
        json_compatible_result = json.loads(
            json.dumps(result, cls=NumpyEncoder)
        )
        
        # Return JSON response
        return JSONResponse(content=json_compatible_result)
        
    except Exception as e:
        print(f"[ERROR] Analysis error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# This section is for local development. Render will start the server automatically.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)