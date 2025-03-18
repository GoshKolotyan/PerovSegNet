import pytest
import numpy as np
from processing.image_processor import ImageProcessor

@pytest.fixture
def sample_image():
    return np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

def test_image_processing(sample_image):
    processor = ImageProcessor()
    result, percentage = processor.process_image(sample_image)
    
    assert result.shape == sample_image.shape
    assert 0 <= percentage <= 100
    assert np.any(result != 0)

def test_invalid_input():
    processor = ImageProcessor()
    with pytest.raises(ValueError):
        processor.process_image(b'invalid_data')