from fastapi import APIRouter, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel
import os
import time
import traceback

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

async def get_browser_instance(session_id: str):
    """Retrieve or create a new browser session using async Playwright."""
    if session_id not in BROWSER_SESSIONS:
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            
            # Check if the cookie file exists before loading it
            cookie_file = f"{session_id}_cookies.json"
            if not os.path.exists(cookie_file):
                print(f"⚠️ Cookie file {cookie_file} not found. Creating a fresh session.")

            context = await browser.new_context(storage_state=cookie_file if os.path.exists(cookie_file) else None)
            page = await context.new_page()

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
        await page.goto(request.url, wait_until="networkidle")
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
        return log_debug(request.session_id, "get_page_title", details={"title": await page.title()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "get_page_title", error=e))

@router.post("/api/web/get-links")
async def get_links(request: GetLinksRequest):
    """Extracts all links from the current webpage."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        links = await page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")

        return log_debug(request.session_id, "get_links", details={"links_found": len(links), "sample_links": links[:3]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "get_links", error=e))

@router.post("/api/web/search-google")
async def google_search(request: GoogleSearchRequest):
    """Performs a Google Search and returns the top 5 results."""
    try:
        session = await get_browser_instance(request.session_id)
        page = session["pages"][session["active_tab"]]
        await page.goto("https://www.google.com")
        await page.fill("input[name=q]", request.query)
        await page.press("input[name=q]", "Enter")
        await page.wait_for_load_state("networkidle")

        results = await page.eval_on_selector_all("h3", "elements => elements.map(el => el.textContent)")
        links = await page.eval_on_selector_all("h3 a", "elements => elements.map(el => el.href)")

        return log_debug(request.session_id, "search_google", details={"query": request.query, "results_found": len(results), "sample_results": list(zip(results[:3], links[:3]))})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "search_google", details={"query": request.query}, error=e))

@router.post("/api/web/save-session")
async def save_cookies(request: SaveSessionRequest):
    """Saves cookies for persistent login."""
    try:
        session = await get_browser_instance(request.session_id)
        await session["context"].storage_state(path=f"{request.session_id}_cookies.json")
        return log_debug(request.session_id, "save_session", details={"cookies_saved": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=log_debug(request.session_id, "save_session", error=e))

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
        await page.screenshot(path=screenshot_path)
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
        dom_structure = await page.evaluate("""
            () => {
                function traverse(node) {
                    return {
                        tag: node.tagName,
                        text: node.innerText.slice(0, 50), // Limit text length
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
