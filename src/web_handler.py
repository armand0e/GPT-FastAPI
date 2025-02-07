from fastapi import APIRouter, HTTPException, Query
from playwright.sync_api import sync_playwright
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

def get_browser_instance(session_id: str):
    """Retrieve or create a new browser session with multi-tab support."""
    if session_id not in BROWSER_SESSIONS:
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(storage_state=f"{session_id}_cookies.json")
            page = context.new_page()

            BROWSER_SESSIONS[session_id] = {
                "browser": browser,
                "context": context,
                "pages": {"default": page},
                "history": [],
                "active_tab": "default",
                "playwright": playwright
            }
        except Exception as e:
            return HTTPException(status_code=500, detail=log_debug(session_id, "initialize_browser", error=e))
    return BROWSER_SESSIONS[session_id]

@router.post("/api/web/open-tab")
async def open_new_tab(session_id: str, tab_name: str = "new_tab"):
    """Opens a new tab and assigns it a name."""
    try:
        session = get_browser_instance(session_id)
        if tab_name in session["pages"]:
            return HTTPException(status_code=400, detail=log_debug(
                session_id, "open_new_tab", error="Tab name already exists.",
                suggestion="Use a different tab name."
            ))

        new_page = session["context"].new_page()
        session["pages"][tab_name] = new_page
        session["active_tab"] = tab_name

        return log_debug(session_id, "open_new_tab", details={"tab_name": tab_name})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "open_new_tab", error=e,
            suggestion="Ensure a valid session exists before opening a new tab."
        ))

@router.post("/api/web/switch-tab")
async def switch_tab(session_id: str, tab_name: str):
    """Switches to a different open tab."""
    try:
        session = get_browser_instance(session_id)
        if tab_name not in session["pages"]:
            return HTTPException(status_code=404, detail=log_debug(
                session_id, "switch_tab", error="Tab not found.",
                suggestion="Ensure the tab exists before switching."
            ))

        session["active_tab"] = tab_name
        return log_debug(session_id, "switch_tab", details={"active_tab": tab_name})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "switch_tab", error=e,
            suggestion="Ensure the session and tab exist before switching."
        ))

@router.get("/api/web/list-tabs")
async def list_open_tabs(session_id: str):
    """Lists all open tabs for the session."""
    try:
        session = get_browser_instance(session_id)
        return log_debug(session_id, "list_open_tabs", details={"tabs": list(session["pages"].keys())})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "list_open_tabs", error=e,
            suggestion="Ensure a valid session exists before listing tabs."
        ))

@router.post("/api/web/rename-tab")
async def rename_tab(session_id: str, old_tab_name: str, new_tab_name: str):
    """Renames a tab for better navigation."""
    try:
        session = get_browser_instance(session_id)

        if old_tab_name not in session["pages"]:
            return HTTPException(status_code=404, detail=log_debug(
                session_id, "rename_tab", error="Tab not found.",
                suggestion="Ensure the old tab name exists before renaming."
            ))

        if new_tab_name in session["pages"]:
            return HTTPException(status_code=400, detail=log_debug(
                session_id, "rename_tab", error="New tab name already exists.",
                suggestion="Use a different tab name."
            ))

        session["pages"][new_tab_name] = session["pages"].pop(old_tab_name)
        if session["active_tab"] == old_tab_name:
            session["active_tab"] = new_tab_name

        return log_debug(session_id, "rename_tab", details={"old_tab_name": old_tab_name, "new_tab_name": new_tab_name})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "rename_tab", error=e,
            suggestion="Ensure the session and old tab exist before renaming."
        ))

@router.post("/api/web/close-tab")
async def close_tab(session_id: str, tab_name: str):
    """Closes a specific tab."""
    try:
        session = get_browser_instance(session_id)

        if tab_name not in session["pages"]:
            return HTTPException(status_code=404, detail=log_debug(
                session_id, "close_tab", error="Tab not found.",
                suggestion="Ensure the tab name is correct before closing."
            ))

        session["pages"][tab_name].close()
        del session["pages"][tab_name]

        if session["active_tab"] == tab_name:
            session["active_tab"] = list(session["pages"].keys())[0] if session["pages"] else None

        return log_debug(session_id, "close_tab", details={"tab_closed": tab_name, "remaining_tabs": list(session["pages"].keys())})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "close_tab", error=e,
            suggestion="Ensure the tab exists before attempting to close it."
        ))

@router.post("/api/web/open-page")
async def open_page(session_id: str, url: str):
    """Opens a webpage and returns the full HTML content with debug logs."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        page.goto(url, wait_until="networkidle")
        session["history"].append(url)

        return log_debug(session_id, "open_page", details={"url": url})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "open_page", details={"url": url}, 
            error=e, suggestion="Ensure the URL is valid and reachable."
        ))

@router.get("/api/web/get-title")
async def get_page_title(session_id: str):
    """Gets the title of the currently open webpage with debug logs."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        return log_debug(session_id, "get_page_title", details={"title": page.title()})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "get_page_title", error=e, 
            suggestion="Ensure a webpage is currently open before requesting the title."
        ))

