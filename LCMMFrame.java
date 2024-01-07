import java.awt.*;
import javax.swing.*;
import javax.swing.event.*;
import java.awt.event.*;
import java.io.*;
import java.util.*;
import java.awt.datatransfer.*;
import java.awt.dnd.*;
import java.net.*;

public class LCMMFrame extends JFrame implements MouseListener, ActionListener, DocumentListener, DropTargetListener {

    JLabel msgLabel;
    JList<String> listBox;
    DefaultListModel<String> list;

    LCMMConfig config;
    ModHandler modHandler;

    // File
    DataInputStream dis;
    File myFile;

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
    JMenu editSubMenu;
    JMenu optionsSubMenu;
    JMenu helpSubMenu;

    LCMMFrame(){ //Constuctor
        config = new LCMMConfig();
        modHandler = new ModHandler(config);
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
        listBox.addMouseListener(this);
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

        ImageIcon icon = new ImageIcon(LCMM.class.getClassLoader().getResource("icon.png"));
        this.setIconImage(icon.getImage());

        setVisible(true);
    } // end of setupMainFrame()

    void refreshList() {
        list.clear();
        File directory = new File(config.pluginsFolder);
        if (directory.isDirectory()) {
            // Get the list of files in the directory
            modList = directory.listFiles();

            // Check if there are any files in the directory
            if (modList != null) {
                // Print the names of the files in the directory

                for (File mod : modList) {
                    if (mod.getName().trim().toUpperCase().endsWith(".DLL")) {
                        //String modNameTrimmed = mod.getName().substring(0, mod.getName().lastIndexOf("."));
                        list.add(list.getSize(), mod.getName());
                    }
                }
            }
        }
    }

    private void openContextMenu(int Xcord, int Ycord) {
        JPopupMenu popup;
        JMenuItem item;

        popup = new JPopupMenu();
        item = new JMenuItem("Uninstall " + listBox.getSelectedValue());
        item.addActionListener(this);
        item.setActionCommand("UNINSTALL");
        popup.add(item);
        popup.show(this, Xcord, Ycord);
    }

    private JMenuBar newMenuBar() {
        menuBar = new JMenuBar();

        editSubMenu = new JMenu("Edit");
        editSubMenu.setMnemonic('E');
        editSubMenu.add(newItem("Install Mod", "INSTALL", this, KeyEvent.VK_I, KeyEvent.VK_I, "Install a mod."));
        editSubMenu.add(newItem("Uninstall Mod", "UNINSTALL", this, KeyEvent.VK_U, KeyEvent.VK_U, "Uninstall selected mod."));
        editSubMenu.add(newItem("Refresh List", "REFRESH", this, KeyEvent.VK_R, KeyEvent.VK_R, "Refresh the mod list."));
        menuBar.add(editSubMenu);

        // Edit
        optionsSubMenu = new JMenu("Options");
        optionsSubMenu.setMnemonic('O');
        optionsSubMenu.add(newItem("Update BepInEx", "UPDATE", this, KeyEvent.VK_B, KeyEvent.VK_B, "Download and Install the latest BepInEx."));
        optionsSubMenu.add(newItem("Open Game Directroy", "OPEN", this, KeyEvent.VK_O, KeyEvent.VK_O, "Open the directroy your game and mods are installed."));
        optionsSubMenu.add(newItem("Set Game Directroy", "SET", this, KeyEvent.VK_G, KeyEvent.VK_G, "Set the directroy your game and mods are installed."));
        menuBar.add(optionsSubMenu);

        helpSubMenu = new JMenu("Help");
        helpSubMenu.setMnemonic('H');
        helpSubMenu.add(newItem("Download Mods", "DOWNLOAD", this, KeyEvent.VK_D, KeyEvent.VK_D, "Download mods from thunderstore.io"));
        helpSubMenu.add(newItem("Troubleshooting", "TROUBLE", this, KeyEvent.VK_T, KeyEvent.VK_T, "Common issues and how to fix them"));
        helpSubMenu.add(newItem("About", "ABOUT", this, KeyEvent.VK_A, KeyEvent.VK_A, "Product Infomration."));
        menuBar.add(helpSubMenu);

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

    // This is a gross function do not look at this function.
    // There definitely a better way to do this but this is my way.
    // And my way is special :)
    void updateBepinex() {
        String osName = System.getProperty("os.name");
        boolean modLoaderTruth = config.modloaderFound;
        config.modloaderFound = true;
        if (validateAction("install BepInEx")) {
            config.modloaderFound = modLoaderTruth;
            new BepinexUpdater(config);
            verifyFiles();
            if (config.modloaderFound == true) {
                if (osName.startsWith("Linux")) {
                    JOptionPane.showMessageDialog(this, "Latest BepInEx Installed\nYou will need to add the following line to your games launch options\n\nWINEDLLOVERRIDES=\"winhttp.dll=n,b\" %command%", "BepInEx Installed", JOptionPane.INFORMATION_MESSAGE);
                } else {
                    JOptionPane.showMessageDialog(this, "Latest BepInEx Installed", "BepInEx Installed", JOptionPane.INFORMATION_MESSAGE);
                }
            } else {
                JOptionPane.showMessageDialog(this, "BepInEx Failed To Installed", "Warning", JOptionPane.WARNING_MESSAGE);
            }
        } else {
            config.modloaderFound = modLoaderTruth;
        }
    }

    void setGameFolder() {

        final JFileChooser fileChooser = new JFileChooser();
        int result;

        fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        File initialDirectory = new File(config.gameFolder);
        fileChooser.setCurrentDirectory(initialDirectory);
        result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            // User selected a file
            java.io.File selectedFile = fileChooser.getSelectedFile();
            config.setGameFolder(selectedFile.getAbsolutePath());
            refreshList();
        }
        verifyFiles();
    }

