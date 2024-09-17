import zipfile
import json
import os

class ModHandler:

    def __init__(self, config):
        self.config = config

    def install(self, package):
        with zipfile.ZipFile(package, 'r') as package:
            package_info=json.loads(package.read("manifest.json"))

            for file in package.namelist():
                match file:
                    case "CHANGELOG.md":
                        package.extract(file, os.path.join(config["lmdata_directory"], package_info["name"]))
                    case "icon.png":
                        package.extract(file, os.path.join(config["lmdata_directory"], package_info["name"]))
                    case "manifest.json":
                        package.extract(file, os.path.join(config["lmdata_directory"], package_info["name"]))
                    case "README.md":
                        package.extract(file, os.path.join(config["lmdata_directory"], package_info["name"]))
                    case _:
                        package.extract(file, self.getDestination(file))

            with open(os.path.join(config["lmdata_directory"], package_info["name"], "filelist.txt"), 'w') as change_file:
                for files in package.namelist():
                    change_file.write(f"{files}\n")

    def uninstall(self, modname):
        with open(os.path.join(config["lmdata_directory"], modname, "filelist.txt"), 'r') as change_file:
            for file in change_file:
                file = file.strip()
                match file:
                    case "CHANGELOG.md":
                        self.removeFile(os.path.join(config["lmdata_directory"], modname, file))
                    case "icon.png":
                        self.removeFile(os.path.join(config["lmdata_directory"], modname, file))
                    case "manifest.json":
                        self.removeFile(os.path.join(config["lmdata_directory"], modname, file))
                    case "README.md":
                        self.removeFile(os.path.join(config["lmdata_directory"], modname, file))
                    case _:
                        self.removeFile(os.path.join(self.getDestination(file), file))
        self.removeFile(os.path.join(config["lmdata_directory"], modname, "filelist.txt"))

    def removeFile(self, path):
        if not os.path.isdir(path):
            if os.path.exists(path):
                os.remove(path)
            else:
                print(path)


    def getDestination(self, file):
        if os.path.dirname(file):
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
#modhandler.uninstall("LethalCompanyVariables")
