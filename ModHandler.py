import zipfile
import json
import os
import os.path as path

class ModHandler:

    def __init__(self, config):
        self.config = config

    def install(self, package):
        with zipfile.ZipFile(package, 'r') as package:
            package_info=json.loads(package.read("manifest.json"))

            for file in package.namelist():
                if  self.in_file_blocklist(file):
                    package.extract(file, path.join(config["lmdata_directory"], package_info["name"]))
                else:
                    package.extract(file, self.get_destination(file))

            with open(path.join(config["lmdata_directory"], package_info["name"], "filelist.txt"), 'w') as change_file:
                for files in package.namelist():
                    change_file.write(f"{files}\n")

    def uninstall(self, modname):
        with open(path.join(config["lmdata_directory"], modname, "filelist.txt"), 'r') as change_file:
            for file in change_file:
                file = file.strip()
                if  self.in_file_blocklist(file):
                    self.remove_file(path.join(config["lmdata_directory"], modname, file))
                else:
                    self.remove_file(path.join(self.get_destination(file), file))
        self.remove_file(path.join(config["lmdata_directory"], modname, "filelist.txt"))

    def disable(self, modname):
        with open(path.join(config["lmdata_directory"], modname, "filelist.txt"), 'r') as change_file:
            for file in change_file:
                file = file.strip()
                if not self.in_file_blocklist(file):
                    self.move_file(path.join(self.get_destination(file), file), path.join(config["lmdata_directory"], modname, file))

    def enable(self, modname):
        with open(path.join(config["lmdata_directory"], modname, "filelist.txt"), 'r') as change_file:
            for file in change_file:
                file = file.strip()
                if not self.in_file_blocklist(file):
                    self.move_file(path.join(config["lmdata_directory"], modname, file), path.join(self.get_destination(file), file))

    def remove_file(self, file):
        if not path.isdir(file):
            if path.exists(file):
                os.remove(file)


    def move_file(self, path_old, path_new):
        if not path.isdir(path_old):
            if not path.exists(path.dirname(path_new)):
                makedirs(path.dirname(path_new))
            if path.exists(path_old):
                os.rename(path_old, path_new)

    def in_file_blocklist(self, file):
        if file == "CHANGELOG.md" or file == "icon.png" or file == "manifest.json" or file == "README.md":
            return True
        else:
            return False

    def get_destination(self, file):
        if path.dirname(file):
            if "BepInEx" in file:
                return config["game_directory"]
            else:
                return config["bepinex_directory"]
        else:
            return config["plugins_directory"]

config={
        "game_directory": "./test_env/",
        "bepinex_directory": "./test_env/BepInEx",
        "plugins_directory": "./test_env/BepInEx/plugins",
        "lmdata_directory": "./test_env/BepInEx/lmdata"
    }
modhandler = ModHandler("config")

modhandler.install("./test_env/Test.zip")
#modhandler.disable("LethalCompanyVariables")
#modhandler.enable("LethalCompanyVariables")
#modhandler.uninstall("LethalCompanyVariables")
