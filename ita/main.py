#!/usr/bin/env python3
import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QLineEdit,
    QPushButton, QAction, QMenu, QShortcut
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView


class BrowserView(QWidget):
    """Widget che incapsula QWebEngineView con barra URL."""
    def __init__(self, main_window, initial_url="https://www.google.com"):
        super().__init__()
        self.main_window = main_window

        # Barra URL + pulsante Vai
        self.url_bar = QLineEdit(initial_url)
        self.go_btn  = QPushButton("Vai")
        self.go_btn.clicked.connect(self.load_url)

        top_h = QHBoxLayout()
        top_h.setContentsMargins(0, 0, 0, 0)
        top_h.addWidget(self.url_bar)
        top_h.addWidget(self.go_btn)

        # WebEngineView
        self.webview = QWebEngineView()
        self.webview.load(QUrl(initial_url))
        self.webview.titleChanged.connect(self.update_tab_title)

        # intercetto focus
        self.webview.installEventFilter(self)

        main_v = QVBoxLayout(self)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.addLayout(top_h)
        main_v.addWidget(self.webview)

    def load_url(self):
        txt = self.url_bar.text().strip()
        if not txt.startswith(("http://", "https://")):
            txt = "http://" + txt
        self.webview.load(QUrl(txt))

    def update_tab_title(self):
        idx = self.main_window.tabs.currentIndex()
        title = self.webview.title() or "Nuova Scheda"
        if idx >= 0:
            self.main_window.tabs.setTabText(idx, title)

    def eventFilter(self, obj, evt):
        if obj is self.webview and evt.type() == evt.FocusIn:
            self.main_window.set_current_browser(self)
        return super().eventFilter(obj, evt)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SplitBrowser")
        self.resize(1200, 800)

        # stato full-screen pane
        self.is_pane_fs           = False
        self.fs_old_central       = None
        self.fs_old_tab_container = None
        self.fs_parent            = None
        self.fs_index             = None
        self.fs_pane_list         = []
        self.fs_current_pane      = None

        # QTabWidget principale
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

        self._create_actions()
        self._create_menus()
        self._create_shortcuts()

        self.add_tab()

    def _create_actions(self):
        # File
        self.new_tab_act   = QAction("Nuova scheda", self, shortcut="Ctrl+T",   triggered=self.add_tab)
        self.close_tab_act = QAction("Chiudi scheda", self, shortcut="Ctrl+W", triggered=self.close_current_tab)
        self.exit_act      = QAction("Esci", self, shortcut="Ctrl+Q",           triggered=self.close)

        # Split
        self.split_reset = QAction("1 parte", self, triggered=lambda: self.split_current(None, 1))

        self.split_h = QMenu("Orizzontale", self)
        self.split_v = QMenu("Verticale",   self)
        for i in (2, 3, 4):
            self.split_h.addAction(QAction(f"{i} parti", self,
                triggered=lambda _, c=i: self.split_current(Qt.Horizontal, c)))
            self.split_v.addAction(QAction(f"{i} parti", self,
                triggered=lambda _, c=i: self.split_current(Qt.Vertical, c)))

        # Fullscreen
        self.full_tab_act  = QAction("FullScreen Tab",  self,
                                    shortcut="F11", checkable=True,
                                    triggered=self.toggle_fullscreen_tab)
        self.full_pane_act = QAction("FullScreen Pane", self,
                                    shortcut="Shift+F11", checkable=True,
                                    triggered=self.toggle_fullscreen_pane)

    def _create_menus(self):
        mb = self.menuBar()
        # File
        fm = mb.addMenu("File")
        fm.addAction(self.new_tab_act)
        fm.addAction(self.close_tab_act)
        fm.addSeparator()
        fm.addAction(self.exit_act)
        # Split
        sm = mb.addMenu("Split")
        sm.addAction(self.split_reset)
        sm.addSeparator()
        sm.addMenu(self.split_h)
        sm.addMenu(self.split_v)
        # View
        vm = mb.addMenu("View")
        vm.addAction(self.full_tab_act)
        vm.addAction(self.full_pane_act)

    def _create_shortcuts(self):
        # switch tab in full-screen tab
        QShortcut(QKeySequence("Ctrl+PgDown"), self, activated=self.next_tab)
        QShortcut(QKeySequence("Ctrl+PgUp"),   self, activated=self.prev_tab)
        # switch pane in full-screen pane
        QShortcut(QKeySequence("Ctrl+Tab"),    self, activated=lambda: self.switch_pane(1))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=lambda: self.switch_pane(-1))
        # Esc per uscire da qualunque full-screen
        QShortcut(QKeySequence("Escape"), self, activated=self._exit_fullscreen_any)

    def add_tab(self):
        cont = QWidget()
        cont.current_browser = None
        lay = QVBoxLayout(cont)
        lay.setContentsMargins(0, 0, 0, 0)

        split = QSplitter(Qt.Horizontal)
        split.setHandleWidth(6)
        browser = BrowserView(self)
        split.addWidget(browser)
        lay.addWidget(split)

        cont.current_browser = browser
        self.tabs.addTab(cont, "Nuova Scheda")
        self.tabs.setCurrentWidget(cont)
        self.current_browser = browser

    def close_current_tab(self):
        i = self.tabs.currentIndex()
        if i != -1:
            self.close_tab(i)

    def close_tab(self, idx):
        self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self.add_tab()

    def on_tab_changed(self, idx):
        cont = self.tabs.widget(idx)
        if cont:
            self.current_browser = getattr(cont, "current_browser", None)

    def set_current_browser(self, pane):
        self.current_browser = pane
        # sincronizza il tab corrente
        for i in range(self.tabs.count()):
            c = self.tabs.widget(i)
            if getattr(c, "current_browser", None) is pane:
                self.tabs.setCurrentIndex(i)
                break

    def split_current(self, orient, count):
        cont = self.tabs.currentWidget()
        if not cont or not self.current_browser:
            return
        old = cont.current_browser
        old_url = old.webview.url().toString()

        # pulisco il layout
        lay = cont.layout()
        while lay.count():
            itm = lay.takeAt(0)
            w = itm.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        # 1 parte = reset
        if count == 1:
            split = QSplitter(Qt.Horizontal); split.setHandleWidth(6)
            nb = BrowserView(self, old_url)
            split.addWidget(nb)
            lay.addWidget(split)
            cont.current_browser = nb
            self.current_browser   = nb
            return

        # nuovo splitter orientato
        split = QSplitter(orient); split.setHandleWidth(6)
        first = BrowserView(self, old_url)
        split.addWidget(first)
        for _ in range(count - 1):
            split.addWidget(BrowserView(self))
        split.setSizes([1] * count)
        lay.addWidget(split)

        cont.current_browser = first
        self.current_browser = first

    def toggle_fullscreen_tab(self):
        if self.full_tab_act.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_fullscreen_pane(self):
        if self.is_pane_fs:
            # esci da full-pane
            pane = self.fs_current_pane
            self.setCentralWidget(self.fs_old_central)
            self.menuBar().setVisible(True)
            self.fs_parent.insertWidget(self.fs_index, pane)
            self.is_pane_fs = False
            self.full_pane_act.setChecked(False)
        else:
            # entra in full-pane
            pane = self.current_browser
            parent = pane.parent(); idx = parent.indexOf(pane)

            self.fs_old_central       = self.centralWidget()
            self.fs_old_tab_container = self.tabs.currentWidget()
            self.fs_parent            = parent
            self.fs_index             = idx
            self.fs_current_pane      = pane

            pane.setParent(None)
            self.menuBar().setVisible(False)
            self.setCentralWidget(pane)
            self.is_pane_fs = True
            self.full_pane_act.setChecked(True)

            # elenco dei pane nella tab originale
            self.fs_pane_list = self._collect_panes(self.fs_old_tab_container)

    def _collect_panes(self, container):
        panes = []
        def recurse(w):
            if isinstance(w, BrowserView):
                panes.append(w)
            elif isinstance(w, QSplitter):
                for i in range(w.count()):
                    recurse(w.widget(i))
        lay = container.layout()
        if not lay or lay.count() == 0:
            return panes
        recurse(lay.itemAt(0).widget())
        return panes

    def switch_pane(self, step):
        if not self.is_pane_fs: return
        lst = self.fs_pane_list; cur = self.fs_current_pane
        if cur not in lst: return
        nxt = lst[(lst.index(cur) + step) % len(lst)]
        # esco e rientro sul nuovo
        self.toggle_fullscreen_pane()
        self.current_browser = nxt
        self.toggle_fullscreen_pane()

    def next_tab(self):
        i = (self.tabs.currentIndex() + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(i)

    def prev_tab(self):
        i = (self.tabs.currentIndex() - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(i)

    def _exit_fullscreen_any(self):
        # Esc esce da entrambe le modalità
        if self.is_pane_fs:
            self.toggle_fullscreen_pane()
        elif self.full_tab_act.isChecked():
            self.full_tab_act.setChecked(False)
            self.toggle_fullscreen_tab()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
      QSplitter::handle {
        background-color: #5c85d6;
      }
      QSplitter::handle:horizontal { width: 6px; }
      QSplitter::handle:vertical   { height: 6px; }
    """)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
