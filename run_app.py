import sys
import os
import webbrowser
import threading
import time
from streamlit.web import cli as stcli

def open_browser():
    """
    Waits a few seconds for the server to initialize, then opens the browser.
    This function runs in a separate thread.
    """
    time.sleep(4) # Give the server a moment to start
    url = "http://localhost:8501/dota2analytics"
    print(f"Opening application in browser: {url}")
    webbrowser.open(url, new=2)

if __name__ == "__main__":
    # Start the browser-opening function in a background thread.
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()

    # --- RUN THE STREAMLIT SERVER IN THE MAIN THREAD ---
    # This is the primary, blocking call that will run until the app is closed.
    app_path = os.path.join(os.path.dirname(__file__), 'app.py')
    port = "8501"
    base_url = "dota2analytics"

    print("\n" + "="*60)
    print("  Application server is starting...")
    print("  To shut down, close this window.")
    print("="*60 + "\n")

    sys.argv = [
        "streamlit", "run", app_path,
        "--server.port", port,
        "--server.headless", "true",
        "--server.baseUrlPath", base_url,
        "--global.developmentMode", "false",
    ]
    
    stcli.main()
