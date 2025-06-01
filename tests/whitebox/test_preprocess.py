# tests/test_preprocess.py

import sys, os
# __file__ is tests/whitebox/test_preprocess.py → go up two levels to the project root
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, root)

from app import preprocess_array
import numpy as np
import pytest

def test_preprocess_rgb_image_shape_and_range():
    # Create a 256×256 RGB image (values 0–255)
    dummy = np.random.randint(0, 256, (256,256,3), dtype=np.uint8)
    
    out = preprocess_array(dummy, size=128)
    
    # It should have shape (1,128,128,3)
    assert out.shape == (1,128,128,3)
    
    # All values must be floats between 0 and 1
    assert out.dtype == float
    assert out.min() >= 0.0 and out.max() <= 1.0

def test_preprocess_grayscale_image():
    ""
    # Create a 256×256 single‐channel image
    gray = np.random.randint(0, 256, (256,256), dtype=np.uint8)
    
    out = preprocess_array(gray, size=64)
    
    # preprocess_array should convert to RGB under the hood
    assert out.shape == (1,64,64,3)
    assert out.dtype == float

def test_preprocess_invalid_input_raises():
    # A 1D array is invalid
    with pytest.raises(Exception):
        preprocess_array(np.array([1,2,3]), size=128)
