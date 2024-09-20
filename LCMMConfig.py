import configparser
import os
from pathlib import Path
import traceback

class Config:

    parser = configparser.ConfigParser()
    config_path = os.path.join(Path.home(), '.lmconfig.ini')
    config = { }

    def __init__(self):
        self.load_config()
        print(self.config)

    def load_config(self):
        try:
            self.parser['General'] = { }
            self.parser.read(self.config_path)
            self.set_game_directory(self.parser['General']["game_directory"])
            self.config["darkmode"] = self.parser['General']["darkmode"]
        except:
            print("[INFO] No valid config, creating one.")
            self.config["darkmode"] = "True"
            self.set_game_directory(self.get_platform_defaults())
            self.save_config()

    def save_config(self):
        try:
            self.parser['General']["game_directory"] = self.config["game_directory"]
            self.parser['General']["darkmode"] = self.config["darkmode"]
            with open(self.config_path, 'w') as configfile:
                self.parser.write(configfile)
            print("[INFO] Saved config")
        except:
            self.display_error("[ERROR] Config save failed. Do we have permission?")

    def set_game_directory(self, new_directory):
        self.config["game_directory"] = new_directory
        self.config["bepinex_directory"] = os.path.join(self.config["game_directory"], "BepInEx")
        self.config["plugins_directory"] = os.path.join(self.config["bepinex_directory"], "plugins")
        self.config["lmdata_directory"] = os.path.join(self.config["bepinex_directory"], "lmdata")

    def verify_files(self):
        modLoaderCore = os.path.join(self.config["bepinex_directory"], "core")
        modLoaderWinhtpp = os.path.join(self.config["game_directory"], "winhttp.dll")
        gameDirectory = os.path.join(self.config["game_directory"], "Lethal Company.exe")
        self.config["gameFound"] = False
        self.config["modloaderFound"] = False
        if os.path.isfile(gameDirectory):
            print("[INFO] Game is found.")
            self.config["gameFound"] = True
        if os.path.isdir(modLoaderCore) and os.path.isfile(modLoaderWinhtpp):
            print("[INFO] BepInEx is found.")
            self.config["modloaderFound"] = True
        return self.config["gameFound"], self.config["modloaderFound"]


    def get_platform_defaults(self):
        if os.name == "posix":  # If we are on Linux or MacOS
            return os.path.join(Path.home(), ".steam/steam/steamapps/common/Lethal Company")
        else:                   # If we are on Windows
            return "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Lethal Company"

    def display_error(self, context):
        print("\n====================================================================================")
        print(context)
        print("Ah shit, here we go again.")
        print(traceback.format_exc())
        print("Hello beta tester, You found one!")
        print("Please Report the error above: https://github.com/YourBoyRory/Lethal-Manager/issues")
        print("====================================================================================\n")
