#!/usr/bin/env python3
"""
=============================================================================
RemoteCam - Mouse Controller Module
=============================================================================
Controls the mouse cursor using relative coordinates (0.0 to 1.0).
Handles coordinate mapping, smoothing, and clicking.
=============================================================================
"""

import pyautogui
try:
    from screeninfo import get_monitors
    SCREENINFO_AVAILABLE = True
except ImportError:
    SCREENINFO_AVAILABLE = False
import time
import math
import sys

# Disable fail-safe (moving mouse to corner throws exception)
pyautogui.FAILSAFE = False

class MouseController:
    def __init__(self, smoothing: float = 0.5, screen_index: int = 0):
        """
        Initialize mouse controller.
        
        Args:
            smoothing: Smoothing factor (0.0 = no smoothing, 0.9 = heavy smoothing)
            screen_index: Monitor index to control (default 0 = primary)
        """
        self.smoothing = max(0.0, min(0.95, smoothing))
        
        # Get screen dimensions
        if SCREENINFO_AVAILABLE:
            try:
                monitors = get_monitors()
                if 0 <= screen_index < len(monitors):
                    monitor = monitors[screen_index]
                    self.screen_width = monitor.width
                    self.screen_height = monitor.height
                    self.screen_x = monitor.x
                    self.screen_y = monitor.y
                else:
                    self.screen_width, self.screen_height = pyautogui.size()
                    self.screen_x, self.screen_y = 0, 0
            except Exception:
                self.screen_width, self.screen_height = pyautogui.size()
                self.screen_x, self.screen_y = 0, 0
        else:
            self.screen_width, self.screen_height = pyautogui.size()
            self.screen_x, self.screen_y = 0, 0
            
        print(f"Mouse Controller initialized: {self.screen_width}x{self.screen_height} at ({self.screen_x}, {self.screen_y})")
        
        # State
        self.prev_x = 0
        self.prev_y = 0
        self.is_dragging = False
        self.last_click_time = 0
        self.click_cooldown = 0.3  # Seconds between clicks
        
    def move(self, x_ratio: float, y_ratio: float):
        """
        Move mouse to relative coordinates (0.0 - 1.0).
        
        Args:
            x_ratio: X position (0.0 = left, 1.0 = right)
            y_ratio: Y position (0.0 = top, 1.0 = bottom)
        """
        # Clamp values
        x_ratio = max(0.0, min(1.0, x_ratio))
        y_ratio = max(0.0, min(1.0, y_ratio))
        
        # Map to screen pixels
        target_x = self.screen_x + (x_ratio * self.screen_width)
        target_y = self.screen_y + (y_ratio * self.screen_height)
        
        # Apply soothing (Exponential Moving Average)
        curr_x = (self.prev_x * self.smoothing) + (target_x * (1 - self.smoothing))
        curr_y = (self.prev_y * self.smoothing) + (target_y * (1 - self.smoothing))
        
        # Update history
        self.prev_x = curr_x
        self.prev_y = curr_y
        
        # Move actual mouse (if changed significantly)
        if abs(curr_x - target_x) > 0.5 or abs(curr_y - target_y) > 0.5:
            pyautogui.moveTo(int(curr_x), int(curr_y), _pause=False)
            
    def click(self):
        """Perform a left click."""
        now = time.time()
        if now - self.last_click_time > self.click_cooldown:
            pyautogui.click()
            self.last_click_time = now
            
    def set_drag(self, dragging: bool):
        """Update drag state."""
        if dragging and not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True
        elif not dragging and self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False
            
    def scroll(self, amount: int):
        """Scroll mouse wheel."""
        pyautogui.scroll(amount)

if __name__ == "__main__":
    print("Testing Mouse Controller...")
    mouse = MouseController(smoothing=0.5)
    
    # Simple circle movement test
    center_x, center_y = 0.5, 0.5
    radius = 0.2
    
    try:
        for i in range(100):
            angle = i * 0.1
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            mouse.move(x, y)
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