@router.get("/api/web/get-links")
async def get_links(session_id: str):
    """Extracts all links from the current webpage with debug logs."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        links = page.eval_on_selector_all("a", "elements => elements.map(el => el.href)")

        return log_debug(session_id, "get_links", details={"links_found": len(links), "sample_links": links[:3]})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "get_links", error=e,
            suggestion="Ensure a webpage is open before requesting links."
        ))

@router.get("/api/web/search-google")
async def google_search(session_id: str, query: str):
    """Performs a Google Search and returns the top 5 results with AI debugging logs."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        page.goto("https://www.google.com")
        page.fill("input[name=q]", query)
        page.press("input[name=q]", "Enter")
        page.wait_for_load_state("networkidle")

        results = page.eval_on_selector_all("h3", "elements => elements.map(el => el.textContent)")
        links = page.eval_on_selector_all("h3 a", "elements => elements.map(el => el.href)")

        return log_debug(session_id, "search_google", details={"query": query, "results_found": len(results), "sample_results": list(zip(results[:3], links[:3]))})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "search_google", details={"query": query}, 
            error=e, suggestion="Ensure Google is accessible and that captchas are not blocking searches."
        ))

@router.post("/api/web/save-session")
async def save_cookies(session_id: str):
    """Saves cookies for persistent login with AI debugging logs."""
    try:
        session = get_browser_instance(session_id)
        session["context"].storage_state(path=f"{session_id}_cookies.json")
        return log_debug(session_id, "save_session", details={"cookies_saved": True})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "save_session", error=e, 
            suggestion="Ensure the browser session exists before saving cookies."
        ))

@router.get("/api/web/get-history")
async def get_browsing_history(session_id: str):
    """Returns the browsing history of the session with AI debugging logs."""
    try:
        session = get_browser_instance(session_id)
        return log_debug(session_id, "get_history", details={"history": session["history"]})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "get_history", error=e, 
            suggestion="Ensure the session ID is valid."
        ))

@router.post("/api/web/screenshot")
async def take_screenshot(session_id: str):
    """Takes a screenshot of the current page with AI debugging logs."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        screenshot_path = f"screenshot_{int(time.time())}.png"
        page.screenshot(path=screenshot_path)
        return log_debug(session_id, "take_screenshot", details={"screenshot_path": screenshot_path})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "take_screenshot", error=e, 
            suggestion="Ensure a valid page is open before taking a screenshot."
        ))


@router.post("/api/web/close-session")
async def close_browser_session(session_id: str):
    """Closes a browser session with AI debugging logs."""
    try:
        if session_id in BROWSER_SESSIONS:
            BROWSER_SESSIONS[session_id]["browser"].close()
            BROWSER_SESSIONS[session_id]["playwright"].stop()
            del BROWSER_SESSIONS[session_id]
            return log_debug(session_id, "close_session", details={"session_closed": True})
        return log_debug(session_id, "close_session", error="Session not found")
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "close_session", error=e,
            suggestion="Ensure the session ID is valid before closing."
        ))
        
@router.post("/api/web/send-keys")
async def send_keys(session_id: str, keys: str):
    """Simulates keystrokes on the active page."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        page.keyboard.type(keys)
        return log_debug(session_id, "send_keys", details={"keys_sent": keys})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "send_keys", error=e, 
            suggestion="Ensure the page is focused before sending keystrokes."
        ))


@router.post("/api/web/wait-for-element")
async def wait_for_element(session_id: str, selector: str, timeout: int = 5000):
    """Waits for an element to appear before proceeding."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        page.wait_for_selector(selector, timeout=timeout)
        return log_debug(session_id, "wait_for_element", details={"selector": selector, "timeout": timeout})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "wait_for_element", error=e, 
            suggestion="Ensure the selector is correct and the page has fully loaded."
        ))

@router.get("/api/web/get-dom-structure")
async def get_dom_structure(session_id: str):
    """Returns a structured representation of the page's DOM elements."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        dom_structure = page.evaluate("""
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
        return log_debug(session_id, "get_dom_structure", details={"dom_structure": dom_structure})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "get_dom_structure", error=e, 
            suggestion="Ensure a valid page is open before extracting DOM structure."
        ))

@router.post("/api/web/click-element")
async def click_element(session_id: str, selector: str):
    """Clicks on a specific element on the page."""
    try:
        session = get_browser_instance(session_id)
        page = session["pages"][session["active_tab"]]
        page.click(selector)
        return log_debug(session_id, "click_element", details={"selector": selector})
    except Exception as e:
        return HTTPException(status_code=500, detail=log_debug(
            session_id, "click_element", error=e, 
            suggestion="Ensure the selector is correct and the element is clickable."
        ))

