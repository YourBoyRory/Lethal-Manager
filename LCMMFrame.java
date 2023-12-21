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


public class LCMMFrame extends JFrame implements ActionListener, DocumentListener, DropTargetListener {

    JLabel msgLabel;
    JList<String> listBox;
    DefaultListModel<String> list;

    // File
    DataInputStream dis;
    File myFile;

    URL url;
    InputStreamReader isr;
    String urlString;
    BufferedReader pageReader;
    JLabel loadStatus;
    File modList[];

    JPanel topPanel;
    JPanel bottomPanel;
    JPanel leftPanel;
    JPanel rightPanel;

    //Menu bar
    JMenuBar menuBar;
    JMenu optionsSubMenu;

    String verString = "Lethal Manager v0.1.0";
    boolean gameFound;
    boolean modloaderFound;

    // Locations
    String configPath = System.getProperty("user.home") + File.separator + ".lcmm.dat";
    String gameFolder;
    String bepinexFolder;
    String pluginsFolder;

    LCMMFrame(){ //Constuctor
        loadConfig();

        JPanel topPanel; // Menu

        JScrollPane listBoxScrollPane; // List

        // Button
        topPanel = new JPanel();
        bottomPanel = new JPanel();
        leftPanel = new JPanel();
        rightPanel = new JPanel();

        // Text Field

        // Top Bar
        add(topPanel, BorderLayout.NORTH);
        add(bottomPanel, BorderLayout.SOUTH);
        add(leftPanel, BorderLayout.WEST);
        add(rightPanel, BorderLayout.EAST);

        // list Box
        list = new DefaultListModel();
        listBox = new JList(list);
        listBoxScrollPane = new JScrollPane(listBox);
        add(listBoxScrollPane, BorderLayout.CENTER);

        setJMenuBar(newMenuBar());
        refreshList();

        new DropTarget(this, DnDConstants.ACTION_COPY_OR_MOVE, this);

        // Frame
        setupMainFrame();

        verifyFiles();

    } // end Constuctor

    void setupMainFrame() {
        Toolkit    tk;
        Dimension   d;

        tk = Toolkit.getDefaultToolkit();    // Toolkit subclass is platform dependent.
        d = tk.getScreenSize();              // Get screen resolution.
        setSize(300, 400);      // Set size and location based
        //pack();
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);  // kill the program if the user closes the window

        setTitle("Lethal Manager");  // For the title bar

