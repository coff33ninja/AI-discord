# api_manager Module

Google Gemini AI API integration with rate limiting, request handling, and multi-key rotation support.

## Overview

The `api_manager` module handles all interactions with Google's Generative AI (Gemini) API. It provides:
- Intelligent request handling with timeout protection
- API key rotation for improved reliability
- Rate limit handling and cooldown management
- Usage tracking and analytics
- Error recovery and retry logic

## Key Classes

### GeminiAPIManager

Main class for managing Gemini API interactions.

```python
from modules.api_manager import GeminiAPIManager

# Initialize
api_manager = GeminiAPIManager()

# Generate content
response = await api_manager.generate_content("What is AI?")

# Check status
status = api_manager.get_status()
```

## Main Functions

### `generate_content(prompt, max_retries=2, timeout=30)`
Generate AI response from prompt.

**Parameters:**
- `prompt` (str) - User question/message
- `max_retries` (int) - Retry attempts on failure (default: 2)
- `timeout` (int) - Request timeout in seconds (default: 30)

**Returns:** str - AI response text

**Raises:**
- `APIError` - If all retry attempts fail
- `TimeoutError` - If request exceeds timeout

**Example:**
```python
response = await api_manager.generate_content("Tell me a joke")
print(response)  # "Why did the AI go to school?..."
```

### `get_status()`
Get current API status and usage information.

**Returns:** dict with keys:
- `available` (bool) - API is functioning
- `current_key` (int) - Which API key is active (1-3)
- `usage` (dict) - Request counts and timestamps
- `last_error` (str) - Last error message if any

**Example:**
```python
status = api_manager.get_status()
if status['available']:
    print(f"Using key #{status['current_key']}")
    print(f"Requests today: {status['usage']['request_count']}")
```

### `rotate_api_keys()`
Manually rotate to next API key.

**Returns:** bool - True if rotation successful

**Note:** Automatic rotation happens on API errors

### `check_rate_limit()`
Check if currently rate limited.

**Returns:** dict with:
- `limited` (bool) - Currently rate limited
- `wait_time` (int) - Seconds to wait before next request
- `requests_today` (int) - Request count today

## Configuration

### Environment Variables

Required in `.env`:
```env
GEMINI_API_KEY=your_primary_key
GEMINI_API_KEY_2=your_second_key      # Optional
GEMINI_API_KEY_3=your_third_key       # Optional
```

### Settings

```python
# Timeout (in seconds)
DEFAULT_TIMEOUT = 30

# Max retries
DEFAULT_MAX_RETRIES = 2

# Rate limit cooldown (seconds)
RATE_LIMIT_COOLDOWN = 60
```

## Usage Examples

### Basic Prompt

```python
api_manager = GeminiAPIManager()

response = await api_manager.generate_content(
    "What's the capital of France?"
)
print(response)  # "The capital of France is Paris."
```

### With Custom Personality

```python
prompt = """You are a tsundere AI assistant. Be helpful but act annoyed about it.
User asked: What time is it?

Respond in character:"""

response = await api_manager.generate_content(prompt)
```

### With Timeout Control

```python
# 10 second timeout for quick responses
response = await api_manager.generate_content(
    "Quick question: yes or no?",
    timeout=10
)
```

### Check API Health

```python
status = api_manager.get_status()
if status['available']:
    print("API is working!")
else:
    print(f"API error: {status['last_error']}")
```

## Rate Limiting

The API manager automatically handles rate limits:

```python
limit_info = api_manager.check_rate_limit()
if limit_info['limited']:
    print(f"Please wait {limit_info['wait_time']} seconds")
else:
    # Safe to proceed
    response = await api_manager.generate_content(prompt)
```

## Error Handling

```python
try:
    response = await api_manager.generate_content(prompt)
except APIError as e:
    print(f"API error: {e}")
except TimeoutError:
    print("Request timed out - try again")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Key Rotation

Automatic rotation occurs when:
1. Current key hits rate limit
2. Current key returns authentication error
3. Multiple consecutive failures

Manual rotation:
```python
success = api_manager.rotate_api_keys()
if success:
    print("Switched to next API key")
```

## Monitoring & Analytics

```python
status = api_manager.get_status()
print(f"API Status: {'Active' if status['available'] else 'Down'}")
print(f"Current Key: {status['current_key']}/3")
print(f"Today's Requests: {status['usage']['request_count']}")
print(f"Last 24h Requests: {status['usage']['daily_count']}")
```

## Performance Notes

- **Timeout:** Default 30 seconds (configurable)
- **Retry Logic:** Automatic with exponential backoff
- **Rate Limits:** Built-in cooldown and request throttling
- **Multi-key:** Automatic rotation for reliability
- **Async:** Full async/await support for non-blocking calls

## Dependencies

- `google-generativeai` - Official Gemini API client
- `aiohttp` - Async HTTP requests
- Built-in `asyncio` - Async execution

## Related Documentation

- [Commands Reference](../commands.md) - AI commands
- [Modules Overview](../MODULES.md) - Other modules
- See docstrings in `api_manager.py` for implementation details

---

*Last Updated: 2025-11-14*
