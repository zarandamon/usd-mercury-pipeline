import sys
import maya.cmds as cmds

root_directory = "D:/USD-M/Usd_Mercury_Pipeline"

# Add the root directory to sys.path
if root_directory not in sys.path:
    sys.path.append(str(root_directory))

from plugins.maya.main_maya import MercuryWindow

# Hold a reference to the window to be able to close it later
mercury_window = None

def initializePlugin(mobject):
    """Initialize the plugin when Maya loads it."""
    global mercury_window
    mercury_window = MercuryWindow()
    mercury_window.show()
    print("USD Mercury Pipeline Plugin loaded dynamically.")

def uninitializePlugin(mobject):
    """Uninitialize the plugin when Maya unloads it."""
    global mercury_window

    # Unimport the maya_main module
    modules_list = {
        'plugins.maya.main_maya',
        'ui.ui_mainWindow',
        'ui.ui_utils',
        'lib.usd_manager',
        'lib.file_manager',
        'lib.maya_utils',
        'lib.data_base',
    }

    for module in modules_list:
        if module in sys.modules:
            del sys.modules[module]

    # Remove the root directory from sys.path
    if root_directory in sys.path:
        sys.path.remove(str(root_directory))

    print("USD Mercury Pipeline Plugin unloaded.")