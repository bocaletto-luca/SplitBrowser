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
    def __init__(self, main, url="https://www.google.com"):
        super().__init__()
        self.main = main

        # Barra URL + Pulsanti
        self.url_bar = QLineEdit(url)
        self.back_btn    = QPushButton("◀")
        self.forward_btn = QPushButton("▶")
        self.reload_btn  = QPushButton("⟳")
        self.cache_btn   = QPushButton("🗑")
        self.go_btn      = QPushButton("Vai")

        self.back_btn.clicked.connect(lambda: self.web.back())
        self.forward_btn.clicked.connect(lambda: self.web.forward())
        self.reload_btn.clicked.connect(lambda: self.web.reload())
        self.cache_btn.clicked.connect(self.clear_cache)
        self.go_btn.clicked.connect(self.load_url)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        for w in (self.back_btn, self.forward_btn,
                  self.reload_btn, self.cache_btn,
                  self.url_bar, self.go_btn):
            top.addWidget(w)

        # WebEngineView
        self.web = QWebEngineView()
        self.web.load(QUrl(url))
        self.web.titleChanged.connect(self.update_tab_title)
        self.web.installEventFilter(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top)
        layout.addWidget(self.web)

    def load_url(self):
        txt = self.url_bar.text().strip()
        if not txt.startswith(("http://", "https://")):
            txt = "http://" + txt
        self.web.load(QUrl(txt))

    def update_tab_title(self):
        idx = self.main.tabs.currentIndex()
        if idx >= 0:
            title = self.web.title() or "Nuova Scheda"
            self.main.tabs.setTabText(idx, title)

    def clear_cache(self):
        prof = QWebEngineProfile.defaultProfile()
        prof.clearHttpCache()

    def eventFilter(self, obj, evt):
        if obj is self.web and evt.type() == evt.FocusIn:
            self.main.set_current(self)
        return super().eventFilter(obj, evt)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SplitBrowser")
        self.resize(1200, 800)

        # stato full-tab
        self.act_fullTab = None

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
        self.act_new_tab   = QAction("Nuova scheda", self, shortcut="Ctrl+T")
        self.act_close_tab = QAction("Chiudi scheda", self, shortcut="Ctrl+W")
        self.act_exit      = QAction("Esci", self, shortcut="Ctrl+Q")

        # Split
        self.act_split1 = QAction("1 parte", self)
        self.act_split1.triggered.connect(lambda: self.split_current(None, 1))

        # Full-screen
        self.act_fullPane = QAction("FullScreen Pane", self, shortcut="Shift+F11", checkable=True)
        # la tab full-screen la colleghiamo dopo aver creato il menu per
        # poter memorizzare l’azione in self.act_fullTab

    def _create_menus(self):
        mb = self.menuBar()

        # File menu
        fm = mb.addMenu("File")
        fm.addAction(self.act_new_tab)
        fm.addAction(self.act_close_tab)
        fm.addSeparator()
        fm.addAction(self.act_exit)
        self.act_new_tab.triggered.connect(self.add_tab)
        self.act_close_tab.triggered.connect(self.close_current_tab)
        self.act_exit.triggered.connect(self.close)

        # Split menu
        sm = mb.addMenu("Split")
        sm.addAction(self.act_split1)
        sm.addSeparator()

        hmenu = sm.addMenu("Orizzontale")
        for n in (2, 3, 4):
            a = QAction(f"{n} parti", self)
            a.triggered.connect(lambda _, n=n: self.split_current(Qt.Horizontal, n))
            hmenu.addAction(a)

        vmenu = sm.addMenu("Verticale")
        for n in (2, 3, 4):
            a = QAction(f"{n} parti", self)
            a.triggered.connect(lambda _, n=n: self.split_current(Qt.Vertical, n))
            vmenu.addAction(a)

        # View menu
        vm = mb.addMenu("View")
        # FullScreen Tab
        self.act_fullTab = QAction("FullScreen Tab", self, shortcut="F11", checkable=True)
        self.act_fullTab.triggered.connect(self.toggle_full_tab)
        vm.addAction(self.act_fullTab)
        # FullScreen Pane
        vm.addAction(self.act_fullPane)

    def _create_shortcuts(self):
        # switch schede
        QShortcut(QKeySequence("Ctrl+PgDown"), self, activated=self.next_tab)
        QShortcut(QKeySequence("Ctrl+PgUp"),   self, activated=self.prev_tab)
        # switch pane in full-pane
        QShortcut(QKeySequence("Ctrl+Tab"),       self, activated=lambda: self.switch_pane(1))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=lambda: self.switch_pane(-1))
        # Esc esce da qualunque full-screen
        QShortcut(QKeySequence("Escape"), self, activated=self.exit_fullscreen)

    def add_tab(self):
        cont = QWidget()
        cont.prev_sizes = None
        cont.isPaneFS   = False

        lay = QVBoxLayout(cont)
        lay.setContentsMargins(0, 0, 0, 0)

        sp = QSplitter(Qt.Horizontal)
        sp.setHandleWidth(6)
        bv = BrowserView(self)
        sp.addWidget(bv)
        lay.addWidget(sp)

        cont.splitter = sp
        cont.current  = bv

        self.tabs.addTab(cont, "Nuova Scheda")
        self.tabs.setCurrentWidget(cont)
        self.set_current(bv)

    def close_current_tab(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.close_tab(idx)

    def close_tab(self, idx):
        self.tabs.removeTab(idx)
        if self.tabs.count() == 0:
            self.add_tab()

    def on_tab_changed(self, idx):
        cont = self.tabs.widget(idx)
        if cont:
            self.set_current(cont.current)

    def set_current(self, bv):
        self.current = bv
        # sincronizza tab attiva
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if getattr(w, "current", None) is bv:
                self.tabs.setCurrentIndex(i)
                break

    def split_current(self, orient, count):
        cont = self.tabs.currentWidget()
        if not cont or not hasattr(cont, "current"):
            return

        old = cont.current
        url = old.web.url().toString()

        lay = cont.layout()
        # svuota
        while lay.count():
            w = lay.takeAt(0).widget()
            if w:
                w.deleteLater()

        # ricrea splitter
        sp = QSplitter(orient if count > 1 else Qt.Horizontal)
        sp.setHandleWidth(6)

        first = BrowserView(self, url)
        sp.addWidget(first)
        for _ in range(count - 1):
            sp.addWidget(BrowserView(self))

        # percentuali corrette
        sizes = [1] * count
        sp.setSizes(sizes)

        lay.addWidget(sp)
        cont.splitter = sp
        cont.current  = first
        cont.prev_sizes = None
        cont.isPaneFS   = False
        self.set_current(first)

    def toggle_full_tab(self, checked):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_full_pane(self):
        cont = self.tabs.currentWidget()
        if not cont:
            return

        sp  = cont.splitter
        idx = sp.indexOf(self.current)
        n   = sp.count()

        if not cont.isPaneFS:
            # entra full-pane: salva dimensioni e isola corrente
            cont.prev_sizes = sp.sizes()
            total = sum(cont.prev_sizes)
            new_sizes = [0] * n
            new_sizes[idx] = total
            sp.setSizes(new_sizes)
            cont.isPaneFS = True
            self.act_fullPane.setChecked(True)
        else:
            # esci full-pane: ripristina
            if cont.prev_sizes:
                sp.setSizes(cont.prev_sizes)
            cont.isPaneFS = False
            self.act_fullPane.setChecked(False)

    def switch_pane(self, step):
        cont = self.tabs.currentWidget()
        if not cont or not cont.isPaneFS:
            return

        sp = cont.splitter
        panes = [sp.widget(i) for i in range(sp.count())]
        if self.current not in panes:
            return

        # toggle off current
        self.toggle_full_pane()
        idx = panes.index(self.current)
        nxt = panes[(idx + step) % len(panes)]
        self.set_current(nxt)
        # toggle on new
        self.toggle_full_pane()

    def next_tab(self):
        i = (self.tabs.currentIndex() + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(i)

    def prev_tab(self):
        i = (self.tabs.currentIndex() - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(i)

    def exit_fullscreen(self):
        cont = self.tabs.currentWidget()
        if cont and cont.isPaneFS:
            self.toggle_full_pane()
        elif self.act_fullTab.isChecked():
            self.act_fullTab.trigger()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
      QSplitter::handle { background-color: #5c85d6; }
      QSplitter::handle:horizontal { width: 6px; }
      QSplitter::handle:vertical   { height: 6px; }
      QPushButton { min-width: 24px; }
    """)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
