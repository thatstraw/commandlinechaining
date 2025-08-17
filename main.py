import sys
import os
from pathlib import Path
from typing import Tuple, Dict, Optional

from PyQt5 import QtWidgets, uic, QtGui, QtCore


APP_NAME = "StudentPortal"
DATA_DIR = Path(__file__).parent / "data"
UI_DIR = Path(__file__).parent / "ui"
UI_FILE = UI_DIR / "main_window.ui"
CREDENTIALS_FILE = DATA_DIR / "credentials.txt"
NOTES_FILE = DATA_DIR / "notes.txt"
DATES_FILE = DATA_DIR / "dates.txt"


def ensure_data_dir() -> None:
	DATA_DIR.mkdir(parents=True, exist_ok=True)


def read_key_value_file(path: Path) -> Dict[str, str]:
	result: Dict[str, str] = {}
	if not path.exists():
		return result
	with path.open("r", encoding="utf-8") as f:
		for raw_line in f:
			line = raw_line.strip()
			if not line or line.startswith("#") or "=" not in line:
				continue
			key, value = line.split("=", 1)
			result[key.strip().lower()] = value.strip()
	return result


def write_key_value_file(path: Path, data: Dict[str, str]) -> None:
	with path.open("w", encoding="utf-8") as f:
		for key, value in data.items():
			f.write(f"{key}={value}\n")


def bootstrap_default_credentials() -> None:
	"""Create a placeholder credentials file if none exists."""
	if CREDENTIALS_FILE.exists():
		return
	ensure_data_dir()
	placeholder = {
		"username": "YOUR_SURNAME",
		"password": "YOUR_STUDENT_NUMBER",
	}
	write_key_value_file(CREDENTIALS_FILE, placeholder)


def load_credentials() -> Tuple[Optional[str], Optional[str]]:
	data = read_key_value_file(CREDENTIALS_FILE)
	username = data.get("username")
	password = data.get("password")
	return username, password


