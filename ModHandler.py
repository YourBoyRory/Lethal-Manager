from urllib.request import urlretrieve
import requests
import zipfile

class ModHandler:

    def __init__(self, config):
        self.config = config

    def install(self, package):
        try:
            with zipfile.ZipFile(package, 'r') as package:
                for files in package.namelist():
                    print(files)
            print("[INFO] Mod Package Installed.")
            return True
        except:
            print("[ERROR] Install Failed.")
            return False

    def uninstall(self, package):
        print("TODO")

modhandler = ModHandler("Dummy")

modhandler.install("./test_env/BepinEx.zip")
