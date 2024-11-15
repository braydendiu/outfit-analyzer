# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from services.image_processor import EnhancedImageProcessor
# import uvicorn
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],  # Vite's default port
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize services
# image_processor = EnhancedImageProcessor()

# @app.post("/api/analyze-image")
# async def analyze_image(file: UploadFile = File(...)):
#     try:
#         logger.info(f"Received image: {file.filename}")
        
#         if not file.content_type.startswith("image/"):
#             raise HTTPException(status_code=400, detail="File must be an image")
        
#         result = await image_processor.analyze(file)
#         logger.info("Analysis completed successfully")
#         return result
        
#     except Exception as e:
#         logger.error(f"Error processing image: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/health")
# async def health_check():
#     return {"status": "healthy"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.image_processor import EnhancedImageProcessor
import json
import numpy as np

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

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

image_processor = EnhancedImageProcessor()

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    gender: str = Form(default='women')
):
    try:
        result = await image_processor.analyze(file, gender)
        
        # Convert result to JSON-serializable format
        json_compatible_result = json.loads(
            json.dumps(result, cls=NumpyEncoder)
        )
        
        return JSONResponse(content=json_compatible_result)
        
    except Exception as e:
        print(f"[ERROR] Analysis error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)