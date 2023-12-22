import java.io.*;
import java.util.*;
import java.util.zip.*;
import java.nio.file.*;


public class ModHandler {

    LCMMConfig config;

    ModHandler(LCMMConfig config){
        this.config = config;
    }

    void install(File inFile) {
        File entryDestination;

        try (ZipFile zip = new ZipFile(inFile)) {
            Enumeration<? extends ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                entryDestination = getDestination(entry.getName());
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
                        e.getMessage();
                    }
                }
            }
        } catch (ZipException ze) {
            entryDestination = getDestination(inFile.getName());

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
                e.getMessage();
            }
        } catch (Exception e) {
            e.getMessage();
        }
    }

    void uninstall(String modName) {
        Path path = Paths.get(config.pluginsFolder + File.separator + modName);
        try {
            Files.delete(path);
        } catch (IOException ioe) {
            ioe.getMessage();
        }
    }

    File getDestination(String str) {
        if (str.contains("/") || str.contains("\\")) {
            if (str.trim().toUpperCase().startsWith("BEPINEX")) {
                return new File(config.gameFolder, str);
            } else {
                return new File(config.bepinexFolder, str);
            }
        } else {
            if (str.trim().toUpperCase().endsWith(".DLL")) {
                return new File(config.pluginsFolder, str);
            } else {
                return new File(config.bepinexFolder, str);
            }
        }


    }

}
