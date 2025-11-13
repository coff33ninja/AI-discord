# search Module

Web search functionality using DuckDuckGo with intelligent result parsing and caching.

## Overview

The `search` module provides web search capabilities with:
- DuckDuckGo integration (no API key required)
- HTML result parsing with BeautifulSoup
- Smart result extraction and formatting
- Instant answer detection
- Result caching for performance
- Dual search methods for reliability

## Key Classes

### SearchEngine

Main class for web search operations.

```python
from modules.search import SearchEngine, get_search_engine

# Get singleton instance
search = get_search_engine()

# Search the web
results = await search.search("Python tutorials")

# Get instant answer
answer = await search.get_instant_answer("What is AI?")
```

## Main Functions

### `search(query, max_results=5)`
Search the web using DuckDuckGo.

**Parameters:**
- `query` (str) - Search query
- `max_results` (int) - Max results to return (default: 5)

**Returns:** list of dict with:
- `title` (str) - Result title
- `url` (str) - Result URL
- `description` (str) - Result snippet
- `source` (str) - Source name

**Example:**
```python
results = await search.search("Python best practices")
for result in results:
    print(f"{result['title']}")
    print(f"  {result['description']}")
    print(f"  {result['url']}\n")
```

### `get_instant_answer(query)`
Get instant answer for simple questions.

**Parameters:**
- `query` (str) - Question

**Returns:** str or None - Instant answer if available

**Example:**
```python
answer = await search.get_instant_answer("What is the capital of France?")
if answer:
    print(answer)  # "Paris"
```

### `search_with_fallback(query)`
Search with automatic fallback method.

**Returns:** list of results with fallback safety

**Example:**
```python
results = await search.search_with_fallback("ESP32 specifications")
print(f"Found {len(results)} results")
```

## Search Methods

### Method 1: DuckDuckGo API
- No authentication required
- Fast results
- Good for general queries

### Method 2: HTML Parsing
- Backup method if API fails
- Uses BeautifulSoup
- More reliable but slower

## Usage Examples

### Basic Web Search

```python
search = get_search_engine()

results = await search.search("machine learning algorithms")
if results:
    for result in results:
        print(f"**{result['title']}**")
        print(f"{result['description']}")
        print(f"📍 {result['url']}\n")
else:
    print("No results found")
```

### Instant Answers

```python
# Simple facts
answer = await search.get_instant_answer("What is Python?")
print(f"Answer: {answer}")

# Calculations
answer = await search.get_instant_answer("What is 2+2?")
print(f"2+2 = {answer}")

# Definitions
answer = await search.get_instant_answer("Define API")
print(f"API is: {answer}")
```

### Integration with AI Responses

```python
# Search to enhance AI responses
search_results = await search.search("latest AI news 2024")

if search_results:
    search_context = "\n".join([
        f"- {r['title']}: {r['description']}"
        for r in search_results[:3]
    ])
    
    # Pass to AI with context
    ai_response = await api_manager.generate_content(
        f"Based on these search results:\n{search_context}\n\n"
        f"User question: {user_question}"
    )
```

### Error Handling

```python
try:
    results = await search.search("query")
    if not results:
        print("No results found, try different keywords")
except SearchError as e:
    print(f"Search failed: {e}")
except TimeoutError:
    print("Search timed out, try again")
```

## Configuration

### Environment Variables
None required - DuckDuckGo is free and open.

### Settings in Code
```python
# Max results per search
MAX_RESULTS = 5

# Search timeout
SEARCH_TIMEOUT = 10

# Cache results
ENABLE_CACHE = True
```

## Search Tips

1. **Use specific keywords** - "Python tutorial" vs "Python"
2. **Add context** - "Python web scraping tutorial" for better results
3. **Use quotes** - "exact phrase" for exact matches
4. **Use minus** - "Python -snake" to exclude words

## Result Structure

Each search result contains:
```python
{
    'title': 'Result Title',
    'url': 'https://example.com',
    'description': 'Brief description of the result',
    'source': 'example.com'
}
```

## Caching

Results are automatically cached:
```python
# First search - hits API
results1 = await search.search("Python")

# Second identical search - uses cache
results2 = await search.search("Python")  # Faster!
```

## Performance

- **First search**: ~1-2 seconds
- **Cached search**: ~0.1 seconds
- **Instant answer**: ~0.5 seconds
- **Timeout**: 10 seconds

## Limitations

1. **No authentication needed** - Limited features vs paid APIs
2. **IP-based limits** - Respect rate limits
3. **Basic results** - No advanced filtering
4. **No instant answers always** - Some queries won't have instant answers

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- Built-in `asyncio` - Async operations

## Related Documentation

- [Commands Reference](../commands.md#-search--information-commands) - Search commands
- [Modules Overview](../MODULES.md) - Other modules
- See docstrings in `search.py` for implementation details

---

*Last Updated: 2025-11-14*