def draw_logo_pixmap(size: int = 160) -> QtGui.QPixmap:
	"""Draw a simple vector logo to avoid external image files."""
	pixmap = QtGui.QPixmap(size, size)
	pixmap.fill(QtCore.Qt.transparent)

	painter = QtGui.QPainter(pixmap)
	painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

	# Background circle with gradient
	radius = size // 2 - 6
	center = QtCore.QPoint(size // 2, size // 2)
	gradient = QtGui.QRadialGradient(center, radius)
	gradient.setColorAt(0.0, QtGui.QColor(120, 180, 255))
	gradient.setColorAt(1.0, QtGui.QColor(30, 90, 200))

	painter.setBrush(QtGui.QBrush(gradient))
	painter.setPen(QtGui.QPen(QtGui.QColor(20, 50, 120), 3))
	painter.drawEllipse(center, radius, radius)

	# Accent shape
	accent_color = QtGui.QColor(255, 255, 255, 200)
	painter.setBrush(accent_color)
	painter.setPen(QtGui.QPen(QtCore.Qt.transparent))
	accent_rect = QtCore.QRect(size // 4, size // 3, size // 2, size // 3)
	painter.drawRoundedRect(accent_rect, 16, 16)

	# App initials text
	painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
	font = QtGui.QFont("Arial", size // 7, QtGui.QFont.Bold)
	painter.setFont(font)
	painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, "SP")

	painter.end()
	return pixmap


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		uic.loadUi(str(UI_FILE), self)

		self.setWindowTitle(APP_NAME)

		# Set up runtime assets
		self._logo_pixmap = draw_logo_pixmap(size=160)
		self._connect_widgets()
		self._apply_logo_images()
		self._init_state()

	def _connect_widgets(self) -> None:
		# Login
		self.buttonLogin.clicked.connect(self.on_login_clicked)
		self.buttonCancel.clicked.connect(self.on_cancel_clicked)

		# Dashboard
		self.buttonToCalendar.clicked.connect(lambda: self._goto_page(self.pageCalendar))
		self.buttonToNotes.clicked.connect(lambda: self._goto_page(self.pageNotes))
		self.buttonLogout.clicked.connect(self.on_logout_clicked)
		self.buttonSimulateProgress.clicked.connect(self.on_simulate_progress)
		self.horizontalSlider.valueChanged.connect(self.progressBar.setValue)

		# Calendar page
		self.buttonAddDate.clicked.connect(self.on_add_date_clicked)
		self.buttonRemoveDate.clicked.connect(self.on_remove_date_clicked)
		self.buttonSaveDates.clicked.connect(self.on_save_dates_clicked)
		self.buttonLoadDates.clicked.connect(self.on_load_dates_clicked)
		self.buttonBackFromCalendar.clicked.connect(lambda: self._goto_page(self.pageDashboard))

		# Notes page
		self.buttonSaveNotes.clicked.connect(self.on_save_notes_clicked)
		self.buttonLoadNotes.clicked.connect(self.on_load_notes_clicked)
		self.buttonClearNotes.clicked.connect(self.on_clear_notes_clicked)
		self.buttonBackFromNotes.clicked.connect(lambda: self._goto_page(self.pageDashboard))

	def _apply_logo_images(self) -> None:
		for label_name in [
			"labelLogoLogin",
			"labelLogoDashboard",
			"labelLogoCalendar",
			"labelLogoNotes",
		]:
			label: QtWidgets.QLabel = getattr(self, label_name, None)
			if label is not None:
				label.setPixmap(self._logo_pixmap)
				label.setScaledContents(True)

	def _init_state(self) -> None:
		bootstrap_default_credentials()
		self._goto_page(self.pageLogin)
		self.labelLoginStatus.setText("Please enter your Surname and Student Number.")
		self.lineEditPassword.setEchoMode(QtWidgets.QLineEdit.Password)
		self.progressBar.setValue(self.horizontalSlider.value())
		self.labelWelcomeName.setText("")
		# Pre-load notes if available
		self.on_load_notes_clicked(silent=True)
		# Pre-load dates if available
		self.on_load_dates_clicked(silent=True)

	def _goto_page(self, page_widget: QtWidgets.QWidget) -> None:
		self.stackedWidget.setCurrentWidget(page_widget)

	# -------------------- Login Handlers --------------------
	def on_login_clicked(self) -> None:
		entered_username = self.lineEditUsername.text().strip()
		entered_password = self.lineEditPassword.text().strip()

		stored_username, stored_password = load_credentials()

		if not stored_username or not stored_password:
			self.labelLoginStatus.setText(
				"Credentials file missing or incomplete. A placeholder was created in data/credentials.txt. Please update it with YOUR surname and student number."
			)
			QtWidgets.QMessageBox.warning(
				self,
				"Setup required",
				"A placeholder credentials file has been created at data/credentials.txt.\n\nEdit it to set your surname and student number, then try again.",
			)
			return

		if entered_username == stored_username and entered_password == stored_password:
			self.labelLoginStatus.setText("Login successful.")
			self.labelWelcomeName.setText(f"Welcome, {entered_username}!")
			self._goto_page(self.pageDashboard)
		else:
			self.labelLoginStatus.setText("Invalid username or password. Please try again.")
			QtWidgets.QMessageBox.critical(self, "Login failed", "Invalid username or password.")

	def on_cancel_clicked(self) -> None:
		self.close()

	def on_logout_clicked(self) -> None:
		self.lineEditUsername.clear()
		self.lineEditPassword.clear()
		self.labelLoginStatus.setText("Logged out. Enter credentials to log in again.")
		self._goto_page(self.pageLogin)

	# -------------------- Dashboard Handlers --------------------
	def on_simulate_progress(self) -> None:
		# Simple progress animation using a QTimer
		start_value = self.progressBar.value()
		end_value = 100 if start_value < 100 else 0
		self._animate_progress(start_value, end_value)

	def _animate_progress(self, start: int, end: int) -> None:
		self._progress_anim_timer = QtCore.QTimer(self)
		self._progress_anim_timer.setInterval(15)

		step = 1 if end > start else -1
		current = start

		def tick() -> None:
			nonlocal current
			current += step
			self.progressBar.setValue(current)
			self.horizontalSlider.blockSignals(True)
			self.horizontalSlider.setValue(current)
			self.horizontalSlider.blockSignals(False)
			if current == end:
				self._progress_anim_timer.stop()

		self._progress_anim_timer.timeout.connect(tick)
		self._progress_anim_timer.start()

	# -------------------- Calendar Handlers --------------------
	def on_add_date_clicked(self) -> None:
		qdate: QtCore.QDate = self.calendarWidget.selectedDate()
		date_str = qdate.toString("yyyy-MM-dd")
		# Avoid duplicates
		for i in range(self.listWidgetDates.count()):
			if self.listWidgetDates.item(i).text() == date_str:
				return
		self.listWidgetDates.addItem(date_str)

	def on_remove_date_clicked(self) -> None:
		row = self.listWidgetDates.currentRow()
		if row >= 0:
			self.listWidgetDates.takeItem(row)

	def on_save_dates_clicked(self, silent: bool = False) -> None:
		ensure_data_dir()
		lines = []
		for i in range(self.listWidgetDates.count()):
			lines.append(self.listWidgetDates.item(i).text())
		with DATES_FILE.open("w", encoding="utf-8") as f:
			f.write("\n".join(lines))
		if not silent:
			QtWidgets.QMessageBox.information(self, "Saved", f"Saved {len(lines)} date(s) to {DATES_FILE}.")

	def on_load_dates_clicked(self, silent: bool = False) -> None:
		self.listWidgetDates.clear()
		if not DATES_FILE.exists():
			return
		with DATES_FILE.open("r", encoding="utf-8") as f:
			for raw in f:
				date_str = raw.strip()
				if date_str:
					self.listWidgetDates.addItem(date_str)
		if not silent:
			QtWidgets.QMessageBox.information(self, "Loaded", f"Loaded dates from {DATES_FILE}.")

	# -------------------- Notes Handlers --------------------
	def on_save_notes_clicked(self, silent: bool = False) -> None:
		ensure_data_dir()
		text = self.textEditNotes.toPlainText()
		with NOTES_FILE.open("w", encoding="utf-8") as f:
			f.write(text)
		if not silent:
			QtWidgets.QMessageBox.information(self, "Saved", f"Notes saved to {NOTES_FILE}.")

	def on_load_notes_clicked(self, silent: bool = False) -> None:
		if not NOTES_FILE.exists():
			return
		with NOTES_FILE.open("r", encoding="utf-8") as f:
			self.textEditNotes.setPlainText(f.read())
		if not silent:
			QtWidgets.QMessageBox.information(self, "Loaded", f"Notes loaded from {NOTES_FILE}.")

	def on_clear_notes_clicked(self) -> None:
		self.textEditNotes.clear()



def run(smoke_test: bool = False) -> int:
	# For headless smoke-test environments, allow offscreen
	if smoke_test and os.environ.get("QT_QPA_PLATFORM") is None:
		os.environ["QT_QPA_PLATFORM"] = "offscreen"

	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	if smoke_test:
		# Do not show the window in smoke test
		return 0
	window.show()
	return app.exec_()


if __name__ == "__main__":
	is_smoke = "--smoke-test" in sys.argv
	sys.exit(run(smoke_test=is_smoke))