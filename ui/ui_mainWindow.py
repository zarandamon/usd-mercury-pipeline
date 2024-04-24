from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QButtonGroup, QPushButton, QStackedWidget, QLabel,
                                QLineEdit, QTreeWidget, QGridLayout, QListWidget, QGroupBox, QPushButton, QSizePolicy)

running_in_maya = False

try:
    import maya.cmds as cmds
    running_in_maya = True
except ImportError:
    print("Not running in Maya, certain functionalities will be disabled.")


class MainWindow(QMainWindow):
    """
    The MainWindow class serves as the primary window for the USD Mercury Pipeline application. 
    It is responsible for initializing the user interface, including creating and managing layouts, 
    widgets, and connections between the UI components. The main window is organized around a 
    central widget containing a QVBoxLayout, with additional layouts for different functional areas 
    of the application, such as scene file management and USD configuration.

    This class facilitates the switching between different UI modes (e.g., SceneFiles, USD Config) 
    through a set of toggleable QPushButton instances. Each mode presents a different set of options 
    and configurations to the user, organized within a QStackedWidget for dynamic content switching.
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent) if running_in_maya is True else super().__init__()
        self.setWindowTitle("USD Mercury Pipeline")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(self.app_style_sheet())
        self.init_ui()
        
    def init_ui(self):
        """
        Create the main window frame
        """
        # Create Status Bar 
        self.status_bar = self.statusBar()

        # Create central widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.main_layout = QVBoxLayout(self.centralWidget)

        # Create mode buttons
        self.mode_buttons_layout = QHBoxLayout()
        self.mode_buttons_layout.addStretch(1)
        self.mode_buttons_layout.setSpacing(0)
        self.button_group = QButtonGroup(self.centralWidget)
        
        self.scene_files_button = QPushButton("SceneFiles")
        self.scene_files_button.setObjectName("scene_files_QPushButton")
        self.scene_files_button.setCheckable(True)
        self.scene_files_button.setChecked(True)
        
        self.usd_config_button = QPushButton("USD Config")
        self.usd_config_button.setObjectName("usd_config_QPushButton")
        self.usd_config_button.setCheckable(True)
        
        # Add mode buttons to centralWidget
        self.button_group.addButton(self.scene_files_button)
        self.button_group.addButton(self.usd_config_button)
        
        self.mode_buttons_layout.addWidget(self.scene_files_button)
        self.mode_buttons_layout.addWidget(self.usd_config_button)

        self.mode_buttons_layout.addStretch(1)
        
        self.main_layout.addLayout(self.mode_buttons_layout)

        # Create StackedWidget for modes
        self.mode_stackedWidget = QStackedWidget()
        self.main_layout.addWidget(self.mode_stackedWidget)

        # Link Pages to Functions
        scene_files_widget = self.scene_files_layout()
        usd_config_widget = self.usd_config_layout()
        
        # Add Pages to mode_StackedWidget
        self.mode_stackedWidget.addWidget(scene_files_widget)
        self.mode_stackedWidget.addWidget(usd_config_widget)

        # Switch Index for mode_StackedWidget
        self.scene_files_button.clicked.connect(lambda: self.mode_stackedWidget.setCurrentIndex(0))
        self.usd_config_button.clicked.connect(lambda: self.mode_stackedWidget.setCurrentIndex(1))
   
    def scene_files_layout(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Buttons Container Layout
        buttons_container_layout = QHBoxLayout()

        # 1st Column: Buttons Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(0)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # Create buttons
        self.scene_files_assets_button = QPushButton("Assets")
        self.scene_files_assets_button.setObjectName("scene_files_assets_QPushButton")
        self.scene_files_assets_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.scene_files_shots_button = QPushButton("Shots")
        self.scene_files_shots_button.setObjectName("scene_files_shots_QPushButton")
        self.scene_files_shots_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.scene_files_assets_button.setCheckable(True)
        self.scene_files_shots_button.setCheckable(True)
        self.scene_files_shots_button.setChecked(True)

        # Add them to a button group so only one can be true at the same time
        group_box = QButtonGroup(widget)
        group_box.addButton(self.scene_files_assets_button)
        group_box.addButton(self.scene_files_shots_button)


        # Add buttons to layout
        buttons_layout.addWidget(self.scene_files_assets_button)
        buttons_layout.addWidget(self.scene_files_shots_button)
        buttons_container_layout.addLayout(buttons_layout)

        # 2nd/3rd Column: Spacers
        buttons_container_layout.addWidget(QLabel(""))
        buttons_container_layout.addWidget(QLabel(""))

        # add layout to main layout
        layout.addLayout(buttons_container_layout)

        # Create a scene_files_stackedWidge
        self.scene_files_stackedWidget = QStackedWidget()

        # Link Pages to Functions
        assets_widget = self.scene_files_assets_widget()
        shots_widget = self.scene_files_shots_widget()

        # Add Pages to the stacked widget
        self.scene_files_stackedWidget.addWidget(assets_widget)
        self.scene_files_stackedWidget.addWidget(shots_widget)

        # Connect buttons to change the stacked widget index
        self.scene_files_assets_button.clicked.connect(lambda: self.scene_files_stackedWidget.setCurrentIndex(0))
        self.scene_files_shots_button.clicked.connect(lambda: self.scene_files_stackedWidget.setCurrentIndex(1))

        # Add the stacked widget to the main layout
        layout.addWidget(self.scene_files_stackedWidget)

        # Bot Comments
        comment_layout = QHBoxLayout()
        comment_layout.addWidget(QLabel("Comment"))
        self.scene_files_comment_QLineEdit = QLineEdit()
        self.scene_files_comment_QLineEdit.setObjectName("scene_files_comment_QLineEdit")
        comment_layout.addWidget(self.scene_files_comment_QLineEdit)
        self.load_version_QPushButton = QPushButton("Load Version")
        self.load_version_QPushButton.setObjectName("load_version_QPushButton")
        self.save_version_QPushButton = QPushButton("Save Version")
        self.save_version_QPushButton.setObjectName("save_version_QPushButton")
        comment_layout.addWidget(self.load_version_QPushButton)
        comment_layout.addWidget(self.save_version_QPushButton)

        layout.addLayout(comment_layout)

        return widget

    def scene_files_assets_widget(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)

        # Column 1: QTreeWidget
        col1_layout = QVBoxLayout()
        col1_tree_widget_label = QLabel("")
        self.scene_files_assets_QtreeWidget = QTreeWidget()
        self.scene_files_assets_QtreeWidget.setObjectName("scene_files_assets_QtreeWidget")
        self.scene_files_assets_QtreeWidget.setHeaderHidden(True)
        self.scene_files_assets_QtreeWidget.setMaximumWidth(200)
        col1_layout.addWidget(col1_tree_widget_label)
        col1_layout.addWidget(self.scene_files_assets_QtreeWidget)
        main_layout.addLayout(col1_layout)

        # 2nd Column: QVBoxLayout for the labels and QListWidgets, blank group box
        col2_layout = QVBoxLayout() 
        lists_horizontal_items = QGridLayout()

        # Creating and adding the "Department" label and QListWidget
        department_label = QLabel("Department")
        self.scene_files_assets_department_QListWidget = QListWidget()
        self.scene_files_assets_department_QListWidget.setObjectName("scene_files_assets_department_QListWidget")
        self.scene_files_assets_department_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(department_label, 0, 0) 
        lists_horizontal_items.addWidget(self.scene_files_assets_department_QListWidget, 1, 0) 

        # Creating and adding the "Variant" label and QListWidget
        task_label = QLabel("Task")
        self.scene_files_assets_task_QListWidget = QListWidget()
        self.scene_files_assets_task_QListWidget.setObjectName("scene_files_assets_task_QListWidget")
        self.scene_files_assets_task_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(task_label, 0, 1)
        lists_horizontal_items.addWidget(self.scene_files_assets_task_QListWidget, 1, 1) 

        col2_layout.addLayout(lists_horizontal_items)


        main_layout.addLayout(col2_layout)

        # Column 3: QTreeWidget
        col3_layout = QVBoxLayout()
        col3_tree_widget_label = QLabel("Files")
        self.scene_files_assets_files_QtreeWidget = QTreeWidget()
        self.scene_files_assets_files_QtreeWidget.setObjectName("scene_files_assets_files_QtreeWidget")
        self.scene_files_assets_files_QtreeWidget.setHeaderHidden(True)
        col3_layout.addWidget(col3_tree_widget_label)
        col3_layout.addWidget(self.scene_files_assets_files_QtreeWidget)
        main_layout.addLayout(col3_layout)

        # Configuration 
        main_layout.setStretch(0, 2)  # First column
        main_layout.setStretch(1, 1)  # Second column
        main_layout.setStretch(2, 2)  # Third column

        return widget

    def scene_files_shots_widget(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)

        # Column 1: QTreeWidget for Shots
        col1_layout = QVBoxLayout()
        self.scene_files_shots_QtreeWidget = QTreeWidget()
        self.scene_files_shots_QtreeWidget.setObjectName("scene_files_shots_QtreeWidget")
        self.scene_files_shots_QtreeWidget.setHeaderHidden(True)
        self.scene_files_shots_QtreeWidget.setMaximumWidth(200)
        col1_layout.addWidget(QLabel("Shots"))
        col1_layout.addWidget(self.scene_files_shots_QtreeWidget)
        
        # Column 2: QVBoxLayout for the labels and QListWidgets
        col2_layout = QVBoxLayout() 
        lists_horizontal_items = QGridLayout()
        
        # Department and Task lists
        department_label = QLabel("Department")
        self.scene_files_shots_department_QListWidget = QListWidget()
        self.scene_files_shots_department_QListWidget.setObjectName("scene_files_shots_department_QListWidget")
        self.scene_files_shots_department_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(department_label, 0, 0)
        lists_horizontal_items.addWidget(self.scene_files_shots_department_QListWidget, 1, 0)

        task_label = QLabel("Task")
        self.scene_files_shots_task_QListWidget = QListWidget()
        self.scene_files_shots_task_QListWidget.setObjectName("scene_files_shots_task_QListWidget")
        self.scene_files_shots_task_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(task_label, 0, 1)
        lists_horizontal_items.addWidget(self.scene_files_shots_task_QListWidget, 1, 1)
        
        col2_layout.addLayout(lists_horizontal_items)
        
        # Column 3: QTreeWidget for Files
        col3_layout = QVBoxLayout()
        self.scene_files_shots_files_QtreeWidget = QTreeWidget()
        self.scene_files_shots_files_QtreeWidget.setObjectName("scene_files_shots_files_QtreeWidget")
        self.scene_files_shots_files_QtreeWidget.setHeaderHidden(True)
        col3_layout.addWidget(QLabel("Files"))
        col3_layout.addWidget(self.scene_files_shots_files_QtreeWidget)

        # Adding columns to the main layout
        main_layout.addLayout(col1_layout)
        main_layout.addLayout(col2_layout)
        main_layout.addLayout(col3_layout)

        # Configure the layout stretching
        main_layout.setStretch(0, 1) 
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 1)

        return widget

    def usd_config_layout(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Buttons Container Layout
        buttons_container_layout = QHBoxLayout()

        # 1st Column: Buttons Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(0)
        buttons_layout.setAlignment(Qt.AlignCenter)

        # Create buttons
        self.usd_config_assets_QPushButton = QPushButton("Assets")
        self.usd_config_assets_QPushButton.setObjectName("usd_config_assets_QPushButton")
        self.usd_config_shots_QPushButton = QPushButton("Shots")
        self.usd_config_shots_QPushButton.setObjectName("usd_config_shots_QPushButton")
        self.usd_config_assets_QPushButton.setCheckable(True)
        self.usd_config_shots_QPushButton.setCheckable(True)
        self.usd_config_shots_QPushButton.setChecked(True)

        # Add them to a button group so only one can be true at the same time
        group_box = QButtonGroup(widget)
        group_box.addButton(self.usd_config_assets_QPushButton)
        group_box.addButton(self.usd_config_shots_QPushButton)

        # Add buttons to layout
        buttons_layout.addWidget(self.usd_config_assets_QPushButton)
        buttons_layout.addWidget(self.usd_config_shots_QPushButton)
        buttons_container_layout.addLayout(buttons_layout)

        # 2nd/3rd Column: Spacers
        buttons_container_layout.addWidget(QLabel(""))
        buttons_container_layout.addWidget(QLabel(""))

        # add layout to main layout
        layout.addLayout(buttons_container_layout)

        # Create a usd_config_stackedWidget
        self.usd_config_stackedWidget = QStackedWidget()

        # Link Pages to Functions
        assets_widget = self.usd_config_assets_widget()
        shots_widget = self.usd_config_shots_widget()

        # Add Pages to the stacked widget
        self.usd_config_stackedWidget.addWidget(assets_widget)
        self.usd_config_stackedWidget.addWidget(shots_widget)

        # Connect buttons to change the stacked widget index
        self.usd_config_assets_QPushButton.clicked.connect(lambda: self.usd_config_stackedWidget.setCurrentIndex(0))
        self.usd_config_shots_QPushButton.clicked.connect(lambda: self.usd_config_stackedWidget.setCurrentIndex(1))

        # Add the stacked widget to the main layout
        layout.addWidget(self.usd_config_stackedWidget)

        # Bot Comments
        comment_layout = QHBoxLayout()
        comment_layout.addWidget(QLabel("Comment"))

        self.usd_config_comment_QLineEdit = QLineEdit()
        self.usd_config_comment_QLineEdit.setObjectName("usd_config_comment_QLineEdit")
        comment_layout.addWidget(self.usd_config_comment_QLineEdit)

        self.publish_version_QPushButton = QPushButton("Publish Version")
        self.publish_version_QPushButton.setObjectName("publish_version_QPushButton")
        comment_layout.addWidget(self.publish_version_QPushButton)
        
        layout.addLayout(comment_layout)
        return widget

    def usd_config_assets_widget(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        
        # 1st Column: QTreeWidget for assets
        col1_layout = QVBoxLayout()
        col1_tree_widget_label = QLabel("")
        self.usd_config_assets_QtreeWidget = QTreeWidget()
        self.usd_config_assets_QtreeWidget.setObjectName("usd_config_assets_QtreeWidget")
        self.usd_config_assets_QtreeWidget.setHeaderHidden(True)
        self.usd_config_assets_QtreeWidget.setMaximumWidth(200)
        col1_layout.addWidget(col1_tree_widget_label)
        col1_layout.addWidget(self.usd_config_assets_QtreeWidget)
        main_layout.addLayout(col1_layout)

        # 2nd Column: QVBoxLayout for the labels and QListWidgets
        col2_layout = QVBoxLayout() 

        lists_horizontal_items = QGridLayout()

        # Creating and adding the "Department" label and QListWidget
        department_label = QLabel("Department")
        self.usd_config_assets_department_QListWidget = QListWidget()
        self.usd_config_assets_department_QListWidget.setObjectName("usd_config_assets_department_QListWidget")
        self.usd_config_assets_department_QListWidget.setMinimumWidth(100)
        self.usd_config_assets_department_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(department_label, 0, 0) 
        lists_horizontal_items.addWidget(self.usd_config_assets_department_QListWidget, 1, 0)

        # Creating and adding the "Set Variant" label and QListWidget
        set_variant_label = QLabel("Set Variant")
        self.usd_config_assets_setVar_QListWidget = QListWidget()
        self.usd_config_assets_setVar_QListWidget.setObjectName("usd_config_assets_setVar_QListWidget")
        self.usd_config_assets_setVar_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(set_variant_label, 0, 1)
        lists_horizontal_items.addWidget(self.usd_config_assets_setVar_QListWidget, 1, 1)

        # Creating and adding the "Variant" label and QListWidget
        variant_label = QLabel("Variant")
        self.usd_config_assets_variant_QListWidget = QListWidget()
        self.usd_config_assets_variant_QListWidget.setObjectName("usd_config_assets_variant_QListWidget")
        self.usd_config_assets_variant_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(variant_label, 0, 2)
        lists_horizontal_items.addWidget(self.usd_config_assets_variant_QListWidget, 1, 2)
        
        col2_layout.addLayout(lists_horizontal_items)


        group_box = QGroupBox("AssetInfo:")
        group_box.setAutoFillBackground(False)
        group_box.setFixedHeight(200) 

        group_box_layout = QVBoxLayout()
        group_box_layout.setAlignment(Qt.AlignTop)
        group_box_layout.setSpacing(5) 

        # Blank Layout
        blank_QLabel = QLabel("")
        group_box_layout.addWidget(blank_QLabel)

        # Asset Type
        asset_type_layout = QHBoxLayout()
        label1 = QLabel("Asset Type:")
        asset_type_info = QLabel("") 
        asset_type_info.setObjectName("usd_config_asset_type_QLabel")
        asset_type_info.setAlignment(Qt.AlignRight)
        asset_type_layout.addWidget(label1)
        asset_type_layout.addWidget(asset_type_info)
        group_box_layout.addLayout(asset_type_layout)

        # Description
        description_layout = QHBoxLayout()
        label4 = QLabel("Description:")
        description_info = QLabel("") 
        description_info.setObjectName("usd_config_asset_description_QLabel")
        description_info.setAlignment(Qt.AlignRight)
        description_layout.addWidget(label4)
        description_layout.addWidget(description_info)
        group_box_layout.addLayout(description_layout)

        # Latest Version
        latest_version_layout = QHBoxLayout()
        label2 = QLabel("Var. Latest Version:")
        latest_version_info = QLabel("")
        latest_version_info.setObjectName("usd_config_asset_latest_version_QLabel")
        latest_version_info.setAlignment(Qt.AlignRight)
        latest_version_layout.addWidget(label2)
        latest_version_layout.addWidget(latest_version_info)
        group_box_layout.addLayout(latest_version_layout)

        group_box.setLayout(group_box_layout)

        col2_layout.addWidget(group_box)
        main_layout.addLayout(col2_layout)

        # Column 3: QTreeWidget
        col3_layout = QVBoxLayout()
        col3_tree_widget_label = QLabel("Versions")
        self.usd_config_assets_variantVersions_QtreeWidget = QTreeWidget()
        self.usd_config_assets_variantVersions_QtreeWidget.setObjectName("usd_config_assets_variantVersions_QtreeWidget")
        self.usd_config_assets_variantVersions_QtreeWidget.setHeaderHidden(True)

        col3_layout.addWidget(col3_tree_widget_label)
        col3_layout.addWidget(self.usd_config_assets_variantVersions_QtreeWidget)

        main_layout.addLayout(col3_layout)

        main_layout.setStretch(0, 2)  # First column
        main_layout.setStretch(1, 1)  # Second column
        main_layout.setStretch(2, 2)  # Third column

        return widget

    def usd_config_shots_widget(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        
        # 1st Column: QTreeWidget for assets
        col1_layout = QVBoxLayout()
        col1_tree_widget_label = QLabel("")
        self.usd_config_shots_QtreeWidget = QTreeWidget()
        self.usd_config_shots_QtreeWidget.setObjectName("usd_config_shots_QtreeWidget")
        self.usd_config_shots_QtreeWidget.setHeaderHidden(True)
        self.usd_config_shots_QtreeWidget.setMaximumWidth(200)
        col1_layout.addWidget(col1_tree_widget_label)
        col1_layout.addWidget(self.usd_config_shots_QtreeWidget)
        main_layout.addLayout(col1_layout)

        # 2nd Column: QVBoxLayout for the labels and QListWidgets, blank group box
        col2_layout = QVBoxLayout() 

        lists_horizontal_items = QGridLayout()

        # Creating and adding the "Department" label and QListWidget
        department_label = QLabel("Department")
        self.usd_config_shots_department_QListWidget = QListWidget()
        self.usd_config_shots_department_QListWidget.setObjectName("usd_config_shots_department_QListWidget")
        self.usd_config_shots_department_QListWidget.setMaximumWidth(200)
        lists_horizontal_items.addWidget(department_label, 0, 0)
        lists_horizontal_items.addWidget(self.usd_config_shots_department_QListWidget, 1, 0)

        col2_layout.addLayout(lists_horizontal_items)

        # Bottom Item
        group_box = QGroupBox("ShotInfo")
        group_box.setFixedHeight(200)  # Set the fixed height for the group box

        group_box_layout = QVBoxLayout()
        label1 = QLabel("Type:")
        label2 = QLabel("Framerange:")
        label3 = QLabel("Description:")
        group_box_layout.addWidget(label1)
        group_box_layout.addWidget(label2)
        group_box_layout.addWidget(label3)

        group_box.setLayout(group_box_layout)
        col2_layout.addWidget(group_box)
        main_layout.addLayout(col2_layout)

        # Column 3: QTreeWidget
        col3_layout = QVBoxLayout()
        col3_tree_widget_label = QLabel("Versions")
        self.usd_config_shots_variantVersions_QtreeWidget = QTreeWidget()
        self.usd_config_shots_variantVersions_QtreeWidget.setObjectName("usd_config_shots_variantVersions_QtreeWidget")
        self.usd_config_shots_variantVersions_QtreeWidget.setHeaderHidden(True)
        col3_layout.addWidget(col3_tree_widget_label)
        col3_layout.addWidget(self.usd_config_shots_variantVersions_QtreeWidget)
        main_layout.addLayout(col3_layout)

        main_layout.setStretch(0, 2)  # First column
        main_layout.setStretch(1, 1)  # Second column
        main_layout.setStretch(2, 2)  # Third column

        return widget

    def app_style_sheet(self):
            appStyleSheet = ("""
                    QMenuBar, QStatusBar {
                        background-color: rgb(35, 35, 35);
                        color: white;
                    }
                    QMenu {
                        background-color: rgb(35, 35, 35);
                        color: white;
                    }
                    QAction:hover { 
                        background-color: #333;
                    }       
                    QPushButton { 
                        color: white;
                        border: none;
                        border-radius: 2px;
                        background-color: rgb(35, 35, 35);
                        padding: 5px;
                    }
                    QPushButton:hover { 
                        background-color: #555;
                    }
                    QPushButton:checked { 
                        selection-background-color: #0078d7;
                    }
                    QGroupBox {   
                        border-radius: 5px;     
                    }
                    QPushButton:hover { 
                        background-color: #555;
                    }
                    QPushButton:checked { 
                        background-color: #0078d7;
                    }
                    QTreeWidget, QListWidget, QLineEdit {
                        background-color: rgb(35, 35, 35);
                        border-radius: 5px;
                        selection-background-color: #0078d7;
                        font-size: 9pt;
                        letter-spacing: 1px;     
                    }
                    QLabel {
                        color: #AAA;
                    }
                    QMainWindow, QDialog{
                        background-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                                    stop:0 rgb(47, 53, 56), 
                                                    stop:1 rgb(34, 45, 50));
                    }
                """)
            return appStyleSheet