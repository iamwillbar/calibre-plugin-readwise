from calibre.customize import InterfaceActionBase

class ReadwisePlugin(InterfaceActionBase):
  name = 'Readwise'
  description = 'Export highlights to Readwise'
  supported_platforms = ['windows', 'osx', 'linux']
  author = 'William Bartholomew'
  version = (0, 1, 2)
  minimum_calibre_version = (5, 0, 1)
  actual_plugin = 'calibre_plugins.readwise.ui:InterfacePlugin'

  def is_customizable(self):
    return True

  def config_widget(self):
    from calibre_plugins.readwise.config import ConfigWidget
    return ConfigWidget()
  
  def save_settings(self, config_widget):
    config_widget.save_settings()
    ac = self.actual_plugin_
    if ac is not None:
      ac.apply_settings()
