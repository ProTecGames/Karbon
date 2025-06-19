import webview
from queue import Queue

preview_queue = Queue()
window = None

def webview_main():
    global window
    window = webview.create_window("Live Preview", html="<h1>Waiting for AI...</h1>", width=900, height=500)
    webview.start(func=process_updates)

def process_updates():
    import time
    while True:
        while not preview_queue.empty():
            html = preview_queue.get()
            if window:
                window.load_html(html)
        time.sleep(0.5)

def update_preview(html_code: str):
    preview_queue.put(html_code)
