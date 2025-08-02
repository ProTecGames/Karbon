import webview
from queue import Queue
import threading
import time

preview_queue = Queue()
window = None

def webview_main():
    global window
    
    def start_webview():
        global window
        window = webview.create_window("Live Preview", html="<h1>Waiting for AI...</h1>", width=900, height=500)
        webview.start()
    
    # Start the update processor in a separate thread
    update_thread = threading.Thread(target=process_updates, daemon=True)
    update_thread.start()
    
    # Run webview on the main thread (this will block until window is closed)
    start_webview()

def process_updates():
    while True:
        try:
            while not preview_queue.empty():
                html = preview_queue.get()
                if window and hasattr(window, 'load_html'):
                    try:
                        window.load_html(html)
                    except Exception as e:
                        print(f"Error loading HTML in preview: {e}")
            time.sleep(0.1)  # Reduced sleep time for more responsive updates
        except Exception as e:
            print(f"Error in process_updates: {e}")
            time.sleep(1)

def update_preview(html_code: str):
    if html_code:
        try:
            preview_queue.put(html_code)
            print("Preview update queued successfully")
        except Exception as e:
            print(f"Error queuing preview update: {e}")
    else:
        print("No HTML code provided for preview")

def is_preview_ready():
    """Check if the preview window is ready to receive updates"""
    return window is not None and hasattr(window, 'load_html')