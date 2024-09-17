from urllib.request import urlretrieve
import requests
import zipfile
import os

class BepinexUpdater:

    def __init__(self, config):
        package_directory = os.path.join(config['game_directory'], "BepinEx.zip")
        url = self.getLatestURL()
        if url is not None:
            if self.downloadFile(url, package_directory):
                self.install(package_directory, config['game_directory'])

    def getLatestURL(self):
        try:
            response = requests.get("https://api.github.com/repos/BepInEx/BepInEx/releases/latest").json()
            print("[INFO] Connected to Github API.")
            for packages in response["assets"]:
                if "win_x64" in packages["browser_download_url"]:
                    return packages["browser_download_url"]
            print("[WARN] Could not find package match, guessing from avalible packages...")
            return response["assets"][4]["browser_download_url"]
        except:
            print("[ERROR] API Call Failed, Update Aborted.")
            return None

    def downloadFile(self, url, destination):
        try:
            urlretrieve(url, destination)
            print("[INFO] Downloaded BepinEx Package.")
            return True
        except:
            print("[ERROR] Download Failed, Update Aborted.")
            return False

    def install(self, package, destination):
        try:
            with zipfile.ZipFile(package, 'r') as package:
                package.extractall(destination)
            print("[INFO] Installed BepinEx Package.")
            return True
        except:
            print("[ERROR] Install Failed, Update Aborted.")
            return False

config={"game_directory": "./test_env/"}
BepinexUpdater(config)
