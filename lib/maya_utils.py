import maya.standalone
import maya.cmds as cmds

from PySide2.QtGui import QPixmap
from PySide2.QtCore import QByteArray, QBuffer
import tempfile
from datetime import datetime
import sys
import os

class ExternalMayaUtils:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def initialize_maya(self):
        """Initializes Maya in standalone mode."""
        maya.standalone.initialize(name='python')
    
    def create_asset_scene(self):
        """Creates a new blank Maya scene and saves it as an .ma file."""
        cmds.file(new=True, force=True)
        
        # Create the group structure
        root_group = cmds.group(em=True, name='root')
        geo_group = cmds.group(em=True, name='geo', parent=root_group)
        render_group = cmds.group(em=True, name='render', parent=geo_group)
        proxy_group = cmds.group(em=True, name='proxy', parent=geo_group)

        cmds.file(rename=self.file_path)
        cmds.file(save=True, type="mayaAscii")
    
    def uninitialize_maya(self):
        """Uninitializes Maya standalone."""
        maya.standalone.uninitialize()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        creator = ExternalMayaUtils(sys.argv[1])
        creator.initialize_maya()
        creator.create_asset_scene()
        creator.uninitialize_maya()
    else:
        print("Error: Please specify a file path for the new scene.")

class InternalMayaUtils:
    def __init__(self):
        pass

    def capture_snapshot(self):
        temp_dir = tempfile.gettempdir()
        time = datetime.now()
        timecode = time.strftime("%Y%m%d%H%M%S")
        filename = f"viewport_capture_{timecode}.jpg"
        save_path = os.path.join(temp_dir, filename) # Contains the captured image.

        cmds.playblast(format='image', completeFilename=save_path, clearCache=1, viewer=0, frame=[cmds.currentTime(query=True)],
                       showOrnaments=0, offScreen=True, percent=100, compression='jpg', quality=70, widthHeight=(90, 50))

        img_blob = self.img_to_blob(save_path)
        print(f"img_blob created at {save_path}")

        return img_blob
        
    def img_to_blob(self, img_path):
        with open(img_path, 'rb') as file:
            img_blob = file.read()
        return img_blob

    def blob_to_pixmap(self, blob_data):
        # Convert the blob data to a QPixmap
        if isinstance(blob_data, str):
            blob_data = blob_data.encode('utf-8')  # Encoding to bytes

        qbyte_array = QByteArray(blob_data)
        buffer = QBuffer(qbyte_array)
        buffer.open(QBuffer.ReadOnly)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.data())
        
        return pixmap