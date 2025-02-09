import mss
import base64
import pytesseract
import cv2
import numpy as np
from fastapi import APIRouter
from PIL import Image
import io

router = APIRouter()

@router.get("/screenshot")
async def take_screenshot():
    """Captures a screenshot and returns it as a Base64 string."""
    with mss.mss() as sct:
        filename = sct.shot(output="screenshot.png")
    
    img = Image.open("screenshot.png").convert("RGB")  
    img = img.resize((1280, 720))  
    buffered = io.BytesIO()  
    img.save(buffered, format="PNG")  
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")  
    return {"image": encoded} 

@router.get("/read-screen")
async def read_screen():
    """Extracts text from the screen using OCR."""
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
    
    img = np.array(screenshot)
    text = pytesseract.image_to_string(img)
    
    return {"extracted_text": text}
