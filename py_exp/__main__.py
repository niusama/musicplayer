from PyQt5 import QtWidgets
import sys
from PyQt5.QtWidgets import QDialog
import UI
def main():
    app = QtWidgets.QApplication(sys.argv)
    dialog = UI.LoginDialog()
    if dialog.exec_() == QDialog.Accepted:
        gui = UI.MainUi(dialog.get_username())
        gui.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()