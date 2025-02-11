import mss
import base64
import pytesseract
import cv2
import numpy as np
from fastapi import APIRouter
from PIL import Image
import io

router = APIRouter()

@router.post("/screenshot")
async def take_screenshot():
    """Captures a screenshot, compresses it, and returns a Base64 string."""
    with mss.mss() as sct:
        filename = sct.shot(output="screenshot.jpg")  # Use JPEG format

    # Open the image, resize it, and compress
    img = Image.open("screenshot.jpg").convert("RGB")
    img = img.resize((800, 450))  # Resize to 800x450 for smaller data size
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=50)  # Compress using JPEG quality

    # Convert to Base64 and limit length
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")[:5000]  # Limit length

    return {"image": encoded}

@router.post("/read-screen")
async def read_screen():
    """Extracts text from the screen using OCR."""
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
    
    img = np.array(screenshot)
    text = pytesseract.image_to_string(img)
    
    return {"extracted_text": text}
