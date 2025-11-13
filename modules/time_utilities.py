"""
Time-based Utilities Module
Handles reminders, scheduled notifications, and time-based subscriptions
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .ai_database import ai_db
from .persona_manager import PersonaManager

logger = logging.getLogger(__name__)

class TimeBasedUtilities:
    """Handles time-based features like reminders and scheduled notifications"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.persona_manager = PersonaManager()
        self.active_reminders = {}
        self.running_tasks = {}
        
    async def initialize_database_tables(self):
        """Initialize additional database tables for time-based features"""
        try:
            async with ai_db.db_path.parent.joinpath(ai_db.db_path.name).open() as _:
                pass
        except Exception:
            pass
            
        # We'll use the existing ai_database connection
        import aiosqlite
        async with aiosqlite.connect(ai_db.db_path) as db:
            # Reminders table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    guild_id TEXT,
                    reminder_text TEXT NOT NULL,
                    remind_time DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_recurring BOOLEAN DEFAULT FALSE,
                    recurrence_pattern TEXT
                )
            """)
            
            # Create indexes for reminders table
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_remind_time ON user_reminders (remind_time)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_active ON user_reminders (user_id, is_active)
            """)
            
            # User subscriptions for time-based features
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    guild_id TEXT,
                    subscription_type TEXT NOT NULL,
                    subscription_data TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_triggered DATETIME,
                    UNIQUE(user_id, channel_id, subscription_type)
                )
            """)
            
            await db.commit()
            logger.info("Time-based utilities database tables initialized")
    
    async def set_reminder(self, user_id: str, channel_id: str, guild_id: str, 
                          reminder_text: str, remind_time: datetime, 
                          is_recurring: bool = False, recurrence_pattern: str = None) -> int:
        """Set a reminder for a user"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO user_reminders 
                    (user_id, channel_id, guild_id, reminder_text, remind_time, is_recurring, recurrence_pattern)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, channel_id, guild_id, reminder_text, remind_time.isoformat(), 
                      is_recurring, recurrence_pattern))
                
                reminder_id = cursor.lastrowid
                await db.commit()
                
                # Schedule the reminder
                await self._schedule_reminder(reminder_id, remind_time, user_id, channel_id, 
                                            reminder_text, is_recurring, recurrence_pattern)
                
                logger.info(f"Reminder set for user {user_id}: {reminder_text} at {remind_time}")
                return reminder_id
                
        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            raise
    
    async def _schedule_reminder(self, reminder_id: int, remind_time: datetime, 
                               user_id: str, channel_id: str, reminder_text: str,
                               is_recurring: bool = False, recurrence_pattern: str = None):
        """Schedule a reminder task"""
        try:
            delay = (remind_time - datetime.now()).total_seconds()
            
            if delay > 0:
                task = asyncio.create_task(
                    self._reminder_task(reminder_id, delay, user_id, channel_id, 
                                      reminder_text, is_recurring, recurrence_pattern)
                )
                self.running_tasks[reminder_id] = task
                logger.info(f"Scheduled reminder {reminder_id} for {delay} seconds")
            else:
                logger.warning(f"Reminder {reminder_id} time is in the past")
                
        except Exception as e:
            logger.error(f"Error scheduling reminder {reminder_id}: {e}")
    
    async def _reminder_task(self, reminder_id: int, delay: float, user_id: str, 
                           channel_id: str, reminder_text: str, 
                           is_recurring: bool = False, recurrence_pattern: str = None):
        """Task that executes the reminder"""
        try:
            await asyncio.sleep(delay)
            
            if self.bot:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    # Create tsundere reminder message
                    user_mention = f"<@{user_id}>"
                    
                    # Get persona response for reminder with fallback
                    try:
                        persona_responses = self.persona_manager.persona.get("activity_responses", {}).get("reminders", {})
                        reminder_intros = persona_responses.get("reminder_ping", [])
                    except Exception:
                        reminder_intros = []
                    
                    # Fallback reminder intros if none found
                    if not reminder_intros:
                        # Use persona manager for fallback reminder intros
                        from .persona_manager import PersonaManager
                        pm = PersonaManager()
                        try:
                            reminder_intro = pm.get_activity_response("reminders", "reminder_ping", user_mention=user_mention)
                            reminder_intros = [reminder_intro]
                        except Exception:
                            # Ultimate fallback
                            reminder_intros = [
                                "Hey {user_mention}! Here's your reminder:",
                                "{user_mention}, you asked me to remind you about this:",
                                "Reminder for {user_mention}:"
                            ]
                    
                    import random
                    intro = random.choice(reminder_intros).format(user_mention=user_mention)
                    message = f"{intro}\n\n📝 **Reminder:** {reminder_text}"
                    
                    await channel.send(message)
                    logger.info(f"Reminder {reminder_id} sent to user {user_id}")
                    
                    # Handle recurring reminders
                    if is_recurring and recurrence_pattern:
                        next_time = self._calculate_next_occurrence(datetime.now(), recurrence_pattern)
                        if next_time:
                            await self._schedule_reminder(reminder_id, next_time, user_id, channel_id,
                                                        reminder_text, is_recurring, recurrence_pattern)
                    else:
                        # Mark as completed
                        await self._mark_reminder_completed(reminder_id)
            
            # Clean up task reference
            if reminder_id in self.running_tasks:
                del self.running_tasks[reminder_id]
                
        except Exception as e:
            logger.error(f"Error executing reminder {reminder_id}: {e}")
    
    def _calculate_next_occurrence(self, current_time: datetime, pattern: str) -> Optional[datetime]:
        """Calculate next occurrence for recurring reminders"""
        try:
            if pattern == "daily":
                return current_time + timedelta(days=1)
            elif pattern == "weekly":
                return current_time + timedelta(weeks=1)
            elif pattern == "hourly":
                return current_time + timedelta(hours=1)
            elif pattern.startswith("every_"):
                # Format: every_30_minutes, every_2_hours, every_3_days
                parts = pattern.split("_")
                if len(parts) == 3:
                    interval = int(parts[1])
                    unit = parts[2]
                    
                    if unit.startswith("minute"):
                        return current_time + timedelta(minutes=interval)
                    elif unit.startswith("hour"):
                        return current_time + timedelta(hours=interval)
                    elif unit.startswith("day"):
                        return current_time + timedelta(days=interval)
            
            return None
        except Exception as e:
            logger.error(f"Error calculating next occurrence: {e}")
            return None
    
    async def _mark_reminder_completed(self, reminder_id: int):
        """Mark a reminder as completed"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                await db.execute("""
                    UPDATE user_reminders 
                    SET is_active = FALSE 
                    WHERE id = ?
                """, (reminder_id,))
                await db.commit()
        except Exception as e:
            logger.error(f"Error marking reminder {reminder_id} as completed: {e}")
    
    async def get_user_reminders(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """Get all reminders for a user"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                if active_only:
                    cursor = await db.execute("""
                        SELECT * FROM user_reminders 
                        WHERE user_id = ? AND is_active = TRUE
                        ORDER BY remind_time ASC
                    """, (user_id,))
                else:
                    cursor = await db.execute("""
                        SELECT * FROM user_reminders 
                        WHERE user_id = ?
                        ORDER BY remind_time DESC
                    """, (user_id,))
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting reminders for user {user_id}: {e}")
            return []
    
    async def cancel_reminder(self, reminder_id: int, user_id: str) -> bool:
        """Cancel a specific reminder"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                cursor = await db.execute("""
                    UPDATE user_reminders 
                    SET is_active = FALSE 
                    WHERE id = ? AND user_id = ?
                """, (reminder_id, user_id))
                
                await db.commit()
                
                # Cancel the running task if it exists
                if reminder_id in self.running_tasks:
                    self.running_tasks[reminder_id].cancel()
                    del self.running_tasks[reminder_id]
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error canceling reminder {reminder_id}: {e}")
            return False
    
    async def subscribe_to_feature(self, user_id: str, channel_id: str, guild_id: str,
                                 subscription_type: str, subscription_data: Dict = None) -> bool:
        """Subscribe user to a time-based feature"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_subscriptions 
                    (user_id, channel_id, guild_id, subscription_type, subscription_data, is_active)
                    VALUES (?, ?, ?, ?, ?, TRUE)
                """, (user_id, channel_id, guild_id, subscription_type, 
                      json.dumps(subscription_data) if subscription_data else None))
                
                await db.commit()
                logger.info(f"User {user_id} subscribed to {subscription_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to {subscription_type}: {e}")
            return False
    
    async def unsubscribe_from_feature(self, user_id: str, channel_id: str, 
                                     subscription_type: str) -> bool:
        """Unsubscribe user from a time-based feature"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                cursor = await db.execute("""
                    UPDATE user_subscriptions 
                    SET is_active = FALSE 
                    WHERE user_id = ? AND channel_id = ? AND subscription_type = ?
                """, (user_id, channel_id, subscription_type))
                
                await db.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id} from {subscription_type}: {e}")
            return False
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict]:
        """Get all active subscriptions for a user"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM user_subscriptions 
                    WHERE user_id = ? AND is_active = TRUE
                    ORDER BY created_at DESC
                """, (user_id,))
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                subscriptions = []
                for row in rows:
                    sub = dict(zip(columns, row))
                    if sub['subscription_data']:
                        try:
                            sub['subscription_data'] = json.loads(sub['subscription_data'])
                        except Exception:
                            pass
                    subscriptions.append(sub)
                
                return subscriptions
                
        except Exception as e:
            logger.error(f"Error getting subscriptions for user {user_id}: {e}")
            return []
    
    async def load_existing_reminders(self):
        """Load and schedule existing active reminders on bot startup"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM user_reminders 
                    WHERE is_active = TRUE AND remind_time > datetime('now')
                    ORDER BY remind_time ASC
                """)
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                loaded_count = 0
                for row in rows:
                    reminder = dict(zip(columns, row))
                    remind_time = datetime.fromisoformat(reminder['remind_time'])
                    
                    await self._schedule_reminder(
                        reminder['id'], remind_time, reminder['user_id'], 
                        reminder['channel_id'], reminder['reminder_text'],
                        reminder['is_recurring'], reminder['recurrence_pattern']
                    )
                    loaded_count += 1
                
                logger.info(f"Loaded {loaded_count} existing reminders")
                
        except Exception as e:
            logger.error(f"Error loading existing reminders: {e}")
    
    async def get_subscriptions_by_type(self, subscription_type: str) -> List[Dict]:
        """Get all active subscriptions of a specific type"""
        try:
            import aiosqlite
            async with aiosqlite.connect(ai_db.db_path) as db:
                cursor = await db.execute("""
                    SELECT * FROM user_subscriptions 
                    WHERE subscription_type = ? AND is_active = TRUE
                    ORDER BY created_at DESC
                """, (subscription_type,))
                
                rows = await cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                subscriptions = []
                for row in rows:
                    sub = dict(zip(columns, row))
                    if sub['subscription_data']:
                        try:
                            sub['subscription_data'] = json.loads(sub['subscription_data'])
                        except Exception:
                            pass
                    subscriptions.append(sub)
                
                return subscriptions
                
        except Exception as e:
            logger.error(f"Error getting subscriptions of type {subscription_type}: {e}")
            return []
    
    def parse_time_input(self, time_input: str) -> Optional[datetime]:
        """Parse various time input formats"""
        try:
            time_input = time_input.lower().strip()
            now = datetime.now()
            
            # Handle relative times
            if "in" in time_input:
                # "in 5 minutes", "in 2 hours", "in 1 day"
                parts = time_input.split()
                if len(parts) >= 3 and parts[0] == "in":
                    try:
                        amount = int(parts[1])
                        unit = parts[2]
                        
                        if unit.startswith("minute"):
                            return now + timedelta(minutes=amount)
                        elif unit.startswith("hour"):
                            return now + timedelta(hours=amount)
                        elif unit.startswith("day"):
                            return now + timedelta(days=amount)
                        elif unit.startswith("week"):
                            return now + timedelta(weeks=amount)
                    except ValueError:
                        pass
            
            # Handle specific times
            elif "at" in time_input:
                # "at 3pm", "at 15:30", "tomorrow at 9am"
                if "tomorrow" in time_input:
                    base_date = now + timedelta(days=1)
                else:
                    base_date = now
                
                # Extract time part
                time_part = time_input.split("at")[-1].strip()
                
                # Parse common time formats
                if "pm" in time_part or "am" in time_part:
                    try:
                        time_obj = datetime.strptime(time_part, "%I%p").time()
                        return datetime.combine(base_date.date(), time_obj)
                    except Exception:
                        try:
                            time_obj = datetime.strptime(time_part, "%I:%M%p").time()
                            return datetime.combine(base_date.date(), time_obj)
                        except Exception:
                            pass
                
                # 24-hour format
                if ":" in time_part:
                    try:
                        time_obj = datetime.strptime(time_part, "%H:%M").time()
                        return datetime.combine(base_date.date(), time_obj)
                    except Exception:
                        pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing time input '{time_input}': {e}")
            return None


# Global instance
time_utils = TimeBasedUtilities()

async def initialize_time_utilities(bot):
    """Initialize time-based utilities"""
    global time_utils
    time_utils = TimeBasedUtilities(bot)
    await time_utils.initialize_database_tables()
    await time_utils.load_existing_reminders()
    logger.info("Time-based utilities initialized")