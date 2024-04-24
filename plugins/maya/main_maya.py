import sys

root_directory = "D:/USD-M/Usd_Mercury_Pipeline"
sys.path.append(str(root_directory))

from ui.ui_mainWindow import MainWindow
from lib.usd_manager import UsdManager
from ui.ui_utils import SceneFileItemWidget, UsdFileItemWidget, AssetInputDialog, DepartmentSelectionDialog, GeoSanityCheck, CustomQDialog
from lib.file_manager import FileManager, CreateProject
from lib.data_base import ProjectDataBase

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIcon
from pathlib import Path
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import os

# Initializing project global variable.
project = None

class ProjectData:
    """
    Main class that caches the database information to be used in the lists.

    """
    def __init__(self, db_path):
        self.db = ProjectDataBase(db_path)

        self.assets_cache = {}
        self.asset_departments_cache = {}
        self.setVars_cache = {}
        self.variants_cache = {}
        self.variant_usds_cache = {}
        
        self.sequences_cache = {}
        self.sequence_departments_cache = {}

        self.shots_cache = {}
        self.shot_departments_cache = {}

        self.tasks_cache = {}
        self.files_cache = {}
        self.sublayer_usds_cache = {}

    def get_assets(self):
        if not self.assets_cache:
            assets = self.db.get_asset(all=True)
            self.assets_cache = {asset['name']: asset for asset in assets}
        return self.assets_cache
    
    def get_asset_departments(self, asset_id):
        # Cache by asset_id, not globally
        if asset_id not in self.asset_departments_cache:
            departments = self.db.get_department("asset", asset_id, all=True)
            self.asset_departments_cache[asset_id] = {department['name']: department for department in departments}
        return self.asset_departments_cache.get(asset_id, {})
    
    def get_setVars(self, department_id):
        # Cache by department_id, not globally
        if department_id not in self.setVars_cache:
            setVars = self.db.get_setVar(department_id, all=True)
            self.setVars_cache[department_id] = {setVar['name']: setVar for setVar in setVars}
        return self.setVars_cache.get(department_id, {})

    def get_variants(self, setVar_id):
        # Cache by setVar_id, not globally
        if setVar_id not in self.variants_cache:
            variants = self.db.get_variant(setVar_id, all=True)
            self.variants_cache[setVar_id] = {variant['name']: variant for variant in variants}
        return self.variants_cache.get(setVar_id, {})

    def get_variant_usds(self, variant_id):
        # Cache by variant_id, not globally
        if variant_id not in self.variant_usds_cache:
            variant_usds = self.db.get_variantVersion('variant', variant_id, all=True)
            self.variant_usds_cache[variant_id] = {variant_usd['version']: variant_usd for variant_usd in variant_usds}
        return self.variant_usds_cache.get(variant_id, {})
    
    def get_sequences(self):
        if not self.sequences_cache:
            sequences = self.db.get_sequence(all=True)
            self.sequences_cache = {sequence['name']: sequence for sequence in sequences}
        return self.sequences_cache
    
    def get_sequence_departments(self, sequence_id):
        if sequence_id not in self.sequence_departments_cache:
            departments = self.db.get_department("sequence", sequence_id, all=True)
            self.sequence_departments_cache[sequence_id] = {department['name']: department for department in departments}
        return self.sequence_departments_cache.get(sequence_id, {})
    
    def get_files(self, task_id):
        if task_id not in self.files_cache:
            files = self.db.get_file(task_id, all=True)
            self.files_cache[task_id] = {file['version']: file for file in files}
        return self.files_cache.get(task_id, {})

    def get_shots(self, sequence_id):
        if sequence_id not in self.shots_cache:
            shots = self.db.get_shot(sequence_id, all=True)
            self.shots_cache[sequence_id] = {shot['name']: shot for shot in shots}
        return self.shots_cache.get(sequence_id, {})

    def get_tasks(self, department_id):
        if department_id not in self.tasks_cache:
            tasks = self.db.get_task(department_id, all=True)
            self.tasks_cache[department_id] = {task['name']: task for task in tasks}
        return self.tasks_cache.get(department_id, {})

    def get_sublayer_usds(self, department_id):
        # Cache by variant_id, not globally
        if department_id not in self.sublayer_usds_cache:
            sublayer_usds = self.db.get_variantVersion('department', department_id, all=True)
            self.sublayer_usds_cache[department_id] = {sublayer_usd['version']: sublayer_usd for sublayer_usd in sublayer_usds}
        return self.sublayer_usds_cache.get(department_id, {})
    
    def clear_cache(self, entity_type=None):
        if entity_type is None:
            # Clear all caches
            self.assets_cache = {}
            self.asset_departments_cache = {}
            self.setVars_cache = {}
            self.variants_cache = {}
            self.variant_usds_cache = {}
            self.sequences_cache = {}
            self.sequence_departments_cache = {}
            self.shots_cache = {}
            self.shot_departments_cache = {}
            self.tasks_cache = {}
            self.files_cache = {}
            self.sublayer_usds_cache = {}
        else:
            # Clear specific cache
            if entity_type == "assets":
                self.assets_cache = {}
            elif entity_type == "asset_departments":
                self.asset_departments_cache = {}
            elif entity_type == "setVars":
                self.setVars_cache = {}
            elif entity_type == "variants":
                self.variants_cache = {}
            elif entity_type == "variant_usds":
                self.variant_usds_cache = {}
            elif entity_type == "sequences":
                self.sequences_cache = {}
            elif entity_type == "sequence_departments":
                self.sequence_departments_cache = {}
            elif entity_type == "shots":
                self.shots_cache = {}
            elif entity_type == "shot_departments":
                self.shot_departments_cache = {}
            elif entity_type == "tasks":
                self.tasks_cache = {}
            elif entity_type == "files":
                self.files_cache = {}
            elif entity_type == "sublayer_usds":
                self.sublayer_usds_cache = {}

