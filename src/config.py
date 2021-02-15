from calibre.utils.config import JSONConfig
from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit

prefs = JSONConfig('plugins/readwise')
prefs.defaults['access_token'] = ''

class ConfigWidget(QWidget):
  def __init__(self):
    QWidget.__init__(self)
    self.l = QHBoxLayout()
    self.setLayout(self.l)

    self.label = QLabel('Access &token:')
    self.l.addWidget(self.label)
    self.at = QLineEdit(self)
    self.at.setEchoMode(QLineEdit.Password)
    self.at.setText(prefs['access_token'])
    self.l.addWidget(self.at)
    self.label.setBuddy(self.at)
    self.access_token_link_label = QLabel('<a href="https://readwise.io/access_token">Get access token</a>')
    self.access_token_link_label.setOpenExternalLinks(True)
    self.l.addWidget(self.access_token_link_label)

  def save_settings(self):
    prefs['access_token'] = self.at.text()
