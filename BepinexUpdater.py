from urllib.request import urlretrieve
from PyQt5.QtWidgets import QMessageBox
import requests
import zipfile
import os
import traceback

class BepinexUpdater:

    def __init__(self, parent, config):
        self.config = config
        package_directory = os.path.join(self.config.config['game_directory'], "BepinEx.zip")
        url, version = self.getLatestURL("https://api.github.com/repos/BepInEx/BepInEx/releases/latest")
        if url is not None:
            if self.downloadFile(url, package_directory):
                status = self.install(package_directory, self.config.config['game_directory'])
                if status:
                    if self.config.config["modloaderFound"]:
                        if self.config.config['bepinex_version'] == version:
                            msg = self.make_popup_window(parent, QMessageBox.Information, "BepInEx Updated", f"BepInEx updated.", f"{self.config.config['bepinex_version']} -> {version}")
                            self.config.config['bepinex_version'] = version
                            self.config.save_config()
                        else:
                            msg = self.make_popup_window(parent, QMessageBox.Information, "BepInEx Updated", f"BepInEx was up to date.", f"{version} Reinstalled ")
                    else:
                        msg = self.make_popup_window(parent, QMessageBox.Information, "BepInEx Installed", f"BepInEx {version} Installed", "")
                        self.config.config['bepinex_version'] = version
                        self.config.save_config()
                else:
                    # Could not install BepInEx, Permissions maybe?
                    msg = self.make_popup_window(parent, QMessageBox.Critical, "BepInEx Updater Error", "BepInEx Failed during installation.", "Failed while extracting BepInEx package.\nCheck that the game folder is correct and you have permissions.")
            else:
                # Could not download file
                msg = self.make_popup_window(parent, QMessageBox.Critical, "BepInEx Updater Error", "Failed to download BepInEx package.", "We connected to the API, but the package download failed.\nContact me on Github and ensure that the game folder is correct and you have permissions.\n\nhttps://github.com/YourBoyRory")
        else:
            msg = self.make_popup_window(parent, QMessageBox.Critical, "BepInEx Updater Error", "Failed to connect to the Github API", "Please check that you have internet and try again.")
        msg.exec()


    def getLatestURL(self, url):
        try:
            response = requests.get(url).json()
            print("[INFO] Connected to Github API.")
            for packages in response["assets"]:
                if "win_x64" in packages["browser_download_url"]:
                    return packages["browser_download_url"], response["tag_name"]
            print("[WARN] Could not find package match, guessing from avalible packages...")
            return response["assets"][4]["browser_download_url"], response["tag_name"]
        except:
            self.display_error("[ERROR] API Call Failed, Update Aborted.")
            return None, None

    def downloadFile(self, url, destination):
        try:
            urlretrieve(url, destination)
            print("[INFO] Downloaded BepinEx Package.")
            return True
        except:
            self.display_error("[ERROR] Download Failed, Update Aborted.")
            return False

    def install(self, package, destination):
        try:
            with zipfile.ZipFile(package, 'r') as package:
                package.extractall(destination)
            print("[INFO] Installed BepinEx Package.")
            return True
        except:
            self.display_error("[ERROR] Install Failed, Update Aborted.")
            return False

    def make_popup_window(self, parent, mtype, title, top_text, bottom_text):
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        if mtype is not None:
            msg.setIcon(mtype)
        msg.setText(top_text)
        msg.setInformativeText(bottom_text)
        msg.setStyleSheet("""
            QLabel {
                min-width:500 px;
                font-size: 12pt;
            }
        """)
        return msg

    def display_error(self, context):
        print("\n====================================================================================")
        print(context)
        print("Ah shit, here we go again.")
        print(traceback.format_exc())
        print("Hello beta tester, You found one!")
        print("Please Report the error above: https://github.com/YourBoyRory/Lethal-Manager/issues")
        print("====================================================================================\n")
