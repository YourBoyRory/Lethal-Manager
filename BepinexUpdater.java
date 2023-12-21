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

public class BepinexUpdater {

    String gameFolder;

    BepinexUpdater(String gameFolder){
        this.gameFolder = gameFolder;
        String latestURL = getLatestURL();
        downloadFile(latestURL, gameFolder +  File.separator + "BepInEx.zip");
        File latestFile = new File(gameFolder +  File.separator + "BepInEx.zip");
        install(latestFile);
    }

    String getLatestURL() {
        try {
            URL url = new URL("https://api.github.com/repos/BepInEx/BepInEx/releases/latest");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            InputStream inputStream = connection.getInputStream();
            Scanner scanner = new Scanner(inputStream).useDelimiter("\\A");
            String responseBody = scanner.hasNext() ? scanner.next() : "";

            String[] lines = responseBody.split(",");

            for (String line : lines) {
                if (line.contains("browser_download_url")) {
                    if (line.contains("x64")) {
                        return line.split(":",2)[1].trim().replaceAll("\"", "").replaceAll("}", "");
                    }
                }
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    void downloadFile(String fileUrl, String fileDestination) {
        try {
            URL url = new URL(fileUrl);
            try (InputStream in = url.openStream()) {
                Path destination = Path.of(fileDestination);
                Files.copy(in, destination, StandardCopyOption.REPLACE_EXISTING);
            }
        } catch (Exception e) {
            //e.printStackTrace();
        }
    }

    void install(File inFile) {
        File entryDestination;
        String outputFolder = inFile.getParent();

        try (ZipFile zip = new ZipFile(inFile)) {
            Enumeration<? extends ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                entryDestination = new File(outputFolder, entry.getName());
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
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
