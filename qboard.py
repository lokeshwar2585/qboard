#!/usr/bin/env python3
"""
Qboard - Queue your clipboard
Copy multiple items, paste in order (FIFO)
"""

import pyperclip
import threading
import time
from pynput.keyboard import GlobalHotKeys
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys

class Qboard:
    def __init__(self):
        self.queue = []
        self.mode = 'inactive'
        self.last_clipboard = ''
        self.paste_index = 0
        self.running = True
        self.icon = None
        self.monitor_thread = None
        self.hotkey_listener = None
        
    def create_icon_image(self):
        """Create a cool modern icon"""
        width = 64
        height = 64
        
        # Colors based on mode
        if self.mode == 'copy':
            color1 = (41, 128, 185)
            color2 = (52, 152, 219)
            symbol_color = 'white'
        elif self.mode == 'paste':
            color1 = (39, 174, 96)
            color2 = (46, 204, 113)
            symbol_color = 'white'
        else:
            color1 = (52, 73, 94)
            color2 = (52, 73, 94)
            symbol_color = 'white'
        
        image = Image.new('RGBA', (width, height), color=(255, 255, 255, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw modern rounded square
        dc.rounded_rectangle([4, 4, width-4, height-4], radius=12, fill=color2)
        dc.rounded_rectangle([8, 8, width-8, height-8], radius=10, outline=color1, width=2)
        
        # Draw symbol based on mode
        if self.mode == 'copy':
            # Download/Copy arrow pointing down
            dc.rectangle([28, 18, 36, 38], fill=symbol_color)
            dc.polygon([32, 42, 24, 34, 40, 34], fill=symbol_color)
            dc.rectangle([20, 12, 44, 14], fill=symbol_color)
            dc.rectangle([22, 16, 42, 18], fill=symbol_color)
            
        elif self.mode == 'paste':
            # Upload/Paste arrow pointing up
            dc.polygon([32, 22, 24, 30, 40, 30], fill=symbol_color)
            dc.rectangle([28, 26, 36, 46], fill=symbol_color)
            dc.rectangle([20, 50, 44, 52], fill=symbol_color)
            
        else:
            # Inactive - clipboard icon
            dc.rounded_rectangle([22, 26, 42, 50], radius=3, fill=symbol_color)
            dc.rounded_rectangle([28, 20, 36, 28], radius=2, fill=symbol_color)
            dc.rounded_rectangle([30, 22, 34, 26], radius=1, fill=color2)
        
        return image
    
    def create_menu(self):
        """Create menu for tray icon"""
        queue_count = len(self.queue)
        remaining = queue_count - self.paste_index
        
        if self.mode == 'paste' and remaining > 0:
            return Menu(
                MenuItem(
                    f'📤 NEXT ITEM ({remaining} left) ⌘⇧N', 
                    self.load_next_for_pasting,
                    default=True
                ),
                Menu.SEPARATOR,
                MenuItem('⏹️ Stop Paste Mode', self.deactivate),
                MenuItem('🗑️ Clear Queue', self.clear_queue),
                Menu.SEPARATOR,
                MenuItem(f'Total: {queue_count} | Pasted: {self.paste_index}', None, enabled=False),
                Menu.SEPARATOR,
                MenuItem('❌ Quit', self.quit_app)
            )
        else:
            return Menu(
                MenuItem(
                    '📥 Copy Mode', 
                    self.activate_copy_mode,
                    checked=lambda item: self.mode == 'copy'
                ),
                MenuItem(
                    '📤 Paste Mode', 
                    self.activate_paste_mode,
                    enabled=lambda item: queue_count > 0
                ),
                MenuItem(
                    '⏹️ Stop', 
                    self.deactivate, 
                    enabled=lambda item: self.mode != 'inactive'
                ),
                Menu.SEPARATOR,
                MenuItem(f'📋 Queue: {queue_count} items', None, enabled=False),
                MenuItem(f'✅ Pasted: {self.paste_index} items', None, enabled=False),
                Menu.SEPARATOR,
                MenuItem(
                    '🗑️ Clear Queue', 
                    self.clear_queue, 
                    enabled=lambda item: queue_count > 0
                ),
                MenuItem('❌ Quit', self.quit_app)
            )
    
    def update_icon(self):
        """Update icon appearance and menu"""
        if self.icon:
            self.icon.icon = self.create_icon_image()
            self.icon.menu = self.create_menu()
    
    def activate_copy_mode(self):
        """Activate copy mode"""
        print("\n" + "🔵"*30)
        print("📥 COPY MODE ACTIVATED!")
        print("Copy items anywhere (Cmd+C)")
        print("🔵"*30 + "\n")
        
        self.mode = 'copy'
        self.paste_index = 0
        self.last_clipboard = pyperclip.paste()
        self.update_icon()
        
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard_copy, daemon=True)
        self.monitor_thread.start()
    
    def activate_paste_mode(self):
        """Activate paste mode"""
        if len(self.queue) == 0:
            print("\n⚠️  Queue is empty!\n")
            return
        
        print("\n" + "🟢"*30)
        print("📤 PASTE MODE ACTIVATED!")
        print(f"Queue has {len(self.queue)} items ready")
        print("\n📋 WORKFLOW:")
        print("  1. Press Cmd+V → pastes first item")
        print("  2. Press Cmd+Shift+N → loads next item")
        print("  3. Press Cmd+V → pastes it")
        print("  4. Repeat 2-3 until done!")
        print("\n⚡ Pattern: Cmd+V, Cmd+Shift+N, Cmd+V, Cmd+Shift+N...")
        print("🟢"*30 + "\n")
        
        self.mode = 'paste'
        self.paste_index = 0
        self.update_icon()
        
        # Load first item immediately
        item = self.queue[0]
        pyperclip.copy(item)
        preview = item[:60].replace('\n', ' ')
        
        print(f"✅ Item #1 READY: \"{preview}...\"")
        print(f"👉 Press Cmd+V to paste it! ({len(self.queue) - 1} remaining)\n")
        
        self.paste_index = 1
        self.update_icon()
    
    def load_next_for_pasting(self):
        """Load next item to clipboard for pasting"""
        if self.mode != 'paste':
            return
        
        if self.paste_index >= len(self.queue):
            print("\n" + "🎉"*30)
            print("ALL ITEMS PASTED! Queue complete!")
            print("🎉"*30 + "\n")
            self.deactivate()
            self.queue = []
            self.paste_index = 0
            self.update_icon()
            return
        
        # Load item to clipboard
        item = self.queue[self.paste_index]
        pyperclip.copy(item)
        
        remaining = len(self.queue) - self.paste_index - 1
        preview = item[:60].replace('\n', ' ')
        
        print(f"✅ Item #{self.paste_index + 1} loaded: \"{preview}...\"")
        print(f"👉 Press Cmd+V to paste it! ({remaining} remaining)\n")
        
        self.paste_index += 1
        self.update_icon()
    
    def deactivate(self):
        """Stop current mode"""
        print("\n⏹️  STOPPED\n")
        self.mode = 'inactive'
        self.update_icon()
    
    def clear_queue(self):
        """Clear the queue"""
        count = len(self.queue)
        self.queue = []
        self.paste_index = 0
        print(f"\n🗑️  Cleared {count} items\n")
        self.update_icon()
    
    def monitor_clipboard_copy(self):
        """Monitor clipboard in COPY mode"""
        while self.mode == 'copy' and self.running:
            try:
                current = pyperclip.paste()
                
                if current and current != self.last_clipboard and current.strip():
                    self.queue.append(current)
                    self.last_clipboard = current
                    
                    preview = current[:60].replace('\n', ' ')
                    print(f"✅ Added #{len(self.queue)}: \"{preview}...\"")
                    
                    self.update_icon()
                    
            except Exception as e:
                pass
            
            time.sleep(0.3)
    
    def quit_app(self):
        """Quit application"""
        print("\n👋 Thanks for using Qboard!\n")
        self.running = False
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.icon:
            self.icon.stop()
        sys.exit(0)
    
    def start_hotkey_listener(self):
        """Start global hotkey listener for Cmd+Shift+N"""
        print("⌨️  Setting up hotkey: Cmd+Shift+N...")
        
        try:
            hotkeys = {
                '<cmd>+<shift>+n': self.load_next_for_pasting,
                '<cmd>+<shift>+N': self.load_next_for_pasting,
            }
            
            self.hotkey_listener = GlobalHotKeys(hotkeys)
            self.hotkey_listener.start()
            print("✅ Hotkey Cmd+Shift+N is active!\n")
            
        except Exception as e:
            print(f"⚠️  Hotkey setup failed: {e}")
            print("💡 You can still use the menu icon\n")
    
    def run(self):
        """Start the application"""
        print("\n" + "="*60)
        print("🚀 QBOARD - Queue Your Clipboard")
        print("="*60)
        print("\n👀 Icon in menu bar (top-right)")
        print("   • Gray clipboard = Inactive")
        print("   • Blue arrow down = Copy Mode")  
        print("   • Green arrow up = Paste Mode")
        print("\n📋 HOW TO USE:")
        print("   1. Click icon → Copy Mode")
        print("   2. Copy: A, B, C (Cmd+C)")
        print("   3. Click icon → Paste Mode")
        print("   4. Cmd+V → A, Cmd+Shift+N, Cmd+V → B, etc.")
        print("="*60 + "\n")
        
        self.start_hotkey_listener()
        
        self.icon = Icon(
            "Qboard",
            self.create_icon_image(),
            "Qboard - Queue Your Clipboard",
            self.create_menu()
        )
        
        print("🎯 Ready!\n")
        self.icon.run()

if __name__ == "__main__":
    try:
        app = Qboard()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
