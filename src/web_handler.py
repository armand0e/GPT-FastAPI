from fastapi import APIRouter, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel
import os
import time
from playwright_stealth import stealth_async
import random
import asyncio

router = APIRouter()

# Store active browser sessions
BROWSER_SESSIONS = {}

def log_debug(session_id, action, details=None, error=None, suggestion=None):
    """Generates an AI-friendly debug log for each browser action."""
    log = {
        "session_id": session_id,
        "action": action,
        "status": "error" if error else "success",
        "details": details,
        "error": str(error) if error else None,
        "suggestion": suggestion if error else None,
    }
    return log

class BrowserSessionRequest(BaseModel):
    session_id: str

class TabRequest(BaseModel):
    session_id: str
    tab_name: str

class RenameTabRequest(BaseModel):
    session_id: str
    old_tab_name: str
    new_tab_name: str
    
class CloseTabRequest(BaseModel):
    session_id: str
    tab_name: str

class OpenPageRequest(BaseModel):
    session_id: str
    url: str

class GetTitleRequest(BaseModel):
    session_id: str

class GetLinksRequest(BaseModel):
    session_id: str

class GoogleSearchRequest(BaseModel):
    session_id: str
    query: str

class SaveSessionRequest(BaseModel):
    session_id: str

class GetHistoryRequest(BaseModel):
    session_id: str

class ScreenshotRequest(BaseModel):
    session_id: str

class CloseSessionRequest(BaseModel):
    session_id: str

class SendKeysRequest(BaseModel):
    session_id: str
    keys: str

class WaitForElementRequest(BaseModel):
    session_id: str
    selector: str
    timeout: int = 5000

class GetDomStructureRequest(BaseModel):
    session_id: str

class ClickElementRequest(BaseModel):
    session_id: str
    selector: str

async def human_like_typing(page, selector, text):
    """Simulates human-like typing with random delays per keystroke."""
    for char in text:
        current_value = await page.eval_on_selector(selector, "el => el.value")
        await page.fill(selector, current_value + char)  # Appends one character at a time
        await asyncio.sleep(random.uniform(0.3, 0.8))  # Random delay between 300ms - 800ms
        
async def get_browser_instance(session_id: str):
    """Retrieve or create a new browser session with OAuth login support."""
    if session_id not in BROWSER_SESSIONS:
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=False)  # Run in visible mode for OAuth login
            context = await browser.new_context()

            page = await context.new_page()
            await stealth_async(page)

            # Load stored cookies if available
            cookies_path = f"{session_id}_cookies.json"
            if os.path.exists(cookies_path):
                await context.add_cookies_from_storage_state(cookies_path)
                print(f"✅ Loaded stored cookies from {cookies_path}")

            BROWSER_SESSIONS[session_id] = {
                "browser": browser,
                "context": context,
                "pages": {"default": page},
                "history": [],
                "active_tab": "default",
                "playwright": playwright
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail={"session_id": session_id, "error": str(e)})
    return BROWSER_SESSIONS[session_id]

