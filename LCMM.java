import javax.swing.*;
import java.io.*;
import java.util.*;

public class LCMM {

    public static void main(String args[]) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        new LCMMFrame();
    }
}

