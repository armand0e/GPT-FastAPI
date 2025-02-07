# WebSocket Routes API Guide

## Overview

This API module provides WebSocket-based real-time communication for log streaming and broadcasting, enabling AI or remote systems to receive live updates efficiently.

## Features

- Secure WebSocket authentication using API Keys (Bearer Token)
- Real-time log broadcasting to multiple connected clients
- Persistent WebSocket connections for efficient event handling
- API endpoint for streaming logs via HTTP for GPT-Builder integration

---

## API Endpoints

### 1. WebSocket Connection for Logs

#### **WebSocket** `/ws/logs`

Establishes a WebSocket connection to receive real-time logs.

**Connection Steps:**

1. Send a WebSocket handshake request with an `Authorization` header:

   ```http
   GET ws://localhost:3000/ws/logs
   Authorization: Bearer <API_KEY>
   ```

2. If authentication succeeds, the connection is established.
3. Logs are streamed in real time to the client.

**Example Log Message Format:**

```json
{
  "log": "Process started successfully"
}
```

#### **Implementation Notes:**

- WebSocket connections are authenticated using an API Key (`Authorization: Bearer <API_KEY>`).
- If authentication fails, the connection is immediately closed with an error message.
- Supports multiple simultaneous clients.

---

### 2. Broadcast Log Messages

#### **Internal Function:** `broadcast_log(message: str)`

Broadcasts log messages to all connected WebSocket clients.

**Example Call:**

```python
await broadcast_log("System update completed.")
```

**Implementation Notes:**

- This function is used internally to send messages to all authenticated WebSocket connections.
- Useful for sending system events, debug logs, or execution statuses.

---

### 3. Stream Logs via HTTP

#### **GET** `/api/get-logs-stream`

Provides an alternative log streaming mechanism via HTTP for GPT-Builder or non-WebSocket clients.

**Usage:**

1. Send a `GET` request to `/api/get-logs-stream`.
2. The response will be a **server-sent event (SSE)** stream providing real-time logs.

**Example Response Format:**

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"log": "Process initiated..."}

data: {"log": "Execution in progress..."}
```

**Implementation Notes:**

- Uses **Server-Sent Events (SSE)** to deliver logs in real-time via an HTTP connection.
- Auto-reconnect support for clients if the connection is lost.
- Works as an alternative for systems that do not support WebSockets.

---

## **Technical Details**

### **WebSocket Authentication**

- WebSocket clients must send an `Authorization: Bearer <API_KEY>` header.
- Invalid or missing API keys result in immediate connection closure.

### **Handling Multiple Connections**

- All active connections are stored in the `active_connections` list.
- The `broadcast_log()` function sends messages to all connected clients.

### **Graceful Disconnections**

- When a client disconnects, it is removed from the `active_connections` list to free up resources.

---

## **Security Considerations**

- **Secure API Key Authentication:** Prevents unauthorized access.
- **Rate Limiting (Optional):** Consider implementing limits to prevent abuse.
- **Error Handling:** Ensures graceful connection termination on errors.

---

## **Final Thoughts**

This module provides an efficient WebSocket-based logging system with an HTTP-based alternative, ensuring flexible real-time communication for AI and remote debugging systems.

🚀 **Next Steps:**

- Implement filtering mechanisms to allow clients to subscribe to specific log categories.
- Add **client acknowledgment** to confirm log receipt.
- Support **reconnecting clients** in case of network failures.
