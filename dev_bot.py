#!/usr/bin/env python3
"""
Development runner for Discord AI Bot
Automatically restarts the bot when files are modified

⚠️ NOTE: Requires watchdog library and Python 3.10-3.12
         For Python 3.13, use: python bot.py (no auto-restart)
"""

import sys
import time
import subprocess

# Check Python version compatibility
python_version = sys.version_info
if python_version.minor == 13:
    print("⚠️  WARNING: Python 3.13 has watchdog threading issues!")
    print("✅ SOLUTION: Downgrade to Python 3.12 or use: python bot.py")
    print("\nTo fix:")
    print("  uv python install 3.12.4")
    print("  uv venv --python 3.12.4")
    sys.exit(1)

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog not installed!")
    print("Install with: uv pip install watchdog==6.0.0")
    print("Or run normally with: python bot.py")
    sys.exit(1)

class BotRestartHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Only restart for Python files
        if not event.src_path.endswith('.py'):
            return
            
        # Avoid rapid restarts
        current_time = time.time()
        if current_time - self.last_restart < 2:
            return
            
        print(f"\n📝 File changed: {event.src_path}")
        print("🔄 Restarting bot...")
        self.last_restart = current_time
        self.restart_callback()

class BotRunner:
    def __init__(self):
        self.process = None
        self.observer = None
        
    def start_bot(self):
        """Start the bot process"""
        if self.process:
            self.stop_bot()
            
        print("🤖 Starting Discord AI Bot...")
        self.process = subprocess.Popen([sys.executable, "bot.py"])
        
    def stop_bot(self):
        """Stop the bot process"""
        if self.process:
            print("⏹️  Stopping bot...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("🔨 Force killing bot...")
                self.process.kill()
                self.process.wait()
            self.process = None
            
    def restart_bot(self):
        """Restart the bot"""
        self.stop_bot()
        time.sleep(1)  # Brief pause
        self.start_bot()
        
    def start_watching(self):
        """Start watching for file changes"""
        print("👀 Watching for file changes...")
        handler = BotRestartHandler(self.restart_bot)
        
        try:
            self.observer = Observer()
            
            # Watch current directory and modules
            self.observer.schedule(handler, ".", recursive=False)
            self.observer.schedule(handler, "modules", recursive=True)
            
            self.observer.start()
        except Exception as e:
            print(f"❌ Error starting file watcher: {e}")
            print("💡 Tip: Make sure watchdog is installed: uv pip install watchdog==6.0.0")
            print("    Or use Python 3.12 instead of 3.13")
            raise
        
    def run(self):
        """Main run loop"""
        print("🚀 Discord AI Bot Development Runner")
        print("=" * 30)
        print("Features:")
        print("- Auto-restart on file changes")
        print("- Ctrl+C to stop")
        print("- Watches .py files in current dir and modules/")
        print()
        
        try:
            self.start_bot()
            self.start_watching()
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
                # Check if bot process died
                if self.process and self.process.poll() is not None:
                    print("💀 Bot process died, restarting...")
                    self.start_bot()
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
        finally:
            self.stop_bot()
            if self.observer:
                try:
                    self.observer.stop()
                    self.observer.join(timeout=5)
                except Exception as e:
                    print(f"⚠️  Error stopping observer: {e}")
            print("👋 Goodbye!")

if __name__ == "__main__":
    runner = BotRunner()
    runner.run()