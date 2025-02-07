# AI Guide: Using the Web Search API Effectively

## 📌 Introduction
This document provides structured guidance for interacting with the web using the API. The AI must understand how to **navigate web pages, extract useful data, handle interactions, debug errors, and optimize efficiency**.

---

## 🌍 Understanding the Web Environment
When interacting with web pages, consider the following:
1. **Web Pages Are Dynamic** – Some elements may take time to load.
2. **Multiple Tabs Can Be Used** – You can **open, rename, switch, and close** tabs.
3. **DOM Elements Vary** – Buttons, links, input fields, etc., must be correctly identified using **selectors**.
4. **Sites May Restrict Automation** – Some sites have bot detection mechanisms.

---

## 🏁 Starting a Browser Session
All web interactions require an **active session ID**.

### **🚀 Initialize a Web Session**
1. **Start a session:** `POST /api/web/open-tab?session_id=<SESSION_ID>&tab_name=default`
2. **Verify success:** The response will include `status: success`.

---

## 📑 Managing Tabs
AI should use tabs to **organize searches and multitask efficiently**.

### **🆕 Open a New Tab**
- `POST /api/web/open-tab?session_id=<SESSION_ID>&tab_name=<TAB_NAME>`  
- Ensure **tab names are unique**.

### **🔄 Switch Between Tabs**
- `POST /api/web/switch-tab?session_id=<SESSION_ID>&tab_name=<TAB_NAME>`

### **✏ Rename a Tab**
- `POST /api/web/rename-tab?session_id=<SESSION_ID>&old_tab_name=<OLD_NAME>&new_tab_name=<NEW_NAME>`

### **❌ Close a Tab**
- `POST /api/web/close-tab?session_id=<SESSION_ID>&tab_name=<TAB_NAME>`  
- Always verify **at least one tab remains open**.

### **📜 List Open Tabs**
- `GET /api/web/list-tabs?session_id=<SESSION_ID>`

---

## 🌐 Navigating the Web
AI can search, extract data, and interact with pages.

### **🔍 Open a Web Page**
- `POST /api/web/open-page?session_id=<SESSION_ID>&url=<PAGE_URL>`

### **🔗 Get All Links on the Page**
- `GET /api/web/get-links?session_id=<SESSION_ID>`  
- Useful for **finding relevant navigation paths**.

### **📌 Search Google & Extract Results**
- `GET /api/web/search-google?session_id=<SESSION_ID>&query=<SEARCH_QUERY>`  
- **Limitations:** Google may show captchas for bots.

---

## 🖱️ Interacting with Pages
AI must correctly **identify and interact** with elements.

### **📝 Fill Input Fields**
- `POST /api/web/fill-form?session_id=<SESSION_ID>&selector=<ELEMENT_SELECTOR>&text=<TEXT_INPUT>`  
- Use when filling **login forms, search bars, or text fields**.

### **🖱 Click Elements (Buttons, Links, etc.)**
- `POST /api/web/click-element?session_id=<SESSION_ID>&selector=<ELEMENT_SELECTOR>`  
- Ensure the element is **visible & clickable**.

### **⌨ Simulate Keystrokes**
- `POST /api/web/send-keys?session_id=<SESSION_ID>&keys=<KEY_INPUT>`  
- Useful for **pressing Enter, typing dynamically**.

### **📜 Scroll the Page**
- `POST /api/web/scroll?session_id=<SESSION_ID>&amount=1000`  
- Allows interaction with **lazy-loaded content**.

---

## 🔎 Extracting Information
AI must **interpret page content effectively**.

### **📑 Get Page Title**
- `GET /api/web/get-title?session_id=<SESSION_ID>`

### **📃 Extract Text from an Element**
- `GET /api/web/extract-text?session_id=<SESSION_ID>&selector=<ELEMENT_SELECTOR>`

### **🖼 Capture a Screenshot**
- `POST /api/web/screenshot?session_id=<SESSION_ID>`  
- Useful for **debugging visual content**.

### **📊 Get Page Structure (DOM)**
- `GET /api/web/get-dom-structure?session_id=<SESSION_ID>`  
- Helps AI understand **element relationships**.

---

## 🛠 Debugging & Handling Errors
AI should be **self-aware of failures & adapt accordingly**.

### **🚧 Handling Load Issues**
- **If an element is missing**, use:  
  `POST /api/web/wait-for-element?session_id=<SESSION_ID>&selector=<ELEMENT_SELECTOR>&timeout=5000`

### **🔄 Retry Mechanism**
- If an API request **fails**, retry **up to 3 times** with delays.

### **📜 Log & Analyze Errors**
- Every response contains:
  - `"status": "error"` if an action fails.
  - `"suggestion": "Possible fix"` for troubleshooting.
  - `"details": "Additional debugging info"`.

---

## 🔄 Saving & Restoring Sessions
AI should **retain its state** for continuous learning.

### **🔒 Save Cookies & Session Data**
- `POST /api/web/save-session?session_id=<SESSION_ID>`  
- Useful for **staying logged in**.

### **📜 Retrieve Browsing History**
- `GET /api/web/get-history?session_id=<SESSION_ID>`  
- AI can track previous pages visited.

### **🔚 Close the Browser Session**
- `POST /api/web/close-session?session_id=<SESSION_ID>`  
- Always **close unused sessions** to **free up memory**.

---

## ⚡ Best Practices for AI Web Searching
✅ **Be Efficient**: Don't open too many tabs or make unnecessary requests.  
✅ **Handle Failures Smartly**: If a page fails to load, retry or use an alternative.  
✅ **Extract What Matters**: Don't return full-page HTML unless necessary.  
✅ **Respect Websites**: Avoid overwhelming servers with rapid requests.  
✅ **Use Debugging Logs**: Review error messages and adapt accordingly.  

---

## 🎯 Conclusion
These API requests allows you to **navigate the web, extract data, and interact with pages** effectively. Following structured best practices ensures **efficient, accurate, and robust** web automation.

"""