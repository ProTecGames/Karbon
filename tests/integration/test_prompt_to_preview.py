import pytest
import tkinter as tk
from unittest.mock import patch
from ui_items.karbon_ui import KarbonUI
from unittest.mock import patch

from unittest.mock import patch
from ui_items.karbon_ui import KarbonUI
import tkinter as tk
import pytest

@pytest.fixture
def karbon_ui():
    root = tk.Tk()
    ui = KarbonUI(root)
    return ui

def test_prompt_to_preview_flow(karbon_ui):
    test_prompt = "Generate a simple webpage"
    dummy_code = "<html><body>Test Page</body></html>"

    with patch("ui_items.karbon_ui.update_preview") as mock_preview:
        karbon_ui.handle_prompt_generated(prompt_text=test_prompt, code=dummy_code)
        mock_preview.assert_called_once_with(dummy_code)


