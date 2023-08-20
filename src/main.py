from calibre_plugins.readwise.config import prefs
from PyQt5.Qt import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
import urllib.request
import json

class ReadwiseDialog(QDialog):
  def __init__(self, gui, icon, do_user_config):
    QDialog.__init__(self, gui)
    self.gui = gui
    self.do_user_config = do_user_config

    self.db = gui.current_db

    self.l = QVBoxLayout()
    self.setLayout(self.l)

    self.setWindowTitle('Readwise')
    self.setWindowIcon(icon)

    self.about_button = QPushButton('&About', self)
    self.about_button.clicked.connect(self.about)
    self.l.addWidget(self.about_button)

    self.sync_button = QPushButton(
        '&Export to Readwise', self)
    self.sync_button.clicked.connect(self.sync)
    self.l.addWidget(self.sync_button)

    self.conf_button = QPushButton(
            '&Configure this plugin', self)
    self.conf_button.clicked.connect(self.config)
    self.l.addWidget(self.conf_button)

    self.resize(self.sizeHint())
    self.update_button_state()

  def about(self):
    text = get_resources('about.txt')
    QMessageBox.about(self, 'About the Readwise plugin',
            text.decode('utf-8'))

  def sync(self):
    db = self.db.new_api

    books = {}
    for annotation in db.all_annotations(None, None, 'highlight', True, None):
      books.setdefault(annotation['book_id'], []).append(annotation)

    if len(books) == 0:
      QMessageBox.information(self, "Readwise", "There are no highlights to export.")
      return

    body = {
      'highlights': []
    }
    for book_id, annotations in books.items():
      metadata = db.get_metadata(book_id)
      for annotation in annotations:
        highlight = {
          'text': annotation['annotation']['highlighted_text'],
          'title': metadata.title,
          'author': metadata.authors[0],
          'source_type': 'book',
          'note': annotation['annotation'].get('notes', None),
          'highlighted_at': annotation['annotation']['timestamp']
        }
        body['highlights'].append(highlight)

    headers = {
      'Authorization': f"Token {prefs['access_token']}",
      'Content-Type': 'application/json',
      'User-Agent': 'Calibre.app',
    }

    request = urllib.request.Request(
      'https://readwise.io/api/v2/highlights/',
      headers=headers,
      method="POST",
      data=json.dumps(body).encode('utf-8')
    )

    try:
      if self.gui:
        self.gui.status_bar.showMessage('Exporting to Readwise...')

      response = urllib.request.urlopen(request)
      QMessageBox.information(self, "Readwise", "Export completed successfully.")


    except urllib.error.HTTPError as e:
      if e.code == 401:
        QMessageBox.critical(self, "Readwise", "Export failed due to incorrect access token. Please update the access token and try again.")
      else:
        QMessageBox.critical(self, "Readwise", f"Export failed with status code: {e.code}")

    except urllib.error.URLError as e:
        QMessageBox.critical(self, "Readwise", f"Export failed with reason: {e.reason}")

    finally:
      if self.gui:
        self.gui.status_bar.clearMessage()

  def config(self):
    self.do_user_config(parent=self)
    self.update_button_state()

  def update_button_state(self):
    self.sync_button.setEnabled(len(prefs['access_token']) > 0)
