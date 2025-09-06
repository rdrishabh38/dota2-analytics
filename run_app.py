# Dota 2 Analytics Hub
# A personal desktop dashboard to download, analyze, and visualize your Dota 2 metadata.
# Copyright (C) 2025 Kocha rdrishabh38@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


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
