# AI Handler API Documentation

## Overview
The AI Handler API enables interaction with a pre-trained transformer model for generating sentence embeddings. These embeddings are useful for various NLP tasks, including similarity search, clustering, and AI reasoning.

## Endpoints

### `POST /api/sentence-embedding`
**Description:**  
Generates a numerical embedding for a given text input using a transformer-based model.

**Request Parameters:**  
- `text` (string, required): The text input that needs to be encoded into an embedding.

**Response:**  
- `embedding` (list of floats): The generated embedding for the input text.

**Example Request:**
```json
{
  "text": "Artificial intelligence is transforming industries."
}
```

**Example Response:**
```json
{
  "embedding": [[0.3456, -0.1234, 0.7890, ...]]
}
```

## Implementation Details
- Uses the `sentence-transformers` library with the `all-MiniLM-L6-v2` model.
- Provides a simple API wrapper around the embedding generation process.
- Supports embedding extraction for AI-driven applications requiring semantic understanding of text.

## Notes
- Ensure that `sentence-transformers` is installed in the environment before using this API.
- This API can be expanded to support multiple transformer models or additional NLP capabilities.