    void verifyFiles() {
        int result;
        config.verifyFiles();
        if (!config.gameFound) {
            result = JOptionPane.showConfirmDialog(this, "Unable to locate game!\nPlease specify game install location.", "Warning", JOptionPane.OK_CANCEL_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                setGameFolder();
            } else {
                //System.exit(0);
            }
        } else if (!config.modloaderFound) {
            result = JOptionPane.showConfirmDialog(this, "BepInEx does not appear to be installed, This will be needed to run mods.\nWould you like to installed BepInEx now?", "Install BepInEx?", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                updateBepinex();
            } else {
                //System.exit(0);
            }
        }
    }

    boolean validateAction(String action) {
        int result;
        if (!config.gameFound) {
            result = JOptionPane.showConfirmDialog(this, "The game does not appear to be installed in the selected folder.\nAre you sure you want to attempt to " + action + " anyways?", "Warning", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                return true;
            } else {
                return false;
            }
        } else if (!config.modloaderFound) {
            result = JOptionPane.showConfirmDialog(this, "BepInEx does not appear to be installed.\nAre you sure you want to attempt to " + action + " anyways?", "Warning", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);
            if (result == JFileChooser.APPROVE_OPTION) {
                return true;
            } else {
                return false;
            }
        }
        return true;
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
                        modHandler.install(selectedFile);
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
                JOptionPane.showMessageDialog(this, "\n" + LCMM.VERSION_STRING + "\n\nRory - Progammer and UI Design\nJustin - Platfrom tester and application icon designer", "About", JOptionPane.PLAIN_MESSAGE);
                break;
            case "UNINSTALL":
                if (listBox.getSelectedValue() != null) {
                    modHandler.uninstall(listBox.getSelectedValue());
                    refreshList();
                }
                break;
            case "DOWNLOAD":
                openDownload();
                break;
            case "TROUBLE":
                JOptionPane.showMessageDialog(this, "If your mods are not loading make sure the program is pointing that the games\ninstall directroy.\n\nIf you have confirmed the games install directory make sure BepInEx is up to date\nby installing in through [Options] > [Update BepInEx] \n\nIf you are on a unix based platform (Mac or Linux)\nyou will need to add the following line to your games launch options:\n\nWINEDLLOVERRIDES=\"winhttp.dll=n,b\" %command%", "Help", JOptionPane.PLAIN_MESSAGE);
                break;
            case "OPEN":
                openGameFolder();
                break;
        }
    }


    void openDownload() {
        if (Desktop.isDesktopSupported() && Desktop.getDesktop().isSupported(Desktop.Action.BROWSE)) {
            try {
                Desktop.getDesktop().browse(new URI("https://thunderstore.io/c/lethal-company/"));
            } catch (Exception e) {
                e.printStackTrace();;
            }
        } else {
            System.out.println("Desktop browsing is not supported on this platform.");
        }
    }

    void openGameFolder() {
        try {
            // Create a File object for the specified directory
            File directory = new File(config.gameFolder);
            // Check if the directory exists
            if (directory.exists()) {
                // Get the Desktop instance
                Desktop desktop = Desktop.getDesktop();
                // Open the directory using the default file manager
                desktop.open(directory);
            } else {
                verifyFiles();
            }
        } catch (Exception e) {
            e.printStackTrace();;
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
                        modHandler.install(file);
                    }
                    dtde.dropComplete(true);
                } catch (Exception e) {
                    e.printStackTrace();;
                    dtde.dropComplete(false);
                }
            } else {
                dtde.rejectDrop();
            }
            refreshList();
        }
    }

    public void mouseEntered(MouseEvent e) {}
    public void mouseExited(MouseEvent e) {}
    public void mousePressed(MouseEvent e) {}
    public void mouseReleased(MouseEvent e) {}
    public void mouseClicked(MouseEvent e) {
        if(e.getButton() == e.BUTTON3 && listBox.getSelectedValue() != null) {
            openContextMenu(e.getX(), e.getY());
        }
    } // end mouseClicked()

}
