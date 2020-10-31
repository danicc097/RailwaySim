from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import inspect

# ? Has to be manually defined for each widget, unfortunately


def guisave(self, settings):
    """Saves GUI values to a settings file (.ini format)"""
    counter_a = 0
    counter_s = 0
    for name, obj in inspect.getmembers(self):
        counter_a += 1
        if isinstance(obj, QComboBox):
            name = obj.objectName()
            index = obj.currentIndex()
            text = obj.itemText(index)
            settings.setValue(name, text)
            counter_s += 1

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)
            counter_s += 1

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            state = obj.checkState()
            settings.setValue(name, state)
            counter_s += 1

        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            state = obj.isChecked()
            settings.setValue(name, state)
            counter_s += 1

        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)
            counter_s += 1

        if isinstance(obj, QDoubleSpinBox):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)
            counter_s += 1

        if isinstance(obj, QGroupBox):
            name = obj.objectName()
            state = obj.isChecked()
            settings.setValue(name, bool(state))
            counter_s += 1

    print("{} items accessed, {} items saved.".format(counter_a, counter_s))
    settings.sync()


def guirestore(self, settings):
    """Restores GUI values from a settings file (.ini format)"""
    counter_a = 0
    counter_s = 0
    # Loop through the list of MainWindow members
    for name, obj in inspect.getmembers(self):
        counter_a += 1
        if isinstance(obj, QComboBox):
            name = obj.objectName()
            value = str(settings.value(name))
            if value == "":
                continue
            # Restore the index associated to the string
            index = obj.findText(value)
            if index == -1:
                obj.insertItems(0, [value])
                index = obj.findText(value)
                obj.setCurrentIndex(index)
            else:
                obj.setCurrentIndex(index)
            counter_s += 1

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = str(settings.value(name))
            obj.setText(value)
            counter_s += 1

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            value = settings.value(name)
            if value == 'false':
                obj.setChecked(False)
            counter_s += 1

        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            value = settings.value(name)
            if value == 'false':
                obj.setChecked(False)
            counter_s += 1

        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            value = settings.value(name)
            obj.setValue(int(value))
            counter_s += 1

        if isinstance(obj, QDoubleSpinBox):
            name = obj.objectName()
            value = settings.value(name)
            obj.setValue(float(value))
            counter_s += 1

        if isinstance(obj, QGroupBox):
            name = obj.objectName()
            state = bool(settings.value(name))
            obj.setChecked(state)
            counter_s += 1

    print("{} items accessed, {} items restored.".format(counter_a, counter_s))


def grab_GC(self, settings):
    """Creates a global dictionary from the values stored in the given settings file (.ini format)"""
    global GC
    GC = dict()
    for name, obj in inspect.getmembers(self):

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = str(settings.value(name))
            GC[name] = value

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            value = settings.value(name)
            GC[name] = bool(value)

        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            value = settings.value(name)
            GC[name] = bool(value)

        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            value = settings.value(name)
            GC[name] = int(value)

        if isinstance(obj, QDoubleSpinBox):
            name = obj.objectName()
            value = settings.value(name)
            GC[name] = float(value)

        if isinstance(obj, QGroupBox):
            name = obj.objectName()
            value = bool(settings.value(name))
            GC[name] = value
