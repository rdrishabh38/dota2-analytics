# Dota 2 Analytics Hub

A personal desktop dashboard to download, analyze, and visualize your Dota 2 account metadata. Built with Python and Streamlit, this tool allows you to track your behavior score and commend history over time across multiple Steam accounts.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Made with Streamlit](https://img.shields.io/badge/made%20with-Streamlit-red.svg)

---

## Overview

This application provides a user-friendly interface to fetch and process your personal Dota 2 game data from your Steam profile. It solves the problem of not being able to easily see or track your behavior score history directly on Steam. The entire application is self-contained and runs locally on your machine.

### Key Features
* **Multi-Profile Management**: Securely add and switch between multiple Steam accounts directly within the UI.
* **Automated Data Syncing**: Performs a full historical download on the first run and efficient incremental syncs on subsequent runs to only fetch new data.
* **Data Visualization**: View your behavior score trend on an interactive line chart and see key metrics at a glance.
* **Standalone Application**: A simple executable is provided for users who don't have Python installed.
* **Secure & Private**: All your data, including sensitive cookie information, is stored locally on your computer and is never sent anywhere.

## Application Demo

![Application Demo](readme_assets/dota2_analytics.gif)

---

## How to Use

There are two ways to use this application, depending on your needs.

### 1. For Regular Users (Recommended)
The easiest way to get started is by using the pre-built standalone executable.

1.  Go to the **[Releases Page](https://github.com/rdrishabh38/dota2-analytics/releases)** of this repository.
2.  Download the `Dota2AnalyticsHub.exe` file from the latest release.
3.  Double-click the `.exe` file to run it. The application will start and open in your web browser.

### 2. For Developers (Running from Source)
If you have Python installed and want to run the code directly, follow these setup instructions.

#### Step 1: Clone the Repository
```bash
git clone https://github.com/rdrishabh38/dota2-analytics.git
cd dota2-analytics
```

#### Step 2: Set Up a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
This project's dependencies are listed in the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Application
Once the dependencies are installed, you can start the Streamlit server.
```bash
streamlit run app.py
```
Your web browser will automatically open with the application running.

---

## Building the Executable (for Developers)

If you want to build your own `Dota2AnalyticsHub.exe` binary from the source code, follow these steps.

1.  **Complete the Developer Setup**: Ensure you have followed all the steps in the "For Developers" section above.
2.  **Install PyInstaller**: You'll need the PyInstaller package to create the executable.
    ```bash
    pip install pyinstaller
    ```
3.  **Run the Build Command**: The project includes a `run_app.spec` file that contains the build configuration. Simply run PyInstaller with this file as the target.
    ```bash
    pyinstaller run_app.spec
    ```
4.  **Find Your Executable**: The final, single-file executable will be located in the `dist` folder.

**Note:** Executables are platform-specific. The command above will create a Windows `.exe` when run on Windows, or a macOS/Linux binary when run on those respective systems.

---

## First-Time Configuration

When you run the application for the first time, you will need to add a profile by providing your Steam Custom URL and several cookie values from your browser.

> ### ⚠️ Important Security Warning
> Your `steamLoginSecure` cookie is like a temporary password for your account. 
> **Never share this cookie with anyone.** If someone gets this value, they 
> can gain access to your Steam account. Treat it with the same level of 
> security as your actual password.
>
> To invalidate this cookie, simply log out of Steam on the browser(chrome/firefox/brave etc)
> where you obtained it. This will force the cookie to expire and prevent any unauthorized access.


1.  Open the application and navigate to the **⚙️ Profile Management** tab.
2.  Read the security warning carefully.
3.  Fill in the required fields to create a new profile. The sections below explain how to find this information.

### Finding Your Steam Custom URL
1.  Log in to `steamcommunity.com` in your web browser.
2.  If you use Steam's Family View, you **must** unlock it by entering your PIN.
3.  Navigate to this URL: **https://steamcommunity.com/my/**
4.  Your browser will redirect you to your actual profile URL, which will look something like `https://steamcommunity.com/id/abc123/`.
5.  The `abc123` part is your **Custom URL**. Enter this value into the "Steam Custom URL" field in the application.

### Finding Your Cookie Values
The easiest way to get your cookie values is by using a browser extension.

1.  **Install a Cookie Editor Extension**:
    * For Chrome/Brave/Edge: **[Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)**
    * For Firefox: **[Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)**
2.  **Log in to Steam**: Make sure you are logged in to `steamcommunity.com` and have unlocked Family View (if applicable).
3.  **Open the Extension**: Click the Cookie-Editor icon (🍪) in your browser's toolbar. A list of all cookies for `steamcommunity.com` will appear.
4.  **Copy the Values**: Find each of the following cookies in the list, click on it, and copy its corresponding **"Value"**. Paste each value into the matching field in the application:
    * `sessionid`
    * `steamLoginSecure`
    * `browserid`
    * `steamCountry`
    * `steamparental`



Once all fields are filled, click **"💾 Save Profile"**. You can then navigate back to the **📊 Behaviour Summary** tab to download and view your data.

---


## Disclaimer
This is an unofficial application and is not affiliated with, endorsed by, or in any way officially connected with Valve Corporation or Steam.

Steam and the Steam logo are trademarks and/or registered trademarks of Valve Corporation in the U.S. and/or other countries.

## License
This project is licensed under the **GNU General Public License v3.0**. See the `LICENSE` file in the repository for the full license text.