import pytest
from PIL import Image as PImage


@pytest.fixture
def temp_image_file():
    """Creates a temporary image file and returns its path."""
    return PImage.new("RGB", (60, 30), color="red")
