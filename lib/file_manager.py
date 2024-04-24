

from lib import maya_utils
import os
import shutil
import subprocess
import datetime

running_in_maya = False

try:
    import maya.cmds as cmds
    running_in_maya = True
except ImportError:
    print("")

if running_in_maya:
    import maya.cmds as cmds
    
class FileManager:
    def __init__(self, project):
        self.project = project
        from lib import data_base
        db_path = os.path.join(self.project, "pipeline", "project.db")
        self.db = data_base.ProjectDataBase(db_path)
        self.maya_utils = maya_utils.InternalMayaUtils()
        
        self.usd_assets_folder = os.path.join(self.project, "entity")
        self.usd_sequence_folder = os.path.join(self.project, "sequences")
        self.usd_shots_folder = os.path.join(self.project, "shots")
        self.usd_fragment_folder = os.path.join(self.project, "fragment")

        self.mayapy_path = "C:/Program Files/Autodesk/Maya2024/bin/mayapy.exe"
        self.mayaexe_path = "C:/Program Files/Autodesk/Maya2024/bin/maya.exe"
        self.script_path = "./lib/maya_utils.py"

    def create_task_folder(self, name, department_name, software_name, asset_name=None, sequence_name=None, shot_name=None):

        if sequence_name is not None:
            sequence_info = self.db.get_sequence(sequence_name)
            sequence_id = sequence_info['id']

            id_value = sequence_id
            id_type = "sequence"
            task_dir = os.path.join(self.usd_sequence_folder, sequence_name, software_name, department_name, name)

        if shot_name is not None:
            shot_info = self.db.get_shot(sequence_id, shot_name)
            shot_id = shot_info['id']

            id_value = shot_id
            id_type = "shot"
            task_dir = os.path.join(self.usd_shots_folder, shot_name, software_name, department_name, name)

        if asset_name is not None:
            asset_info = self.db.get_asset(asset_name)
            asset_id = asset_info['id']

            id_value = asset_id
            id_type = "asset"
            task_dir = os.path.join(self.usd_assets_folder, asset_name, software_name, department_name, name)
        
        department_info = self.db.get_department(id_type=id_type, id_value=id_value, department_name=department_name)
        department_id = department_info['department_id']

        os.makedirs(task_dir, exist_ok=True)
        self.db.create_task(department_id, name)

    def delete_task_folder(self, task_type, name, department_type=None, asset_name=None, 
                            sequence_name=None, shot_name=None, department_name=None, 
                            variant_name=None, setVar_name=None):
        """
        Delete the specified task folder.
        """
        # Determine the directory path based on the task and associated details
        if task_type == "department":
            if department_type == "sequence":
                task_dir = os.path.join(self.usd_sequence_folder, sequence_name, department_name, name)
            elif department_type == "shot":
                task_dir = os.path.join(self.usd_shots_folder, shot_name, department_name, name)
        elif task_type == "variant":
            task_dir = os.path.join(self.usd_assets_folder, asset_name, department_name, setVar_name, variant_name, name)
        
        # Check if the directory exists
        if os.path.exists(task_dir):
            try:
                # Attempt to delete the directory and all its contents
                shutil.rmtree(task_dir)
                print(f"Successfully deleted the task folder: {task_dir}")
                # Optionally, remove the task from the database if needed
                # self.db.delete_task(task_identifier)
            except Exception as e:
                print(f"Error deleting the task folder: {e}")
        else:
            print(f"The specified task folder does not exist: {task_dir}")

    def create_file(self, mode, file_format, software_name, comment, asset_name=None, sequence_name=None,
                            shot_name=None, department_name=None, task_name=None):
        
        if asset_name is not None: 
            asset_info = self.db.get_asset(asset_name)
            asset_id = asset_info['id']

            id_value = asset_id
            id_type = "asset"
            

        if sequence_name is not None:
            sequence_info = self.db.get_sequence(sequence_name)
            sequence_id = sequence_info['id']

            id_value = sequence_id
            id_type = "sequence"
            
        
        if shot_name is not None:
            shot_info = self.db.get_shot(sequence_id, shot_name)
            shot_id = shot_info['id']

            id_value = shot_id
            id_type = "shot"
            
        department_info = self.db.get_department(id_type=id_type, id_value=id_value, department_name=department_name)
        department_id = department_info['department_id']

        task_info = self.db.get_task(department_id, task_name)
        task_id = task_info['task_id']

        highest_version = 0
        file_list = self.db.get_file(task_id, all=True)
        for entry in file_list:
            entry_version = entry['version']
            highest_version = max(highest_version, entry_version)
                
        version_int = highest_version + 1
        version_str = f"v{version_int:03d}"

        if asset_name is not None:
            file_name = f"{asset_name}_{department_name}_{task_name}_{version_str}{file_format}"
            file_dir = os.path.join(self.usd_assets_folder, asset_name, software_name, department_name, task_name)
            file_path = os.path.join(file_dir, file_name)
        if sequence_name is not None:
            file_name = f"{sequence_name}_{department_name}_{task_name}_{version_str}{file_format}"
            file_dir = os.path.join(self.usd_sequence_folder, sequence_name, software_name, department_name, task_name)
            file_path = os.path.join(file_dir, file_name)
        if shot_name is not None:
            file_name = f"{sequence_name}_{shot_name}_{department_name}_{task_name}_{version_str}{file_format}"
            file_dir = os.path.join(self.usd_shots_folder, shot_name, software_name, department_name, task_name)
            file_path = os.path.join(file_dir, file_name)

        if mode == "create":
            if running_in_maya is True:
                img_blob = self.maya_utils.capture_snapshot()
                cmds.file(new=True, force=True)
        
                # Create the group structure
                root_group = cmds.group(em=True, name='root')
                geo_group = cmds.group(em=True, name='geo', parent=root_group)
                render_group = cmds.group(em=True, name='render', parent=geo_group)
                proxy_group = cmds.group(em=True, name='proxy', parent=geo_group)

                cmds.file(rename=file_path)
                cmds.file(save=True, type="mayaAscii")

                if os.path.exists(file_path):
                    timestamp = os.path.getmtime(file_path)
                    timestamp_date = datetime.datetime.fromtimestamp(timestamp)
                    date = timestamp_date.strftime("%Y-%m-%d %H:%M:%S")
                    self.db.create_file(task_id=task_id, file_type=file_format, version=version_int, comment=comment, date=date, file_path=file_path, snapshot=img_blob)
                else:
                    print("File does not exist. It may not have been created.")

            else:
                os.makedirs(file_dir, exist_ok=True)
                command = [self.mayapy_path, self.script_path, file_path]
                result = subprocess.run(command, capture_output=True)
                
                # Check if the subprocess was successful
                if result.returncode == 0:
                    print("Subprocess completed successfully.")

                    # Check if the file was actually created
                    if os.path.exists(file_path):
                        timestamp = os.path.getmtime(file_path)
                        timestamp_date = datetime.datetime.fromtimestamp(timestamp)
                        date = timestamp_date.strftime("%Y-%m-%d %H:%M:%S")
                        self.db.create_file(task_id=task_id, file_type=file_format, version=version_int, comment=comment, date=date, file_path=file_path, snapshot=None)
                    else:
                        print("File does not exist. It may not have been created.")
                else:
                    # Handle subprocess error
                    print(f"Error in subprocess: {result.stderr.decode('utf-8')}")

        elif mode == "save":
            img_blob = self.maya_utils.capture_snapshot()

            os.makedirs(file_dir, exist_ok=True)
            cmds.file(rename=file_path)
            cmds.file(save=True, type='mayaAscii')
            
            print(f"Scene saved as: {file_path}")
            
            # Check if the file was actually created
            if os.path.exists(file_path):
                timestamp = os.path.getmtime(file_path)
                timestamp_date = datetime.datetime.fromtimestamp(timestamp)
                date = timestamp_date.strftime("%Y-%m-%d %H:%M:%S")
                self.db.create_file(task_id=task_id, file_type=file_format, version=version_int, comment=comment, date=date, file_path=file_path, snapshot=img_blob)
            else:
                print("File does not exist. It may not have been created.")
        
        else:
            pass

    def load_file(self, file_version, file_format, asset_name=None, sequence_name=None, shot_name=None,
                   department_name=None, task_name=None):
        
        if file_format == ".ma":
            file_name = f"{asset_name}_{department_name}_{task_name}_v{file_version}{file_format}"
            file_dir = os.path.join(self.usd_assets_folder, asset_name, "maya", department_name, task_name)
            file_path = os.path.join(file_dir, file_name)
            file_path = file_path.replace('\\', '/')

            if running_in_maya:
                if cmds.file(query=True, modified=True):
                    # Prompt the user that there are unsaved changes
                    cmds.confirmDialog(
                        title='Unsaved Changes',
                        message='You have unsaved changes. Please save your work before opening a new file.',
                        button=['OK'],
                        defaultButton='OK',
                        cancelButton='OK',
                        dismissString='OK')
                else:
                    # If there are no unsaved changes, show the confirmation dialog for opening a file
                    result = cmds.confirmDialog(
                        title='Confirm',
                        message='Are you sure you want to open this file?',
                        button=['Yes', 'No'],
                        defaultButton='Yes',
                        cancelButton='No',
                        dismissString='No')

                    # If the user clicks 'Yes', proceed with opening the file
                    if result == 'Yes':
                        cmds.file(file_path, open=True)
            else:
                try: 
                    print("file_path:", file_path)
                    subprocess.call([self.mayaexe_path, "-file", file_path])
                except subprocess.SubprocessError as e:
                    print(f"Failed to open {file_path} with MayaPy due to a subprocess error: {e}")

        elif file_format == ".hip":
            pass

class CreateProject:
    def __init__(self, directory):
        self.project_folders = {
            "entity",
            "fragment",
            "pipeline",
            "documentation",
            "hdri",
            "external",
            "reference",
            "render",
            "resources",
            "sequences",
            "shots"
        }
        self.create_folders(directory)

    def create_folders(self, directory):
        # Create the base directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create each folder in the directory
        for folder in self.project_folders:
            folder_path = os.path.join(directory, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Created folder: {folder_path}")
            else:
                print(f"Folder already exists: {folder_path}")