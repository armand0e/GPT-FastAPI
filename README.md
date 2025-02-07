# FastAPI Terminal Server

## 📌 Overview
This is a **FastAPI-based** server that replicates and enhances the functionality of a Node.js-based terminal API. It allows:
- ✅ Running shell commands via API
- ✅ Retrieving real-time terminal logs
- ✅ Interrupting running processes
- ✅ Reading and writing large files
- ✅ Secure authentication for API requests
- ✅ WebSocket support for live updates
- ✅ Firebase integration for data storage
- ✅ Auto-generated OpenAPI documentation

## 🚀 Features
| Feature                      | Status |
|------------------------------|--------|
| Run shell commands via API   | ✅      |
| Retrieve real-time logs      | ✅      |
| Interrupt terminal commands  | ✅      |
| Read & Write large files     | ✅      |
| WebSockets for live updates  | ✅      |
| Secure authentication        | ✅      |
| Firebase integration         | ✅      |
| Auto-generated API docs      | ✅      |

---

## 🔧 Installation
Ensure you have **Python 3.10+** installed.

### 1️⃣ Clone Repository
```bash
git clone https://github.com/yourrepo/fastapi-terminal-server.git
cd fastapi-terminal-server
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Server
Start the FastAPI server with:
```bash
uvicorn main:app --reload
```

The server runs on **http://127.0.0.1:8000** by default.

### 📑 API Documentation
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔗 API Endpoints
### **Terminal Commands**
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST   | `/api/run-terminal-script` | Execute a shell command |
| GET    | `/api/get-terminal-logs` | Fetch terminal output |
| POST   | `/api/interrupt` | Interrupt running processes |

### **File Handling**
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET    | `/api/read-file?filename={name}` | Read a file |
| POST   | `/api/write-file` | Write to a file |
| POST   | `/api/upload-file` | Upload a file |

### **WebSockets**
- **Live Logs**: Connect to `/ws/logs`

---

## 🛡️ Authentication
API requests require an **Authorization Token**:
```json
{
    "Authorization": "Bearer YOUR_SECRET_TOKEN"
}
```

Set your token in the `.env` file:
```bash
AUTH_TOKEN=your_secret_token
```

---

## 🛠️ Firebase Integration
This project integrates **Firebase** for data storage.
- Ensure you have a valid `firebaseAdmin.json` file in the root directory.

### **Firebase Setup**
```python
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebaseAdmin.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
```

---

## 🔥 Deployment
### **Using Docker**
```bash
docker build -t fastapi-terminal .
docker run -p 8000:8000 fastapi-terminal
```

### **Using Gunicorn (Production)**
```bash
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### **Fix Port Binding Issues**
Use a different port:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## 📜 License
MIT License. See [LICENSE](LICENSE) for details.

---

## 💡 Future Enhancements
- [ ] Add database caching
- [ ] Improve security with JWT authentication
- [ ] Implement async task processing

For contributions, feel free to submit a **pull request**! 🚀

