from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import inspect

# ? Has to be manually defined for each widget, unfortunately


def guisave(self, settings):
    """Saves GUI values to a settings file (.ini format)"""
    counter_accessed = 0
    counter_saved = 0
    for name, obj in inspect.getmembers(self):
        counter_accessed += 1
        if isinstance(obj, QComboBox):
            name = obj.objectName()
            index = obj.currentIndex()
            text = obj.itemText(index)
            settings.setValue(name, text)
            counter_saved += 1

        if isinstance(obj, QLineEdit):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, value)
            counter_saved += 1

        if isinstance(obj, QCheckBox):
            name = obj.objectName()
            state = obj.checkState()
            settings.setValue(name, state)
            counter_saved += 1

        if isinstance(obj, QRadioButton):
            name = obj.objectName()
            state = obj.isChecked()
            settings.setValue(name, state)
            counter_saved += 1

        if isinstance(obj, QSpinBox):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, int(value))
            counter_saved += 1

        if isinstance(obj, QDoubleSpinBox):
            name = obj.objectName()
            value = obj.text()
            settings.setValue(name, float(value.replace(",", ".")))
            counter_saved += 1

        if isinstance(obj, QGroupBox):
            name = obj.objectName()
            state = obj.isChecked()
            settings.setValue(name, state)
            counter_saved += 1

    print("{} items accessed, {} items saved.".format(counter_accessed, counter_saved))
    settings.sync()


def guirestore(self, settings):
    """Restores GUI values from a settings file (.ini format)"""
    counter_accessed = 0
    counter_restored = 0
    counter_failed = 0
    for name, obj in inspect.getmembers(self):
        counter_accessed += 1
        if isinstance(obj, QComboBox):
            try:
                name = obj.objectName()
                value = str(settings.value(name))
                if value == "":
                    continue
                # Restore the index associated to the string
                index = obj.findText(value)
                # OPTIONAL add to list if not found
                if index == -1:
                    obj.insertItems(0, [value])
                    index = obj.findText(value)
                    obj.setCurrentIndex(index)
                else:
                    obj.setCurrentIndex(index)
                counter_restored += 1
            except:
                counter_failed += 1

        if isinstance(obj, QLineEdit):
            try:
                name = obj.objectName()
                value = str(settings.value(name))
                obj.setText(value)
                counter_restored += 1
            except:
                counter_failed = +1

        if isinstance(obj, QCheckBox):
            try:
                name = obj.objectName()
                value = bool(int(settings.value(name)))
                if value:
                    obj.setChecked(True)
                else:
                    obj.setChecked(False)
                counter_restored += 1
            except:
                counter_failed = +1

        if isinstance(obj, QRadioButton):
            try:
                name = obj.objectName()
                value = bool(int(settings.value(name)))
                if bool(value):
                    obj.setChecked(True)
                else:
                    obj.setChecked(False)
                counter_restored += 1
            except:
                counter_failed = +1

        if isinstance(obj, QSpinBox):
            try:
                name = obj.objectName()
                value = settings.value(name)
                obj.setValue(int(value))
                counter_restored += 1
            except:
                counter_failed = +1

        if isinstance(obj, QDoubleSpinBox):
            try:
                name = obj.objectName()
                value = settings.value(name)
                obj.setValue(float(value.replace(",", ".")))
                counter_restored += 1
            except:
                counter_failed = +1

        if isinstance(obj, QGroupBox):
            try:
                name = obj.objectName()
                state = str(settings.value(name))
                if state == 'true':
                    obj.setChecked(True)
                else:
                    obj.setChecked(False)
                counter_restored += 1
            except:
                counter_failed = +1

    print(
        "{} items accessed, {} restored, {} failed.".format(
            counter_accessed, counter_restored, counter_failed
        )
    )


def grab_GC(window, settings):
    """Creates a global dictionary from the values stored in the given settings file (.ini format)"""
    GC = dict()
    for name, obj in inspect.getmembers(window):

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
    return GC