import requests
import base64
from PIL import Image
from io import BytesIO
import time

BASE_URL = "http://localhost:3000/api"

headers = {
    "Content-Type": "application/json"
}

def test_run_command():
    print("\n🔹 Testing run-command:")
    payload = {"command": "whoami"}  # Change to "dir" on Windows
    response = requests.post(f"{BASE_URL}/system/run-command", json=payload, headers=headers)
    print("➡️ Request:", payload)
    print("⬅️ Response:", response.json())

def test_control_mouse():
    print("\n🔹 Testing mouse control:")
    payload = {"x": 500, "y": 400, "action": "click"}
    response = requests.post(f"{BASE_URL}/system/mouse", json=payload, headers=headers)
    print("➡️ Request:", payload)
    print("⬅️ Response:", response.json())

def test_control_keyboard():
    print("\n🔹 Testing keyboard control:")
    payload = {"key": "enter"}
    response = requests.post(f"{BASE_URL}/system/keyboard", json=payload, headers=headers)
    print("➡️ Request:", payload)
    print("⬅️ Response:", response.json())

def test_take_screenshot():
    print("\n🔹 Testing screenshot capture:")
    response = requests.get(f"{BASE_URL}/vision/screenshot", headers=headers)
    data = response.json()
    
    if "image" in data:
        image_data = base64.b64decode(data["image"])
        image = Image.open(BytesIO(image_data))
        image.save("test_screenshot.png")
        print("✅ Screenshot saved as test_screenshot.png")
    else:
        print("❌ Failed to capture screenshot")

def test_read_screen():
    print("\n🔹 Testing screen OCR:")
    response = requests.get(f"{BASE_URL}/vision/read-screen", headers=headers)
    print("⬅️ Response:", response.json())

if __name__ == "__main__":
    print("\n🚀 Running AI Control API Tests...")
    test_run_command()
    time.sleep(1)
    
    test_control_mouse()
    time.sleep(1)

    test_control_keyboard()
    time.sleep(1)

    test_take_screenshot()
    time.sleep(1)

    test_read_screen()
    time.sleep(1)

    print("\n✅ All tests completed!")
