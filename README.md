## StudentPortal - 4 Page Qt App

This project implements a 4-page GUI built with Qt Designer and PyQt5:

- Login screen (Username = your surname, Password = your student number)
- Dashboard (basic controls and navigation)
- Calendar page (select dates and save/load via files)
- Notes page (edit notes and save/load via files)

A simple graphic logo is generated programmatically and displayed on each page.

### Requirements

- Python 3.8+
- PyQt5

Install dependencies:

```bash
pip install -r requirements.txt
```

### First Run and Credentials

On first run, the app creates a placeholder file at `data/credentials.txt`:

```
username=YOUR_SURNAME
password=YOUR_STUDENT_NUMBER
```

Edit this file to set YOUR surname and YOUR student number. Using any other student's details may cause penalties per your brief.

### Run the App

```bash
python main.py
```

If you are in a headless environment and want to verify that the UI loads, you can run a smoke test:

```bash
QT_QPA_PLATFORM=offscreen python main.py --smoke-test
```

### Files Used (Traditional File Handling)

- `data/credentials.txt` — stores the login credentials
- `data/notes.txt` — stores your notes
- `data/dates.txt` — stores selected calendar dates (one per line, YYYY-MM-DD)

### Structure

- `ui/main_window.ui` — Qt Designer UI (4 pages via `QStackedWidget`)
- `main.py` — Python logic that loads the `.ui` file and wires up all functionality
- `data/` — files created by the app for storage

### Notes

- Keep the login credentials as your own surname and student number as required.
- Buttons on all pages are wired and functional.