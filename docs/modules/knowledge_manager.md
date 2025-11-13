# knowledge_manager Module

Custom knowledge base management for storing and retrieving bot-specific facts, context, and custom information.

## Overview

The `knowledge_manager` module handles:
- Custom knowledge base storage
- Fact storage and retrieval
- Knowledge indexing
- Context-aware fact lookup
- Knowledge persistence
- Semantic search in knowledge base
- Integration with Gemini AI

## Key Classes

### KnowledgeManager

Singleton manager for custom knowledge.

```python
from modules.knowledge_manager import KnowledgeManager, get_knowledge_manager

# Get singleton instance
km = get_knowledge_manager()

# Add facts
await km.add_fact("Akeno", "Akeno is a high school student")

# Retrieve facts
facts = await km.get_facts("Akeno")

# Search knowledge
results = await km.search("school")
```

## Main Functions

### `add_fact(key, fact, category=None)`

Add a fact to knowledge base.

**Parameters:**
- `key` (str) - Entity key (e.g., "Akeno", "user_123")
- `fact` (str) - Fact text
- `category` (str) - Optional category

**Returns:** bool - Success

**Example:**
```python
km = get_knowledge_manager()

await km.add_fact(
    key="Akeno",
    fact="Akeno loves spicy food",
    category="preferences"
)
```

### `get_facts(key, category=None)`

Get all facts for an entity.

**Parameters:**
- `key` (str) - Entity key
- `category` (str) - Optional category filter

**Returns:** list - Facts

**Example:**
```python
facts = await km.get_facts("Akeno")
print(facts)
# ["Akeno is a high school student", "Akeno loves spicy food"]
```

### `search(query, limit=10)`

Search knowledge base semantically.

**Parameters:**
- `query` (str) - Search query
- `limit` (int) - Max results

**Returns:** list - Matching facts

**Example:**
```python
results = await km.search("food preferences")
for fact in results:
    print(fact)
```

### `add_category(key, category)`

Add category to fact.

**Parameters:**
- `key` (str) - Entity key
- `category` (str) - Category name

**Returns:** bool - Success

**Example:**
```python
await km.add_category("Akeno", "personality_type")
```

### `delete_fact(key, fact)`

Remove a fact.

**Parameters:**
- `key` (str) - Entity key
- `fact` (str) - Fact text

**Returns:** bool - Success

**Example:**
```python
await km.delete_fact("Akeno", "old fact")
```

### `clear_knowledge(key)`

Delete all facts for entity.

**Parameters:**
- `key` (str) - Entity key

**Returns:** bool - Success

**Example:**
```python
await km.clear_knowledge("temporary_user")
```

### `get_context(key)`

Get formatted context for AI.

**Parameters:**
- `key` (str) - Entity key

**Returns:** str - Formatted facts

**Example:**
```python
context = await km.get_context("Akeno")
# Use in AI prompt for better responses
```

### `import_facts(key, facts_list)`

Bulk import facts.

**Parameters:**
- `key` (str) - Entity key
- `facts_list` (list) - Facts to import

**Returns:** int - Number imported

**Example:**
```python
facts = [
    "Born in 1995",
    "Loves anime",
    "Studies engineering"
]

count = await km.import_facts("Akeno", facts)
print(f"Imported {count} facts")
```

## Knowledge Categories

Standard categories:

| Category | Purpose | Example |
|----------|---------|---------|
| **personality** | Personality traits | "Tsundere personality" |
| **preferences** | Likes and dislikes | "Loves spicy food" |
| **skills** | Abilities | "Good at cooking" |
| **relationships** | Connections | "Friend with John" |
| **history** | Background | "Born in Tokyo" |
| **interests** | Hobbies | "Interested in anime" |
| **memories** | Specific events | "Met user on 2024-01-01" |
| **custom** | User-defined | Any custom fact |

## Usage Examples

### Store User Preferences

```python
user_id = "user_123"
km = get_knowledge_manager()

# Store multiple preferences
preferences = [
    "Prefers tea over coffee",
    "Doesn't like spicy food",
    "Loves video games",
    "Morning person"
]

await km.import_facts(user_id, preferences)
```

### Retrieve and Use Facts in Responses

