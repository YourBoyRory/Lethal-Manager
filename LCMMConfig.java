import javax.swing.*;
import java.io.*;
import java.util.*;

public class LCMMConfig {

    public String configPath = System.getProperty("user.home") + File.separator + ".lcmm.dat";
    public String gameFolder;
    public String bepinexFolder;
    public String pluginsFolder;

    public boolean gameFound;
    public boolean modloaderFound;

    LCMMConfig(){
        loadConfig();
    }

    public void saveConfig() {
        try {
            DataOutputStream configDOS = new DataOutputStream(new FileOutputStream(configPath));
            Properties propertiesFile = new Properties();
            propertiesFile.setProperty("gameFolder", gameFolder);
            propertiesFile.store(configDOS, LCMM.VERSION_STRING);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void loadConfig() {
        try {
            DataInputStream configDIS = new DataInputStream(new FileInputStream(configPath)); // makes a dis using the passed file
            Properties propertiesFile = new Properties();
            propertiesFile.load(configDIS);
            gameFolder = propertiesFile.getProperty("gameFolder");
        } catch (IOException ioe) {
            gameFolder = getPlatformDefault();
            saveConfig();
        }
        bepinexFolder = gameFolder + File.separator + "BepInEx";
        pluginsFolder = bepinexFolder + File.separator  + "plugins";
    }

    public void setGameFolder(File newGameFolder) {
        gameFolder = newGameFolder.getAbsolutePath();
        bepinexFolder = gameFolder + File.separator + "BepInEx";
        pluginsFolder = bepinexFolder + File.separator  + "plugins";
        saveConfig();
    }

    public void verifyFiles() {
        File modLoaderCore = new File(bepinexFolder + File.separator + "core");
        File modLoaderWinhtpp = new File(gameFolder + File.separator + "winhttp.dll");
        File gameDirectory = new File(gameFolder + File.separator + "Lethal Company.exe");
        int result;
        gameFound = true;
        modloaderFound = true;
        if (!gameDirectory.exists()) {
            gameFound = false;
        } else if (!modLoaderCore.exists() || !modLoaderWinhtpp.exists()) {
            modloaderFound = false;
        }
    }

    public boolean validateAction(String action) {
        int result;
        if (gameFound == false) {
            result = JOptionPane.showInternalConfirmDialog(null, "The game does not appear to be installed in the selected folder.\nAre you sure you want to attempt to " + action + " anyways?", "Warning", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                return true;
            } else {
                return false;
            }
        } else if (modloaderFound == false) {
            result = JOptionPane.showInternalConfirmDialog(null, "BepInEx does not appear to be installed.\nAre you sure you want to attempt to " + action + " anyways?", "Warning", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                return true;
            } else {
                return false;
            }
        }
        return true;
    }

    private String getPlatformDefault() {
        String osName = System.getProperty("os.name");
        // You can perform further actions based on the detected OS
        if (osName.startsWith("Windows")) {
            return "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Lethal Company";
        } else if (osName.startsWith("Linux")) {
            return System.getProperty("user.home") + "/.steam/steam/steamapps/common/Lethal Company";
        } else {
            return null;
        }
    }

}
