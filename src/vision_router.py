import mss
import base64
import pytesseract
import cv2
import numpy as np
from fastapi import APIRouter
from PIL import Image
import io
from pathlib import Path

router = APIRouter()

TEMP_IMAGE_PATH = Path("/tmp/screenshot.jpg") if not Path.cwd().anchor.startswith("C:") else Path.cwd() / "screenshot.jpg"

@router.post("/screenshot")
async def take_screenshot():
    """Captures a screenshot, compresses it, and returns a Base64 string."""
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
    
    img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
    img = img.resize((800, 450))  # Resize for smaller data size

    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=50)  # Compress using JPEG quality

    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")[:5000]  # Limit length

    return {"image": encoded}

@router.post("/read-screen")
async def read_screen():
    """Extracts text from the screen using OCR with preprocessing."""
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
    
    img = np.array(screenshot)

    # Convert to grayscale and apply adaptive thresholding
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    text = pytesseract.image_to_string(processed_img)

    return {"extracted_text": text}
