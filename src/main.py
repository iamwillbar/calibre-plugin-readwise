from calibre_plugins.readwise.config import prefs
from PyQt5.Qt import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
import urllib.request
from urllib.parse import quote
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
    library_id = getattr(db, 'server_library_id', None)
    library_id = '_hex_-' + library_id.encode('utf-8').hex()
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
        link_prefix = f'calibre://view-book/{library_id}/{book_id}/{annotation["format"]}?open_at='
        spine_index = (1 + annotation['annotation']['spine_index']) * 2
        cfi = annotation['annotation']['start_cfi']
        link = (link_prefix + quote(f'epubcfi(/{spine_index}{cfi})')).replace(')', '%29')
        highlight = {
          'text': annotation['annotation']['highlighted_text'],
          'title': metadata.title,
          'author': metadata.authors[0],
          'source_type': 'book',
          'note': annotation['annotation'].get('notes', None),
          'highlighted_at': annotation['annotation']['timestamp'],
          'location_type': 'location',
          'location': annotation['id'],
          'highlight_url': link
        }

        body['highlights'].append(highlight)

    headers = {
      'Authorization': f"Token {prefs['access_token']}",
      'Content-Type': 'application/json'
    }
    request = urllib.request.Request('https://readwise.io/api/v2/highlights/', json.dumps(body).encode('utf-8'), headers = headers)

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
