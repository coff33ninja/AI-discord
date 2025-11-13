# games Module

Game implementations for interactive entertainment including guessing, rock-paper-scissors, trivia, and magic 8-ball.

## Overview

The `games` module provides interactive games with:
- Number guessing with hints and tracking
- Rock-paper-scissors with strategy
- Timed trivia questions
- Magic 8-ball with dramatic responses
- Per-user game state management
- Score tracking and statistics

## Key Classes

### GameManager

Main class managing all games.

```python
from modules.games import GameManager, get_game_manager

# Get singleton instance
games = get_game_manager()

# Start guessing game
game_id = await games.start_guessing_game(user_id, max_number=100)

# Make a guess
result = await games.make_guess(user_id, 50)

# Play rock-paper-scissors
outcome = await games.play_rps(user_id, "rock")
```

## Game Types

### 1. Number Guessing Game

#### `start_guessing_game(user_id, max_number=100)`
Start a new guessing game.

**Parameters:**
- `user_id` (str) - Discord user ID
- `max_number` (int) - Maximum number to guess (default: 100)

**Returns:** dict with:
- `game_id` (str) - Game ID
- `max` (int) - Max number
- `attempts` (int) - Attempts made
- `status` (str) - "active"

**Example:**
```python
game = await games.start_guessing_game(user_id, max_number=100)
print(f"Guess a number between 1 and {game['max']}")
```

#### `make_guess(user_id, guess)`
Make a guess in active game.

**Parameters:**
- `user_id` (str) - Discord user ID
- `guess` (int) - Your guess

**Returns:** dict with:
- `correct` (bool) - Correct guess?
- `hint` (str) - "higher" or "lower"
- `attempts` (int) - Total attempts
- `number` (int) - The number (if won)

**Example:**
```python
result = await games.make_guess(user_id, 50)
if result['correct']:
    print(f"You won in {result['attempts']} attempts!")
else:
    print(f"Go {result['hint']}!")
```

### 2. Rock-Paper-Scissors

#### `play_rps(user_id, choice)`
Play rock-paper-scissors.

**Parameters:**
- `user_id` (str) - Discord user ID
- `choice` (str) - "rock", "paper", or "scissors"

**Returns:** dict with:
- `player_choice` (str) - Your choice
- `bot_choice` (str) - Bot choice
- `result` (str) - "win", "lose", or "tie"
- `message` (str) - Tsundere response

**Example:**
```python
outcome = await games.play_rps(user_id, "rock")
print(f"You: {outcome['player_choice']}")
print(f"Bot: {outcome['bot_choice']}")
print(outcome['message'])  # Tsundere response
```

### 3. Trivia Game

#### `start_trivia(user_id)`
Start a timed trivia game.

**Parameters:**
- `user_id` (str) - Discord user ID

**Returns:** dict with:
- `game_id` (str) - Game ID
- `question` (str) - Trivia question
- `time_limit` (int) - Seconds to answer (30)
- `started_at` (datetime) - Start time

**Example:**
```python
trivia = await games.start_trivia(user_id)
print(f"Q: {trivia['question']}")
print(f"You have {trivia['time_limit']} seconds!")
```

#### `answer_trivia(user_id, answer)`
Submit trivia answer.

**Parameters:**
- `user_id` (str) - Discord user ID
- `answer` (str) - Your answer

**Returns:** dict with:
- `correct` (bool) - Correct answer?
- `answer` (str) - Correct answer
- `explanation` (str) - Why it's correct
- `time_taken` (int) - Seconds taken

**Example:**
```python
result = await games.answer_trivia(user_id, "Tokyo")
if result['correct']:
    print(f"Correct! ({result['time_taken']}s)")
else:
    print(f"Wrong. The answer is: {result['answer']}")
```

#### `get_trivia_stats(user_id)`
Get user's trivia statistics.

**Returns:** dict with:
- `played` (int) - Games played
- `correct` (int) - Correct answers
- `accuracy` (float) - Percentage correct
- `best_time` (int) - Fastest correct answer

**Example:**
```python
stats = await games.get_trivia_stats(user_id)
print(f"Accuracy: {stats['accuracy']}%")
print(f"Best time: {stats['best_time']}s")
```

