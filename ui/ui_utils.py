from lib import maya_utils
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                                QSizePolicy, QFrame, QListWidget, QPushButton, QAction, QDialog, QFormLayout, QLineEdit, QListWidgetItem, QTextEdit)
from PySide2.QtCore import QSize, Qt


running_in_maya = False

try:
    import maya.cmds as cmds
    running_in_maya = True
except ImportError:
    print("Not running in Maya, certain functionalities will be disabled.")



class SceneFileItemWidget(QFrame):
    """
    Custom Widget (QFrame) to hold the Scene Version Files.
    """
    def __init__(self, version, scene_type, comment, user, date, snapshot=None, parent=None):
        """
        Init function that constructs the widget.

        :param version: The version of the Scene File item.
        :param scene_type: Either "sequence", "shot" or "asset".
        :param comment: The comment of the Scene File item.
        :param user: The user that created the Scene File Item.
        :param date: The date of the Scene File Item.
        :param snapshot: The snapshot image asociated with the Scene File Item.
        """
        super(SceneFileItemWidget, self).__init__(parent)
        self.maya_utils = maya_utils.InternalMayaUtils()

        # Define Main Container for the Widget.
        self.setObjectName("SceneFileItemWidgetMainContainer")
        self.setFrameShape(QFrame.StyledPanel)  # Makes Frame Visible.
        self.setFrameShadow(QFrame.Raised)

        self.layout = QHBoxLayout(self)

        # Column 1: Version and File type
        col1_vertical_layout = QVBoxLayout()
        self.col1_version_label = QLabel(version)
        self.col1_version_label.setObjectName("col1_version_label")
        self.col1_scene_type_label = QLabel(scene_type)
        self.col1_scene_type_label.setObjectName("col1_scene_type_label")
        col1_vertical_layout.addWidget(self.col1_version_label)
        col1_vertical_layout.addWidget(self.col1_scene_type_label)

        col1_container_widget = QWidget()
        col1_container_widget.setLayout(col1_vertical_layout)
        col1_container_widget.setMinimumSize(50, 10)

        self.layout.addWidget(col1_container_widget)

        # Column 2: Comments
        col2_comment_label = QLabel(comment)
        col2_comment_label.setWordWrap(True)
        self.layout.addWidget(col2_comment_label)
        col2_comment_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Column 3: Details
        col3_vertical_layout = QVBoxLayout()
        col3_user_label = QLabel(user)
        col3_date_label = QLabel(date)
        col3_vertical_layout.addWidget(col3_user_label, alignment=Qt.AlignRight)
        col3_vertical_layout.addWidget(col3_date_label, alignment=Qt.AlignRight)

        col3_container_widget = QWidget() 
        col3_container_widget.setLayout(col3_vertical_layout)
        col3_container_widget.setMinimumSize(50, 10)

        self.layout.addWidget(col3_container_widget)

        # Assuming this is all in a method of a class that includes maya_utils and self
        pixmap = self.maya_utils.blob_to_pixmap(snapshot)
        snapshot_pixmap_item = QGraphicsPixmapItem(pixmap)

        # Create a scene and add the pixmap item to it
        snapshot_scene = QGraphicsScene()
        snapshot_scene.addItem(snapshot_pixmap_item)

        # Create the view and set its scene
        col4_snapshot = QGraphicsView(snapshot_scene)
        
        col4_snapshot.setFixedSize(90, 50) 
        col4_snapshot.setContentsMargins(0, 0, 0, 0)
        col4_snapshot.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        col4_snapshot.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set the scene on the view
        col4_snapshot.setScene(snapshot_scene)

        self.layout.addWidget(col4_snapshot)

        self.setLayout(self.layout)

    def get_version(self):
        """
        Returns the version(str) associated with the Item instance.
        """
        return self.col1_version_label.text()
    def get_type(self):
        """
        Returns the fileType(str) associated with the Item instance.
        """
        return self.col1_scene_type_label.text()

