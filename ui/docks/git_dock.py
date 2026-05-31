import os
import subprocess

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QMessageBox,
)


def _run_git(path, *args):
    try:
        result = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, timeout=10,
            cwd=path,
        )
        return result.stdout.strip(), result.stderr.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None, None


class GitDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Git", parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self._root = None
        self._colors = None

        self.container = QWidget()
        self.container.setObjectName("gitDockContainer")
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Branch label
        self._branch_label = QLabel("No repository")
        self._branch_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        layout.addWidget(self._branch_label)

        # Action buttons
        btn_row = QHBoxLayout()
        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(self._refresh_btn)

        self._commit_btn = QPushButton("Commit")
        self._commit_btn.clicked.connect(self._on_commit)
        btn_row.addWidget(self._commit_btn)

        self._pull_btn = QPushButton("Pull")
        self._pull_btn.clicked.connect(self._on_pull)
        btn_row.addWidget(self._pull_btn)

        self._push_btn = QPushButton("Push")
        self._push_btn.clicked.connect(self._on_push)
        btn_row.addWidget(self._push_btn)

        layout.addLayout(btn_row)

        # Status tree
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["File", "Status"])
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self._tree.setRootIsDecorated(False)
        self._tree.setAnimated(True)
        self._tree.setIndentation(12)
        self._tree.setFont(QFont("Consolas", 9))
        layout.addWidget(self._tree, 1)

        self._info_label = QLabel("Open a project to see Git status")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._info_label)

        self.setWidget(self.container)

        from themes.theme_manager import ThemeManager
        self.apply_theme(ThemeManager.colors())

    def apply_theme(self, colors):
        self._colors = colors
        bg = colors.get("main_bg", "#1e1e1e")
        panel_bg = colors.get("panel_bg", "#2b2b2b")
        fg = colors.get("text", "#dcdcdc")
        border = colors.get("border", "#555555")
        sel = colors.get("editor_selection", "#264f78")
        hover = colors.get("panel_hover", "#3c3f41")

        self.container.setStyleSheet(
            f"#gitDockContainer {{ background-color: {bg}; }}"
        )
        self._branch_label.setStyleSheet(f"""
            QLabel {{
                color: {colors.get("accent", "#3d7eff")};
                padding: 4px;
                background: {panel_bg};
                border: 1px solid {border};
                border-radius: 3px;
            }}
        """)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {panel_bg};
                color: {fg};
                border: 1px solid {border};
                font-size: 9pt;
                font-family: Consolas, monospace;
            }}
            QTreeWidget::item {{
                padding: 3px 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {sel};
            }}
            QTreeWidget::item:hover {{
                background-color: {hover};
            }}
        """)
        self._info_label.setStyleSheet(
            f"color: {colors.get('text_secondary', '#aaaaaa')}; padding: 20px;"
        )
        btn_style = f"""
            QPushButton {{
                background-color: {colors.get("panel_bg", "#2b2b2b")};
                color: {fg};
                border: 1px solid {border};
                padding: 4px 8px;
                font-size: 9pt;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {sel};
                border-color: {colors.get("accent", "#3d7eff")};
            }}
        """
        self._refresh_btn.setStyleSheet(btn_style)
        self._commit_btn.setStyleSheet(btn_style)
        self._pull_btn.setStyleSheet(btn_style)
        self._push_btn.setStyleSheet(btn_style)

    def set_root(self, path):
        self._root = path
        self.refresh()

    def refresh(self):
        self._tree.clear()
        self._info_label.hide()

        root = self._root
        if not root or not os.path.isdir(os.path.join(root, ".git")):
            self._branch_label.setText("No repository")
            self._info_label.setText("No Git repository found")
            self._info_label.show()
            return

        self._branch_label.setText(self._get_branch())
        self._populate_status()

    def _get_branch(self):
        out, _ = _run_git(self._root, "rev-parse", "--abbrev-ref", "HEAD")
        if out:
            return f"  {out}"
        return "  (no branch)"

    def _status_color(self, code):
        if not self._colors:
            return "#dcdcdc"
        c = {
            "M": self._colors.get("text", "#dcdcdc"),
            "A": "#4ec9b0",
            "D": "#f14c4c",
            "R": "#c586c0",
            "C": "#c586c0",
            "U": "#dcdcaa",
            "?": "#6a9955",
        }
        return c.get(code, "#aaaaaa")

    def _populate_status(self):
        out, _ = _run_git(self._root, "status", "--porcelain")
        if out is None:
            self._info_label.setText("Git not found in PATH")
            self._info_label.show()
            return

        lines = out.split("\n")
        if not lines or lines == [""]:
            self._info_label.setText("Working tree clean")
            self._info_label.show()
            return

        for line in lines:
            if not line.strip():
                continue
            status_code = line[:2].strip()
            filepath = line[3:]
            item = QTreeWidgetItem(self._tree, [filepath, status_code])
            item.setForeground(0, self._colors.get("text", "#dcdcdc") if self._colors else "#dcdcdc")
            item.setForeground(1, self._status_color(status_code))
            item.setToolTip(0, filepath)

    def _on_commit(self):
        QMessageBox.information(
            self, "Git Commit",
            "Commit via terminal:\n"
            "  git add .\n"
            '  git commit -m "message"'
        )

    def _on_pull(self):
        out, err = _run_git(self._root, "pull")
        if out:
            QMessageBox.information(self, "Git Pull", out)
        elif err:
            QMessageBox.warning(self, "Git Pull", err)
        self.refresh()

    def _on_push(self):
        out, err = _run_git(self._root, "push")
        if out:
            QMessageBox.information(self, "Git Push", out)
        elif err:
            QMessageBox.warning(self, "Git Push", err)