def get_maya_main_window():
    """
    Retrieve Maya's main window as a QWidget.

    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return wrapInstance(int(main_window_ptr), QWidget)
    
class MercuryWindow:
    def __init__(self, parent=get_maya_main_window()):
        """
        Initialize the MercuryWindow application.

        Sets up the application, creates the main window, applies the style sheet,
        and initiates the project setup process.
        """
        self.app = QApplication.instance()  # Use the existing QApplication
        self.main_window = MainWindow(parent=parent)  # Parent to Maya's main window

        # Script Dir.
        self.script_dir = Path(__file__).parent.parent.parent
        self.icons_dir = os.path.join(self.script_dir, "resources", "icons")

        self.set_project()

    # Set Project Bascis.    
    def set_project(self):
        """
        Set the current project directory and initialize the database connection.

        """
        # Sets the Project for the plugin.
        global project
        if project is None:
            project =  self.set_project_directory()

        if project:
            self.project = project
            db_path = os.path.join(self.project, "pipeline", "project.db")
            self.db = ProjectDataBase(db_path)
            self.db_cache = ProjectData(db_path)
        else:
            self.main_window.status_bar.showMessage("Project not set. User cancelled or no directory returned.", 5000)
        
        # Calling instance of UsdManager and FileManager.
        self.um = UsdManager(project)
        self.fm = FileManager(project)

        # Setting Comments QLineEdits first.
        self.scene_files_comment_QLineEdit = self.main_window.findChild(QLineEdit, "scene_files_comment_QLineEdit")
        self.usd_config_comment_QLineEdit = self.main_window.findChild(QLineEdit, "usd_config_comment_QLineEdit")

        # Button Scene Files and Usd Config.
        self.scene_files_QPushButton = self.main_window.findChild(QPushButton, "scene_files_QPushButton")
        self.usd_config_QPushButton = self.main_window.findChild(QPushButton, "usd_config_QPushButton")
        self.scene_files_QPushButton.clicked.connect(lambda: self.on_context_button_clicked(context="sceneFiles"))
        self.usd_config_QPushButton.clicked.connect(lambda: self.on_context_button_clicked(context="usdConfig"))

        self.load_version_QPushButton = self.main_window.findChild(QPushButton, "load_version_QPushButton")
        self.load_version_QPushButton.clicked.connect(self.on_load_version_button_clicked)

        self.save_version_QPushButton = self.main_window.findChild(QPushButton, "save_version_QPushButton")
        self.save_version_QPushButton.clicked.connect(self.on_save_version_button_clicked)

        self.publish_version_QPushButton = self.main_window.findChild(QPushButton, "publish_version_QPushButton")
        self.publish_version_QPushButton.clicked.connect(self.on_publish_version_button_clicked)

        
        self.create_menu_bar()
        self.setup_scene_files_connections()
        self.setup_usd_config_connections()
        self.populate_shots_list(context="sceneFiles")

    def set_project_directory(self):
        directory = QFileDialog.getExistingDirectory(self.main_window, "Select Project Directory")
        if directory:  
            create_project = CreateProject(directory) # Creates Folder Structure for project.
            self.main_window.status_bar.showMessage(f"Project directory set to: {directory}", 5000)
            return directory
        
    # Set Connections.
    def setup_scene_files_connections(self):
        """
        Setup the signal-slot connections for UI elements.

        """

        # Button Assets and Shots
        self.scene_files_shots_QPushButton = self.main_window.findChild(QPushButton, "scene_files_shots_QPushButton")
        self.scene_files_assets_QPushButton = self.main_window.findChild(QPushButton, "scene_files_assets_QPushButton")
        self.scene_files_shots_QPushButton.clicked.connect(lambda: self.populate_shots_list(context="sceneFiles"))
        self.scene_files_assets_QPushButton.clicked.connect(lambda: self.populate_assets_list(context="sceneFiles"))
        
        # Shots-QTreeList
        self.scene_files_shots_QtreeWidget = self.main_window.findChild(QTreeWidget, "scene_files_shots_QtreeWidget")
        # self.scene_files_shots_QtreeWidget.itemSelectionChanged.connect(self.populate_selection_details)
        self.scene_files_shots_QtreeWidget.itemSelectionChanged.connect(lambda: self.populate_departments_list(context="sceneFiles", type="shots"))
        self.scene_files_shots_QtreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_shots_QtreeWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="sceneFiles_shots"))
        # Assets-QTreeList
        self.scene_files_assets_QtreeWidget = self.main_window.findChild(QTreeWidget, "scene_files_assets_QtreeWidget")
        # self.scene_files_assets_QtreeWidget.itemSelectionChanged.connect(self.populate_selection_details)
        self.scene_files_assets_QtreeWidget.itemSelectionChanged.connect(lambda: self.populate_departments_list(context="sceneFiles", type="assets"))
        self.scene_files_assets_QtreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_assets_QtreeWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="sceneFiles_assets"))

        # Shots-Department Qlist
        self.scene_files_shots_department_QListWidget = self.main_window.findChild(QListWidget, "scene_files_shots_department_QListWidget")
        self.scene_files_shots_department_QListWidget.itemSelectionChanged.connect(lambda: self.populate_tasks_list(type="shots"))
        self.scene_files_shots_department_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_shots_department_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="sceneFiles_department", type="shots"))
        # Assets-Department Qlist
        self.scene_files_assets_department_QListWidget = self.main_window.findChild(QListWidget, "scene_files_assets_department_QListWidget")
        self.scene_files_assets_department_QListWidget.itemSelectionChanged.connect(lambda: self.populate_tasks_list(type="assets"))
        self.scene_files_assets_department_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_assets_department_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="sceneFiles_department", type="assets"))

        # Shots-Task Qlist
        self.scene_files_shots_task_QListWidget = self.main_window.findChild(QListWidget, "scene_files_shots_task_QListWidget")
        self.scene_files_shots_task_QListWidget.itemSelectionChanged.connect(lambda: self.populate_files_list(type="shots"))
        self.scene_files_shots_task_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_shots_task_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="task", type="shots"))
        # Assets-Task Qlist
        self.scene_files_assets_task_QListWidget = self.main_window.findChild(QListWidget, "scene_files_assets_task_QListWidget")
        self.scene_files_assets_task_QListWidget.itemSelectionChanged.connect(lambda: self.populate_files_list(type="assets"))
        self.scene_files_assets_task_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_assets_task_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="task", type="assets"))

        # Shots-Files QTreeList
        self.scene_files_shots_files_QtreeWidget = self.main_window.findChild(QTreeWidget, "scene_files_shots_files_QtreeWidget")
        self.scene_files_shots_files_QtreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_shots_files_QtreeWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="files", type="shots"))
        # Assets-Files QTreeList
        self.scene_files_assets_files_QtreeWidget = self.main_window.findChild(QTreeWidget, "scene_files_assets_files_QtreeWidget")
        self.scene_files_assets_files_QtreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scene_files_assets_files_QtreeWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="files", type="assets"))

    def setup_usd_config_connections(self):
        """
        Setup the signal-slot connections for UI elements.

        """
        # Button Assets and Shots
        self.usd_config_shots_QPushButton = self.main_window.findChild(QPushButton, "usd_config_shots_QPushButton")
        self.usd_config_assets_QPushButton = self.main_window.findChild(QPushButton, "usd_config_assets_QPushButton")
        self.usd_config_shots_QPushButton.clicked.connect(lambda: self.populate_shots_list(context="usdConfig"))
        self.usd_config_assets_QPushButton.clicked.connect(lambda: self.populate_assets_list(context="usdConfig"))
        
        # Shots-QTreeList
        self.usd_config_shots_QtreeWidget = self.main_window.findChild(QTreeWidget, "usd_config_shots_QtreeWidget")
        # self.usd_config_shots_QtreeWidget.itemSelectionChanged.connect(self.populate_selection_details)
        self.usd_config_shots_QtreeWidget.itemSelectionChanged.connect(lambda: self.populate_departments_list(context="usdConfig", type="shots"))
        self.usd_config_shots_QtreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usd_config_shots_QtreeWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="usdConfig_shots"))

        # Assets-QTreeList
        self.usd_config_assets_QtreeWidget = self.main_window.findChild(QTreeWidget, "usd_config_assets_QtreeWidget")
        self.usd_config_assets_QtreeWidget.itemSelectionChanged.connect(lambda: self.populate_selection_details(context="usdConfig", type="assets"))
        self.usd_config_assets_QtreeWidget.itemSelectionChanged.connect(lambda: self.populate_departments_list(context="usdConfig", type="assets"))
        self.usd_config_assets_QtreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usd_config_assets_QtreeWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="usdConfig_assets"))

        # Shots-Department Qlist
        self.usd_config_shots_department_QListWidget = self.main_window.findChild(QListWidget, "usd_config_shots_department_QListWidget")
        self.usd_config_shots_department_QListWidget.itemSelectionChanged.connect(lambda: self.populate_usds_list(type="shots"))
        self.usd_config_shots_department_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usd_config_shots_department_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="usdConfig_department", type="shots"))
        # Assets-Department Qlist
        self.usd_config_assets_department_QListWidget = self.main_window.findChild(QListWidget, "usd_config_assets_department_QListWidget")
        self.usd_config_assets_department_QListWidget.itemSelectionChanged.connect(self.populate_setVars_list)
        self.usd_config_assets_department_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usd_config_assets_department_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="usdConfig_department", type="assets"))

        # Assets-setVariant Qlist
        self.usd_config_assets_setVar_QListWidget = self.main_window.findChild(QListWidget, "usd_config_assets_setVar_QListWidget")
        self.usd_config_assets_setVar_QListWidget.itemSelectionChanged.connect(self.populate_variants_list)
        self.usd_config_assets_setVar_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usd_config_assets_setVar_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="setVar", type="assets"))

        # Assets-variant Qlist
        self.usd_config_assets_variant_QListWidget = self.main_window.findChild(QListWidget, "usd_config_assets_variant_QListWidget")
        self.usd_config_assets_variant_QListWidget.itemSelectionChanged.connect(lambda: self.populate_usds_list(type="assets"))
        self.usd_config_assets_variant_QListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usd_config_assets_variant_QListWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="variant", type="assets"))


        # AssetInfo QGroupBox
        self.usd_config_asset_type_QLabel = self.main_window.findChild(QLabel, "usd_config_asset_type_QLabel")
        self.usd_config_asset_description_QLabel = self.main_window.findChild(QLabel, "usd_config_asset_description_QLabel")
        self.usd_config_asset_latest_version_QLabel = self.main_window.findChild(QLabel, "usd_config_asset_latest_version_QLabel")

        # Shots-Files QTreeList
        self.usd_config_shots_variantVersions_QtreeWidget = self.main_window.findChild(QTreeWidget, "usd_config_shots_variantVersions_QtreeWidget")
        # Assets-variantVersions QTreeList
        self.usd_config_assets_variantVersions_QtreeWidget = self.main_window.findChild(QTreeWidget, "usd_config_assets_variantVersions_QtreeWidget")
        self.usd_config_assets_variantVersions_QtreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.usd_config_assets_variantVersions_QtreeWidget.customContextMenuRequested.connect(lambda point: self.on_context_menu(point=point, context="variantVersion", type="assets"))
        
        self.usd_config_assets_QPushButton.click()
        self.scene_files_assets_QPushButton.click()
    
    # On click Button Events.
    def on_context_button_clicked(self, context):
        """
        Handle the 'SceneFiles' button click event.

        """
        if context == "sceneFiles":
            if self.scene_files_shots_QPushButton.isChecked():
                self.populate_shots_list(context)
            else:
                self.populate_assets_list(context)
        else:
            if self.usd_config_shots_QPushButton.isChecked():
                self.populate_shots_list(context)
            else:
                self.populate_assets_list(context)

    # /SHARED First List.
    def populate_shots_list(self, context):
        """
        Populate the shots list in the UI.
        
        """
        self.db_cache.clear_cache("shots")
        self.db_cache.clear_cache("sequences")

        self.clear_lists(context, "shots", 0)

        if context == "sceneFiles":
            selected_list = self.scene_files_shots_QtreeWidget
        else:
            selected_list = self.usd_config_shots_QtreeWidget

    
        # Gets all sequences and shots and adds them as items to the QTreeWidget
        self.sequences = self.db_cache.get_sequences()

        for sequence_info in self.sequences:
            sequence_item = QTreeWidgetItem(selected_list, [sequence_info['name']])

            self.shots = self.db_cache.get_shots(sequence_info['id'])

            for shot_info in self.shots:
                QTreeWidgetItem(sequence_item, [shot_info['name']])

    def populate_assets_list(self, context):
        """
        Populate the shots list in the UI.
        
        """
        self.clear_lists(context, "assets", 0)
        self.db_cache.clear_cache("assets")

        selected_list = self.scene_files_assets_QtreeWidget if context == "sceneFiles" else self.usd_config_assets_QtreeWidget
        
        # Gets all sequences and shots and adds them as items to the QTreeWidget.
        self.assets = self.db_cache.get_assets()

        type_parent_items = {}

        for asset_info in self.assets.values():
            asset_type = asset_info['type']
            asset_name = asset_info['name']

            # Check if the asset type category already exists.
            if asset_type not in type_parent_items:
                # Create a new parent item for the new asset type.
                parent_item = QTreeWidgetItem(selected_list, [asset_type])
                parent_item_icon = self.get_icons("asset", "type")
                parent_item.setIcon(0, parent_item_icon)
                type_parent_items[asset_type] = parent_item
            else:
                # Retrieve the existing parent item.
                parent_item = type_parent_items[asset_type]

            # Add the current asset as a child to the corresponding asset type category.
            QTreeWidgetItem(parent_item, [asset_name])
     
    # /SHARED Second List.
    def populate_departments_list(self, context, type):
        """
        Populate the department list based on the selected shot or asset on both contexts.

        :param context: "sceneFiles" - "usdConfig"
        :param type: "shots" - "assets"
        """
        
        if context == "sceneFiles":
            
            shot_selected_item = self.scene_files_shots_QtreeWidget.currentItem()

            if type == "shots" and shot_selected_item is not None:
                self.clear_lists(context, type, 1)

                selected_text = shot_selected_item.text(0)

                if shot_selected_item.parent() is None:
                    self.db_cache.clear_cache("sequence_departments")

                    self.is_sequence = True
                    sequence_name = self.sequences.get(selected_text)
                    self.departments = self.db_cache.get_sequence_departments(sequence_name['id'])
                    for department_info in self.departments:
                        
                        self.scene_files_shots_department_QListWidget.addItem(department_info['name'])

                    ## CREATING SEQUENCE SELECTION.

                    self.sequence_item = self.scene_files_shots_QtreeWidget.currentItem()
                    self.sequence_name = self.sequence_item.item(0)

                else:
                    self.db_cache.clear_cache("shot_departments")

                    self.is_sequence = False
                    selected_item_parent = shot_selected_item.parent()
                    selected_parent_text = selected_item_parent.text(0)
                    sequence_info = self.sequences.get(selected_parent_text)

                    self.shots = self.db_cache.get_shots(sequence_info['id'])
                    shot_info = self.shots.get(selected_text)

                    self.departments = self.db_cache.get_shot_departments(shot_info['id'])
                    for department_info in self.departments:
                        self.scene_files_shots_department_QListWidget.addItem(department_info['name'])
                    
                    ## CREATING SHOT SELECTION.

                    self.shot_item = self.scene_files_shots_QtreeWidget.currentItem()
                    self.shot_name = self.shot_item.item(0)

            asset_selected_item = self.scene_files_assets_QtreeWidget.currentItem()        
            asset_selected_parent = asset_selected_item.parent()

            if type == "assets" and asset_selected_parent is not None:
                self.clear_lists(context, type, 1)
                self.db_cache.clear_cache("asset_departments")

                selected_text = asset_selected_item.text(0)
                asset_name = self.assets.get(selected_text)
                self.departments = self.db_cache.get_asset_departments(asset_name['id'])
                
                for department_key, department_value in self.departments.items():
                    department_item_name = department_value['name']
                    list_item = QListWidgetItem(department_item_name)

                    icon = self.get_icons("department", department_item_name)
                    list_item.setIcon(icon)  # Set the icon.

                    self.scene_files_assets_department_QListWidget.insertItem(0, list_item)

                ## CREATING ASSET SELECTION.
                self.asset_item = self.scene_files_assets_QtreeWidget.currentItem()
                self.asset_name = self.asset_item.text(0)

        elif context == "usdConfig":

            shot_selected_item = self.usd_config_shots_QtreeWidget.currentItem()
            
            if type == "shots" and shot_selected_item is not None:
                self.clear_lists(context, type, 1)

                selected_text = shot_selected_item.text(0)

                if shot_selected_item.parent() is None:
                    self.db_cache.clear_cache("sequence_departments")

                    sequence_name = self.sequences.get(selected_text)
                    self.departments = self.db_cache.get_sequence_departments(sequence_name['id'])
                    for department_key, department_value in self.departments.items():
                        department_item = department_value['name']
                        self.scene_files_assets_department_QListWidget.addItem(department_item)
                    
                    ## CREATING SEQUENCE SELECTION.

                    self.sequence_item = self.usd_config_shots_QtreeWidget.currentItem()
                    self.sequence_name = self.sequence_item.item(0)

                else:
                    self.db_cache.clear_cache("shot_departments")

                    selected_item_parent = shot_selected_item.parent()
                    selected_parent_text = selected_item_parent.text(0)
                    sequence_info = self.sequences.get(selected_parent_text)

                    self.shots = self.db_cache.get_shots(sequence_info['id'])
                    shot_info = self.shots.get(selected_text)

                    self.departments = self.db_cache.get_shot_departments(shot_info['id'])
                    for department_key, department_value in self.departments.items():
                        department_item = department_value['name']
                        self.scene_files_assets_department_QListWidget.addItem(department_item)
                    
                    ## CREATING SHOT SELECTION.

                    self.shot_item = self.usd_config_shots_QtreeWidget.currentItem()
                    self.shot_name = self.shot_item.item(0)

            asset_selected_item = self.usd_config_assets_QtreeWidget.currentItem()        
            asset_selected_parent = asset_selected_item.parent()

            if type == "assets" and asset_selected_parent is not None:
                self.clear_lists(context, type, 1)
                self.db_cache.clear_cache("asset_departments")

                selected_text = asset_selected_item.text(0)
                asset_name = self.assets.get(selected_text)
                self.departments = self.db_cache.get_asset_departments(asset_name['id'])

                for department_key, department_value in self.departments.items():
                    department_item_name = department_value['name']
                    list_item = QListWidgetItem(department_item_name)
                    icon = self.get_icons("department", department_item_name)
                    list_item.setIcon(icon)  # Set the icon.
                    self.usd_config_assets_department_QListWidget.insertItem(0, list_item)  # Insert the item.

                ## CREATING ASSET SELECTION.
                self.asset_item = self.usd_config_assets_QtreeWidget.currentItem()
                self.asset_name = self.asset_item.text(0)

    # /SHARED Third List.
    def populate_setVars_list(self):
        """
        Populates asset/department/setVar list for both contexts. Only for asset Type.

        :param context: "sceneFiles" - "usdConfig"
        :logic: CACHE/WIDGETS/CREATE_ITEMS/FETCH_INFO/POPULATE
        """
        # Clear cache and list selections.
        self.db_cache.clear_cache("setVars")
        self.clear_lists("usdConfig", "assets", 2)

        # Determine the appropriate widgets based on context.
        department_widget = self.usd_config_assets_department_QListWidget
        setVar_widget = self.usd_config_assets_setVar_QListWidget

        # CREATE DEPARTMENT ITEM AND NAME.
        self.department_item = department_widget.currentItem()
        if not self.department_item:
            print("No department selected.")
            return
        self.department_name = self.department_item.text()
        
        # Get Department from Selection.
        setVar_name = self.departments.get(self.department_name)
        if not setVar_name:
            print(f"Failed to retrieve valid setVar data for department: {self.department_name}")
            return

        # Get setVars from Department selection.
        self.setVars = self.db_cache.get_setVars(setVar_name['department_id'])
        if not self.setVars:
            print(f"No setVars found for department ID: {setVar_name['department_id']}")
            return

        # Populate list with SetVar Items.
        for setVar_key, setVar_value in self.setVars.items():
            setVar_item = setVar_value['name']
            setVar_widget.addItem(setVar_item)  # Use the widget determined by the context
            
    # /SHARED Fourth List.
    def populate_variants_list(self):
        """
        Populates asset/department/setVar/variant list for both contexts.

        :param context: "sceneFiles" - "usdConfig"
        :logic: CACHE/WIDGETS/CREATE_ITEMS/FETCH_INFO/POPULATE
        """
        # Clear cache and list selections.
        self.db_cache.clear_cache("variants")
        self.clear_lists("usdConfig", "assets", 3)

        # Determine the appropriate widgets based on context.
        setVar_widget = self.usd_config_assets_setVar_QListWidget
        variant_widget = self.usd_config_assets_variant_QListWidget

        # Get setVar from Selection.
        self.setVar_item = setVar_widget.currentItem()
        if not self.setVar_item:
            print("No setVar selected.")
            return
        self.setVar_name = self.setVar_item.text()

        # Get variant from setVar selection.
        variant_name = self.setVars.get(self.setVar_name) # Already Retrieved from setVar function.
        if not variant_name:
            print(f"Failed to retrieve valid variant data for setVar: {self.setVar_name}")
            return
        self.variants = self.db_cache.get_variants(variant_name['setVar_id'])
        if not self.variants:
            print(f"No setVars found for department ID: {variant_name['setVar_id']}")
            return
        
        # Populate list with variant Items.
        for variant_key, variant_value in self.variants.items():
            variant_item = variant_value['name']
            variant_widget.addItem(variant_item)
            
    # /SCENE_FILES SPECIFIC.
    def populate_tasks_list(self, type):
        """
        Populates Tasks list for both types. Only in sceneFiles Context.

        :param type: "shots" - "assets"
        """
        # Clear list selection.
        self.clear_lists("sceneFiles", type, 4) if type == "shots" else self.clear_lists("sceneFiles", type, 2)
        self.db_cache.clear_cache("tasks")

        # Determine the appropriate widgets based on context.
        selected_widget = self.scene_files_shots_department_QListWidget if type == "shots" else self.scene_files_assets_department_QListWidget
        task_widget = self.scene_files_shots_task_QListWidget if type == "shots" else self.scene_files_assets_task_QListWidget

        
        # Get Department from selection.
        self.department_item = selected_widget.currentItem()
        if not self.department_item:
            print("No department selected.")
            return
        self.department_name = self.department_item.text()
        

        # Get Task from Department selection.
        task_name = self.departments.get(self.department_name)
        if not task_name:
            print(f"Failed to retrieve valid task data for Department: {self.department_name}")
            return
        
        # Clear Cache and get task from Department selection.
        self.tasks = self.db_cache.get_tasks(task_name['department_id'])

        # Populate Task list.
        for task_key, task_value in self.tasks.items():
            task_item = task_value['name']
            task_widget.addItem(task_item)

    def populate_files_list(self, type):
        """
        Populates files list for both types. Only in sceneFiles Context.

        :param type: "shots" - "assets"
        """
        self.clear_lists("sceneFiles", type, 3)
        self.db_cache.clear_cache("files")

        # Determine the appropriate widgets based on context.
        task_widget = self.scene_files_shots_task_QListWidget if type == "shots" else self.scene_files_assets_task_QListWidget
        file_widget = self.scene_files_shots_files_QtreeWidget if type == "shots" else self.scene_files_assets_files_QtreeWidget
        
        # Get Taks from selection.
        self.task_item = task_widget.currentItem()
        if not self.task_item:
                print("No Task selected.")
                return
        self.task_name = self.task_item.text()

        # Get File from Task selection.
        file_name = self.tasks.get(self.task_name) # Already Retrieved from tasks function.
        if not file_name:
            print(f"Failed to retrieve valid file data for Task: {self.task_name}")
            return

        
        self.files = self.db_cache.get_files(file_name['task_id'])
        if not self.files:
                    print(f"No Files found for Task ID: {file_name['task_id']}")
                    return
        
        # Extract sqlite3.Row objects into a list.
        files_list = list(self.files.values())
        sorted_files = sorted(files_list, key=lambda x: x['version'], reverse=True)

        for file_info in sorted_files:
            version = f"{file_info['version']:03}"
            comment = file_info['comment'] if file_info['comment'] is not None else ""
            type = file_info['file_type'] if file_info['file_type'] is not None else ""
            date = file_info['date'] if file_info['date'] is not None else ""
            # user = file['user'] if file['user'] is not None else ""
            snapshot = file_info['snapshot'] if file_info['snapshot'] is not None else ""

            tree_item = QTreeWidgetItem(file_widget)
            custom_widget = SceneFileItemWidget(version, type, comment, user="R.Zandarin", date=date, snapshot=snapshot)
            file_widget.setItemWidget(tree_item, 0, custom_widget)

    # /USD_CONFIG SPECIFIC.
    def populate_usds_list(self, type):
        """
        Populates asset/department/setVar/variant/usd_version list for both types. Only in usdConfig Context.

        :param type: "shots" - "assets"
        """
        # Clear list selection.
        self.clear_lists("usdConfig", type, 4)

        # Determine the appropriate widgets based on context.
        selected_widget = self.usd_config_shots_department_QListWidget if type == "shots" else self.usd_config_assets_variant_QListWidget
        usd_widget = self.usd_config_shots_variantVersions_QtreeWidget if type == "shots" else self.usd_config_assets_variantVersions_QtreeWidget

        if type == "shots":
            # UPDATE DEPARTMENT ITEM AND LIST.
            self.department_item = selected_widget.currentItem()
            self.department_name = self.department_item.text()

            department_name = self.departments.get(self.department_name)

            self.db_cache.clear_cache("sublayer_usds")
            self.usds = self.db_cache.get_sublayer_usds(department_name['department_id'])
        else:
            self.variant_item = selected_widget.currentItem()
            self.variant_name = self.variant_item.text()

            variant_name = self.variants.get(self.variant_name)

            self.db_cache.clear_cache("variant_usds")
            self.usds = self.db_cache.get_variant_usds(variant_name['var_id'])

        # Extract sqlite3.Row objects into a list.
        usds_list = list(self.usds.values())
        sorted_usds = sorted(usds_list, key=lambda x: x['version'], reverse=True)

        for file_info in sorted_usds:
            version = f"{file_info['version']:03}"
            comment = file_info['comment'] if file_info['comment'] is not None else ""
            date = file_info['date'] if file_info['date'] is not None else ""
            # user = file['user'] if file['user'] is not None else ""
            snapshot = file_info['snapshot'] if file_info['snapshot'] is not None else ""
            pinned = file_info['pinned'] if file_info['pinned'] is not None else ""

            tree_item = QTreeWidgetItem(usd_widget)
            custom_widget = UsdFileItemWidget(version, comment, user="R.Zandarin", date=date, pinned=pinned, snapshot=snapshot)
            usd_widget.setItemWidget(tree_item, 0, custom_widget)
        
        # Pass Latest version to details.
        latest_version = self.get_latest_version(mode="usdConfig", type=type)
        self.usd_config_asset_latest_version_QLabel.setText(latest_version)
       
    def populate_selection_details(self, context, type):
        if context == "usdConfig":
            type_widget_item = self.usd_config_assets_QtreeWidget.currentItem() if type =="assets" else self.usd_config_shots_QtreeWidget.currentItem()
        elif context == "sceneFiles":
            type_widget_item = self.scene_files_assets_QtreeWidget.currentItem() if type =="assets" else self.scene_files_shots_QtreeWidget.currentItem()
        
        if type_widget_item.parent() is not None:
            type_widget_parent_item = type_widget_item.parent()
            if type_widget_parent_item is not None:
                type_widget_parent_name = type_widget_parent_item.text(0)
                type_widget_name = type_widget_item.text(0)

                self.usd_config_asset_type_QLabel.setText(type_widget_parent_name)

                assets = self.db_cache.get_assets()
                selected_asset = assets.get(type_widget_name)
                selected_asset_description = selected_asset['description']

                self.usd_config_asset_description_QLabel.setText(selected_asset_description)
        else:
            self.usd_config_asset_type_QLabel.setText("")
            self.usd_config_asset_description_QLabel.setText("")
            self.usd_config_asset_latest_version_QLabel.setText("")
        
    def clear_lists(self, context, type, position):
        # Mapping context and type to specific widget lists.
        widgets_mapping = {
            ('sceneFiles', 'assets'): [
                self.scene_files_assets_QtreeWidget,
                self.scene_files_assets_department_QListWidget,
                self.scene_files_assets_task_QListWidget,
                self.scene_files_assets_files_QtreeWidget
            ],
            ('sceneFiles', 'shots'): [
                self.scene_files_shots_QtreeWidget,
                self.scene_files_shots_department_QListWidget,
                self.scene_files_shots_task_QListWidget,
                self.scene_files_shots_files_QtreeWidget
            ],
            ('usdConfig', 'assets'): [
                self.usd_config_assets_QtreeWidget,
                self.usd_config_assets_department_QListWidget,
                self.usd_config_assets_setVar_QListWidget,
                self.usd_config_assets_variant_QListWidget,
                self.usd_config_assets_variantVersions_QtreeWidget
            ],
            ('usdConfig', 'shots'): [
                self.usd_config_shots_QtreeWidget,
                self.usd_config_shots_department_QListWidget,
                self.usd_config_shots_variantVersions_QtreeWidget
            ]
        }

        # Get the correct list of widgets based on context and type.
        widgets_to_clear = widgets_mapping.get((context, type))

        # Clear the widgets from the specified position onwards.
        if widgets_to_clear and position < len(widgets_to_clear):
            for widget in widgets_to_clear[position:]:
                widget.clear()
        else:
            print("not being executed")

    # Menus.
    def create_menu_bar(self):
        self.menu_bar = self.main_window.menuBar()

        # Create a Project menu.
        self.project_menu = self.menu_bar.addMenu('Project')
        self.set_project_action = QAction('Set Project')
        self.set_project_action.triggered.connect(self.set_project_directory)  # Connect to the slot
        self.project_menu.addAction(self.set_project_action)

        # Asset submenu.
        self.asset_menu = self.menu_bar.addMenu('Asset')
        self.asset_menu_create = QAction('Create Asset')
        self.asset_menu_create.triggered.connect(self.create_asset_usd) 
        self.asset_menu.addAction(self.asset_menu_create)
        self.asset_menu_delete = QAction('Delete Asset')
        self.asset_menu_delete.triggered.connect(self.delete_asset_usd)
        self.asset_menu.addAction(self.asset_menu_delete)
        self.asset_menu_delete_all = QAction('Delete all Assets')
        self.asset_menu_delete_all.triggered.connect(lambda: self.delete_asset_usd(all=True))
        self.asset_menu.addAction(self.asset_menu_delete_all)

        # Sequence submenu.
        self.sequence_menu = self.menu_bar.addMenu('Sequence')
        self.sequence_menu_create = QAction('Create Sequence')
        self.sequence_menu_create.triggered.connect(self.create_sequence_usd)
        self.sequence_menu.addAction(self.sequence_menu_create)
        self.sequence_menu_delete = QAction('Delete Sequence')
        self.sequence_menu_delete.triggered.connect(self.delete_sequence_usd)
        self.sequence_menu.addAction(self.sequence_menu_delete)
        self.sequence_menu_delete_all = QAction('Delete all Sequences')
        self.sequence_menu_delete_all.triggered.connect(lambda: self.delete_sequence_usd(all=True))
        self.sequence_menu.addAction(self.sequence_menu_delete_all)

        # Shot submenu.
        self.shot_menu = self.menu_bar.addMenu('Shot')
        self.shot_menu_create = QAction('Create Shot')
        self.shot_menu_create.triggered.connect(self.create_shot_usd)  # Connect to the slot
        self.shot_menu.addAction(self.shot_menu_create)
        self.shot_menu_delete = QAction('Delete Shot')
        self.shot_menu_delete.triggered.connect(self.delete_shot_usd)  # Connect to the slot
        self.shot_menu.addAction(self.shot_menu_delete)
        self.shot_menu_delete_all = QAction('Delete all Shot')
        self.shot_menu_delete_all.triggered.connect(lambda: self.delete_shot_usd(all=True))  # Connect to the slot
        self.shot_menu.addAction(self.shot_menu_delete_all)

        # Department submenu.
        self.department_menu = self.menu_bar.addMenu('Department')
        self.department_menu.menuAction().setVisible(False)
        self.department_menu_create = QAction('Edit Departments')
        self.department_menu_create.triggered.connect(self.edit_departments_usd)  # Connect to the slot
        self.department_menu.addAction(self.department_menu_create)

        # setVar submenu.
        self.setVar_menu = self.menu_bar.addMenu('SetVariant')
        self.setVar_menu.menuAction().setVisible(False)
        self.setVar_menu_create = QAction('Create SetVariant')
        self.setVar_menu_create.triggered.connect(self.create_setVar_usd)  # Connect to the slot
        self.setVar_menu.addAction(self.setVar_menu_create)
        self.setVar_menu_delete = QAction('Delete SetVariant')
        self.setVar_menu_delete.triggered.connect(self.delete_setVar_usd)  # Connect to the slot
        self.setVar_menu.addAction(self.setVar_menu_delete)
        self.setVar_menu_delete_all = QAction('Delete all SetVariants')
        self.setVar_menu_delete_all.triggered.connect(lambda: self.delete_setVar_usd(all=True))  # Connect to the slot
        self.setVar_menu.addAction(self.setVar_menu_delete_all)

        # Variant submenu.
        self.variant_menu = self.menu_bar.addMenu('Variant')
        self.variant_menu.menuAction().setVisible(False)
        self.variant_menu_create = QAction('Create Variant')
        self.variant_menu_create.triggered.connect(self.create_variant_usd)  # Connect to the slot
        self.variant_menu.addAction(self.variant_menu_create)
        self.variant_menu_delete = QAction('Delete Variant')
        self.variant_menu_delete.triggered.connect(self.delete_variant_usd)  # Connect to the slot
        self.variant_menu.addAction(self.setVar_menu_delete)
        self.variant_menu_delete_all = QAction('Delete all Variants')
        self.variant_menu_delete_all.triggered.connect(lambda: self.delete_variant_usd(all=True))  # Connect to the slot
        self.variant_menu.addAction(self.variant_menu_delete_all)
        self.variant_menu_default_variant = QAction('Set as Default Variant')
        self.variant_menu_default_variant.triggered.connect(self.set_default_variant)  # Connect to the slot
        self.variant_menu.addAction(self.variant_menu_default_variant)

        # Task submenu.
        self.task_menu = self.menu_bar.addMenu('Task')
        self.task_menu.menuAction().setVisible(False)
        self.task_menu_create = QAction('Create Task')
        self.task_menu_create.triggered.connect(self.create_task_folder)  # Connect to the slot
        self.task_menu.addAction(self.task_menu_create)
        self.task_menu_delete = QAction('Delete Task')
        self.task_menu_delete.triggered.connect(self.delete_task_folder)  # Connect to the slot
        self.task_menu.addAction(self.task_menu_delete)
        self.task_menu_delete_all = QAction('Delete all Tasks')
        self.task_menu_delete_all.triggered.connect(lambda: self.delete_task_folder(all=True))  # Connect to the slot
        self.task_menu.addAction(self.task_menu_delete_all)

        # File submenu.
        self.file_menu = self.menu_bar.addMenu('File')
        self.file_menu.menuAction().setVisible(False)
        self.file_menu_create = QAction('Build Asset File')
        self.file_menu_create.triggered.connect(self.create_file)  # Connect to the slot
        self.file_menu.addAction(self.file_menu_create)
        self.file_menu_delete = QAction('Delete File')
        self.file_menu_delete.triggered.connect(self.delete_file)  # Connect to the slot
        self.file_menu.addAction(self.file_menu_delete)
        self.file_menu_delete_all = QAction('Delete all Files')
        self.file_menu_delete_all.triggered.connect(lambda: self.delete_file(all=True))  # Connect to the slot
        self.file_menu.addAction(self.file_menu_delete_all)

        # variantversion submenu.
        self.variantVersion_menu = self.menu_bar.addMenu('variantVersion_menu')
        self.variantVersion_menu.menuAction().setVisible(False)
        self.variantVersion_menu_create = QAction('Pin Version')
        self.variantVersion_menu_create.triggered.connect(lambda: self.pin_usd_version(mode="pin"))  # Connect to the slot
        self.variantVersion_menu.addAction(self.variantVersion_menu_create)
        self.variantVersion_menu_unpin = QAction('Unpin Version')
        self.variantVersion_menu_unpin.triggered.connect(lambda: self.pin_usd_version(mode="unpin"))  # Connect to the slot
        self.variantVersion_menu.addAction(self.variantVersion_menu_unpin)

    def on_context_menu(self, point, context, type=None):
        # Mapping context to widgets and menus.
        context_map = {
            "sceneFiles_shots": {
                "menu": lambda item: self.sequence_menu if item.parent() is None else self.shot_menu,
                "widget": self.scene_files_shots_QtreeWidget
            },
            "sceneFiles_assets": {
                "menu": self.asset_menu,
                "widget": self.scene_files_assets_QtreeWidget
            },
            "sceneFiles_department": {
                "menu": self.department_menu,
                "widget": lambda t: self.scene_files_shots_department_QListWidget if t == "shots" else self.scene_files_assets_department_QListWidget
            },
            "usdConfig_shots": {
                "menu": lambda item: self.sequence_menu if item.parent() is None else self.shot_menu,
                "widget": self.usd_config_shots_QtreeWidget
            },
            "usdConfig_assets": {
                "menu": self.asset_menu,
                "widget": self.usd_config_assets_QtreeWidget
            },
            "usdConfig_department": {
                "menu": self.department_menu,
                "widget": lambda t: self.usd_config_shots_department_QListWidget if t == "shots" else self.usd_config_assets_department_QListWidget
            },
            "task": {
                "menu": self.task_menu,
                "widget": lambda t: self.scene_files_shots_task_QListWidget if t == "shots" else self.scene_files_assets_task_QListWidget
            },
            "files": {
                "menu": self.file_menu,
                "widget": lambda t: self.scene_files_shots_files_QtreeWidget if t == "shots" else self.scene_files_assets_files_QtreeWidget
            },
            "setVar": {
                "menu": self.setVar_menu,
                "widget": self.usd_config_assets_setVar_QListWidget
            },
            "variant": {
                "menu": self.variant_menu,
                "widget": self.usd_config_assets_variant_QListWidget
            },
            "variantVersion": {
                "menu": self.variantVersion_menu,
                "widget": lambda t: None if t == "shots" else self.usd_config_assets_variantVersions_QtreeWidget
            }
        }

        # Get the context details
        context_details = context_map.get(context)
        if context_details:
            widget = context_details['widget'](type) if callable(context_details['widget']) else context_details['widget']
            menu = context_details['menu'](self.scene_files_shots_QtreeWidget.currentItem()) if callable(context_details['menu']) else context_details['menu']
            if widget and menu:
                menu.exec_(widget.viewport().mapToGlobal(point))

    # Asset SubMenu.
    def create_asset_usd(self):
        dialog = AssetInputDialog()

        if dialog.exec_() == QDialog.Accepted:
            self.asset_name, self.asset_type, self.asset_description = dialog.get_inputs()

        if self.asset_name:
            self.um.create_usd_entity(entity_type="asset", name=self.asset_name, format=".usda", asset_type=self.asset_type, description=self.asset_description)
            self.refresh("asset")

    def delete_asset_usd(self, all=None):
        if all is not None:
            all_items = self.get_all_items(self.scene_files_assets_QtreeWidget)

            for item in all_items:
                self.um.delete_usd_entity(entity_type="asset", name=item)

            self.refresh("asset")
        else:
            asset_item = self.scene_files_assets_QtreeWidget.currentItem()
            asset_name = asset_item.text(0)
            
            self.um.delete_usd_entity(entity_type="asset", name=asset_name)
            self.refresh("asset")
    
    # Sequence SubMenu.
    def create_sequence_usd(self):

        self.sequence_name, ok = QInputDialog.getText(None, "Input Dialog", "Enter Sequence name:")

        if ok and self.sequence_name:
            self.um.create_usd_entity(entity_type="sequence", name=self.sequence_name, format=".usda", description="")
            self.refresh("sequence")
    
    def delete_sequence_usd(self, all=None):
        if all is not None:
            all_items = self.get_all_child_items_with_parents(self.scene_files_shots_QtreeWidget)
            for item in all_items:
                shot_item = item['child']
                sequence_item = item['parent']
                self.um.delete_usd_entity(entity_type="shot", name=shot_item, seq_name=sequence_item)
            for item in all_items:
                shot_item = item['child']
                sequence_item = item['parent']
                self.um.delete_usd_entity(entity_type="sequence", name=sequence_item)
                
            self.refresh("sequence")
        else:
            sequence_item = self.scene_files_shots_QtreeWidget.currentItem()
            sequence_name = sequence_item.text(0)
            
            self.um.delete_usd_entity(entity_type="sequence", name=sequence_name)

            children = []
            for i in range(sequence_item.childCount()):
                child_item = sequence_item.child(i)
                child_name = child_item.text(0)
                self.um.delete_usd_entity(entity_type="shot", name=child_name, seq_name=sequence_name)

            self.refresh("sequence")

    # Shot SubMenu.
    def create_shot_usd(self):

        self.shot_name, ok = QInputDialog.getText(None, "Input Dialog", "Enter Shot name:")

        if ok and self.shot_name:
            self.um.create_usd_entity(entity_type="shot", name=self.shot_name, format=".usda", description="", framerange="1001-1045", seq_name=self.sequence_name)
            self.refresh("shot")
    
    def delete_shot_usd(self, all=None):
        # Get the selected Sequence from the List.
        sequence_item = self.scene_files_shots_QtreeWidget.currentItem()
        sequence_name = sequence_item.text(0)

        # Conditional if All is set to True.
        if all is not None:
            children = []
            for i in range(sequence_item.childCount()):
                child_item = sequence_item.child(i)
                child_name = child_item.text(0)
                self.um.delete_usd_entity(entity_type="shot", name=child_name, seq_name=sequence_name)

            self.refresh("shot")

        # Conditional if All is None.
        else:
            shot_item = self.scene_files_shots_QtreeWidget.currentItem()
            shot_name = shot_item.text(0)
            
            self.um.delete_usd_entity(entity_type="shot", name=shot_name, seq_name=sequence_name)
            self.refresh("shot")


    # Department SubMenu.
    def edit_departments_usd(self):
        # Conditional if Assets Button is checked.
        if self.scene_files_assets_QPushButton.isChecked():
            # Gets the Selected Item from the Assets List.

            asset_selected_item = self.scene_files_assets_QtreeWidget.currentItem()        

            selected_text = asset_selected_item.text(0)
            asset_name = self.assets.get(selected_text)
            self.departments = self.db_cache.get_asset_departments(asset_name['id'])
            
            department_selection = []

            for department_key, department_value in self.departments.items():
                department_selection.append(department_value['name'])
                    
            dialog = DepartmentSelectionDialog(department_selection)

            if dialog.exec_() == QDialog.Accepted:
                selected_info = dialog.get_selected_departments()
                print(selected_info)
                

                for department_name, is_selected, index in selected_info:
                    existing_department = self.departments.get(department_name)
                    print("existing_department", existing_department)
                    if is_selected and existing_department is None: # Create New Department.
                        self.um.create_usd_sublayer(entity_type="asset", parent_name=self.asset_name, sublayer_name=department_name)
                        print("create new department")
                        self.refresh("department")
                    elif not is_selected and existing_department is not None: # Delete Department if Exists.
                        self.um.delete_usd_sublayer(entity_type="asset", parent_name=self.asset_name, sublayer_name=department_name)
                        print(f"deleted {department_name} department")
                        self.refresh("department")

                
        # Conditional if Shots Button is checked.
        elif self.scene_files_shots_QPushButton.isChecked():

            # Get selected Item from the Shots List.
            self.list_item = self.scene_files_shots_QtreeWidget.currentItem()
            self.list_name = self.list_item.text(0)

            # Conditional if Item is Sequence.
            if self.list_item.parent() is None:

                self.department_name, ok = QInputDialog.getText(None, "Input Dialog", "Enter department name:")

                if ok and self.department_name:
                    self.um.create_usd_sublayer(entity_type="sequence", parent_name=self.list_name, sublayer_name=self.department_name) # Passes Selected Item of the List as Parent for the Department.
                    self.refresh("department")

            # Conditional if Item is Shot.
            elif self.list_item.parent() is not None:

                self.department_name, ok = QInputDialog.getText(None, "Input Dialog", "Enter department name:")

                if ok and self.department_name:
                    self.um.create_usd_sublayer(entity_type="shot", parent_name=self.list_name, sublayer_name=self.department_name, seq_name=self.sequence_name) # Passes Selected Item of the List as Parent for the Department.
                    self.refresh("department")
            else:
                return
            
            self.main_window.status_bar.showMessage(f"created new department {self.department_name} for {self.list_name}", 5000)
        else:
            return


    # setVar SubMenu.
    def create_setVar_usd(self):
        if self.usd_config_assets_QPushButton.isChecked():

            dialog = CustomQDialog(text="setVar Name:")

            if dialog.exec_() == QDialog.Accepted:
                self.setVar_name = dialog.get_inputs()

            if self.setVar_name:
                self.um.create_usd_setVar(department_name=self.department_name, asset_name=self.asset_name, name=self.setVar_name)
                self.refresh("setVar")

            self.main_window.status_bar.showMessage(f"created new setVar {self.setVar_name} for {self.department_name}", 5000)
 
    def delete_setVar_usd(self, all=None):
        pass


    # Variant SubMenu.
    def create_variant_usd(self):
        if self.usd_config_assets_QPushButton.isChecked():

            dialog = CustomQDialog(text="Variant Name:")

            if dialog.exec_() == QDialog.Accepted:
                self.variant_name = dialog.get_inputs()

            if self.variant_name:
                self.um.create_variant(setVar_name=self.setVar_name, asset_name=self.asset_name, name=self.variant_name, department_name=self.department_name)
                self.refresh("variant")

            self.main_window.status_bar.showMessage(f"created new variant {self.variant_name} for {self.setVar_name}", 5000)

    def delete_variant_usd(self, all=None):
        pass

    def set_default_variant(self):
        
        variant_item = self.usd_config_assets_variant_QListWidget.currentItem() if self.usd_config_QPushButton.isChecked() else self.scene_files_assets_department_QListWidget.currentItem()
        variant_name = variant_item.text()

        if variant_name is not None:
            self.um.set_default_variant(default_variant=variant_name, asset_name=self.asset_name, department_name=self.department_name, setVar_name=self.setVar_name)
            print(f"using {variant_name} as default variant for {self.setVar_name}")

    # Task SubMenu.
    def create_task_folder(self):
        # Conditional if Shots Button is checked.
        if self.scene_files_shots_QPushButton.isChecked():
            if self.list_item.parent() is None:
                
                dialog = CustomQDialog(text="Task Name:")

                if dialog.exec_() == QDialog.Accepted:
                    self.task_name = dialog.get_inputs()

                if self.task_name:
                    self.fm.create_task_folder(task_type="department", name=self.task_name, department_type="sequence", sequence_name=self.sequence_name, department_name=self.department_name)
                    self.refresh("task")
            else: 

                dialog = CustomQDialog(text="Task Name:")

                if dialog.exec_() == QDialog.Accepted:
                    self.task_name = dialog.get_inputs()

                if self.task_name:
                    self.fm.create_task_folder(task_type="department", name=self.task_name, department_type="shot", sequence_name=self.sequence_name, shot_name=self.shot_name)
                    self.refresh("task")

            self.main_window.status_bar.showMessage(f"created new task {self.task_name} for {self.department_name}", 5000)
        else:
            dialog = CustomQDialog(text="Task Name:")

            if dialog.exec_() == QDialog.Accepted:
                self.task_name = dialog.get_inputs()

            if self.task_name:
                self.fm.create_task_folder(name=self.task_name, department_name=self.department_name, software_name="maya", asset_name=self.asset_name)
            
            self.refresh("task")
        
    def delete_task_folder(self, all=None):
        pass
    
    
    # File SubMenu.
    def create_file(self):
        if self.scene_files_assets_QPushButton.isChecked():

            self.fm.create_file(mode="create", file_format=".ma", software_name="maya", comment="", asset_name=self.asset_name,
                                 department_name=self.department_name, task_name=self.task_name)
            
            self.refresh("file")

        else:
            # item = self.scene_files_shots_QtreeWidget.currentItem()
            # if item.parent() is None:
            pass

    def delete_file(self, all=None):
        pass


    # Action buttons. 
    def on_publish_version_button_clicked(self):
        dialog = GeoSanityCheck()
        if dialog.exec_() == QDialog.Accepted:
            comment_text = self.usd_config_comment_QLineEdit.text()
            self.um.create_usd_variantVersion(setVar_name=self.setVar_name, asset_name=self.asset_name, department_name=self.department_name, var_name=self.variant_name, comment=comment_text)
            self.usd_config_comment_QLineEdit.setText("")
            
            if self.usd_config_assets_variantVersions_QtreeWidget.topLevelItem(0) is not None:
                variantVersions_item = self.usd_config_assets_variantVersions_QtreeWidget.topLevelItem(0)
                variantVersions_widget = self.usd_config_assets_variantVersions_QtreeWidget.itemWidget(variantVersions_item, 0)
                variantVersions_version = variantVersions_widget.get_version() # Returns Text
                variantVersion_latestVersion = int(variantVersions_version) + 1
                variantVersion_latestVersion = str(variantVersion_latestVersion).zfill(3)
            else:
                variantVersion_latestVersion = "001"
            QMessageBox.information(None, "Publish", f"Publish {self.setVar_name} v{variantVersion_latestVersion} successfully", QMessageBox.Ok)
            self.refresh("usds")
            
    def on_save_version_button_clicked(self):
        if self.scene_files_assets_QPushButton.isChecked():
            asset_item = self.scene_files_assets_QtreeWidget.currentItem()
            asset_name = asset_item.text(0)

            department_item = self.scene_files_assets_department_QListWidget.currentItem()
            department_name = department_item.text()

            task_item = self.scene_files_assets_task_QListWidget.currentItem()
            task_name = task_item.text()

            comment_text = self.scene_files_comment_QLineEdit.text()
            
            self.fm.create_file(mode="save", file_format=".ma", software_name="maya", comment=comment_text, asset_name=asset_name, department_name=department_name, task_name=task_name)
            
            file_item = self.scene_files_assets_files_QtreeWidget.topLevelItem(0)
            file_item_widget = self.scene_files_assets_files_QtreeWidget.itemWidget(file_item, 0)
            file_version = file_item_widget.get_version() # Returns Text
            file_latest_version = int(file_version) + 1
            file_latest_version = str(file_latest_version).zfill(3)

            self.scene_files_comment_QLineEdit.setText("")
            QMessageBox.information(None, "Save", f"Saved {asset_name}_{department_name}_{task_name}_v{file_latest_version} successfully", QMessageBox.Ok)
            self.refresh("file")
            
    def on_load_version_button_clicked(self):
        print("on_load_version_button_clicked called")
        if self.scene_files_assets_QPushButton.isChecked():
            asset_item = self.scene_files_assets_QtreeWidget.currentItem()
            asset_name = asset_item.text(0)

            department_item = self.scene_files_assets_department_QListWidget.currentItem()
            department_name = department_item.text()

            task_item = self.scene_files_assets_task_QListWidget.currentItem()
            task_name = task_item.text()

            files_item = self.scene_files_assets_files_QtreeWidget.currentItem()
            files_item_widget = self.scene_files_assets_files_QtreeWidget.itemWidget(files_item, 0)
            files_version = files_item_widget.get_version()
            files_type = files_item_widget.get_type()
            
            self.fm.load_file(file_version=files_version, file_format=files_type, asset_name=asset_name, department_name=department_name, task_name=task_name)
            self.refresh("file")

    def selection_cache(self, context, type, list_type, widget, item=None, name=None, Qlist=None):
        # Check if the current item exists in the widget to prevent errors
        current_item = widget.currentItem()
        if not current_item:
            return  # Early return if there is no selected item

        # Dictionary to map the context and type to the attributes
        cache_map = {
            ("sceneFiles", "assets", "assets"): ("asset_item", "asset_name"),
            ("sceneFiles", "assets", "departments"): ("department_item", "department_name"),
            ("sceneFiles", "assets", "tasks"): ("task_item", "task_name"),
            ("sceneFiles", "assets", "files"): ("file_item", "file_name"),

            ("sceneFiles", "shots", "sequence"): ("sequence_item", "sequence_name"),
            ("sceneFiles", "shots", "shot"): ("shot_item", "shot_name"),
            ("sceneFiles", "shots", "departments"): ("department_item", "department_name"),
            ("sceneFiles", "shots", "tasks"): ("task_item", "task_name"),
            ("sceneFiles", "shots", "files"): ("file_item", "file_name"),

            ("usdConfig", "assets", "assets"): ("asset_item", "asset_name"),
            ("usdConfig", "assets", "departments"): ("department_item", "department_name"),
            ("usdConfig", "assets", "setVars"): ("setVar_item", "setVar_name"),
            ("usdConfig", "assets", "variants"): ("variant_item", "variant_name"),
            ("usdConfig", "assets", "variantVersions"): ("variantVersion_item", "variantVersion_name"),
            
            ("usdConfig", "shots", "sequence"): ("sequence_item", "sequence_name"),
            ("usdConfig", "shots", "shot"): ("shot_item", "shot_name"),
            ("usdConfig", "shots", "departments"): ("department_item", "department_name"),
            ("usdConfig", "shots", "variantVersions"): ("variantVersion_item", "variantVersion_name"),

        }

        # Get attribute names from the map
        attributes = cache_map.get((context, type, list_type), None)
        if attributes:
            item_attr, text_attr = attributes
            # Cache the item and the text from the item
            setattr(self, item_attr, current_item)
            if Qlist is not True:
                setattr(self, text_attr, current_item.text(0))
            else:  
                 setattr(self, text_attr, current_item.text())

    # Pin / Un-pin version.
    def pin_usd_version(self, mode):

        asset_item = self.usd_config_assets_QtreeWidget.currentItem()
        asset_name = asset_item.text(0)
        asset_info = self.db.get_asset(asset_name)
        asset_id = asset_info['id']

        department_item = self.usd_config_assets_department_QListWidget.currentItem()
        department_name = department_item.text()
        department_info = self.db.get_department("asset", asset_id, department_name)
        department_id = department_info['department_id']

        setVar_item = self.usd_config_assets_setVar_QListWidget.currentItem()
        setVar_name = setVar_item.text()
        setVar_info = self.db.get_setVar(department_id, setVar_name)
        setVar_path = setVar_info['usd_path']
        setVar_id = setVar_info['setVar_id']

        var_item = self.usd_config_assets_variant_QListWidget.currentItem()
        var_name = var_item.text()
        var_info = self.db.get_variant(setVar_id, var_name)
        var_id = var_info['var_id']


        variantVersions_item = self.usd_config_assets_variantVersions_QtreeWidget.currentItem()
        variantVersions_widget = self.usd_config_assets_variantVersions_QtreeWidget.itemWidget(variantVersions_item, 0)
        variantVersions_version = variantVersions_widget.get_version() # Returns Text

        variantVersion_info = self.db.get_variantVersion("variant", var_id, variantVersions_version)
        variantVersion_id = variantVersion_info['variantVersion_id']
        variantversion_path = variantVersion_info['usd_path'] 
        
        if mode == "pin":
        
            variantVersions_widget.set_border_color("red")

            self.db.update_variantVersion(variantVersion_id=variantVersion_id, pinned=True)

            self.um.edit_usd_setVar(setVar_path=setVar_path, setVar_name=setVar_name, var_name=var_name, variantVersion_path=variantversion_path)
        elif mode == "unpin":
            variantVersions_widget.set_border_color("")

            self.db.update_variantVersion(variantVersion_id=variantVersion_id, pinned=False)

            highest_version = 0
            highest_version_item = None

            # Iterate over each top-level item in the QTreeWidget
            for i in range(self.usd_config_assets_variantVersions_QtreeWidget.topLevelItemCount()):
                # Get the QTreeWidgetItem at the current index
                tree_item = self.usd_config_assets_variantVersions_QtreeWidget.topLevelItem(i)
                
                # Assuming you have a custom widget in the first column, retrieve the widget
                version_widget = self.usd_config_assets_variantVersions_QtreeWidget.itemWidget(tree_item, 0)
                
                item_version_str = version_widget.get_version()
                try:
                    item_version = int(item_version_str)
                    
                    # Compare and find the highest version number
                    if item_version >= highest_version:
                        highest_version = item_version
                        highest_version_item = tree_item

                except ValueError:
                    print(f"Could not convert version '{item_version_str}' to integer.")
            
            latest_item_version = str(highest_version).zfill(3)
            latest_variantVersion_info = self.db.get_variantVersion("variant", var_id, latest_item_version)
            variantVersion_id = latest_variantVersion_info['variantVersion_id']
            variantversion_path = latest_variantVersion_info['usd_path'] 

            self.um.edit_usd_setVar(setVar_path=setVar_path, setVar_name=setVar_name, var_name=var_name, variantVersion_path=variantversion_path)


        self.populate_usds_list(type="assets")
    

    # Auxiliary functions.
    def get_latest_version(self, mode, type):
        if mode == "usdConfig":
            if type == "assets":
                highest_version = 0
                
                # Iterate over each top-level item in the QTreeWidget
                for i in range(self.usd_config_assets_variantVersions_QtreeWidget.topLevelItemCount()):
                    # Get the QTreeWidgetItem at the current index
                    tree_item = self.usd_config_assets_variantVersions_QtreeWidget.topLevelItem(i)
                    
                    # Assuming you have a custom widget in the first column, retrieve the widget
                    version_widget = self.usd_config_assets_variantVersions_QtreeWidget.itemWidget(tree_item, 0)
                    
                    item_version_str = version_widget.get_version()
                    try:
                        item_version = int(item_version_str)
                        
                        # Compare and find the highest version number
                        if item_version >= highest_version:
                            highest_version = item_version
                            print(highest_version)
                    except ValueError:
                        print(f"Could not convert version '{item_version_str}' to integer.")

        return str(highest_version).zfill(3)

    def toggle_qactions(self):
        if self.scene_files_assets_QPushButton.isChecked():
            self.asset_menu.menuAction().setVisible(True)
            self.department_menu.menuAction().setVisible(True)
            self.setVar_menu.menuAction().setVisible(True)
            self.variant_menu.menuAction().setVisible(True)
            self.file_menu.menuAction().setVisible(True)

            self.sequence_menu.menuAction().setVisible(False)
            self.shot_menu.menuAction().setVisible(False)

        else:
            self.asset_menu.menuAction().setVisible(False)
            self.setVar_menu.menuAction().setVisible(False)
            self.variant_menu.menuAction().setVisible(False)
            
            self.sequence_menu.menuAction().setVisible(True)
            self.shot_menu.menuAction().setVisible(True)
            self.department_menu.menuAction().setVisible(True)
            self.file_menu.menuAction().setVisible(True)

    def get_all_child_items_with_parents(self, tree_widget):
        """
        Returns a list of dictionaries, each containing the name of a child item 
        and the name of its parent in the QTreeWidget.
        """
        child_items_with_parents = []

        def recurse(parent_item):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                # Store child name along with parent's name
                child_items_with_parents.append({"child": child.text(0), "parent": parent_item.text(0)})
                recurse(child)  # Recursively process children

        for i in range(tree_widget.topLevelItemCount()):
            parent_item = tree_widget.topLevelItem(i)
            recurse(parent_item)  # Start recursion for each top-level item

        return child_items_with_parents

    def refresh(self, type):
        """
        Refreshes QTree's and Qlists in the window.

        :param type: "asset", "sequence", "shot", "setVar", "variant", "task", "file"
        """
        if self.scene_files_QPushButton.isChecked():
            # Conditional if assets button is checked
            if self.scene_files_assets_QPushButton.isChecked():
                if type == "asset":
                    QTimer.singleShot(10, lambda: self.populate_assets_list(context="sceneFiles")) # Add delay of 10 miliseconds.
                elif type == "department":
                    QTimer.singleShot(10, lambda: self.populate_departments_list(context="sceneFiles", type="assets")) # Add delay of 10 miliseconds.
                elif type == "task":
                    QTimer.singleShot(10, lambda: self.populate_tasks_list(type="assets")) # Add delay of 10 miliseconds.
                elif type == "file":
                    QTimer.singleShot(10, lambda: self.populate_files_list(type="assets")) # Add delay of 10 miliseconds.
            
            # Conditional if shots button is checked
            elif self.scene_files_shots_QPushButton.isChecked():
                if type == "sequence" or type == "shot":
                    QTimer.singleShot(10, lambda: self.populate_shots_list(context="sceneFiles")) # Add delay of 10 miliseconds.
                elif type == "department":
                    QTimer.singleShot(10, lambda: self.populate_departments_list(context="sceneFiles", type="shots")) # Add delay of 10 miliseconds.
                elif type == "task":
                    QTimer.singleShot(10, lambda: self.populate_tasks_list(type="shots")) # Add delay of 10 miliseconds.
                elif type == "file":
                    QTimer.singleShot(10, lambda: self.populate_files_list(type="shots")) # Add delay of 10 miliseconds.
        else:
            if self.usd_config_assets_QPushButton.isChecked():
                if type == "sequence" or type == "shot":
                    QTimer.singleShot(10, lambda: self.populate_shots_list(context="usdConfig")) # Add delay of 10 miliseconds.
                elif type == "department":
                    QTimer.singleShot(10, lambda: self.populate_departments_list(context="usdConfig", type="assets")) # Add delay of 10 miliseconds.
                elif type == "setVar":
                    QTimer.singleShot(10, self.populate_setVars_list) # Add delay of 10 miliseconds.
                elif type == "variant":
                    QTimer.singleShot(10, self.populate_variants_list) # Add delay of 10 miliseconds.
                elif type == "usds":
                    QTimer.singleShot(10, lambda: self.populate_usds_list(type="assets")) # Add delay of 10 miliseconds.
            elif self.usd_config_shots_QPushButton.isChecked():
                pass
        
        self.main_window.status_bar.showMessage(f"refresh", 5000) 

    def get_icons(self, type, name):
        icon_path = os.path.join(self.icons_dir, f"{type}_{name}_icon.png")
        icon_item = QIcon(icon_path)
        return icon_item

    def show(self):
        self.main_window.show()  # Show the main window

if __name__ == "__main__":
    mercury_window = MercuryWindow()
    mercury_window.show()