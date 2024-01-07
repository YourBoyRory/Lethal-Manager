import javax.swing.*;

public class LCMM {

    public static final String VERSION_STRING = "Lethal Manager v1.0.1";

    public static void main(String args[]) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();;
        }
        new LCMMFrame();
    }
}

