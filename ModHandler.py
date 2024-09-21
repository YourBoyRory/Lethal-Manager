import zipfile
import json
import os
import os.path as path
import traceback

class ModHandler:

    mod_list = { }
    mod_count=0

    def __init__(self, config):
        self.config = config
        self.compile_modlist()

    def install(self, package):
        old_version = None
        try:
            with zipfile.ZipFile(package, 'r') as package:
                package_info=json.loads(package.read("manifest.json"))
                if self.is_installed(package_info["name"]):
                    package_name = package_info["name"]
                    print(f"[INFO] {package_name} already installed. updating...")
                    old_version = self.mod_list[package_info["name"]]["version_number"]
                    self.uninstall(package_info["name"])
                for file in package.namelist():
                    if  self.in_file_blocklist(file):
                        package.extract(file, path.join(self.config["lmdata_directory"], package_info["name"]))
                    else:
                        package.extract(file, self.get_destination(file))
                with open(path.join(self.config["lmdata_directory"], package_info["name"], "filelist.txt"), 'w') as change_file:
                    for files in package.namelist():
                        change_file.write(f"{files}\n")
            package_name = package_info["name"]
            print(f"[INFO] {package_name} Installed.")
            self.compile_modlist()
            return package_info["name"], old_version
        except:
            self.display_error(f"[ERROR] Mod at {package} not Installed, possibly malformed.")
            return None, None

    def uninstall(self, modname):
        if self.is_installed(modname):
            if not self.is_enabled(modname):
                self.enable(modname)
            with open(path.join(self.config["lmdata_directory"], modname, "filelist.txt"), 'r') as change_file:
                for file in change_file:
                    file = file.strip()
                    if  self.in_file_blocklist(file):
                        self.remove_file(path.join(self.config["lmdata_directory"], modname, file))
                    else:
                        self.remove_file(path.join(self.get_destination(file), file))
            self.remove_file(path.join(self.config["lmdata_directory"], modname, "filelist.txt"))
            print(f"[INFO] {modname} Uninstalled.")
            self.compile_modlist()
            return True
        else:
            print(f"[INFO] Nothing to do. {modname} not installed.")
            return False

    def disable(self, modname):
        if self.is_enabled(modname):
            with open(path.join(self.config["lmdata_directory"], modname, "filelist.txt"), 'r') as change_file:
                for file in change_file:
                    file = file.strip()
                    if not self.in_file_blocklist(file):
                        self.move_file(path.join(self.get_destination(file), file), path.join(self.config["lmdata_directory"], modname, file))
            open(path.join(self.config["lmdata_directory"], modname, ".disabled"), 'a')
            print(f"[INFO] {modname} Disabled.")
            self.compile_modlist()
            return True
        else:
            print(f"[INFO] Nothing to do. {modname} already disabled.")
            return False

    def enable(self, modname):
        if not self.is_enabled(modname):
            with open(path.join(self.config["lmdata_directory"], modname, "filelist.txt"), 'r') as change_file:
                for file in change_file:
                    file = file.strip()
                    if not self.in_file_blocklist(file):
                        self.move_file(path.join(self.config["lmdata_directory"], modname, file), path.join(self.get_destination(file), file))
            self.remove_file(path.join(self.config["lmdata_directory"], modname, ".disabled"))
            print(f"[INFO] {modname} Enabled.")
            self.compile_modlist()
            return True
        else:
            print(f"[INFO] Nothing to do. {modname} already enabled.")
            return False

    def compile_modlist(self):
        self.mod_list.clear()
        try:
            for file in os.listdir(self.config["lmdata_directory"]):
                if self.is_installed(file):
                    with open(path.join(self.config["lmdata_directory"], file, "manifest.json"), 'r') as manifest:
                        manifest = json.load(manifest)
                    self.mod_list[file] = manifest
        except:
            print(f"[INFO] No Mods Found.")
        print(f"[INFO] Rebuilt Modlist")
        self.show_modlist()

    def remove_file(self, file):
        if not path.isdir(file):
            if path.exists(file):
                os.remove(file)

    def move_file(self, path_old, path_new):
        if not path.isdir(path_old):
            if not path.exists(path.dirname(path_new)):
                os.makedirs(path.dirname(path_new))
            if path.exists(path_old):
                os.rename(path_old, path_new)

    def get_needed_dependencies(self, modname):
        needed_dependency = []
        needed_enabled = []
        temp = [0]
        with open(path.join(self.config["lmdata_directory"], modname, "manifest.json"), 'r') as manifest:
            manifest = json.load(manifest)
        for dependency in manifest["dependencies"]:
            curr_dependency = dependency[dependency.find('-')+1:dependency.rfind('-')]
            if curr_dependency != "BepInExPack":
                temp[0] = dependency
                if not self.is_installed(curr_dependency):
                    needed_dependency += temp
                elif not self.is_enabled(curr_dependency):
                    needed_enabled += temp
        return needed_dependency, needed_enabled
        
    def check_if_dependent(self, mod, dependent_mod):
        with open(path.join(self.config["lmdata_directory"], dependent_mod, "manifest.json"), 'r') as manifest:
            manifest = json.load(manifest)
        for dependency in manifest["dependencies"]:
            curr_dependency = dependency[dependency.find('-')+1:dependency.rfind('-')]
            if curr_dependency == mod:
                return True
        return False

    def is_installed(self, modname):
        return path.exists(path.join(self.config["lmdata_directory"], modname, "manifest.json"))

    def is_enabled(self, modname):
        return not path.exists(path.join(self.config["lmdata_directory"], modname, ".disabled"))

    def in_file_blocklist(self, file):
        if file == "CHANGELOG.md" or file == "icon.png" or file == "manifest.json" or file == "README.md":
            return True
        else:
            return False

    def show_modlist(self):
        for key, pair in self.mod_list.items():
            print (key)
            for name, items in pair .items():
                print (f"    {name}: {items}")

    def get_destination(self, file):
        if path.dirname(file):
            if "BepInEx" in file:
                return self.config["game_directory"]
            else:
                return self.config["bepinex_directory"]
        else:
            return self.config["plugins_directory"]


    def display_error(self, context):
        print("\n====================================================================================")
        print(context)
        print("Ah shit, here we go again.")
        print(traceback.format_exc())
        print("Hello beta tester, You found one!")
        print("Please Report the error above: https://github.com/YourBoyRory/Lethal-Manager/issues")
        print("====================================================================================\n")
