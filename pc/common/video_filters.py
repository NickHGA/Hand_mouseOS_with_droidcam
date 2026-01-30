#!/usr/bin/env python3
"""
=============================================================================
RemoteCam - Video Filters Module
=============================================================================
Collection of video filters that can be applied to frames.
Filters can be chained together for combined effects.
=============================================================================
"""

import cv2
import numpy as np
from typing import List, Callable, Dict, Any, Optional


# =============================================================================
# Individual Filter Functions
# =============================================================================

def rotate_frame(frame: np.ndarray, angle: int = 90) -> np.ndarray:
    """
    Rotate the frame by the specified angle.
    
    Args:
        frame: Input frame
        angle: Rotation angle (90, 180, 270, or any angle)
        
    Returns:
        Rotated frame
    """
    if angle == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif angle == 270 or angle == -90:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif angle == 0:
        return frame
    else:
        # Arbitrary angle rotation
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(frame, matrix, (w, h))


def mirror_frame(frame: np.ndarray, direction: str = "horizontal") -> np.ndarray:
    """
    Mirror/flip the frame.
    
    Args:
        frame: Input frame
        direction: "horizontal", "vertical", or "both"
        
    Returns:
        Mirrored frame
    """
    if direction == "horizontal":
        return cv2.flip(frame, 1)
    elif direction == "vertical":
        return cv2.flip(frame, 0)
    elif direction == "both":
        return cv2.flip(frame, -1)
    return frame


def grayscale_frame(frame: np.ndarray) -> np.ndarray:
    """
    Convert frame to grayscale (keeps 3 channels for compatibility).
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        Grayscale frame (BGR format, 3 channels)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def blur_frame(frame: np.ndarray, strength: int = 5) -> np.ndarray:
    """
    Apply Gaussian blur to the frame.
    
    Args:
        frame: Input frame
        strength: Blur kernel size (must be odd, will be adjusted if even)
        
    Returns:
        Blurred frame
    """
    if strength <= 0:
        return frame
    
    # Ensure kernel size is odd
    kernel_size = strength if strength % 2 == 1 else strength + 1
    return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)


def edge_detect_frame(frame: np.ndarray, threshold1: int = 100, threshold2: int = 200) -> np.ndarray:
    """
    Apply Canny edge detection.
    
    Args:
        frame: Input frame
        threshold1: First threshold for hysteresis
        threshold2: Second threshold for hysteresis
        
    Returns:
        Edge-detected frame (BGR format)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1, threshold2)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def brightness_frame(frame: np.ndarray, value: int = 0) -> np.ndarray:
    """
    Adjust frame brightness.
    
    Args:
        frame: Input frame
        value: Brightness adjustment (-255 to +255)
        
    Returns:
        Brightness-adjusted frame
    """
    if value == 0:
        return frame
    
    # Convert to float, adjust, clip, and convert back
    adjusted = frame.astype(np.float32) + value
    return np.clip(adjusted, 0, 255).astype(np.uint8)


def contrast_frame(frame: np.ndarray, value: int = 0) -> np.ndarray:
    """
    Adjust frame contrast.
    
    Args:
        frame: Input frame
        value: Contrast adjustment (-100 to +100)
        
    Returns:
        Contrast-adjusted frame
    """
    if value == 0:
        return frame
    
    # Convert value to alpha factor (0.5 to 2.0 range)
    alpha = 1.0 + (value / 100.0)
    alpha = max(0.1, min(3.0, alpha))  # Clamp to reasonable range
    
    # Apply contrast adjustment
    adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=0)
    return adjusted


def vintage_frame(frame: np.ndarray, intensity: float = 1.0) -> np.ndarray:
    """
    Apply a vintage/sepia effect.
    
    Args:
        frame: Input frame
        intensity: Effect intensity (0.0 to 1.0)
        
    Returns:
        Vintage-effect frame
    """
    # Sepia transformation matrix
    sepia_matrix = np.array([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189]
    ])
    
    # Apply sepia
    sepia = cv2.transform(frame, sepia_matrix)
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    
    # Blend with original based on intensity
    if intensity < 1.0:
        sepia = cv2.addWeighted(frame, 1 - intensity, sepia, intensity, 0)
    
    # Add slight vignette effect
    rows, cols = frame.shape[:2]
    X = cv2.getGaussianKernel(cols, cols * 0.5)
    Y = cv2.getGaussianKernel(rows, rows * 0.5)
    kernel = Y * X.T
    mask = kernel / kernel.max()
    
    for i in range(3):
        sepia[:, :, i] = sepia[:, :, i] * mask
    
    return sepia.astype(np.uint8)


def cartoon_frame(frame: np.ndarray) -> np.ndarray:
    """
    Apply a cartoon/comic effect.
    
    Args:
        frame: Input frame
        
    Returns:
        Cartoonized frame
    """
    # Reduce color palette
    color = frame.copy()
    for _ in range(2):
        color = cv2.pyrDown(color)
    for _ in range(7):
        color = cv2.bilateralFilter(color, 9, 9, 7)
    for _ in range(2):
        color = cv2.pyrUp(color)
    
    # Resize to match original
    color = cv2.resize(color, (frame.shape[1], frame.shape[0]))
    
    # Create edge mask
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Combine
    cartoon = cv2.bitwise_and(color, edges)
    return cartoon


