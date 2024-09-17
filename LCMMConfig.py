import configparser
import os
from pathlib import Path

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
        except:
            print("[INFO] No valid config, creating one.")
            self.set_game_directory(self.get_platform_defaults())
            self.save_config()

    def save_config(self):
        try:
            self.parser['General']["game_directory"] = self.config["game_directory"]
            with open(self.config_path, 'w') as configfile:
                self.parser.write(configfile)
        except:
            print("[ERROR] Config save failed. Do we have permission?")

    def set_game_directory(self, new_directory):
        self.config["game_directory"] = new_directory
        self.config["bepinex_directory"] = os.path.join(self.config["game_directory"], "BepInEx")
        self.config["plugins_directory"] = os.path.join(self.config["bepinex_directory"], "plugins")
        self.config["lmdata_directory"] = os.path.join(self.config["bepinex_directory"], "lmdata")
        self.verify_files()

    def verify_files(self):
        modLoaderCore = os.path.join(self.config["bepinex_directory"], "core")
        modLoaderWinhtpp = os.path.join(self.config["game_directory"], "winhttp.dll")
        gameDirectory = os.path.join(self.config["game_directory"], "Lethal Company.exe")
        self.config["gameFound"] = False
        self.config["modloaderFound"] = False
        print(os.path.isfile(modLoaderWinhtpp), os.path.isdir(modLoaderCore))
        if os.path.isfile(gameDirectory):
            self.config["gameFound"] = True
        if os.path.isdir(modLoaderCore) and os.path.isfile(modLoaderWinhtpp):
            self.config["modloaderFound"] = True


    def get_platform_defaults(self):
        if os.name == "posix":  # If we are on Linux or MacOS
            return os.path.join(Path.home(), "/.steam/steam/steamapps/common/Lethal Company");
        else:                   # If we are on Windows
            return "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Lethal Company"




Config()
