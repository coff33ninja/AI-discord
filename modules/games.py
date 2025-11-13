"""
Games module - fun interactive games with persona-driven responses
"""
import random
import asyncio
import json
import re
from collections import deque
from difflib import SequenceMatcher

from .persona_manager import PersonaManager
from .logger import BotLogger

# Initialize logger
logger = BotLogger.get_logger(__name__)

# Game constants
TRIVIA_TIMEOUT = 30
TRIVIA_FAST_THRESHOLD = 5
DEFAULT_GUESSING_MAX = 100
MAGIC_8BALL_DELAY = 2
TRIVIA_START_DELAY = 1
NUMBER_GUESSING_TIMEOUT = 60  # Time limit for number guessing
COUNTDOWN_INTERVAL = 5  # Announce every 5 seconds
TRIVIA_SIMILARITY_THRESHOLD = 0.7  # Fuzzy match threshold (0-1)

class TsundereGames:
    def __init__(self, persona_file="persona_card.json", api_manager=None, search=None, ai_db=None):
        self.active_games = {}  # {user_id: {game_data}}
        self.active_questions = {}  # {question_id: {question_data, answered_users: set()}}
        self.active_timers = {}  # {timer_id: task} to track active countdown timers
        self.persona_manager = PersonaManager(persona_file)
        self.question_counter = 0
        self.timer_counter = 0

        # Optional external services (injected by bot on_ready)
        self.api_manager = api_manager
        self.search = search
        self.ai_db = ai_db
        self.knowledge_manager = None
        # Backwards-compatible: also set knowledge manager if present
        try:
            from .knowledge_manager import knowledge_manager
            if isinstance(knowledge_manager, object) and self.ai_db:
                knowledge_manager.set_ai_db(self.ai_db)
                self.knowledge_manager = knowledge_manager
        except Exception:
            pass

    def set_knowledge_manager(self, km):
        """Inject a KnowledgeManager instance for knowledge operations."""
        self.knowledge_manager = km
        # Recent trivia cache to avoid repeating the same questions
        self._recent_trivia = deque(maxlen=50)

    # Dependency injection helpers
    def set_api_manager(self, api_manager):
        self.api_manager = api_manager

    def set_search(self, search):
        self.search = search

    def set_ai_db(self, ai_db):
        self.ai_db = ai_db
    
    def _is_similar_question(self, new_question: str) -> bool:
        """Check if new_question is similar to any recent trivia question using fuzzy matching."""
        new_q = new_question.lower().strip()
        for recent_q in self._recent_trivia:
            # Use SequenceMatcher to compute similarity ratio
            ratio = SequenceMatcher(None, new_q, recent_q).ratio()
            if ratio >= TRIVIA_SIMILARITY_THRESHOLD:
                return True
        return False
    
    def _parse_answers(self, answer_str: str) -> list:
        """Parse a single answer string that may contain multiple valid answers.
        
        Handles formats like:
        - "Q" (single answer)
        - "Q|The letter Q" (pipe-separated)
        - "Q / the letter Q" (slash-separated)
        - "Q, the letter Q" (comma-separated)
        - "Q or the letter Q" (or-separated)
        
        Returns a list of normalized answer variants.
        """
        if not answer_str:
            return []
        
        # Split by common delimiters
        delimiters = [r'\|', r'/', r'\bor\b', ',']
        variants = [answer_str]
        
        for delimiter in delimiters:
            expanded = []
            for variant in variants:
                parts = re.split(delimiter, variant, flags=re.IGNORECASE)
                expanded.extend(parts)
            variants = expanded
        
        # Normalize: strip whitespace, lowercase
        normalized = [v.strip().lower() for v in variants if v.strip()]
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for v in normalized:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        
        return unique if unique else []
    
    def _get_persona_response(self, category, subcategory, **format_kwargs):
        """Helper method to safely get persona responses from nested dictionaries"""
        try:
            responses = self.persona_manager.persona.get("activity_responses", {}).get(category, {}).get(subcategory, [])
            if responses:
                # Handle both list and single string responses
                if isinstance(responses, list):
                    selected = random.choice(responses)
                else:
                    selected = responses
                return selected.format(**format_kwargs) if format_kwargs else selected
        except (KeyError, TypeError, ValueError) as e:
            print(f"⚠️ Error retrieving persona response: {e}")
        return None

    async def _fetch_additional_facts(self, term: str, max_facts: int = 3) -> list:
        """Attempt to fetch short additional facts about `term`.

        Strategy:
        - If `ai_db` is available, search the knowledge base for matching entries and
          return their content (trimmed to short sentences).
        - Otherwise, if `api_manager` is available, ask the AI to produce 2-3 concise
          facts and parse the response.
        - Returns a list of short fact strings (may be empty).
        """
        facts = []
        if not term:
            return facts

        term_clean = str(term).strip()

        # 1) Try DB search for related knowledge
        try:
            if self.knowledge_manager:
                try:
                    results = await self.knowledge_manager.search_knowledge(term_clean, limit=max_facts)
                except Exception:
                    results = []
            elif self.ai_db:
                try:
                    results = await self.ai_db.search_knowledge(term_clean, limit=max_facts)
                except Exception:
                    results = []

                for r in results:
                    content = r.get('content') or ''
                    # Take the first sentence to keep facts short
                    first_sentence = re.split(r'[\.\n]', content.strip())[0].strip()
                    if first_sentence:
                        facts.append(first_sentence)
                    if len(facts) >= max_facts:
                        break
                if facts:
                    return facts
        except Exception:
            # DB search failed; fall through to AI
            pass

        # 2) Fall back to AI-generated facts
        try:
            if self.api_manager:
                prompt = (
                    f"Provide {max_facts} concise, single-line trivia facts about '{term_clean}'. "
                    "Return only a JSON array named 'facts' when possible, or plain newline-separated lines. "
                    "Keep each fact short (one sentence, ~10-20 words)."
                )
                ai_resp = await self.api_manager.generate_content(prompt)
                # Try to parse JSON array
                parsed = None
                try:
                    m = re.search(r"\{.*\}\s*$", ai_resp, flags=re.S)
                    if m:
                        # attempt to find array inside
                        arr_match = re.search(r"\[.*\]", m.group(0), flags=re.S)
                        if arr_match:
                            parsed = json.loads(arr_match.group(0))
                        else:
                            # maybe the whole response is a JSON array
                            parsed = json.loads(ai_resp)
                    else:
                        # try direct JSON array
                        parsed = json.loads(ai_resp)
                except Exception:
                    parsed = None

                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, str) and item.strip():
                            facts.append(item.strip())
                        if len(facts) >= max_facts:
                            break
                else:
                    # Fallback: split by lines and take short ones
                    lines = [ln.strip('-* \t') for ln in re.split(r"\r?\n", ai_resp) if ln.strip()]
                    for ln in lines:
                        # ignore empty lines
                        if ln:
                            facts.append(ln.strip())
                        if len(facts) >= max_facts:
                            break

                # Final sanitization: keep unique, short facts
                unique = []
                seen = set()
                for f in facts:
                    s = f.strip()
                    if s and s not in seen:
                        seen.add(s)
                        unique.append(s)
                return unique[:max_facts]
        except Exception:
            return []

        return []
    
    async def start_number_guessing(self, user_id, max_number=DEFAULT_GUESSING_MAX, ctx=None):
        """Start a number guessing game with countdown"""
        # Create a shared number-guessing question so multiple players can join
        secret_number = random.randint(1, max_number)
        self.question_counter += 1
        question_id = self.question_counter

        self.timer_counter += 1
        timer_id = self.timer_counter

        # Store as an active question (multiplayer)
        self.active_questions[question_id] = {
            'type': 'number_guess',
            'secret': secret_number,
            'start_time': asyncio.get_event_loop().time(),
            'answers': {},  # {user_id: {'answer': int, 'time': elapsed_time}}
            'timer_id': timer_id,
            'ctx': ctx,
            'game_over': False
        }

        # Store user-specific reference to the shared question
        self.active_games[user_id] = {
            'type': 'number_guess',
            'question_id': question_id
        }

        logger.info(f"Number guessing game started for user {user_id} (1-{max_number}) [QID {question_id}]")
        persona_msg = self._get_persona_response("games", "start")
        start_text = persona_msg or self.persona_manager.get_game_response("number_guess", "start")

        # Start countdown if context provided
        if ctx:
            countdown_task = asyncio.create_task(self._countdown_timer(timer_id, ctx, NUMBER_GUESSING_TIMEOUT, "number_guess", question_id))
            self.active_timers[timer_id] = countdown_task

        return f"{start_text} I picked a number between 1 and {max_number}. Try to guess it! You have {NUMBER_GUESSING_TIMEOUT} seconds."

    async def start_rps(self, user_id, timeout=TRIVIA_TIMEOUT, ctx=None):
        """Start a multiplayer Rock-Paper-Scissors round where players submit choices within the timeout."""
        self.question_counter += 1
        question_id = self.question_counter

        self.timer_counter += 1
        timer_id = self.timer_counter

        self.active_questions[question_id] = {
            'type': 'rps',
            'start_time': asyncio.get_event_loop().time(),
            'choices': {},  # {user_id: {'choice': 'rock', 'time': elapsed}}
            'timer_id': timer_id,
            'ctx': ctx,
            'game_over': False
        }

        # Store starter mapping
        self.active_games[user_id] = {'type': 'rps', 'question_id': question_id}

        # Start countdown
        if ctx:
            countdown_task = asyncio.create_task(self._countdown_timer(timer_id, ctx, timeout, "rps", question_id))
            self.active_timers[timer_id] = countdown_task

        persona_msg = self._get_persona_response("games", "rps_start")
        start_text = persona_msg or "Rock-Paper-Scissors round started! Submit your choice with `!rps <rock|paper|scissors>` or `!answer <choice>`."
        return start_text
    
    async def guess_number(self, user_id, guess, ctx=None):
        """Collect a number guess for a shared number-guessing game (multiplayer)
        If the user doesn't have an active game mapping, try to find an open number-guess game in the same channel.
        """
        # If user doesn't have mapping, try to find a shared question in this channel
        if user_id not in self.active_games or self.active_games[user_id].get('type') != 'number_guess':
            # Try to find an open number_guess question in the same channel
            if ctx:
                found_qid = None
                for qid, qdata in self.active_questions.items():
                    if qdata.get('type') == 'number_guess' and qdata.get('ctx') and qdata.get('ctx').channel.id == ctx.channel.id and not qdata.get('game_over'):
                        found_qid = qid
                        break
                if found_qid:
                    self.active_games[user_id] = {'type': 'number_guess', 'question_id': found_qid}
                else:
                    logger.info(f"No active number guessing game for user {user_id}")
                    return self._get_persona_response("games", "no_active_game") or self.persona_manager.get_game_response("general", "no_active_game")
            else:
                logger.info(f"No active number guessing game for user {user_id} and no context to search")
                return self._get_persona_response("games", "no_active_game") or self.persona_manager.get_game_response("general", "no_active_game")

        # Now we have an active_games mapping pointing to the shared question
        question_id = self.active_games[user_id]['question_id']
        if question_id not in self.active_questions:
            logger.info(f"Question {question_id} not found for user {user_id}")
            del self.active_games[user_id]
            return "The guessing game expired. Start a new one with !startgame number"

        question_data = self.active_questions[question_id]
        elapsed_time = asyncio.get_event_loop().time() - question_data['start_time']

        # Prevent double guesses
        if user_id in question_data.get('answers', {}):
            return "You already submitted a guess for this round!"

        # Store guess
        try:
            guess_val = int(guess)
        except Exception:
            return "Please submit a valid integer guess."

        question_data['answers'][user_id] = {'answer': guess_val, 'time': elapsed_time}
        del self.active_games[user_id]

        # Acknowledge
        user_name = None
        if ctx:
            try:
                user = await ctx.bot.fetch_user(user_id)
                user_name = user.name if hasattr(user, 'name') else str(user_id)
            except Exception:
                user_name = str(user_id)
        if ctx and user_name:
            await ctx.send(f"📝 **{user_name}** submitted a guess!")
        return "Guess received! Waiting for the round to finish."
    
    async def rock_paper_scissors(self, user_choice, user_id=None, ctx=None):
        """Play rock paper scissors"""
        choices = ['rock', 'paper', 'scissors']
        user_choice = user_choice.lower() if isinstance(user_choice, str) else None

        # If there's an active multiplayer RPS round in this channel, collect the player's choice
        if ctx:
            # Find open rps question in this channel
            found_qid = None
            for qid, qdata in self.active_questions.items():
                if qdata.get('type') == 'rps' and qdata.get('ctx') and qdata.get('ctx').channel.id == ctx.channel.id and not qdata.get('game_over'):
                    found_qid = qid
                    break
            if found_qid:
                qdata = self.active_questions[found_qid]
                elapsed = asyncio.get_event_loop().time() - qdata.get('start_time', asyncio.get_event_loop().time())
                if user_choice not in choices:
                    return self.persona_manager.get_validation_response("rps_choice")
                # Prevent double submissions
                if user_id in qdata.get('choices', {}):
                    return "You already submitted a choice for this round!"
                qdata.setdefault('choices', {})[user_id] = {'choice': user_choice, 'time': elapsed}
                # create temporary mapping so generic answer flow stays consistent
                if user_id in self.active_games:
                    try:
                        del self.active_games[user_id]
                    except Exception:
                        pass
                # Acknowledge
                try:
                    user = await ctx.bot.fetch_user(user_id)
                    user_name = user.name if hasattr(user, 'name') else str(user_id)
                except Exception:
                    user_name = str(user_id)
                await ctx.send(f"📝 **{user_name}** submitted their R/P/S choice!")
                return "Choice received! Waiting for the round to finish."

        # No active multiplayer round found — fall back to immediate bot duel
        bot_choice = random.choice(choices)
        if not user_choice or user_choice not in choices:
            logger.warning(f"Invalid choice in rock-paper-scissors: {user_choice}")
            return self.persona_manager.get_validation_response("rps_choice")

        logger.info(f"Rock-paper-scissors: user chose {user_choice}, bot chose {bot_choice}")
        # Get username for announcement
        user_name = None
        if ctx and user_id:
            try:
                user = await ctx.bot.fetch_user(user_id)
                user_name = user.name if hasattr(user, 'name') else str(user_id)
            except Exception:
                user_name = str(user_id)

        if user_choice == bot_choice:
            persona_msg = self._get_persona_response("games", "tie", choice=bot_choice)
            response = persona_msg or self.persona_manager.get_game_response("rps", "tie", choice=bot_choice)
            # Announce tie to channel
            if ctx and user_name:
                await ctx.send(f"🤝 **{user_name}** and bot both chose **{bot_choice}** - it's a tie!")
            return response
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'paper' and bot_choice == 'rock') or \
             (user_choice == 'scissors' and bot_choice == 'paper'):
            logger.info("Rock-paper-scissors: user won")
            persona_msg = self._get_persona_response("games", "win")
            response = f"{persona_msg or self.persona_manager.get_game_response('rps', 'win')} You picked {user_choice}, I picked {bot_choice}."
            # Announce winner to channel
            if ctx and user_name:
                await ctx.send(f"🎉 **{user_name}** won! {user_choice} beats {bot_choice}!")
            return response
        else:
            logger.info("Rock-paper-scissors: bot won")
            persona_msg = self._get_persona_response("games", "lose")
            response = f"{persona_msg or self.persona_manager.get_game_response('rps', 'lose')} I picked {bot_choice}, you picked {user_choice}."
            # Announce bot win to channel
            if ctx and user_name:
                await ctx.send(f"🤖 Bot won against **{user_name}**! {bot_choice} beats {user_choice}!")
            return response
    
    async def magic_8ball(self, question, ctx=None):
        """Magic 8-ball with persona responses and countdown"""
        # Add dramatic pause using asyncio
        await asyncio.sleep(MAGIC_8BALL_DELAY)  # Tsundere thinking time
        
        persona_msg = self._get_persona_response("magic_8ball", "action")
        answers = self.persona_manager.persona.get("activity_responses", {}).get("magic_8ball", {}).get("answers", ["Maybe?"])
        answer = random.choice(answers)
        
        action_text = persona_msg or "Shakes the 8-ball..."
        response = f"{action_text}\n\n{answer}"
        
        # Start countdown if context provided
        if ctx:
            self.timer_counter += 1
            timer_id = self.timer_counter
            countdown_task = asyncio.create_task(self._countdown_timer(timer_id, ctx, MAGIC_8BALL_DELAY, "magic 8-ball"))
            self.active_timers[timer_id] = countdown_task
        
        return response
    
    async def trivia_game(self, user_id, ctx=None, source: str = None):
        """Start a trivia game with dramatic timing and countdown.

        The trivia question can come from:
        - DB (`ai_db` knowledge_base) when available
        - AI (`api_manager`) when available
        - Fallback static list

        `source` can be 'db', 'ai', or None (auto-select).
        """
        # Static fallback pool
        questions = [
            {"q": "What's the capital of Japan?", "a": "tokyo | tokyo, japan"},
            {"q": "What's 7 x 8?", "a": "56"},
            {"q": "What color do you get mixing red and blue?", "a": "purple | violet"},
            {"q": "How many days are in a leap year?", "a": "366"},
            {"q": "What's the largest planet in our solar system?", "a": "jupiter"}
        ]

        question_data = None

        # Attempt order: AI (preferred if available and not explicitly DB), then DB, then static
        question_data = None
        source_used = None
        last_ai_resp = None
        last_db_entry = None

        # If user explicitly requested AI but API manager is missing, fail early
        if source == 'ai' and not self.api_manager:
            return self._get_persona_response('games', 'ai_unavailable') or "Sorry, AI is not available right now. Try again later."

        MAX_ATTEMPTS = 6

        # 1) Try AI first (if available and user didn't force DB)
        if self.api_manager and source != 'db':
            for attempt in range(MAX_ATTEMPTS):
                try:
                    prompt = (
                        "Generate a single short trivia question with multiple acceptable answers. "
                        "Return a JSON object with keys 'question' and 'answers'. "
                        "'answers' should be an array of equivalent or acceptable answer variations. "
                        "For example: {\"question\": \"What is the only letter that does not appear in any U.S. state name?\", "
                        "\"answers\": [\"Q\", \"the letter Q\", \"letter Q\"]} "
                        "Keep both concise. Provide at least 2 answer variants when possible."
                    )
                    ai_resp = await self.api_manager.generate_content(prompt)
                    last_ai_resp = ai_resp
                    parsed = None
                    try:
                        m = re.search(r"\{.*\}", ai_resp, flags=re.S)
                        if m:
                            parsed = json.loads(m.group(0))
                        else:
                            parsed = json.loads(ai_resp)
                    except Exception:
                        parsed = None

                    candidate = None
                    if parsed and isinstance(parsed, dict) and parsed.get('question'):
                        question = parsed['question'].strip()
                        # Handle both 'answers' (array) and 'answer' (string) keys
                        answer_variants = parsed.get('answers') or [parsed.get('answer')]
                        
                        if isinstance(answer_variants, list):
                            # Join multiple answers with pipe delimiter
                            answer = ' | '.join([str(a).strip() for a in answer_variants if a])
                        else:
                            answer = str(answer_variants).strip()
                        
                        if question and answer:
                            candidate = {'q': question, 'a': answer}
                    else:
                        # Fallback parsing for 'Question:' and 'Answer:' format
                        if isinstance(ai_resp, str):
                            qmatch = re.search(r"Question\s*[:\-]\s*(.+)", ai_resp, flags=re.I)
                            amatch = re.search(r"Answer\s*[:\-]\s*(.+)", ai_resp, flags=re.I)
                            if qmatch and amatch:
                                candidate = {'q': qmatch.group(1).strip(), 'a': amatch.group(1).strip()}

                    if candidate:
                        if not self._is_similar_question(candidate['q']):
                            question_data = candidate
                            source_used = 'AI'
                            break
                        # else: we got a repeat, try again
                except Exception:
                    continue

        # 2) Try DB if AI didn't yield or user requested DB
        if not question_data and self.ai_db and source != 'ai':
            for attempt in range(MAX_ATTEMPTS):
                try:
                    db_entry = await self.ai_db.get_random_knowledge('trivia')
                    last_db_entry = db_entry
                except Exception:
                    db_entry = None

                if not db_entry:
                    break

                key = db_entry.get('key_term') or ''
                content = db_entry.get('content') or ''

                q = None
                a = None
                if '|' in content:
                    parts = [p.strip() for p in content.split('|', 1)]
                    if len(parts) == 2:
                        q, a = parts[0], parts[1]
                elif '\n' in content:
                    parts = [p.strip() for p in content.splitlines() if p.strip()]
                    if len(parts) >= 2:
                        q, a = parts[0], parts[1]
                if not q and key:
                    q = key
                    a = content

                if q and a:
                    if not self._is_similar_question(q):
                        question_data = {'q': q, 'a': a}
                        source_used = 'DB'
                        break
                    # else: repeat, try again

        # 3) Static fallback - prefer one not recently used
        if not question_data:
            candidate = None
            for item in questions:
                if not self._is_similar_question(item['q']):
                    candidate = item
                    break
            if not candidate:
                candidate = random.choice(questions)
            question_data = {'q': candidate['q'], 'a': candidate['a']}
            source_used = 'static'

        # Record recent question to avoid repeats (store normalized version)
        try:
            self._recent_trivia.append(question_data['q'].lower().strip())
        except Exception:
            pass

        # Persist AI-generated or static-seeded questions to DB for future reuse
        if source_used in ('AI', 'static') and self.ai_db:
            try:
                # store key_term as question, content as answer
                await self.ai_db.add_knowledge('trivia', question_data['q'], question_data['a'])
            except Exception:
                pass
        self.question_counter += 1
        question_id = self.question_counter
        
        self.timer_counter += 1
        timer_id = self.timer_counter
        
        # Store the shared question data
        self.active_questions[question_id] = {
            'type': 'trivia',
            'question': question_data['q'],
            'answer': question_data['a'],
            'start_time': asyncio.get_event_loop().time(),
            'answered_users': set(),
            'answers': {},  # {user_id: {'answer': answer_text, 'time': elapsed_time}}
            'timer_id': timer_id,
            'ctx': ctx,  # Store context for countdown announcements
            'game_over': False  # Flag to indicate if timer has completed
        }
        
        # Store user-specific game reference
        self.active_games[user_id] = {
            'type': 'trivia',
            'question_id': question_id
        }
        
        logger.info(f"Trivia game started for user {user_id} (Question ID: {question_id})")
        
        # Dramatic pause before asking
        await asyncio.sleep(TRIVIA_START_DELAY)
        
        persona_msg = self._get_persona_response("games", "trivia_start", question=question_data['q'])
        initial_message = persona_msg or f"Question: {question_data['q']}"

        # Announce the source for debugging/visibility
        try:
            if 'db_entry' in locals() and db_entry:
                source_used = 'DB'
            elif source == 'ai' or (self.api_manager and 'ai_resp' in locals() and ai_resp):
                source_used = 'AI'
            else:
                source_used = 'static'
            initial_message += f"\n\n*(source: {source_used})*"
        except Exception:
            # don't break on source annotation
            pass
        
        # Start countdown announcements in background
        if ctx:
            countdown_task = asyncio.create_task(self._countdown_timer(timer_id, ctx, TRIVIA_TIMEOUT, "trivia", question_id))
            self.active_timers[timer_id] = countdown_task
        
        return initial_message
    
    async def _countdown_timer(self, timer_id, ctx, timeout_duration, game_name, question_id=None):
        """Generic countdown timer that announces every COUNTDOWN_INTERVAL seconds, then tallies results"""
        start_time = asyncio.get_event_loop().time()
        announced_times = set()
        
        try:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = timeout_duration - elapsed
                
                if remaining <= 0:
                    # Timer finished - tally results if this is a timed game with questions
                    if question_id and question_id in self.active_questions:
                        question_data = self.active_questions[question_id]
                        question_data['game_over'] = True
                        await self._tally_game_results(question_id, ctx, game_name)
                    if timer_id in self.active_timers:
                        del self.active_timers[timer_id]
                    break
                
                # Announce at COUNTDOWN_INTERVAL boundaries (e.g., 25, 20, 15, 10, 5 seconds)
                # Avoid announcing immediately at the full timeout value (so we don't repeat the question instantly)
                for announce_time in range(int(timeout_duration), 0, -COUNTDOWN_INTERVAL):
                    if announce_time >= int(timeout_duration):
                        # skip announcing the full timeout value immediately after question
                        continue
                    if remaining <= announce_time and announce_time not in announced_times:
                        announced_times.add(announce_time)
                        await ctx.send(f"⏱️ **{announce_time} seconds left for {game_name}!**")
                        break
                
                # Check every 0.5 seconds
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error in countdown timer for {game_name}: {e}")
        finally:
            if timer_id in self.active_timers:
                del self.active_timers[timer_id]
    
    async def answer_trivia(self, user_id, answer, ctx=None):
        """Collect trivia answer - stores it for later tallying when timer completes"""
        # If user doesn't have mapping, try to find an open trivia question in the same channel
        if user_id not in self.active_games or self.active_games[user_id].get('type') != 'trivia':
            if ctx:
                found_qid = None
                for qid, qdata in self.active_questions.items():
                    if qdata.get('type') == 'trivia' and qdata.get('ctx') and qdata.get('ctx').channel.id == ctx.channel.id and not qdata.get('game_over'):
                        found_qid = qid
                        break
                if found_qid:
                    # create a temporary mapping so the rest of the logic can proceed
                    self.active_games[user_id] = {'type': 'trivia', 'question_id': found_qid}
                else:
                    logger.info(f"No active trivia game for user {user_id}")
                    persona_msg = self._get_persona_response("games", "no_active_game")
                    return f"{persona_msg or self.persona_manager.get_game_response('trivia', 'no_active_game')} Start one with !trivia"
            else:
                logger.info(f"No active trivia game for user {user_id} and no context to search")
                persona_msg = self._get_persona_response("games", "no_active_game")
                return f"{persona_msg or self.persona_manager.get_game_response('trivia', 'no_active_game')} Start one with !trivia"
        
        question_id = self.active_games[user_id]['question_id']
        
        if question_id not in self.active_questions:
            logger.info(f"Question {question_id} not found for user {user_id}")
            del self.active_games[user_id]
            return "The trivia question expired. Start a new one with !trivia"
        
        question_data = self.active_questions[question_id]
        elapsed_time = asyncio.get_event_loop().time() - question_data['start_time']
        
        # Check if user already answered this question
        if user_id in question_data['answered_users']:
            logger.info(f"User {user_id} attempted to answer question {question_id} twice")
            return "You already answered this question, baka! Wait for the results!"
        
        # Check if game is already over
        if question_data['game_over']:
            logger.info(f"Attempted answer after game over for user {user_id}")
            return "Time's up! Results are being tallied..."
        
        # Store the answer for later tallying
        question_data['answered_users'].add(user_id)
        question_data['answers'][user_id] = {
            'answer': answer,
            'time': elapsed_time
        }
        del self.active_games[user_id]
        
        logger.info(f"Trivia answer collected for user {user_id}: '{answer}' at {elapsed_time:.1f}s")
        
        # Get username for acknowledgment
        user_name = None
        if ctx:
            try:
                user = await ctx.bot.fetch_user(user_id)
                user_name = user.name if hasattr(user, 'name') else str(user_id)
            except Exception:
                user_name = str(user_id)
        
        # Send acknowledgment but don't reveal if correct/wrong yet
        persona_msg = self._get_persona_response("games", "answer_received")
        response = persona_msg or "✓ Answer received! Waiting for timer to complete..."
        
        # Optionally announce that someone answered
        if ctx and user_name:
            await ctx.send(f"📝 **{user_name}** submitted an answer!")
        
        return response
        
    
    async def _tally_game_results(self, question_id, ctx, game_name):
        """Tally results for all players who answered - called when timer completes"""
        if question_id not in self.active_questions:
            logger.warning(f"Question {question_id} not found for tallying")
            return

        question_data = self.active_questions[question_id]
        qtype = question_data.get('type', 'trivia')
        answers = question_data.get('answers', {})

        if not answers:
            # No one answered
            if ctx:
                if qtype == 'trivia':
                    correct_answer = question_data.get('answer')
                    await ctx.send(f"⏰ Time's up! No one answered. The answer was **{correct_answer}**!")
                else:
                    await ctx.send(f"⏰ Time's up! No one participated in the {qtype} round.")
            logger.info(f"No answers submitted for question {question_id}")
            del self.active_questions[question_id]
            return

        if qtype == 'trivia':
            correct_answer = question_data.get('answer')
            # Parse multiple valid answers from the stored answer string
            valid_answers = self._parse_answers(correct_answer)
            if not valid_answers:
                valid_answers = [correct_answer.lower().strip()]
            
            # Separate correct and incorrect answers, sorted by time
            correct_users = []
            incorrect_users = []
            for user_id, answer_data in answers.items():
                user_answer = str(answer_data['answer']).lower().strip()
                # Check if user's answer matches any of the valid answers
                is_correct = user_answer in valid_answers
                
                if is_correct:
                    correct_users.append((user_id, answer_data['time']))
                else:
                    incorrect_users.append((user_id, answer_data['answer'], answer_data['time']))

            # Sort by time (fastest first)
            correct_users.sort(key=lambda x: x[1])

            # Announce results
            if ctx:
                # Announce correct answers
                if correct_users:
                    if len(correct_users) == 1:
                        user_id, elapsed_time = correct_users[0]
                        user = await ctx.bot.fetch_user(user_id)
                        user_name = user.name if hasattr(user, 'name') else str(user_id)
                        if elapsed_time < TRIVIA_FAST_THRESHOLD:
                            await ctx.send(f"🎉 **{user_name}** got it right in {elapsed_time:.1f} seconds! That's lightning fast!")
                        else:
                            await ctx.send(f"🏆 **{user_name}** answered correctly in {elapsed_time:.1f} seconds!")
                    else:
                        # Multiple correct answers
                        winners = []
                        for user_id, elapsed_time in correct_users:
                            user = await ctx.bot.fetch_user(user_id)
                            user_name = user.name if hasattr(user, 'name') else str(user_id)
                            winners.append(f"**{user_name}** ({elapsed_time:.1f}s)")
                        await ctx.send(f"🏆 Correct answers: {', '.join(winners)}")
                    
                        # Show all valid answer variants
                        if len(valid_answers) > 1:
                            answers_display = ", ".join([f"**{v}**" for v in valid_answers])
                            await ctx.send(f"💡 Additional acceptable answers: {answers_display}")
                else:
                    # No correct answers
                        await ctx.send(f"⏰ Time's up! No one got it right. The answer was **{correct_answer}**!")
                        # Show all valid answer variants even when no one got it right
                        if len(valid_answers) > 1:
                            answers_display = ", ".join([f"**{v}**" for v in valid_answers])
                            await ctx.send(f"💡 Other acceptable answers: {answers_display}")

                # Try to fetch and show a few additional facts about the answer (if available)
                try:
                    key_term = None
                    # Prefer variants that match DB knowledge entries (most relevant)
                    if valid_answers and self.ai_db:
                        best_candidate = None
                        best_score = -1
                        for candidate in valid_answers:
                            try:
                                results = await self.ai_db.search_knowledge(candidate, limit=1)
                            except Exception:
                                results = []
                            if results:
                                # use relevance_score if available, else treat as match
                                score = results[0].get('relevance_score') or 1.0
                                if score > best_score:
                                    best_score = score
                                    best_candidate = candidate
                        if best_candidate:
                            key_term = best_candidate

                    # If no DB match or no DB available, prefer multi-word variants (more specific), then longest
                    if not key_term and valid_answers:
                        # choose by number of words, then by length
                        key_term = max(valid_answers, key=lambda s: (len(s.split()), len(s)))

                    # Final fallback
                    if not key_term:
                        key_term = correct_answer

                    if (self.ai_db or self.api_manager) and key_term:
                        facts = await self._fetch_additional_facts(key_term, max_facts=3)
                        if facts:
                            facts_display = "\n".join([f"- {f}" for f in facts])
                            await ctx.send(f"📚 Additional facts about **{key_term}**:\n{facts_display}")
                except Exception:
                    # Don't let facts retrieval break result flow
                    logger.exception("Failed to fetch additional facts")
                    pass

                # Announce a few incorrect answers
                if incorrect_users and len(correct_users) > 0:  # Only show wrong answers if someone got it right
                    incorrect_users.sort(key=lambda x: x[2])  # Sort by time
                    sample = incorrect_users[:2]  # Show up to 2 incorrect answers
                    wrong_answers = []
                    for user_id, answer, elapsed_time in sample:
                        user = await ctx.bot.fetch_user(user_id)
                        user_name = user.name if hasattr(user, 'name') else str(user_id)
                        wrong_answers.append(f"**{user_name}**: '{answer}'")
                    if wrong_answers:
                        await ctx.send(f"❌ Some close tries: {', '.join(wrong_answers)}")

            logger.info(f"Trivia results for question {question_id}: {len(correct_users)} correct, {len(incorrect_users)} incorrect")
            del self.active_questions[question_id]
            return

        if qtype == 'number_guess':
            secret = question_data.get('secret')
            # answers: {user_id: {'answer': int, 'time': float}}
            exact_matches = []
            all_guesses = []
            for user_id, data in answers.items():
                try:
                    val = int(data['answer'])
                except Exception:
                    continue
                all_guesses.append((user_id, val, data.get('time', 0)))
                if val == secret:
                    exact_matches.append((user_id, data.get('time', 0)))

            if exact_matches:
                # Sort by time and announce winners
                exact_matches.sort(key=lambda x: x[1])
                if ctx:
                    if len(exact_matches) == 1:
                        user_id, elapsed = exact_matches[0]
                        user = await ctx.bot.fetch_user(user_id)
                        user_name = user.name if hasattr(user, 'name') else str(user_id)
                        await ctx.send(f"🏆 **{user_name}** guessed the number {secret} in {elapsed:.1f} seconds!")
                    else:
                        winners = []
                        for user_id, elapsed in exact_matches:
                            user = await ctx.bot.fetch_user(user_id)
                            user_name = user.name if hasattr(user, 'name') else str(user_id)
                            winners.append(f"**{user_name}** ({elapsed:.1f}s)")
                        await ctx.send(f"🏆 Multiple winners: {', '.join(winners)} guessed {secret}!")
                logger.info(f"Number guess winners for question {question_id}: {len(exact_matches)} exact matches")
                del self.active_questions[question_id]
                return

            # No exact matches: find closest guesses
            if not all_guesses:
                if ctx:
                    await ctx.send("⏰ Time's up! No valid guesses submitted.")
                del self.active_questions[question_id]
                return

            # Compute minimal distance
            diffs = []
            for user_id, val, t in all_guesses:
                diffs.append((user_id, abs(val - secret), val, t))
            diffs.sort(key=lambda x: (x[1], x[3]))  # sort by distance then time
            best_diff = diffs[0][1]
            winners = [d for d in diffs if d[1] == best_diff]
            if ctx:
                if len(winners) == 1:
                    user_id, diff, val, t = winners[0]
                    user = await ctx.bot.fetch_user(user_id)
                    user_name = user.name if hasattr(user, 'name') else str(user_id)
                    await ctx.send(f"🥈 Closest guess: **{user_name}** guessed {val} (off by {diff})")
                else:
                    parts = []
                    for user_id, diff, val, t in winners:
                        user = await ctx.bot.fetch_user(user_id)
                        user_name = user.name if hasattr(user, 'name') else str(user_id)
                        parts.append(f"**{user_name}** guessed {val} (off by {diff})")
                    await ctx.send(f"🥈 Closest guesses: {', '.join(parts)}")
                # Optionally show sample guesses
                sample = diffs[:3]
                sample_parts = []
                for user_id, diff, val, t in sample:
                    user = await ctx.bot.fetch_user(user_id)
                    user_name = user.name if hasattr(user, 'name') else str(user_id)
                    sample_parts.append(f"**{user_name}**: {val}")
                if sample_parts:
                    await ctx.send(f"🔍 Sample guesses: {', '.join(sample_parts)}. The secret was **{secret}**.")

            logger.info(f"Number guess results for question {question_id}: winners {len(winners)}, total {len(all_guesses)}")
            del self.active_questions[question_id]
            return

        # Fallback: remove question
        del self.active_questions[question_id]
    
    async def answer(self, user_id, answer, ctx=None):
        """Generic answer handler for all game types - routes to appropriate game handler"""
        # If user doesn't have an active mapping, try to find an open question in this channel
        if user_id not in self.active_games:
            if ctx:
                found = None
                for qid, qdata in self.active_questions.items():
                    if qdata.get('ctx') and qdata.get('ctx').channel.id == ctx.channel.id and not qdata.get('game_over'):
                        found = (qid, qdata)
                        break
                if found:
                    qid, qdata = found
                    qtype = qdata.get('type')
                    logger.info(f"Generic answer router found open question {qid} of type {qtype} in channel {ctx.channel.id}")
                    if qtype == 'trivia':
                        return await self.answer_trivia(user_id, answer, ctx)
                    elif qtype == 'number_guess':
                        try:
                            guess = int(answer)
                            return await self.guess_number(user_id, guess, ctx)
                        except ValueError:
                            return "That's not a valid number! Try again with a whole number."
                    else:
                        return f"Unknown open game type: {qtype}"
            logger.info(f"No active game for user {user_id}")
            return "You don't have an active game! Start one with !trivia, !guess, or !8ball"

        game_type = self.active_games[user_id].get('type')
        logger.info(f"Generic answer handler: user {user_id}, game type: {game_type}, answer: {answer[:50]}")
        
        if game_type == 'trivia':
            return await self.answer_trivia(user_id, answer, ctx)
        elif game_type == 'number_guess':
            # Convert answer to int for number guessing
            try:
                guess = int(answer)
                return await self.guess_number(user_id, guess, ctx)
            except ValueError:
                return "That's not a valid number! Try again with a whole number."
        else:
            return f"Unknown game type: {game_type}"