@router.post("/api/web/google-login")
async def google_login(request: BrowserSessionRequest):
    """Opens Google OAuth login page for manual authentication."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]

        print("🌍 Opening Google Sign-In Page...")
        await page.goto("https://accounts.google.com/signin", wait_until="domcontentloaded")

        print("🛑 Please log in manually, then press Enter in the terminal when done.")
        input("Press Enter once you have logged in...")  # Wait for user confirmation

        # Save authentication cookies
        cookies_path = f"{request.session_id}_cookies.json"
        await page.context.storage_state(path=cookies_path)
        print(f"✅ Saved cookies to {cookies_path}")

        return {"message": "Login successful. Cookies saved for future use."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "google_login", error=e))

@router.post("/api/web/open-tab")
async def open_new_tab(request: TabRequest):
    """Opens a new tab and assigns it a name."""
    session = await get_browser_instance(request.session_id)
    if request.tab_name in session["pages"]:
        raise HTTPException(status_code=400, detail=log_debug(request.session_id, "open_new_tab", error="Tab name already exists."))

    new_page = await session["context"].new_page()
    session["pages"][request.tab_name] = new_page
    session["active_tab"] = request.tab_name

    return log_debug(request.session_id, "open_new_tab", details={"tab_name": request.tab_name})

@router.post("/api/web/switch-tab")
async def switch_tab(request: TabRequest):
    """Switches to a different open tab."""
    session = await get_browser_instance(request.session_id)
    if request.tab_name not in session["pages"]:
        raise HTTPException(status_code=404, detail=log_debug(request.session_id, "switch_tab", error="Tab not found."))

    session["active_tab"] = request.tab_name
    return log_debug(request.session_id, "switch_tab", details={"active_tab": request.tab_name})

@router.post("/api/web/list-tabs")
async def list_open_tabs(request: BrowserSessionRequest):
    """Lists all open tabs for the session."""
    session = await get_browser_instance(request.session_id)
    return log_debug(request.session_id, "list_open_tabs", details={"tabs": list(session["pages"].keys())})

@router.post("/api/web/rename-tab")
async def rename_tab(request: RenameTabRequest):
    """Renames a tab for better navigation."""
    session = await get_browser_instance(request.session_id)

    if request.old_tab_name not in session["pages"]:
        raise HTTPException(status_code=404, detail=log_debug(request.session_id, "rename_tab", error="Tab not found."))

    if request.new_tab_name in session["pages"]:
        raise HTTPException(status_code=400, detail=log_debug(request.session_id, "rename_tab", error="New tab name already exists."))

    session["pages"][request.new_tab_name] = session["pages"].pop(request.old_tab_name)
    if session["active_tab"] == request.old_tab_name:
        session["active_tab"] = request.new_tab_name

    return log_debug(request.session_id, "rename_tab", details={"old_tab_name": request.old_tab_name, "new_tab_name": request.new_tab_name})

@router.post("/api/web/close-tab")
async def close_tab(request: CloseTabRequest):
    """Closes a specific tab."""
    try:
        session = await get_browser_instance(request.session_id)

        if request.tab_name not in session["pages"]:
            raise HTTPException(status_code=404, detail=log_debug(
                request.session_id, "close_tab", error="Tab not found."
            ))

        await session["pages"][request.tab_name].close()
        del session["pages"][request.tab_name]

        if session["active_tab"] == request.tab_name:
            session["active_tab"] = list(session["pages"].keys())[0] if session["pages"] else None

        return log_debug(request.session_id, "close_tab", details={"tab_closed": request.tab_name, "remaining_tabs": list(session["pages"].keys())})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "close_tab", error=e))

@router.post("/api/web/open-page")
async def open_page(request: OpenPageRequest):
    """Opens a webpage and logs the action."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        await page.goto(request.url, wait_until="networkidle")  # FIXED: added await
        session["history"].append(request.url)

        return log_debug(request.session_id, "open_page", details={"url": request.url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "open_page", details={"url": request.url}, error=e))

@router.post("/api/web/get-title")
async def get_page_title(request: GetTitleRequest):
    """Gets the title of the currently open webpage."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        title = await page.title()  # FIXED: added await
        return log_debug(request.session_id, "get_page_title", details={"title": title})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "get_page_title", error=e))

@router.post("/api/web/get-links")
async def get_links(request: GetLinksRequest):
    """Extracts all links from the current webpage."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        links = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")  # FIXED: added await

        return log_debug(request.session_id, "get_links", details={"links_found": len(links), "sample_links": links[:3]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "get_links", error=e))