### 4. Magic 8-Ball

#### `ask_8ball(user_id, question)`
Ask the magic 8-ball a question.

**Parameters:**
- `user_id` (str) - Discord user ID
- `question` (str) - Your question

**Returns:** dict with:
- `question` (str) - Your question
- `answer` (str) - 8-ball answer
- `type` (str) - "yes", "no", "maybe", "outlook"
- `message` (str) - Dramatic response

**Example:**
```python
result = await games.ask_8ball(user_id, "Will it rain tomorrow?")
print(f"Q: {result['question']}")
print(result['message'])  # Dramatic 8-ball response
```

## Usage Examples

### Complete Guessing Game Flow

```python
games = get_game_manager()

# Start game
game = await games.start_guessing_game(user_id, max_number=100)
await ctx.send(f"I'm thinking of a number between 1 and {game['max']}!")

# User makes guesses...
for _ in range(10):  # 10 tries max
    guess = int(await get_user_input())
    result = await games.make_guess(user_id, guess)
    
    if result['correct']:
        await ctx.send(f"You won in {result['attempts']} attempts!")
        break
    else:
        await ctx.send(f"Go {result['hint'].upper()}!")
```

### RPS Tournament

```python
wins = 0
for round_num in range(1, 4):
    outcome = await games.play_rps(user_id, get_player_choice())
    await ctx.send(outcome['message'])
    
    if outcome['result'] == 'win':
        wins += 1

await ctx.send(f"You won {wins}/3 rounds!")
```

### Trivia Game with Timer

```python
import asyncio

trivia = await games.start_trivia(user_id)
await ctx.send(f"Q: {trivia['question']} (30 seconds!)")

try:
    answer = await asyncio.wait_for(
        get_user_answer(),
        timeout=30
    )
    result = await games.answer_trivia(user_id, answer)
    
    if result['correct']:
        await ctx.send(f"✅ Correct in {result['time_taken']}s!")
    else:
        await ctx.send(f"❌ Wrong. Answer: {result['answer']}")
except asyncio.TimeoutError:
    await ctx.send("⏰ Time's up!")
```

### Game Statistics

```python
stats = await games.get_trivia_stats(user_id)
await ctx.send(
    f"📊 Your Trivia Stats:\n"
    f"Games Played: {stats['played']}\n"
    f"Correct: {stats['correct']}\n"
    f"Accuracy: {stats['accuracy']}%\n"
    f"Best Time: {stats['best_time']}s"
)
```

## Game Rules

### Guessing Game
- Bot thinks of a number
- You have unlimited attempts
- Bot hints "higher" or "lower"
- Win by guessing exactly

### Rock-Paper-Scissors
- Choose rock, paper, or scissors
- Rock beats scissors
- Scissors beats paper
- Paper beats rock
- Each choice is independent

### Trivia
- 30 seconds to answer
- Questions from trivia database
- Multiple choice format
- Score tracked by accuracy

### Magic 8-Ball
- Ask yes/no questions
- Get random dramatic response
- For entertainment only
- Try multiple times for "rerolls"

## Game State Management

Games are tracked per user:
```python
# Active games stored in memory
games.active_games[user_id] = {
    'type': 'guessing',
    'started_at': datetime.now(),
    'data': {...}
}
```

## Scoring & Stats

Each game updates user statistics:
- **Guessing**: Tracks attempts and wins
- **RPS**: Tracks wins/losses/ties
- **Trivia**: Tracks accuracy and best times
- **8-Ball**: Entertainment only (no scoring)

## Performance

- **Game start**: < 100ms
- **Move processing**: < 50ms
- **Stats retrieval**: < 100ms
- **Concurrent games**: Supports many per-user

## Dependencies

- Built-in `random` - Random choices
- Built-in `datetime` - Game timing
- Built-in `asyncio` - Async operations

## Related Documentation

- [Commands Reference](../commands.md#-game-commands) - Game commands
- [Modules Overview](../MODULES.md) - Other modules
- See docstrings in `games.py` for implementation details

---

*Last Updated: 2025-11-14*