        setVisible(true);
    } // end of setupMainFrame()

    void refreshList() {
        list.clear();
        File directory = new File(pluginsFolder);
        if (directory.isDirectory()) {
            // Get the list of files in the directory
            modList = directory.listFiles();

            // Check if there are any files in the directory
            if (modList != null) {
                // Print the names of the files in the directory

                for (File mod : modList) {
                    list.add(list.getSize(), mod.getName());
                }
            }
        }
    }

    private JMenuBar newMenuBar() {
        menuBar = new JMenuBar();

        // Edit
        optionsSubMenu = new JMenu("Options");
        optionsSubMenu.setMnemonic('O');
        optionsSubMenu.add(newItem("Install Mod", "INSTALL", this, KeyEvent.VK_I, KeyEvent.VK_I, "Install a mod."));
        optionsSubMenu.add(newItem("Refresh List", "REFRESH", this, KeyEvent.VK_R, KeyEvent.VK_R, "Refresh the mod list."));
        optionsSubMenu.add(newItem("Update BepInEx", "UPDATE", this, KeyEvent.VK_B, KeyEvent.VK_B, "Download and Install the latest BepInEx."));
        optionsSubMenu.add(newItem("Set Game Directroy", "SET", this, KeyEvent.VK_G, KeyEvent.VK_G, "Set the directroy your game and mods are installed."));
        optionsSubMenu.add(newItem("About", "ABOUT", this, KeyEvent.VK_A, KeyEvent.VK_A, "Product Infomration."));
        menuBar.add(optionsSubMenu);

        return menuBar;

    } // end newMenuBar()

    private JMenuItem newItem(String label, String actionCommand, ActionListener menuListener, int mnemonic, int keyCode, String toolTipText) {
        JMenuItem m;

        m = new JMenuItem(label, mnemonic);
        m.setAccelerator(KeyStroke.getKeyStroke(keyCode, KeyEvent.ALT_MASK));
        m.setToolTipText(toolTipText);
        m.setActionCommand(actionCommand);
        m.addActionListener(menuListener);

        return m;
    } // end newItem()

    private void handelFile(File inFile) {
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

    void saveConfig() {
        try {
            DataOutputStream configDOS = new DataOutputStream(new FileOutputStream(configPath));
            Properties propertiesFile = new Properties();

            propertiesFile.setProperty("gameFolder", gameFolder);
            propertiesFile.store(configDOS, verString);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    void loadConfig() {
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

    void setGameFolder() {

        final JFileChooser fileChooser = new JFileChooser();
        int result;

        fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        File initialDirectory = new File(gameFolder);
        fileChooser.setCurrentDirectory(initialDirectory);
        result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            // User selected a file
            java.io.File selectedFile = fileChooser.getSelectedFile();
            gameFolder = selectedFile.getAbsolutePath();
            bepinexFolder = gameFolder + File.separator + "BepInEx";
            pluginsFolder = bepinexFolder + File.separator  + "plugins";
            refreshList();
            saveConfig();
        }
        verifyFiles();
    }

    void verifyFiles() {
        File modLoaderCore = new File(bepinexFolder + File.separator + "core");
        File modLoaderWinhtpp = new File(gameFolder + File.separator + "winhttp.dll");
        File gameDirectory = new File(gameFolder + File.separator + "Lethal Company.exe");
        int result;
        gameFound = true;
        modloaderFound = true;


        if (!gameDirectory.exists()) {
            gameFound = false;
            result = JOptionPane.showInternalConfirmDialog(null, "Unable to locate game!\nPlease specify game install location.", "Warning", JOptionPane.OK_CANCEL_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                setGameFolder();
            } else {
                //System.exit(0);
            }
        } else if (!modLoaderCore.exists() || !modLoaderWinhtpp.exists()) {
            modloaderFound = false;
            result = JOptionPane.showInternalConfirmDialog(null, "BepInEx does not appear to be installed, This will be needed to run mods.\nWould you like to installed BepInEx now?", "Install BepInEx?", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                updateBepinex();
            } else {
                //System.exit(0);
            }
        }
    }

    boolean validateAction(String action) {
        int result;
        if (gameFound == false) {
            result = JOptionPane.showInternalConfirmDialog(null, "The game does not appear to be installed in the selected folder.\nAre you sure you want to attempt to " + action + " anyways?", "Warning", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                return true;
            } else {
                return false;
            }
        }
        if (modloaderFound == false && gameFound == true) {
            result = JOptionPane.showInternalConfirmDialog(null, "BepInEx does not appear to be installed.\nAre you sure you want to attempt to " + action + " anyways?", "Warning", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                return true;
            } else {
                return false;
            }
        }
        return true;
    }

    void updateBepinex() {
        String osName = System.getProperty("os.name");
        boolean modLoaderTruth = modloaderFound;
        modloaderFound = true;
        if (validateAction("install BepInEx")) {
            modloaderFound = modLoaderTruth;
            new BepinexUpdater(gameFolder);
            verifyFiles();
            if (modloaderFound == true) {
                if (osName.startsWith("Linux")) {
                    JOptionPane.showInternalMessageDialog(null, "Latest BepInEx Installed\nYou will need to add the following line to your games launch options\n\nWINEDLLOVERRIDES=\"winhttp.dll=n,b\" %command%", "BepInEx Installed", JOptionPane.INFORMATION_MESSAGE);
                } else {
                    JOptionPane.showInternalMessageDialog(null, "Latest BepInEx Installed", "BepInEx Installed", JOptionPane.INFORMATION_MESSAGE);
                }
            } else {
                JOptionPane.showInternalMessageDialog(null, "BepInEx Failed To Installed", "Warning", JOptionPane.WARNING_MESSAGE);
            }
        } else {
            modloaderFound = modLoaderTruth;
        }
    }

    //ActionListener
    public void actionPerformed(ActionEvent e) {
        switch (e.getActionCommand()) {
            case "INSTALL":
                final JFileChooser fileChooser = new JFileChooser();
                int result = fileChooser.showOpenDialog(this);
                if (result == JFileChooser.APPROVE_OPTION) {
                    if (validateAction("install the mod(s)")) {
                        // User selected a file
                        java.io.File selectedFile = fileChooser.getSelectedFile();
                        handelFile(selectedFile);
                        refreshList();
                    }
                }
                break;
            case "REFRESH":
                refreshList();
                break;
            case "UPDATE":
                updateBepinex();
                break;
            case "SET":
                setGameFolder();
                break;
            case "ABOUT":
                JOptionPane.showInternalMessageDialog(null, "\n" + verString + "\n\nRory - Progammer and UI Design\n Justin - Platfrom tester and application icon designer", "About", JOptionPane.PLAIN_MESSAGE);
                break;
        }
    }

    String getPlatformDefault() {
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

    // DocumentListener
    public void changedUpdate(DocumentEvent e) {}
    public void insertUpdate(DocumentEvent e) {}
    public void removeUpdate(DocumentEvent e) {}

    // DropTargetListener
    public void dragEnter(DropTargetDragEvent dtde) {}
    public void dragOver(DropTargetDragEvent dtde) {}
    public void dropActionChanged(DropTargetDragEvent dtde) {}
    public void dragExit(DropTargetEvent dte) {}
    public void drop(DropTargetDropEvent dtde) {
        if (validateAction("install the mod(s)")) {
            // Handle drop events
            Transferable transferable = dtde.getTransferable();

            if (transferable.isDataFlavorSupported(DataFlavor.javaFileListFlavor)) {
                dtde.acceptDrop(DnDConstants.ACTION_COPY_OR_MOVE);
                try {
                    java.util.List<File> files = (java.util.List<File>) transferable.getTransferData(DataFlavor.javaFileListFlavor);
                    for (File file : files) {
                        // Process the dropped file(s) as needed
                        handelFile(file);
                    }
                    dtde.dropComplete(true);
                } catch (Exception e) {
                    e.printStackTrace();
                    dtde.dropComplete(false);
                }
            } else {
                dtde.rejectDrop();
            }
            refreshList();
        }
    }

}
