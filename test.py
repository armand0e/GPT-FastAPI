import requests
import json
import time

# Base URL of your FastAPI server
BASE_URL = "http://localhost:3000/api/web"

# Sample session ID for testing
TEST_SESSION_ID = "test_session"

def send_request(endpoint, data):
    """Send a POST request and print the response."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Authorization": "Bearer 0d3d7998-7f71-4d4b-a13f-6846ad5f8634","Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"\n🔹 Testing {endpoint}:")
        print(f"➡️ Request: {json.dumps(data, indent=2)}")
        print(f"⬅️ Response ({response.status_code}): {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error in {endpoint}: {str(e)}")

# 1️⃣ Start a browser session
send_request("open-tab", {"session_id": TEST_SESSION_ID, "tab_name": "default"})

# 2️⃣ Switch to a tab
send_request("switch-tab", {"session_id": TEST_SESSION_ID, "tab_name": "default"})

# 3️⃣ List all open tabs
send_request("list-tabs", {"session_id": TEST_SESSION_ID})

# 4️⃣ Rename a tab
send_request("rename-tab", {"session_id": TEST_SESSION_ID, "old_tab_name": "default", "new_tab_name": "main_tab"})

# 5️⃣ Close a tab
send_request("close-tab", {"session_id": TEST_SESSION_ID, "tab_name": "main_tab"})

# 6️⃣ Open a webpage
send_request("open-page", {"session_id": TEST_SESSION_ID, "url": "https://www.google.com"})

# 7️⃣ Get page title
send_request("get-title", {"session_id": TEST_SESSION_ID})

# 8️⃣ Get all links on the page
send_request("get-links", {"session_id": TEST_SESSION_ID})

# 9️⃣ Perform a Google search
send_request("search-google", {"session_id": TEST_SESSION_ID, "query": "FastAPI tutorial"})

# 🔟 Save the browser session
send_request("save-session", {"session_id": TEST_SESSION_ID})

# 1️⃣1️⃣ Get browsing history
send_request("get-history", {"session_id": TEST_SESSION_ID})

# 1️⃣2️⃣ Take a screenshot
send_request("screenshot", {"session_id": TEST_SESSION_ID})

# 1️⃣3️⃣ Send keystrokes
send_request("send-keys", {"session_id": TEST_SESSION_ID, "keys": "Hello World!"})

# 1️⃣4️⃣ Wait for an element to appear
send_request("wait-for-element", {"session_id": TEST_SESSION_ID, "selector": "input[name=q]", "timeout": 5000})

# 1️⃣5️⃣ Get the DOM structure
send_request("get-dom-structure", {"session_id": TEST_SESSION_ID})

# 1️⃣6️⃣ Click an element (example: Google search button)
send_request("click-element", {"session_id": TEST_SESSION_ID, "selector": "input[name=btnK]"})

# 1️⃣7️⃣ Close the browser session
send_request("close-session", {"session_id": TEST_SESSION_ID})