@router.post("/api/web/search-google")
async def google_search(request: GoogleSearchRequest):
    """Performs a Google Search using the authenticated session."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]

        print("🚀 Navigating to Google...")
        await page.goto("https://www.google.com", wait_until="domcontentloaded")

        # Check if Google remembers the login
        profile_button = await page.query_selector("a[href*='accounts.google.com']")
        if profile_button:
            print("✅ Google account detected. Proceeding with search.")
        else:
            print("⚠️ No Google account detected. You may need to re-login.")

        print("⏳ Waiting for search input to be visible...")
        await page.wait_for_selector("textarea[name=q]", timeout=10000)

        print("⌨️ Typing search query...")
        await human_like_typing(page, "textarea[name=q]", request.query)

        print("🔎 Pressing Enter...")
        await page.press("textarea[name=q]", "Enter")

        print("⏳ Waiting for search results...")
        await page.wait_for_load_state("networkidle")

        print("📋 Extracting results...")
        results = await page.eval_on_selector_all("h3", "elements => elements.map(el => el.textContent)")
        links = await page.eval_on_selector_all("h3 a", "elements => elements.map(el => el.href)")

        return log_debug(request.session_id, "search_google", details={
            "query": request.query, "results_found": len(results), "sample_results": list(zip(results[:3], links[:3]))
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "search_google", details={"query": request.query}, error=e))

@router.post("/api/web/get-history")
async def get_browsing_history(request: GetHistoryRequest):
    """Returns the browsing history of the session."""
    try:
        session = await get_browser_instance(request.session_id)
        return log_debug(request.session_id, "get_history", details={"history": session["history"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "get_history", error=e))

@router.post("/api/web/screenshot")
async def take_screenshot(request: ScreenshotRequest):
    """Takes a screenshot of the current page."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        screenshot_path = f"screenshot_{int(time.time())}.png"
        await page.screenshot(path=screenshot_path)  # FIXED: added await
        return log_debug(request.session_id, "take_screenshot", details={"screenshot_path": screenshot_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "take_screenshot", error=e))

@router.post("/api/web/close-session")
async def close_browser_session(request: CloseSessionRequest):
    """Closes a browser session."""
    try:
        if request.session_id in BROWSER_SESSIONS:
            await BROWSER_SESSIONS[request.session_id]["browser"].close()
            await BROWSER_SESSIONS[request.session_id]["playwright"].stop()
            del BROWSER_SESSIONS[request.session_id]
            return log_debug(request.session_id, "close_session", details={"session_closed": True})
        return log_debug(request.session_id, "close_session", error="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "close_session", error=e))

@router.post("/api/web/send-keys")
async def send_keys(request: SendKeysRequest):
    """Simulates keystrokes on the active page."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        await page.keyboard.type(request.keys)
        return log_debug(request.session_id, "send_keys", details={"keys_sent": request.keys})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "send_keys", error=e))

@router.post("/api/web/wait-for-element")
async def wait_for_element(request: WaitForElementRequest):
    """Waits for an element to appear before proceeding."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]

        print(f"🔍 Checking if selector '{request.selector}' exists...")
        exists = await page.query_selector(request.selector)

        if not exists:
            raise HTTPException(status_code=404, detail=log_debug(request.session_id, "wait_for_element", error=f"Selector '{request.selector}' not found on page."))

        print(f"⏳ Waiting for element '{request.selector}' to become visible...")
        await page.wait_for_selector(request.selector, timeout=request.timeout)

        return log_debug(request.session_id, "wait_for_element", details={"selector": request.selector, "timeout": request.timeout})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "wait_for_element", error=e))

@router.post("/api/web/get-dom-structure")
async def get_dom_structure(request: GetDomStructureRequest):
    """Returns a structured representation of the page's DOM elements."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]

        print("📋 Extracting DOM structure...")
        dom_structure = await page.evaluate("""
            () => {
                function traverse(node) {
                    return {
                        tag: node.tagName,
                        text: node.innerText ? node.innerText.slice(0, 50) : "",  // FIX: Check for missing text
                        children: [...node.children].map(traverse)
                    };
                }
                return traverse(document.body);
            }
        """)
        return log_debug(request.session_id, "get_dom_structure", details={"dom_structure": dom_structure})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "get_dom_structure", error=e))

@router.post("/api/web/click-element")
async def click_element(request: ClickElementRequest):
    """Clicks on a specific element on the page."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        await page.click(request.selector)
        return log_debug(request.session_id, "click_element", details={"selector": request.selector})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "click_element", error=e))