def negative_frame(frame: np.ndarray) -> np.ndarray:
    """
    Create a negative/inverted color effect.
    
    Args:
        frame: Input frame
        
    Returns:
        Negative frame
    """
    return cv2.bitwise_not(frame)


def sharpen_frame(frame: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Sharpen the frame.
    
    Args:
        frame: Input frame
        strength: Sharpening strength (0.5 to 2.0)
        
    Returns:
        Sharpened frame
    """
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ]) * strength
    
    sharpened = cv2.filter2D(frame, -1, kernel)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


# =============================================================================
# Filter Registry
# =============================================================================

AVAILABLE_FILTERS: Dict[str, Callable] = {
    'rotate': rotate_frame,
    'mirror': mirror_frame,
    'grayscale': grayscale_frame,
    'blur': blur_frame,
    'edge': edge_detect_frame,
    'brightness': brightness_frame,
    'contrast': contrast_frame,
    'vintage': vintage_frame,
    'cartoon': cartoon_frame,
    'negative': negative_frame,
    'sharpen': sharpen_frame,
}


# =============================================================================
# Filter Application Functions
# =============================================================================

def apply_filter(
    frame: np.ndarray,
    filter_name: str,
    **kwargs
) -> np.ndarray:
    """
    Apply a single named filter to a frame.
    
    Args:
        frame: Input frame
        filter_name: Name of the filter to apply
        **kwargs: Filter-specific arguments
        
    Returns:
        Filtered frame
    """
    if filter_name not in AVAILABLE_FILTERS:
        print(f"Warning: Unknown filter '{filter_name}'")
        return frame
    
    filter_func = AVAILABLE_FILTERS[filter_name]
    return filter_func(frame, **kwargs)


def apply_filters(
    frame: np.ndarray,
    filter_chain: List[Dict[str, Any]]
) -> np.ndarray:
    """
    Apply a chain of filters to a frame.
    
    Args:
        frame: Input frame
        filter_chain: List of filter specifications, e.g.:
            [
                {'name': 'rotate', 'angle': 90},
                {'name': 'grayscale'},
                {'name': 'brightness', 'value': 20}
            ]
            
    Returns:
        Frame with all filters applied
    """
    result = frame
    
    for filter_spec in filter_chain:
        if isinstance(filter_spec, str):
            # Simple filter name without arguments
            result = apply_filter(result, filter_spec)
        elif isinstance(filter_spec, dict):
            # Filter with arguments
            name = filter_spec.get('name', filter_spec.get('filter'))
            if name:
                kwargs = {k: v for k, v in filter_spec.items() if k not in ('name', 'filter')}
                result = apply_filter(result, name, **kwargs)
    
    return result


def create_filter_chain_from_args(args) -> List[Dict[str, Any]]:
    """
    Create a filter chain from parsed CLI arguments.
    
    Args:
        args: Parsed argparse namespace
        
    Returns:
        List of filter specifications
    """
    chain = []
    
    # Check for rotation
    if hasattr(args, 'rotate') and args.rotate and args.rotate != 0:
        chain.append({'name': 'rotate', 'angle': args.rotate})
    
    # Check for flip/mirror
    if hasattr(args, 'flip') and args.flip and args.flip != 'none':
        chain.append({'name': 'mirror', 'direction': args.flip})
    
    # Check for grayscale
    if hasattr(args, 'grayscale') and args.grayscale:
        chain.append({'name': 'grayscale'})
    
    # Check for blur
    if hasattr(args, 'blur') and args.blur and args.blur > 0:
        chain.append({'name': 'blur', 'strength': args.blur})
    
    # Check for edge detection
    if hasattr(args, 'edge') and args.edge:
        chain.append({'name': 'edge'})
    
    # Check for brightness
    if hasattr(args, 'brightness') and args.brightness and args.brightness != 0:
        chain.append({'name': 'brightness', 'value': args.brightness})
    
    # Check for contrast
    if hasattr(args, 'contrast') and args.contrast and args.contrast != 0:
        chain.append({'name': 'contrast', 'value': args.contrast})
    
    # Check for vintage
    if hasattr(args, 'vintage') and args.vintage:
        chain.append({'name': 'vintage'})
    
    # Check for cartoon
    if hasattr(args, 'cartoon') and args.cartoon:
        chain.append({'name': 'cartoon'})
    
    # Check for negative
    if hasattr(args, 'negative') and args.negative:
        chain.append({'name': 'negative'})
    
    # Check for sharpen
    if hasattr(args, 'sharpen') and args.sharpen:
        chain.append({'name': 'sharpen'})
    
    return chain


if __name__ == "__main__":
    # Test filters with a sample image
    print("=" * 50)
    print("  RemoteCam Video Filters Test")
    print("=" * 50)
    print()
    print("Available filters:")
    for name in AVAILABLE_FILTERS:
        print(f"  - {name}")
    print()
    print("=" * 50)
    
    # Create a test image
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_frame, (100, 100), (540, 380), (0, 255, 0), -1)
    cv2.putText(test_frame, "Test Frame", (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    # Test each filter
    for filter_name in AVAILABLE_FILTERS:
        try:
            filtered = apply_filter(test_frame.copy(), filter_name)
            print(f"✅ {filter_name}: OK (output shape: {filtered.shape})")
        except Exception as e:
            print(f"❌ {filter_name}: FAILED ({e})")