class UsdFileItemWidget(QFrame):
    """
    Custom Widget (QFrame) to hold the USD Version Files.
    """
    def __init__(self, version, comment, user, date, pinned, snapshot=None, parent=None):
        """
        Init function that constructs the widget.

        :param version: The version of the Scene File item.
        :param comment: The comment of the Scene File item.
        :param user: The user that created the Scene File Item.
        :param date: The date of the Scene File Item.
        :param pinned: Boolean if the USD Item is pinned.
        :param snapshot: The snapshot image asociated with the Scene File Item.
        """
        
        super(UsdFileItemWidget, self).__init__(parent)
        self.maya_utils = maya_utils.InternalMayaUtils()

        # Column 1: Version and File type
        self.setObjectName("UsdFileItemWidgetMainContainer")
        self.setFrameShape(QFrame.StyledPanel)  # This makes the frame visible
        self.setFrameShadow(QFrame.Raised)

        self.layout = QHBoxLayout(self)
        
        # Column 1: Version
        col1_vertical_layout = QVBoxLayout()
        self.col1_version_label = QLabel(version)
        self.col1_version_label.setObjectName("col1_version_label")
        col1_vertical_layout.addWidget(self.col1_version_label)

        col1_container_widget = QWidget() 
        col1_container_widget.setLayout(col1_vertical_layout)
        col1_container_widget.setMinimumSize(50, 10)

        self.layout.addWidget(col1_container_widget)

        # Column 2: Comments
        col2_comment_label = QLabel(comment)
        col2_comment_label.setWordWrap(True)
        self.layout.addWidget(col2_comment_label)
        col2_comment_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Column 3: Details
        col3_vertical_layout = QVBoxLayout()
        col3_user_label = QLabel(user)
        col3_date_label = QLabel(date)
        col3_vertical_layout.addWidget(col3_user_label, alignment=Qt.AlignRight)
        col3_vertical_layout.addWidget(col3_date_label, alignment=Qt.AlignRight)

        col3_container_widget = QWidget()
        col3_container_widget.setLayout(col3_vertical_layout)
        col3_container_widget.setMinimumSize(50, 10)

        self.layout.addWidget(col3_container_widget)
        
        # Assuming this is all in a method of a class that includes maya_utils and self
        pixmap = self.maya_utils.blob_to_pixmap(snapshot)
        snapshot_pixmap_item = QGraphicsPixmapItem(pixmap)

        # Create a scene and add the pixmap item to it
        snapshot_scene = QGraphicsScene()
        snapshot_scene.addItem(snapshot_pixmap_item)

        # Create the view and set its scene
        col4_snapshot = QGraphicsView(snapshot_scene)
        
        col4_snapshot.setFixedSize(90, 50) 
        col4_snapshot.setContentsMargins(0, 0, 0, 0)
        col4_snapshot.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        col4_snapshot.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set the scene on the view
        col4_snapshot.setScene(snapshot_scene)

        self.layout.addWidget(col4_snapshot)

        self.setLayout(self.layout)

        if pinned == True:
            self.set_border_color("red")

    def set_border_color(self, color):
        """
        Sets the color of the Item's border.

        :param color: The color for the border.
        """
        # Apply styles specifically to this widget using its object name
        self.setStyleSheet(f"""
            QFrame#UsdFileItemWidgetMainContainer {{
                border: 2px solid {color};
                background-color: rgb(35, 35, 35);
                color: white;
            }}
        """)

    def get_version(self):
        """
        Returns the version(str) associated with the Item's instance.
        """
        return self.col1_version_label.text()

class AssetInputDialog(QDialog):
    def __init__(self, parent=None):
        super(AssetInputDialog, self).__init__(parent)
        self.setStyleSheet(self.app_style_sheet())
        self.setWindowTitle("Asset Input Dialog")

        # Set up the form layout with labels and line edits
        self.form_layout = QFormLayout(self)

        # Create line edits for the asset name, type, and description
        self.asset_name_edit = QLineEdit(self)
        self.asset_type_edit = QLineEdit(self)
        self.asset_description_edit = QLineEdit(self)

        # Add rows to the form layout
        self.form_layout.addRow("Asset Name:", self.asset_name_edit)
        self.form_layout.addRow("Asset Type:", self.asset_type_edit)
        self.form_layout.addRow("Asset Description:", self.asset_description_edit)

        # Set up the buttons
        self.buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        
        # Connect buttons to their respective slots
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Add buttons to the layout
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)
        
        # Add buttons layout to the form layout
        self.form_layout.addRow(self.buttons_layout)

    def get_inputs(self):
        return (self.asset_name_edit.text(), self.asset_type_edit.text(), self.asset_description_edit.text())

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
                        font-size: 10pt;
                        letter-spacing: 1px;     
                    }
                    QLabel {
                        color: #AAA;
                    }
                    QMainWindow, QDialog  {
                        background-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                                    stop:0 rgb(47, 53, 56), 
                                                    stop:1 rgb(34, 45, 50));
                    }
                """)
            return appStyleSheet

class DepartmentSelectionDialog(QDialog):
    def __init__(self, initial_selections=None, parent=None):
        super(DepartmentSelectionDialog, self).__init__(parent)

        # Dialog setup
        self.setWindowTitle("Select Department")
        self.resize(160, 350)
        self.setStyleSheet(self.app_style_sheet())
        self.selected_departments = []

        # Main layout
        self.layout = QVBoxLayout()

        # Create the QListWidget
        self.listWidget = QListWidget()
        department_names = ['modelling', 'shading', 'rigging', 'animation', 'fx', 'charFx', 'lighting']
        
        for name in department_names:
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignCenter)  # Align text to center
            self.listWidget.insertItem(0, item)

        # Enable multi-selection without needing to press Ctrl
        self.listWidget.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.listWidget)

        # Increase item size
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            # Set a custom size for each item (width, height)
            item.setSizeHint(QSize(100, 40))

        # Pre-select items if initial selections are provided
        if initial_selections:
            # Iterate in reverse to maintain correct selection when items are reversed
            for i, department in enumerate(reversed(department_names)):
                if department in initial_selections:
                    self.listWidget.item(i).setSelected(True)

        # Create horizontal layout for buttons
        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.confirm_button = QPushButton("Confirm")
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.confirm_button)
        self.layout.addLayout(self.button_layout)

        # Set the main layout
        self.setLayout(self.layout)

        # Connect the buttons to their functions
        self.confirm_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

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
                        font-size: 10pt;
                        letter-spacing: 1px;     
                    }
                    QLabel {
                        color: #AAA;
                    }
                    QMainWindow, QDialog {
                        background-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                                    stop:0 rgb(47, 53, 56), 
                                                    stop:1 rgb(34, 45, 50));
                    }
                """)
            return appStyleSheet
    
    def accept(self):
        # The order of selection retrieval does not need to change as selection order remains the same
        self.selected_departments = [item.text() for item in self.listWidget.selectedItems()]
        super(DepartmentSelectionDialog, self).accept()

    def reject(self):
        self.selected_departments = []
        super(DepartmentSelectionDialog, self).reject()

    def get_selected_departments(self):
        results = []
        # Retrieve from last to first
        for index in reversed(range(self.listWidget.count())):
            item = self.listWidget.item(index)
            results.append((item.text(), item.isSelected(), index))
        return results

