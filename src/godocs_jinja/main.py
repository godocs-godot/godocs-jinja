from godocs.plugin import Plugin
from godocs.cli import CLICommand


class JinjaPlugin(Plugin):

    def register(self, app: CLICommand):
        print("Plugin registered: godocs-jinja")
        pass
