
from ModHandler import ModHandler
from BepinexUpdater import BepinexUpdater
from LCMMConfig import Config

# Unit Test

config = Config()
for key, pair in config.config.items():
    print(f"[INFO] {key}: {pair}")

# Unit Test
test_package="./test_env/Test.zip"
tast_name="R2API"

config={
    "game_directory": "./test_env/",
    "bepinex_directory": "./test_env/BepInEx",
    "plugins_directory": "./test_env/BepInEx/plugins",
    "lmdata_directory": "./test_env/BepInEx/lmdata"
}
modhandler = ModHandler("config")

modhandler.install(test_package)
x,y = modhandler.get_needed_dependencies(tast_name)
if x:
    print(f"[INFO] Dependencies Needed for {tast_name}.")
if y:
    print(f"[INFO] Dependencies for {tast_name} are Disbaled.")
modhandler.disable(tast_name)
modhandler.disable(tast_name)
modhandler.enable(tast_name)
modhandler.enable(tast_name)
modhandler.uninstall(tast_name)
modhandler.uninstall(tast_name)
    
# Unit test

config={
    "game_directory": "./test_env/",
    "bepinex_directory": "./test_env/BepInEx",
    "plugins_directory": "./test_env/BepInEx/plugins",
    "lmdata_directory": "./test_env/BepInEx/lmdata"
}
test = BepinexUpdater(config)

print("[INFO] Start Failure tests")

test.getLatestURL(None)
test.downloadFile(None, None)
test.install(None, None)
