# **GPT-FastAPI: Project Summary**
## **Overview**
**GPT-FastAPI** is a **FastAPI-based backend service** designed to offer various functionalities, including **authentication, file management, system control, document processing, logging, and computer vision**. The project is structured with modular API routes, each handling a specific domain. It is a powerful **backend system** that offers **remote system management, file operations, automation, and vision capabilities**. With **authentication, process tracking, and logging**, it is well-suited for **secure remote administration and automation tasks**.

# **📌 GPT-FastAPI: Endpoint Summary**
Below is a **summary of each API endpoint** categorized by functionality.

---

## **🔐 Authentication Endpoints (`auth.py`)**
| **Endpoint**      | **Method** | **Description** |
|------------------|-----------|----------------|
| **Protected Endpoints** | _Depends_ | Uses `authenticate_request()` to validate API key in headers (`Bearer <API_KEY>`). |

🛠 **Purpose**: Ensures **API security** by requiring an API key for access.

---

## **📄 API Documentation & Metadata (`docs_router.py`)**
| **Endpoint**      | **Method** | **Description** |
|------------------|-----------|----------------|
| `/docs`          | `POST`  | Returns **OpenAPI documentation**. |
| `/metadata`      | `POST`  | Provides **API metadata** (name, version, description, endpoints). |
| `/health`        | `POST`  | Returns **server status & uptime**. |

🛠 **Purpose**: Exposes API documentation and **health monitoring**.

---

## **📂 File Handling (`file_handler.py`)**
| **Endpoint**      | **Method** | **Description** |
|------------------|-----------|----------------|
| `/read-file`     | `POST`    | Reads **full content** of a file. |
| `/write-file`    | `POST`    | Creates or **overwrites** a file. |
| `/append-file`   | `POST`    | Appends data to a file. |
| `/read-lines`    | `POST`    | Reads **specific lines** from a file. |
| `/replace-function` | `POST`  | Replaces a **Python function** inside a script dynamically. |

🛠 **Purpose**: **Read, write, and modify files remotely**.

---

## **📊 System Information (`info_router.py`)**
| **Endpoint**       | **Method** | **Description** |
|-------------------|-----------|----------------|
| `/info`           | `POST`    | Returns **system info** (OS, CPU, RAM, disk usage). |
| `/host-resources` | `POST`    | Fetches **real-time CPU, RAM, and disk usage**. |
| `/list-running-processes` | `POST` | Lists **all active processes** on the system. |

🛠 **Purpose**: **Monitor system health and performance**.

---

## **📜 Logging (`logger.py`)**
| **Endpoint**      | **Method** | **Description** |
|------------------|-----------|----------------|
| **Logs API Calls** | _Auto_ | Logs **all API events** into `logs/system.log`. |

🛠 **Purpose**: Maintains **detailed logging** for debugging & auditing.

---

## **🖥️ System Control (`system_router.py`)**
| **Endpoint**      | **Method** | **Description** |
|------------------|-----------|----------------|
| `/set-current-directory` | `POST` | Changes the **working directory**. |
| `/get-current-directory` | `POST` | Returns the **current working directory**. |
| `/run-command`   | `POST`  | Executes **a system command** (blocking). |
| `/run-long-command` | `POST` | Runs **a command asynchronously** and returns a `process_id`. |
| `/check-command-status/{process_id}` | `POST` | Checks the **status of a running command**. |
| `/mouse` | `POST` | Moves the **mouse cursor & performs clicks**. |
| `/keyboard` | `POST` | Simulates **keyboard key presses**. |

🛠 **Purpose**: **Execute system commands, automate inputs, and track processes**.

---

## **🖼️ Computer Vision (`vision_router.py`)**
| **Endpoint**      | **Method** | **Description** |
|------------------|-----------|----------------|
| `/screenshot`    | `POST`  | Captures a **screenshot** and returns it as **Base64**. |
| `/read-screen`   | `POST`  | Extracts **text from the screen** using **OCR**. |

🛠 **Purpose**: Supports **remote screen capture & text recognition**.

---

## **📌 Summary of All Endpoints**
| **Category**            | **Key Functionalities** |
|------------------------|-----------------------|
| **🔐 Authentication**  | API Key validation |
| **📄 Documentation**   | OpenAPI, metadata, health check |
| **📂 File Handling**   | Read, write, append, modify files |
| **📊 System Info**     | CPU, RAM, disk, processes |
| **📜 Logging**         | Logs all API requests |
| **🖥️ System Control**  | Run commands, change directories, automate inputs |
| **🖼️ Vision**         | Screenshot, OCR (text recognition) |