```python
# Get facts about user
facts = await km.get_facts(user_id)

# Format for AI context
context = await km.get_context(user_id)

# Use in API request
response = await api_manager.chat(
    message=user_message,
    system_prompt=f"User facts:\n{context}\n\nRespond accordingly.",
)
```

### Search Knowledge Base

```python
# Find all facts about preferences
food_facts = await km.search("food preferences")

# Find facts about hobbies
hobby_facts = await km.search("hobbies")

# General search
results = await km.search("what does Akeno like")
```

### Categorize Facts

```python
# Add organized facts
await km.add_fact("Akeno", "Likes anime", category="interests")
await km.add_fact("Akeno", "Is shy", category="personality")
await km.add_fact("Akeno", "Speaks Japanese", category="skills")

# Retrieve by category
personality_facts = await km.get_facts("Akeno", category="personality")
```

### Build User Profile

```python
@bot.command()
async def profile(ctx, user_name):
    km = get_knowledge_manager()
    
    facts = await km.get_facts(user_name)
    
    if not facts:
        await ctx.send(f"No facts about {user_name}")
        return
    
    embed = discord.Embed(
        title=f"Profile: {user_name}",
        color=discord.Color.blue()
    )
    
    categories = {}
    for fact in facts:
        # Group by category
        category = await km.get_fact_category(fact) or "General"
        if category not in categories:
            categories[category] = []
        categories[category].append(fact)
    
    for cat, facts_list in categories.items():
        embed.add_field(
            name=cat,
            value="\n".join(f"• {f}" for f in facts_list),
            inline=False
        )
    
    await ctx.send(embed=embed)
```

### Context-Aware Responses

```python
# Get user knowledge
facts = await km.get_facts(user_id)
context = await km.get_context(user_id)

# Ask AI to be aware of user facts
message = user_input
system_prompt = f"""You are Akeno.
Here's what you know about the user:
{context}

Remember these facts when responding."""

response = await api_manager.chat(
    message=message,
    system_prompt=system_prompt
)

await ctx.send(response)
```

### Memory Learning

```python
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    km = get_knowledge_manager()
    
    # Extract facts from conversation
    # "I love pizza" -> Add fact
    if "i love" in message.content.lower():
        fact = message.content.split("i love")[1].strip()
        await km.add_fact(
            key=str(message.author.id),
            fact=f"Loves {fact}",
            category="preferences"
        )
```

## Knowledge Storage

Knowledge is persisted in database:

```sql
CREATE TABLE knowledge_base (
    id INTEGER PRIMARY KEY,
    entity_key TEXT NOT NULL,
    fact TEXT NOT NULL,
    category TEXT,
    timestamp DATETIME,
    importance INT DEFAULT 1
);

CREATE INDEX idx_entity ON knowledge_base(entity_key);
CREATE INDEX idx_category ON knowledge_base(category);
```

## Integration with AI

Use knowledge for better responses:

```python
async def get_ai_response(user_id, message):
    km = get_knowledge_manager()
    
    # Get user context
    context = await km.get_context(user_id)
    
    # Enhanced system prompt
    system = f"""You are Akeno, a helpful assistant.
    
About the user:
{context}

Use this information to personalize your response."""
    
    response = await api_manager.chat(
        message=message,
        system_prompt=system
    )
    
    return response
```

## Performance

- **Add fact**: ~10ms
- **Get facts**: ~5ms
- **Search**: ~50-200ms (depends on size)
- **Get context**: ~20ms

## Best Practices

1. **Categorize facts** - Use categories for organization
2. **Update regularly** - Keep facts current
3. **Limit storage** - Archive old facts
4. **Dedup facts** - Check before adding
5. **Review searches** - Verify search results

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| No search results | Try broader query |
| Duplicate facts | Use delete_fact before adding |
| Too many facts | Archive or delete old entries |
| Slow searches | Limit fact count or use categories |

## Dependencies

- **ai_database.py** - Database persistence
- **api_manager.py** - AI integration
- Built-in `asyncio` - Async operations

## Related Documentation

- [ai_database.py](./ai_database.md) - Database operations
- [api_manager.py](./api_manager.md) - AI integration
- [Modules Overview](../MODULES.md) - Other modules

---

*Last Updated: 2025-11-14*
