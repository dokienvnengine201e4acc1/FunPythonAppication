import sys, os
import shutil
import glob
from PyQt5.QtCore import QUrl, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtGui import QKeyEvent

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # User Agent
        self.profile = self.browser.page().profile()
        new_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.118 Safari/537.36"
        self.profile.setHttpUserAgent(new_user_agent)

        # Turn on Javascript
        self.browser.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

        self.browser.setUrl(QUrl("https://www.google.com"))

        # Toolbar
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        back_btn = QAction("←", self)
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(self.browser.forward)
        navtb.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)

        clear_history = QAction("Clear History", self)
        clear_history.triggered.connect(self.clear_history)
        navtb.addAction(clear_history)

        clear_cookies = QAction("Clear Cookies", self)
        clear_cookies.triggered.connect(self.clear_cookies)
        navtb.addAction(clear_cookies)

        clear_cache = QAction("Clear Cache", self)
        clear_cache.triggered.connect(self.clear_cache)
        navtb.addAction(clear_cache)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_urlbar)

        self.setWindowTitle("Classic Browser with Tweak")
        self.resize(1024, 768)

        print("Persistent storage path:", self.profile.persistentStoragePath())
        print("Cache path:", self.profile.cachePath())

        # Fullscreen
        self.is_fullscreen = False
        self.installEventFilter(self)  # Use eventFilter process keyboard

    # ==========================
    # Event Filter process F11 + Esc
    # ==========================
    def eventFilter(self, obj, event):
        if isinstance(event, QKeyEvent):
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_F11:
                    if self.is_fullscreen:
                        self.showNormal()
                        self.is_fullscreen = False
                    else:
                        self.showFullScreen()
                        self.is_fullscreen = True
                    return True  # đã xử lý
                elif event.key() == Qt.Key_Escape and self.is_fullscreen:
                    self.showNormal()
                    self.is_fullscreen = False
                    return True
        return super().eventFilter(obj, event)

    # ==========================
    # Close Event: Clean QtWebEngine and cache
    # ==========================
    def closeEvent(self, event):
        _ = self.cleanup_cache  # VSCode know using

        # Stop browser
        try:
            self.browser.stop()
        except:
            pass

        # Cleaner page & profile
        page = self.browser.page()
        self.browser.setPage(None)
        del page

        profile = self.profile
        self.browser.deleteLater()
        del self.browser
        del self.profile

        # Kill QtWebEngineProcess to free up files
        os.system("taskkill /IM QtWebEngineProcess.exe /F > nul 2>&1")

        # Wait 1 giây before delete cache
        QTimer.singleShot(1000, self.cleanup_cache)

        os.system(r'for /d %u in ("C:\Users\*") do (if exist "%u\AppData\Local\python3\QtWebEngine" rmdir /s /q "%u\AppData\Local\python3\QtWebEngine")')
        os.system(r'for /d %u in ("C:\Users\*") do (if exist "%u\AppData\Local\python3\cache" rmdir /s /q "%u\AppData\Local\python3\cache")')

        event.accept()

    # ==========================
    # Cleanup cache & QtWebEngine
    # ==========================
    def cleanup_cache(self):
        print("[cleanup_cache] Running cleanup...")

        for u in glob.glob(r"C:\Users\*"):
            qt_path = f"{u}\AppData\Local\python3\QtWebEngine"
            cache_path = f"{u}\AppData\Local\python3\cache"

            if os.path.exists(qt_path):
                print("[cleanup_cache] Removing:", qt_path)
                shutil.rmtree(qt_path, ignore_errors=True)
            if os.path.exists(cache_path):
                print("[cleanup_cache] Removing:", cache_path)
                shutil.rmtree(cache_path, ignore_errors=True)
            os.system(r'for /d %u in ("C:\Users\*") do (if exist "%u\AppData\Local\python3\QtWebEngine" rmdir /s /q "%u\AppData\Local\python3\QtWebEngine")')
            os.system(r'for /d %u in ("C:\Users\*") do (if exist "%u\AppData\Local\python3\cache" rmdir /s /q "%u\AppData\Local\python3\cache")')
            os.system(r'for /d %u in ("C:\Users\*") do (if exist "%u\AppData\Local\python3" rmdir /s /q "%u\AppData\Local\python3")')

    # ==========================
    # Toolbar actions
    # ==========================
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def update_urlbar(self, qurl):
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)

    def clear_history(self):
        self.profile.clearAllVisitedLinks()
        QMessageBox.information(self, "Cleared", "Visited links (history) cleared.")

    def clear_cookies(self):
        self.profile.cookieStore().deleteAllCookies()
        QMessageBox.information(self, "Cleared", "Cookies cleared.")

    def clear_cache(self):
        self.profile.clearHttpCache()
        QMessageBox.information(self, "Cleared", "HTTP cache clearing requested.")

# ==========================
# Main
# ==========================
def main():
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
