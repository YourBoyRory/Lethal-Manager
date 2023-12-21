import java.io.*;
import java.util.*;
import java.util.zip.*;


public class ModInstaller {

    LCMMConfig config;

    ModInstaller(File inFile, LCMMConfig config){
        this.config = config;
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
                return new File(config.pluginsFolder, str);
            } else {
                return new File(config.bepinexFolder, str);
            }
        } else if (str.toUpperCase().startsWith("BEPINEX" + File.separator)) {
            return new File(config.gameFolder, str);
        } else {
            return new File(config.bepinexFolder, str);
        }
    }

}
