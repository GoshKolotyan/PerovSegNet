"""
Launcher script for PerovSegNet desktop application.
This script runs Streamlit directly (not as subprocess) for PyInstaller compatibility.
"""
import sys
import os
import webbrowser
from threading import Timer

# Streamlit server port
PORT = 8080

def open_browser():
    """Open browser after a delay."""
    webbrowser.open(f"http://localhost:{PORT}")

def get_app_path():
    """Get the correct path to main.py for both dev and PyInstaller environments."""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, "app", "main.py")

def main():
    # Get the correct app path
    app_path = get_app_path()

    # Verify the app file exists
    if not os.path.exists(app_path):
        print(f"ERROR: Cannot find main.py at {app_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
        if getattr(sys, 'frozen', False):
            print(f"PyInstaller temp dir: {sys._MEIPASS}")
        input("Press Enter to exit...")
        return

    # Change to the app directory
    os.chdir(os.path.dirname(app_path))

    print("="*60)
    print("Starting PerovSegNet Desktop Application")
    print("="*60)
    print(f"\nApp will open at: http://localhost:{PORT}")
    print("Browser will open automatically in 3 seconds...")
    print("\nPress Ctrl+C to stop the application.\n")
    print("="*60 + "\n")

    # Schedule browser to open after 3 seconds
    Timer(3.0, open_browser).start()

    # Import and run Streamlit directly
    try:
        from streamlit.web import cli as stcli

        # Set up Streamlit arguments
        sys.argv = [
            "streamlit",
            "run",
            app_path,
            f"--server.port={PORT}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.address=localhost",
            "--global.developmentMode=false"  # Disable dev mode to allow custom port
        ]

        # Run Streamlit
        sys.exit(stcli.main())

    except ImportError as e:
        print(f"ERROR: Failed to import Streamlit: {e}")
        print("\nThis usually means Streamlit was not properly included in the build.")
        print("Please rebuild using: ./build.sh")
        input("\nPress Enter to exit...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nShutting down PerovSegNet...")
        print("Application closed.")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
