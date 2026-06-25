import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QApplication, QSplashScreen

from ui.main_window import MainWindow


def _resource_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _make_splash_pixmap(screen_size):
    path = os.path.join(_resource_path(), "assets", "icons", "app_icon.png")
    logo = QPixmap(path)

    max_dim = min(screen_size.width(), screen_size.height()) * 9 // 25
    logo = logo.scaled(max_dim, max_dim, Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)

    bg = QPixmap(max_dim, max_dim)
    bg.fill(QColor("#1e1e1e"))
    p = QPainter(bg)
    x = (max_dim - logo.width()) // 2
    y = (max_dim - logo.height()) // 2
    p.drawPixmap(x, y, logo)
    p.end()
    return bg


def main():
    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    if screen:
        splash_pix = _make_splash_pixmap(screen.size())
    else:
        splash_pix = QPixmap(
            os.path.join(_resource_path(), "assets", "icons", "app_icon.png")
        )

    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()

    window = MainWindow()
    window.show()
    splash.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