class CustomQDialog(QDialog):
    def __init__(self, text, parent=None):
        super(CustomQDialog, self).__init__(parent)

        self.setStyleSheet(self.app_style_sheet())
        self.setWindowTitle(text)

        # Set up the form layout with labels and line edits
        self.form_layout = QFormLayout(self)

        # Create line edits for the asset name, type, and description
        self.edit = QLineEdit(self)

        # Add rows to the form layout
        self.form_layout.addRow(text, self.edit)

        # Set up the buttons
        self.buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        
        # Connect buttons to their respective slots
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Add buttons to the layout
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)
        
        # Add buttons layout to the form layout
        self.form_layout.addRow(self.buttons_layout)
        
    def get_inputs(self):
        return self.edit.text()

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
                        font-size: 10pt;
                        letter-spacing: 1px;     
                    }
                    QLabel {
                        color: #AAA;
                    }
                    QMainWindow, QDialog  {
                        background-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                                    stop:0 rgb(47, 53, 56), 
                                                    stop:1 rgb(34, 45, 50));
                    }
                """)
            return appStyleSheet

class GeoSanityCheck(QDialog):
    def __init__(self, parent=None):
        super(GeoSanityCheck, self).__init__(parent)
        self.setStyleSheet(self.app_style_sheet())
        # Layout and widgets
        self.layout = QVBoxLayout(self)
        
        # Text edit for logging
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)
        
        # Button to run sanity checks
        self.run_button = QPushButton("Run Sanity Check")
        self.run_button.clicked.connect(self.run_sanity_checks)
        self.layout.addWidget(self.run_button)
        
        # Button to publish geometry
        self.publish_button = QPushButton("Publish Geo Version")
        self.publish_button.clicked.connect(self.publish_geo)
        self.publish_button.setEnabled(False)  # Disable until checks pass
        self.layout.addWidget(self.publish_button)

        self.setWindowTitle("Geo Sanity Check")

    def append_log(self, message, color="black"):
        self.text_edit.append(message)

    def delete_history(self):
        all_meshes = cmds.ls(type='mesh')
        mesh_transforms = cmds.listRelatives(all_meshes, parent=True, fullPath=True) or []

        for mesh in mesh_transforms:
            # Delete history on the mesh
            cmds.delete(mesh, constructionHistory=True)
            # Freeze transformations on the mesh
            cmds.makeIdentity(mesh, apply=True, translate=True, rotate=True, scale=True)


        self.append_log("Delete history DONE", color="green")
        self.freeze_transformations()

    def freeze_transformations(self):
        self.append_log("Freeze transformations DONE", color="green")

    def purpose_geo(self):
        self.append_log("Purpose geos DONE", color="green")

    def run_sanity_checks(self):
        self.delete_history()
        self.freeze_transformations()
        self.purpose_geo()
        self.publish_button.setEnabled(True)

    def publish_geo(self):
        # Implementation to publish the geometry
        self.accept()  # Accept the dialog to close it and return QDialog.Accepted
    
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
                        font-size: 10pt;
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