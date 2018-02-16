from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QSlider, QTabWidget, QVBoxLayout, QWidget

import effects
from functools import partial


class BrightContrastWidget(QWidget):

    def __init__(self, label_widget=None):

        super(QWidget, self).__init__()

        self.widgetBrightness = TitledSliderWidget("Brightness", label_widget, TitledSliderWidget.slider_brightness)
        self.widgetContrast = TitledSliderWidget("Contrast", label_widget, TitledSliderWidget.slider_contrast)

        # sliders layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 0, 5, 0)

        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetBrightness)
        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetContrast)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def apply(self):
        return self.widgetBrightness.apply(), self.widgetContrast.apply()

    def reset(self):
        self.widgetBrightness.reset()
        self.widgetContrast.reset()


class ProgressBar(QProgressBar):

    def __init__(self):

        super(QWidget, self).__init__()
        self.setAlignment(Qt.AlignCenter)

    @pyqtSlot(int)
    def set_value(self, value):
        self.setValue(value)

    @pyqtSlot(QImage)
    def done(self, image):
        self.setValue(self.maximum())


class RGBWidget(QWidget):

    def __init__(self, label_widget=None):

        super(QWidget, self).__init__()

        self.widgetRed = TitledSliderWidget("Red", label_widget, TitledSliderWidget.slider_red)
        self.widgetGreen = TitledSliderWidget("Green", label_widget, TitledSliderWidget.slider_green)
        self.widgetBlue = TitledSliderWidget("Blue", label_widget, TitledSliderWidget.slider_blue)

        # sliders layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 0, 5, 0)

        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetRed)
        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetGreen)
        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetBlue)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def apply(self):
        return self.widgetRed.apply(), self.widgetGreen.apply(), self.widgetBlue.apply()

    def reset(self):
        self.widgetRed.reset()
        self.widgetGreen.reset()
        self.widgetBlue.reset()


class SliderTabsWidget(QTabWidget):

    def __init__(self, main_window=None):

        super(QTabWidget, self).__init__()
        self.imageLabel = main_window.imageLabel
        self.layout = QVBoxLayout(self)
        self.main_window = main_window

        self.tabs = QTabWidget()
        self.tab_bc = BrightContrastWidget(self.imageLabel)
        self.tab_rgb = RGBWidget(self.imageLabel)

        self.tabs.addTab(self.tab_bc, "Brightness / Contrast")
        self.tabs.addTab(self.tab_rgb, "RGB")
        self.layout.addWidget(self.tabs)

        self.layout_buttons = QHBoxLayout()

        self.progressbar = ProgressBar()
        self.layout_buttons.addWidget(self.progressbar)

        self.button_apply = QPushButton()
        self.button_apply.setText('Apply')
        self.button_apply.setFixedWidth(100)
        self.button_apply.clicked.connect(partial(self.apply))
        self.layout_buttons.addWidget(self.button_apply)

        self.button_reset = QPushButton()
        self.button_reset.setText('Reset')
        self.button_reset.setFixedWidth(100)
        self.button_reset.clicked.connect(self.reset)
        self.layout_buttons.addWidget(self.button_reset)

        self.layout.addLayout(self.layout_buttons)

        self.setLayout(self.layout)
        self.setFixedHeight(200)

    def apply(self):
        filters = self.tab_bc.apply() + self.tab_rgb.apply()
        image = self.imageLabel.pixmap().toImage()
        thread = effects.Threader(image, filters, progressbar=self.progressbar)
        thread.sig_done.connect(self.main_window.effected)
        thread.sig_done.connect(self.progressbar.done)
        thread.sig_step.connect(self.progressbar.set_value)
        self.main_window.updateActions(state=False)
        thread.start()
        self.reset()

    def reset(self):
        self.tab_bc.reset()
        self.tab_rgb.reset()


class TitledSliderWidget(QWidget):
    
    def __init__(self, title="Unnamed", label_widget=None, action=None, labelMin='-50', labelMax='+50'):

        super(QWidget, self).__init__()

        self.action = action
        self.imageLabel = label_widget
        self.old_value = 0

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout_slider = QVBoxLayout()
        self.layout_slider.setSpacing(0)
        self.layout_slider.setContentsMargins(0, 0, 0, 0)

        self.titledSlider = QWidget()
        self.titledSlider.setLayout(self.layout_slider)

        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout_slider.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(0)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(25)
        self.slider.setValue(50)
        self.layout_slider.addWidget(self.slider)

        limit_style = 'font-size: 15px; padding: 10px 0 10px 0;'
        self.lblMin = QLabel(labelMin)
        self.lblMin.setStyleSheet(limit_style)
        self.lblMax = QLabel(labelMax)
        self.lblMax.setStyleSheet(limit_style)

        self.layout.addWidget(self.lblMin)
        self.layout.addWidget(self.titledSlider)
        self.layout.addWidget(self.lblMax)

    def apply(self):
        return self.action(self)

    def effect(self, effect, **kwargs):
        image = self.imageLabel.pixmap().toImage()
        image = effect(self, image, **kwargs)
        pixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(pixmap)

    def reset(self):
        self.old_value = 0
        self.slider.setValue(50)

    def slider_blue(self):

        blue = self.slider.value() - 50 - self.old_value
        if blue != 0:
            self.old_value += blue
            return effects.blue, {'factor': blue}
        return None, None

    def slider_brightness(self):

        brightness = (self.slider.value() - 50) * 1.5 - self.old_value
        if brightness != 0:
            self.old_value += brightness
            return effects.brightness, {'factor': brightness}
        return None, None

    def slider_contrast(self):

        contrast = self.slider.value() - 50 - self.old_value
        if contrast != 0:
            self.old_value += contrast
            return effects.contrast, {'factor': contrast}
        return None, None

    def slider_green(self):

        green = self.slider.value() - 50 - self.old_value
        if green != 0:
            self.old_value += green
            return effects.green, {'factor': green}
        return None, None

    def slider_red(self):

        red = self.slider.value() - 50 - self.old_value
        if red != 0:
            self.old_value += red
            return effects.red, {'factor': red}
        return None, None