import java.awt.*;
import javax.swing.*;
import javax.swing.event.*;
import java.awt.event.*;
import java.io.*;
import java.util.*;
import java.net.*;
import java.awt.datatransfer.*;
import java.awt.dnd.*;
import java.util.zip.*;
import java.util.zip.*;
import java.nio.file.*;

public class ModInstaller {

    String gameFolder;
    String bepinexFolder;
    String pluginsFolder;

    ModInstaller(File inFile, String gameFolder){
        this.gameFolder = gameFolder;
        bepinexFolder = gameFolder + File.separator + "BepInEx";
        pluginsFolder = bepinexFolder + File.separator  + "plugins";
        handelFile(inFile);
    }

    void handelFile(File inFile) {
        File entryDestination;

        try (ZipFile zip = new ZipFile(inFile)) {
            Enumeration<? extends ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                entryDestination = fileDestination(entry.getName());
                // Create parent directories if they do not exist
                if (!entry.isDirectory()) {
                    new File(entryDestination.getParent()).mkdirs();
                }

                if (!entry.isDirectory()) {
                    try (InputStream in = zip.getInputStream(entry);
                            OutputStream out = new FileOutputStream(entryDestination)) {
                        // Transfer bytes from the input file to the output file
                        byte[] buffer = new byte[1024];
                        int len;
                        while ((len = in.read(buffer)) > 0) {
                            out.write(buffer, 0, len);
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }
        } catch (ZipException ze) {
            entryDestination = fileDestination(inFile.getName());

            // Create the parent directories if they don't exist
            if (!entryDestination.getParentFile().exists()) {
                entryDestination.getParentFile().mkdirs();
            }

            try (InputStream inputStream = new FileInputStream(inFile);
                 OutputStream outputStream = new FileOutputStream(entryDestination)) {

                // Set up a buffer for efficient copying
                byte[] buffer = new byte[1024];
                int bytesRead;

                // Read from the input stream and write to the output stream
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, bytesRead);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    File fileDestination(String str) {
        if (!str.contains(File.separator)) {
            if (str.toUpperCase().contains(".DLL")) {
                return new File(pluginsFolder, str);
            } else {
                return new File(bepinexFolder, str);
            }
        } else if (str.toUpperCase().startsWith("BEPINEX" + File.separator)) {
            return new File(gameFolder, str);
        } else {
            return new File(bepinexFolder, str);
        }
    }

}
