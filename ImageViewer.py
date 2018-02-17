#!/usr/bin/env python


from PyQt5.QtCore import QDir, Qt, QThread, pyqtSlot
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
                             QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QVBoxLayout, QWidget)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

from functools import partial

import effects
from components import SliderTabsWidget


class ImageViewer(QMainWindow):

    def __init__(self):

        super(ImageViewer, self).__init__()

        self.filter_read = '''
            All (*.BMP *.GIF *.JPG *.JPEG *.PNG *.PBM *.PGM *.PPM *.XBM *.XPM);;
            Windows Bitmap (*.BMP);;
            Graphic Interchange Format (*.GIF);;
            Joint Photographic Experts Group (*.JPG *.JPEG);;
            Portable Network Graphics (*.PNG);;
            Portable Bitmap (*.PBM);;
            Portable Graymap (*.PGM);;
            Portable Pixmap (*.PPM);;
            X11 Bitmap (*.XBM);;
            X11 Pixmap (*.XPM);;
        '''

        self.filter_write = '''
            Windows Bitmap (*.BMP);;
            Joint Photographic Experts Group (*.JPG *.JPEG);;
            Portable Network Graphics (*.PNG);;
            Portable Pixmap (*.PPM);;
            X11 Bitmap (*.XBM);;
            X11 Pixmap (*.XPM);;
        '''

        self.back_thread = QThread()
        self.back_thread.start()

        self.origin_pixmap = QPixmap()
        self.printer = QPrinter()
        self.scaleFactor = 0.0

        # === image box ===
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.scrollArea.setWidget(self.imageLabel)

        # self.sl.valueChanged.connect(self.valuechange)

        self.SlidersWidget = SliderTabsWidget(self)
        self.SlidersWidget.setDisabled(True)

        # window box
        self.layoutMain = QVBoxLayout()
        self.layoutMain.addWidget(self.scrollArea)
        self.layoutMain.addWidget(self.SlidersWidget)

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.layoutMain)
        self.setCentralWidget(self.mainWidget)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Voover")
        self.resize(500, 400)

    def effect(self, effect):

        self.updateActions(state=False)

        progressbar = self.SlidersWidget.progressbar
        image = self.imageLabel.pixmap().toImage()

        self.thread = effects.Threader(image, effect, progressbar=progressbar)
        self.thread.moveToThread(self.back_thread)

        self.thread.sig_done.connect(progressbar.done)
        self.thread.sig_done.connect(self.effected)
        self.thread.sig_step.connect(progressbar.set_value)

        self.back_thread.started.connect(self.thread.run)
        self.back_thread.started.emit()

    @pyqtSlot(QImage)
    def effected(self, image):
        pixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(pixmap)
        self.updateActions()

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath(), filter=self.filter_read)
        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Voover",
                        "Cannot load %s." % fileName)
                return

            self.origin_pixmap = QPixmap.fromImage(image)
            self.imageLabel.setPixmap(self.origin_pixmap)
            self.scaleFactor = 1.0

            self.fitToWindow_act.setEnabled(True)
            self.updateActions()
            self.reset_sliders()

            if not self.fitToWindow_act.isChecked():
                self.imageLabel.adjustSize()

    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def reset_effects(self):
        self.imageLabel.setPixmap(self.origin_pixmap)
        self.reset_sliders()

    def reset_sliders(self):
        self.SlidersWidget.reset()

    def save(self):

        fileName, fileFormat = QFileDialog.getSaveFileName(self, "Save File", QDir.currentPath(), filter=self.filter_write)
        if fileName:
            image = self.imageLabel.pixmap().toImage()
            if not image.save(fileName):
                QMessageBox.information(self, "Image Voover", "Cannot save %s." % fileName)

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindow_act.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()

    def about(self):
        QMessageBox.about(self, 'About Image Voover',
                '<p><b>Image Voower</b> improved version of '
                '<a href=https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py>Image View</a>'
                '</p>')

    def createActions(self):

        # === FILE ===

        self.open_act = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        self.print_act = QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
        self.save_act = QAction("&Save...", self, shortcut="Ctrl+S", enabled=False, triggered=self.save)
        self.exit_act = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)

        # === VIEW ===

        self.zoomIn_act = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOut_act = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSize_act = QAction("&Normal Size", self, shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        self.fitToWindow_act = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)

        # === FILTERS ===

        self.remove_filters_act = QAction("Remove filters", self, shortcut="Ctrl+Backspace", enabled=False, triggered=self.reset_effects)

        self.greys_act = QAction("Greys", self, enabled=False, triggered=partial(self.effect, effects.grey))
        self.colorize_act = QAction("Colorize", self, enabled=False, triggered=partial(self.effect, effects.floodfill))

        self.sepia_act = QAction("Sepia", self, enabled=False, triggered=partial(self.effect, effects.sepia))
        self.invert_act = QAction("Invert", self, enabled=False, triggered=partial(self.effect, effects.invert))
        self.black_white_act = QAction("Black & White", self, enabled=False, triggered=partial(self.effect, effects.black_white))
        self.noise_act = QAction("Noise", self, enabled=False, triggered=partial(self.effect, effects.noise))
        self.blue_yellow_act = QAction("Blue & Yellow", self, enabled=False, triggered=partial(self.effect, effects.blue_yellow))

        # === ABOUT ===

        self.about_act = QAction("&About", self, triggered=self.about)
        self.aboutQt_act = QAction("About &Qt", self, triggered=QApplication.instance().aboutQt)

    def createMenus(self):

        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.open_act)
        self.fileMenu.addAction(self.print_act)
        self.fileMenu.addAction(self.save_act)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exit_act)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomIn_act)
        self.viewMenu.addAction(self.zoomOut_act)
        self.viewMenu.addAction(self.normalSize_act)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindow_act)

        self.filterMenu = QMenu("&Filters", self)
        self.filterMenu.addAction(self.remove_filters_act)
        self.filterMenu.addSeparator()
        self.filterMenu.addAction(self.greys_act)
        self.filterMenu.addAction(self.colorize_act)
        self.filterMenu.addSeparator()
        self.filterMenu.addAction(self.sepia_act)
        self.filterMenu.addAction(self.invert_act)
        self.filterMenu.addAction(self.black_white_act)
        self.filterMenu.addAction(self.noise_act)
        self.filterMenu.addAction(self.blue_yellow_act)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.about_act)
        self.helpMenu.addAction(self.aboutQt_act)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.filterMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self, state=True):

        self.open_act.setEnabled(state)
        self.print_act.setEnabled(state)
        self.save_act.setEnabled(state)

        self.zoomIn_act.setEnabled(not self.fitToWindow_act.isChecked() if state else False)
        self.zoomOut_act.setEnabled(not self.fitToWindow_act.isChecked() if state else False)
        self.normalSize_act.setEnabled(not self.fitToWindow_act.isChecked() if state else False)
        self.fitToWindow_act.setEnabled(state)

        self.remove_filters_act.setEnabled(state)
        self.greys_act.setEnabled(state)
        self.colorize_act.setEnabled(state)
        self.sepia_act.setEnabled(state)
        self.invert_act.setEnabled(state)
        self.black_white_act.setEnabled(state)
        self.noise_act.setEnabled(state)
        self.blue_yellow_act.setEnabled(state)

        self.about_act.setEnabled(state)
        self.aboutQt_act.setEnabled(state)

        self.SlidersWidget.setEnabled(state)

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomIn_act.setEnabled(self.scaleFactor < 3.0)
        self.zoomOut_act.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.resize(800, 600)
    imageViewer.show()

sys.exit(app.exec_())