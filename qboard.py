#!/usr/bin/env python3
"""
Qboard - Queue your clipboard
Copy multiple items, paste in order (FIFO)
"""

import pyperclip
import threading
import time
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
        
    def create_icon_image(self):
        """Create menu bar icon"""
        width = 64
        height = 64
        
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
        
        dc.rounded_rectangle([4, 4, width-4, height-4], radius=12, fill=color2)
        dc.rounded_rectangle([8, 8, width-8, height-8], radius=10, outline=color1, width=2)
        
        if self.mode == 'copy':
            dc.rectangle([28, 18, 36, 38], fill=symbol_color)
            dc.polygon([32, 42, 24, 34, 40, 34], fill=symbol_color)
            dc.rectangle([20, 12, 44, 14], fill=symbol_color)
            dc.rectangle([22, 16, 42, 18], fill=symbol_color)
            
        elif self.mode == 'paste':
            dc.polygon([32, 22, 24, 30, 40, 30], fill=symbol_color)
            dc.rectangle([28, 26, 36, 46], fill=symbol_color)
            dc.rectangle([20, 50, 44, 52], fill=symbol_color)
            
        else:
            dc.rounded_rectangle([22, 26, 42, 50], radius=3, fill=symbol_color)
            dc.rounded_rectangle([28, 20, 36, 28], radius=2, fill=symbol_color)
            dc.rounded_rectangle([30, 22, 34, 26], radius=1, fill=color2)
        
        return image
    
    def create_menu(self):
        """Create menu bar menu"""
        queue_count = len(self.queue)
        remaining = queue_count - self.paste_index
        
        if self.mode == 'paste' and remaining > 0:
            return Menu(
                MenuItem(
                    f'Next Item ({remaining} left)', 
                    self.load_next_item,
                    default=True
                ),
                Menu.SEPARATOR,
                MenuItem('Stop', self.deactivate),
                MenuItem('Clear Queue', self.clear_queue),
                Menu.SEPARATOR,
                MenuItem(f'Total: {queue_count} | Pasted: {self.paste_index}', None, enabled=False),
                Menu.SEPARATOR,
                MenuItem('Quit', self.quit_app)
            )
        else:
            return Menu(
                MenuItem(
                    'Copy Mode', 
                    self.activate_copy_mode,
                    checked=lambda item: self.mode == 'copy'
                ),
                MenuItem(
                    'Paste Mode', 
                    self.activate_paste_mode,
                    enabled=lambda item: queue_count > 0
                ),
                MenuItem(
                    'Stop', 
                    self.deactivate, 
                    enabled=lambda item: self.mode != 'inactive'
                ),
                Menu.SEPARATOR,
                MenuItem(f'Queue: {queue_count} | Pasted: {self.paste_index}', None, enabled=False),
                Menu.SEPARATOR,
                MenuItem('Clear Queue', self.clear_queue, enabled=lambda item: queue_count > 0),
                MenuItem('Quit', self.quit_app)
            )
    
    def update_icon(self):
        """Update icon and menu"""
        if self.icon:
            self.icon.icon = self.create_icon_image()
            self.icon.menu = self.create_menu()
    
    def activate_copy_mode(self):
        """Activate copy mode"""
        self.mode = 'copy'
        self.paste_index = 0
        self.last_clipboard = pyperclip.paste()
        self.update_icon()
        
        print("\nCopy Mode: Active")
        print("Copy items using Cmd+C\n")
        
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()
    
    def activate_paste_mode(self):
        """Activate paste mode"""
        if len(self.queue) == 0:
            print("Queue is empty")
            return
        
        self.mode = 'paste'
        self.paste_index = 0
        self.update_icon()
        
        # Load first item
        item = self.queue[0]
        pyperclip.copy(item)
        
        print(f"\nPaste Mode: Active")
        print(f"Queue: {len(self.queue)} items")
        print(f"Item 1 ready - press Cmd+V to paste\n")
        
        self.paste_index = 1
        self.update_icon()
    
    def load_next_item(self):
        """Load next item to clipboard"""
        if self.mode != 'paste':
            return
        
        if self.paste_index >= len(self.queue):
            print("All items pasted!")
            print("Switching back to Copy Mode\n")
            self.queue = []
            self.paste_index = 0
            self.activate_copy_mode()
            return
        
        # Load the item
        item = self.queue[self.paste_index]
        pyperclip.copy(item)
        
        remaining = len(self.queue) - self.paste_index - 1
        print(f"Item {self.paste_index + 1} ready - press Cmd+V to paste ({remaining} remaining)")
        
        self.paste_index += 1
        
        # Check if that was the last item
        if self.paste_index >= len(self.queue):
            print("\nAll items pasted!")
            print("Switching back to Copy Mode\n")
            self.queue = []
            self.paste_index = 0
            self.activate_copy_mode()
        else:
            self.update_icon()
    
    def deactivate(self):
        """Stop current mode"""
        self.mode = 'inactive'
        self.update_icon()
        print("Stopped\n")
    
    def clear_queue(self):
        """Clear queue"""
        count = len(self.queue)
        self.queue = []
        self.paste_index = 0
        self.update_icon()
        print(f"Cleared {count} items\n")
    
    def monitor_clipboard(self):
        """Monitor clipboard in copy mode"""
        while self.mode == 'copy' and self.running:
            try:
                current = pyperclip.paste()
                
                if current and current != self.last_clipboard and current.strip():
                    self.queue.append(current)
                    self.last_clipboard = current
                    
                    preview = current[:50].replace('\n', ' ')
                    if len(current) > 50:
                        preview += "..."
                    
                    print(f"Added item {len(self.queue)}: {preview}")
                    self.update_icon()
                    
            except Exception:
                pass
            
            time.sleep(0.3)
    
    def quit_app(self):
        """Quit application"""
        self.running = False
        if self.icon:
            self.icon.stop()
        print("Goodbye\n")
        sys.exit(0)
    
    def run(self):
        """Start application"""
        print("\n" + "="*50)
        print("Qboard - Queue Your Clipboard")
        print("="*50)
        print("\nMenu bar icon:")
        print("  Gray = Inactive")
        print("  Blue = Copy Mode")  
        print("  Green = Paste Mode")
        print("\nHow to use:")
        print("  1. Click icon > Copy Mode")
        print("  2. Copy items (Cmd+C)")
        print("  3. Click icon > Paste Mode")
        print("  4. Click Next Item, then Cmd+V to paste")
        print("  5. Auto-switches to Copy Mode when done")
        print("="*50 + "\n")
        
        self.icon = Icon(
            "Qboard",
            self.create_icon_image(),
            "Qboard",
            self.create_menu()
        )
        
        print("Ready\n")
        self.icon.run()


if __name__ == "__main__":
    try:
        app = Qboard()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
