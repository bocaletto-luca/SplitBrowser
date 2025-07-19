#!/usr/bin/env python3
import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QMenu, QHBoxLayout, QVBoxLayout,
    QSplitter, QLineEdit, QPushButton, QWidget, QTabWidget, QShortcut
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


class BrowserView(QWidget):
    """Single browser pane with URL bar, navigation and cache cleaning."""
    def __init__(self, main_window, url="https://www.google.com"):
        super().__init__()
        self.main = main_window

        # Navigation controls
        self.url_bar            = QLineEdit(url)
        self.back_button        = QPushButton("◀")
        self.forward_button     = QPushButton("▶")
        self.reload_button      = QPushButton("⟳")
        self.clear_cache_button = QPushButton("🗑")
        self.go_button          = QPushButton("Go")

        self.back_button.clicked.connect(lambda: self.webview.back())
        self.forward_button.clicked.connect(lambda: self.webview.forward())
        self.reload_button.clicked.connect(lambda: self.webview.reload())
        self.clear_cache_button.clicked.connect(self.clear_cache)
        self.go_button.clicked.connect(self.load_url)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        for w in (
            self.back_button, self.forward_button,
            self.reload_button, self.clear_cache_button,
            self.url_bar, self.go_button
        ):
            top_layout.addWidget(w)

        # Web view
        self.webview = QWebEngineView()
        self.webview.load(QUrl(url))
        self.webview.titleChanged.connect(self.update_tab_title)
        self.webview.installEventFilter(self)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top_layout)
        layout.addWidget(self.webview)

    def load_url(self):
        txt = self.url_bar.text().strip()
        if not txt.startswith(("http://", "https://")):
            txt = "http://" + txt
        self.webview.load(QUrl(txt))

    def update_tab_title(self):
        idx = self.main.tab_widget.currentIndex()
        if idx >= 0:
            title = self.webview.title() or "New Tab"
            self.main.tab_widget.setTabText(idx, title)

    def clear_cache(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()

    def eventFilter(self, obj, event):
        # When this pane gains focus, mark it active in MainWindow
        if obj is self.webview and event.type() == event.FocusIn:
            self.main.set_current_pane(self)
        return super().eventFilter(obj, event)


class MainWindow(QMainWindow):
    """Main window with tabbed and split browser panes."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Split Browser")
        self.resize(1200, 800)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tab_widget)

        # Full-screen actions
        self.full_tab_action = QAction("FullScreen Tab", self,
                                       shortcut="F11", checkable=True)
        self.full_tab_action.toggled.connect(self.toggle_full_tab)

        self.full_pane_action = QAction("FullScreen Pane", self,
                                        shortcut="Shift+F11", checkable=True)
        self.full_pane_action.toggled.connect(self.toggle_full_pane)

        # Build menu and shortcuts
        self._create_menus()
        self._create_shortcuts()

        # State variables for split and full-pane
        self.current_pane     = None
        self.is_pane_full     = False

        self.add_tab()

    def _create_menus(self):
        mb = self.menuBar()

        # File menu
        file_menu = mb.addMenu("File")
        new_tab = QAction("New Tab", self, shortcut="Ctrl+T")
        new_tab.triggered.connect(self.add_tab)
        file_menu.addAction(new_tab)

        close_tab = QAction("Close Tab", self, shortcut="Ctrl+W")
        close_tab.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab)

        file_menu.addSeparator()
        exit_act = QAction("Exit", self, shortcut="Ctrl+Q")
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Split menu
        split_menu = mb.addMenu("Split")
        reset_act = QAction("1 Panel", self)
        reset_act.triggered.connect(lambda: self.split_current(None, 1))
        split_menu.addAction(reset_act)
        split_menu.addSeparator()

        horiz = split_menu.addMenu("Horizontal")
        vert  = split_menu.addMenu("Vertical")
        for count in (2, 3, 4):
            act_h = QAction(f"{count} Panels", self)
            act_h.triggered.connect(lambda _, c=count: self.split_current(Qt.Horizontal, c))
            horiz.addAction(act_h)

            act_v = QAction(f"{count} Panels", self)
            act_v.triggered.connect(lambda _, c=count: self.split_current(Qt.Vertical, c))
            vert.addAction(act_v)

        # View menu
        view_menu = mb.addMenu("View")
        view_menu.addAction(self.full_tab_action)
        view_menu.addAction(self.full_pane_action)

    def _create_shortcuts(self):
        # Exit any full-screen
        QShortcut(QKeySequence("Escape"), self, activated=self.exit_fullscreen)

        # Switch tabs in full-tab mode
        QShortcut(QKeySequence("Ctrl+PgDown"), self, activated=self.next_tab)
        QShortcut(QKeySequence("Ctrl+PgUp"),   self, activated=self.prev_tab)

        # Switch panes in full-pane mode
        QShortcut(QKeySequence("Ctrl+Tab"),       self, activated=lambda: self.switch_pane(1))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=lambda: self.switch_pane(-1))

    def add_tab(self):
        """Add a new tab with a single browser pane."""
        container = QWidget()
        container.prev_sizes = None
        container.is_pane_fs = False

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)
        pane = BrowserView(self)
        splitter.addWidget(pane)
        layout.addWidget(splitter)

        container.splitter = splitter
        container.current  = pane

        self.tab_widget.addTab(container, "New Tab")
        self.tab_widget.setCurrentWidget(container)
        self.set_current_pane(pane)

    def close_current_tab(self):
        idx = self.tab_widget.currentIndex()
        if idx >= 0:
            self.close_tab(idx)

    def close_tab(self, index):
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.add_tab()

    def on_tab_changed(self, index):
        cont = self.tab_widget.widget(index)
        if cont:
            self.set_current_pane(cont.current)

    def set_current_pane(self, pane):
        """Mark the given BrowserView as active."""
        self.current_pane = pane
        # Sync the active tab
        for i in range(self.tab_widget.count()):
            cont = self.tab_widget.widget(i)
            if getattr(cont, "current", None) is pane:
                self.tab_widget.setCurrentIndex(i)
                break

    def split_current(self, orientation, count):
        """Rebuild the current tab with 'count' equally sized panes."""
        cont = self.tab_widget.currentWidget()
        if not cont or not hasattr(cont, "current"):
            return

        old = cont.current
        url = old.webview.url().toString()

        layout = cont.layout()
        # Clear existing widgets
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Create new splitter
        splitter = QSplitter(orientation if count > 1 else Qt.Horizontal)
        splitter.setHandleWidth(6)

        # First pane uses the current URL
        first = BrowserView(self, url)
        splitter.addWidget(first)
        # Remaining panes
        for _ in range(count - 1):
            splitter.addWidget(BrowserView(self))

        # Distribute sizes equally
        splitter.setSizes([1] * count)

        layout.addWidget(splitter)
        cont.splitter = splitter
        cont.current  = first
        cont.prev_sizes = None
        cont.is_pane_fs  = False
        self.set_current_pane(first)

    def toggle_full_tab(self, checked):
        """F11: toggle full-screen mode for the entire window."""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_full_pane(self, checked):
        """Shift+F11: toggle full-screen mode for the active pane only."""
        cont = self.tab_widget.currentWidget()
        if not cont:
            return

        splitter = cont.splitter
        idx = splitter.indexOf(self.current_pane)
        count = splitter.count()

        if checked:
            # enter pane full-screen
            cont.prev_sizes = splitter.sizes()
            total = sum(cont.prev_sizes)
            sizes = [0] * count
            sizes[idx] = total
            splitter.setSizes(sizes)
            cont.is_pane_fs = True
        else:
            # exit pane full-screen
            if cont.prev_sizes:
                splitter.setSizes(cont.prev_sizes)
            cont.is_pane_fs = False

    def switch_pane(self, step):
        """Ctrl+Tab / Ctrl+Shift+Tab: cycle through panes in full-pane mode."""
        cont = self.tab_widget.currentWidget()
        if not cont or not cont.is_pane_fs:
            return

        splitter = cont.splitter
        panes = [splitter.widget(i) for i in range(splitter.count())]
        if self.current_pane not in panes:
            return

        # Toggle off current
        self.full_pane_action.setChecked(False)
        # Move to next
        idx = panes.index(self.current_pane)
        next_pane = panes[(idx + step) % len(panes)]
        self.set_current_pane(next_pane)
        # Toggle on new
        self.full_pane_action.setChecked(True)

    def next_tab(self):
        """Ctrl+PgDown: switch to next tab."""
        i = (self.tab_widget.currentIndex() + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(i)

    def prev_tab(self):
        """Ctrl+PgUp: switch to previous tab."""
        i = (self.tab_widget.currentIndex() - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(i)

    def exit_fullscreen(self):
        """Esc: exit pane full-screen first, then tab full-screen."""
        cont = self.tab_widget.currentWidget()
        if hasattr(cont, "is_pane_fs") and cont.is_pane_fs:
            self.full_pane_action.setChecked(False)
        elif self.full_tab_action.isChecked():
            self.full_tab_action.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
      QSplitter::handle {
        background-color: #5c85d6;
      }
      QSplitter::handle:horizontal { width: 6px; }
      QSplitter::handle:vertical   { height: 6px; }
      QPushButton { min-width: 24px; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
