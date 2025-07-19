#!/usr/bin/env python3
import sys
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QLineEdit,
    QPushButton, QAction, QMenu
)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class CustomWebView(QWebEngineView):
    viewActivated = pyqtSignal(object)

    def __init__(self, parent_browser):
        super().__init__()
        self.parent_browser = parent_browser

    def focusInEvent(self, event):
        super().focusInEvent(event)
        # Segnala al MainWindow quale BrowserView ha il focus
        self.viewActivated.emit(self.parent_browser)


class BrowserView(QWidget):
    def __init__(self, main_window, initial_url="https://www.google.com"):
        super().__init__()
        self.main_window = main_window

        # URL bar + pulsante Vai
        self.url_bar = QLineEdit(initial_url)
        self.go_button = QPushButton("Vai")
        self.go_button.clicked.connect(self.load_url)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.url_bar)
        top_layout.addWidget(self.go_button)

        # WebEngineView custom
        self.webview = CustomWebView(self)
        self.webview.viewActivated.connect(main_window.set_current_browser)
        self.webview.loadFinished.connect(self.update_tab_title)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.webview)
        self.setLayout(main_layout)

        self.load_url()

    def load_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        self.webview.load(QUrl(url))

    def update_tab_title(self):
        title = self.webview.title() or "Nuova Scheda"
        idx = self.main_window.tabs.currentIndex()
        self.main_window.tabs.setTabText(idx, title)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SplitBrowser")
        self.resize(1200, 800)
        self.current_browser = None

        # Tab widget principale
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

        self._create_actions()
        self._create_menus()

        # Apri la prima scheda
        self.add_tab()

    def _create_actions(self):
        self.new_tab_act   = QAction("Nuova scheda", self, triggered=self.add_tab)
        self.close_tab_act = QAction("Chiudi scheda", self, triggered=self.close_current_tab)
        self.exit_act      = QAction("Esci", self, triggered=self.close)

        # Split 2,3,4 parti orizzontali/verticali
        self.split_actions = []
        for orient, label in [(Qt.Horizontal, "Orizzontale"), (Qt.Vertical, "Verticale")]:
            menu = QMenu(f"{label}", self)
            for parts in (2, 3, 4):
                act = QAction(f"{parts} parti", self,
                              triggered=lambda chk, o=orient, p=parts: self.split_current(o, p))
                menu.addAction(act)
            self.split_actions.append((label, menu))

    def _create_menus(self):
        menubar  = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.new_tab_act)
        file_menu.addAction(self.close_tab_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        split_menu = menubar.addMenu("Split")
        # Aggiunge l'opzione per tornare a singolo pannello
        reset_act = QAction("1 parte", self, triggered=lambda: self.split_current(None, 1))
        split_menu.addAction(reset_act)
        split_menu.addSeparator()
        # Aggiungi i sotto-menu Orizzontale/Verticale
        for label, submenu in self.split_actions:
            split_menu.addMenu(submenu)

    def add_tab(self):
        """Aggiunge una nuova scheda con splitter a 1 pannello."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        browser = BrowserView(self)
        splitter.addWidget(browser)

        layout.addWidget(splitter)
        self.tabs.addTab(container, "Nuova Scheda")
        self.tabs.setCurrentWidget(container)

        # Memorizza il browser corrente in questo container
        container.current_browser = browser
        self.current_browser = browser

    def close_current_tab(self):
        idx = self.tabs.currentIndex()
        if idx != -1:
            self.close_tab(idx)

    def close_tab(self, idx):
        self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self.add_tab()

    def on_tab_changed(self, idx):
        """Quando cambio tab, aggiorno current_browser dal container."""
        container = self.tabs.widget(idx)
        if container and hasattr(container, "current_browser"):
            self.current_browser = container.current_browser

    def set_current_browser(self, browser):
        """Segnalato da CustomWebView quando un mini-browser riceve focus."""
        self.current_browser = browser
        # Aggiorna anche il container
        for i in range(self.tabs.count()):
            container = self.tabs.widget(i)
            if getattr(container, "current_browser", None) is browser:
                self.tabs.setCurrentIndex(i)
                break

    def split_current(self, orientation, count):
        """
        Ricostruisce la scheda corrente con ‘count’ pannelli.
        Per count=1 resetta allo stato iniziale.
        """
        container = self.tabs.currentWidget()
        if not container or not hasattr(container, "current_browser"):
            return

        old_browser = container.current_browser
        # Prende l'URL dell'istanza attiva per riutilizzarla
        old_url = old_browser.webview.url().toString()

        # Svuota completamente il layout precedente
        layout = container.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        # Se reset a 1 pannello
        if count == 1:
            splitter = QSplitter(Qt.Horizontal)
            new_browser = BrowserView(self, old_url)
            splitter.addWidget(new_browser)

            layout.addWidget(splitter)
            container.current_browser = new_browser
            self.current_browser = new_browser
            return

        # Altrimenti crea nuovo splitter con 'count' pannelli
        splitter = QSplitter(orientation)
        # Primo pannello col vecchio URL
        first = BrowserView(self, old_url)
        splitter.addWidget(first)
        # Gli altri pannelli (URL di default)
        for _ in range(count - 1):
            splitter.addWidget(BrowserView(self))

        # Imposta dimensioni proporzionali uguali
        splitter.setSizes([1] * count)

        layout.addWidget(splitter)
        # Memorizza il primo come current
        container.current_browser = first
        self.current_browser = first


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
