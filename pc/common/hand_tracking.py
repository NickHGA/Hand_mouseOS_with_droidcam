#!/usr/bin/env python3
"""
=============================================================================
RemoteCam - Hand Tracking Module
=============================================================================
Uses MediaPipe to detect hands and extract landmarks.
Calculates gestures (pinch, pointing, etc.).
=============================================================================
"""

import cv2
import mediapipe as mp
import numpy as np
import time

class HandTracker:
    def __init__(self, 
                 max_hands: int = 1, 
                 detection_conf: float = 0.7, 
                 tracking_conf: float = 0.7):
        """
        Initialize MediaPipe Hands.
        """
        # Fix for some mediapipe versions where mp.solutions is not directly exposed
        if not hasattr(mp, 'solutions'):
            import mediapipe.python.solutions as solutions
            self.mp_hands = solutions.hands
            self.mp_draw = solutions.drawing_utils
        else:
            self.mp_hands = mp.solutions.hands
            self.mp_draw = mp.solutions.drawing_utils
            
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
            model_complexity=1
        )
        
        # State
        self.results = None
        self.frame_shape = (0, 0)
        
    def process(self, frame_bgr: np.ndarray):
        """
        Process a frame and detect hands.
        Args:
            frame_bgr: BGR image from OpenCV
        """
        self.frame_shape = frame_bgr.shape
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(frame_rgb)
        return self.results
    
    def get_pointer_position(self):
        """
        Get the position of the index finger tip.
        Returns:
            (x, y) coordinates relative to image (0.0 - 1.0)
            None if no hand detected
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return None
            
        # Get first hand
        hand_landmarks = self.results.multi_hand_landmarks[0]
        
        # Index finger tip is landmark 8
        lm_index = hand_landmarks.landmark[8]
        
        return (lm_index.x, lm_index.y)
    
    def is_pinching(self, threshold: float = 0.05):
        """
        Check if thumb and index are pinching (clicking).
        Returns:
            True if pinching, False otherwise
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return False
            
        lm = self.results.multi_hand_landmarks[0].landmark
        
        # 4 = Thumb tip, 8 = Index tip
        thumb = lm[4]
        index = lm[8]
        
        distance = np.sqrt((thumb.x - index.x)**2 + (thumb.y - index.y)**2)
        return distance < threshold
    
    def draw_landmarks(self, frame: np.ndarray):
        """Draw hand landmarks on frame."""
        if not self.results or not self.results.multi_hand_landmarks:
            return frame
            
        annotated_frame = frame.copy()
        for hand_landmarks in self.results.multi_hand_landmarks:
            self.mp_draw.draw_landmarks(
                annotated_frame, 
                hand_landmarks, 
                self.mp_hands.HAND_CONNECTIONS
            )
            
            # Highlight index tip (pointer)
            h, w, c = frame.shape
            cx, cy = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)
            cv2.circle(annotated_frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            
        return annotated_frame

if __name__ == "__main__":
    # Simple webcam test
    print("Testing Hand Tracker (press q to quit)...")
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        tracker.process(frame)
        
        if tracker.get_pointer_position():
            pinching = tracker.is_pinching()
            status = "CLICKING" if pinching else "Moving"
            cv2.putText(frame, status, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        cv2.imshow("Hand Tracking Test", tracker.draw_landmarks(frame))
        if cv2.waitKey(1) == ord('q'): break
        
    cap.release()
    cv2.destroyAllWindows()
