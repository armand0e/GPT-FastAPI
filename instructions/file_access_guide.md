# File Access API Guide

## Overview
This API provides unrestricted access to the entire filesystem. It allows reading, writing, searching, uploading, and deleting files, as well as retrieving metadata.

## ⚠️ Security Warning
This API can **read, modify, and delete** any file or directory on the system. Use with caution!

## Endpoints

### 1. Read a File
**Endpoint:** `GET /api/read-file`
- **Description:** Retrieves the contents of a specified file.
- **Parameters:**
  - `filepath` (string, required) – Full path to the file.
- **Response:**
  ```json
  {
    "filepath": "/path/to/file.txt",
    "content": "File contents here"
  }
  ```

### 2. Write to a File
**Endpoint:** `POST /api/write-file`
- **Description:** Writes content to a file, creating it if necessary.
- **Body:**
  ```json
  {
    "filepath": "/path/to/file.txt",
    "content": "New file content"
  }
  ```
- **Response:**
  ```json
  {
    "message": "File '/path/to/file.txt' saved successfully"
  }
  ```

### 3. Fuzzy Search in a File
**Endpoint:** `POST /api/fuzzy-search-file`
- **Description:** Searches a file for similar matches to a given query.
- **Parameters:**
  - `filepath` (string, required) – Path to the file.
  - `query` (string, required) – Search text.
- **Response:**
  ```json
  {
    "matches": [[3, "Some line with match", 85], [8, "Another match", 78]]
  }
  ```

### 4. Upload a File
**Endpoint:** `POST /api/upload-file`
- **Description:** Uploads a file to a specified location.
- **Parameters:**
  - `filepath` (string, required) – Path where the file should be saved.
  - `file` (file, required) – The file to upload.
- **Response:**
  ```json
  {
    "message": "File '/path/to/file.txt' uploaded successfully"
  }
  ```

### 5. List Files in a Directory
**Endpoint:** `GET /api/list-files`
- **Description:** Lists all files in a given directory.
- **Parameters:**
  - `directory` (string, required) – Path of the directory.
- **Response:**
  ```json
  {
    "directory": "/some/path",
    "files": ["file1.txt", "file2.log"]
  }
  ```

### 6. Get File Metadata
**Endpoint:** `GET /api/file-metadata`
- **Description:** Retrieves size and last modification time of a file.
- **Parameters:**
  - `filepath` (string, required) – Full path to the file.
- **Response:**
  ```json
  {
    "filepath": "/some/path/file.txt",
    "size_bytes": 1024,
    "last_modified": 1700000000.0
  }
  ```

### 7. Delete a File
**Endpoint:** `DELETE /api/delete-file`
- **Description:** Deletes a specified file.
- **Parameters:**
  - `filepath` (string, required) – Full path of the file to delete.
- **Response:**
  ```json
  {
    "message": "File '/path/to/file.txt' deleted successfully"
  }
  ```

### 8. Delete a Directory
**Endpoint:** `DELETE /api/delete-directory`
- **Description:** Deletes a directory and all its contents.
- **Parameters:**
  - `directory` (string, required) – Path of the directory.
- **Response:**
  ```json
  {
    "message": "Directory '/some/path/' deleted successfully"
  }
  ```

## Example Usage
### Read a File
```bash
curl -X GET "http://localhost:3000/api/read-file?filepath=/home/user/document.txt"
```

### Write to a File
```bash
curl -X POST "http://localhost:3000/api/write-file" \
     -H "Content-Type: application/json" \
     -d '{"filepath": "/home/user/newfile.txt", "content": "Hello World!"}'
```

### Delete a File
```bash
curl -X DELETE "http://localhost:3000/api/delete-file?filepath=/home/user/file.txt"
```

## Notes
- This API does **not** restrict file access. It can modify system files.
- Use with caution, especially for deletion endpoints.
- Can be extended with permission controls for added security.

🚀 **Handle with care!**

