

from lib import data_base
from pxr import Usd
import os
import shutil
import datetime

running_in_maya = False

try:
    import maya.cmds as cmds
    running_in_maya = True
except ImportError:
    # Handle the case when not running in Maya
    print("Not running in Maya, certain functionalities will be disabled.")

if running_in_maya:
    from lib import publish_variant
    from lib import maya_utils


class UsdManager:
    def __init__(self, project):
        self.project = project
        db_path = os.path.join(self.project, "pipeline", "project.db")
        self.db = data_base.ProjectDataBase(db_path)

        if running_in_maya:
            self.publish_variant = publish_variant.UsdMeshExporter()
            self.maya_utils = maya_utils.InternalMayaUtils()

        self.usd_assets_folder = os.path.join(self.project, "entity")
        self.usd_sequence_folder = os.path.join(self.project, "sequences")
        self.usd_shots_folder = os.path.join(self.project, "shots")
        self.usd_fragment_folder = os.path.join(self.project, "fragment")
        
    def create_usd_entity(self, entity_type, name, format, asset_type=None, description=None, seq_name=None, framerange=None):
        """
        Creates a new Usd entity and saves it to project path. 

        :param entity_type: Either asset, sequence or shot.
        :param name: The name of the asset.
        :param format: Either .usd/.usda/.usdc
        :param asset_type: The Type of the Asset to be created.
        :param description: Description of the Sequence or Shot.
        :param seq_name: Name of the parent sequence of the shot to be created.
        :param framerange: The framerange fo the Shot to be created.
        """
        if entity_type == "asset":
            file_name = f"{name}{format}"
            file_path = os.path.join(self.usd_assets_folder, name, file_name)

            stage = Usd.Stage.CreateNew(file_path)

            root_prim = stage.DefinePrim("/root", "Xform")
            stage.SetDefaultPrim(root_prim)

            current_asset_info = root_prim.GetAssetInfo()
            current_asset_info['assetType'] = asset_type
            root_prim.SetAssetInfo(current_asset_info)

            stage.GetRootLayer().Save()

            self.db.create_asset(asset_type, name, file_path, description)

        elif entity_type == "sequence":
            file_name = f"{name}{format}"
            file_path = os.path.join(self.usd_sequence_folder, name, file_name)

            stage = Usd.Stage.CreateNew(file_path)

            root_prim = stage.DefinePrim("/root", "Xform")
            stage.SetDefaultPrim(root_prim)

            current_asset_info = root_prim.GetAssetInfo()
            current_asset_info['seqDescription'] = description
            root_prim.SetAssetInfo(current_asset_info)

            stage.GetRootLayer().Save()
            self.db.create_sequence(name, file_path, description)

        elif entity_type == "shot":
            seq_info = self.db.get_sequence(seq_name)
            seq_id = seq_info["id"]

            complete_file_dir = f"{seq_name}_{name}"
            complete_file_name = f"{complete_file_dir}{format}"
            file_path = os.path.join(self.usd_shots_folder, complete_file_dir, complete_file_name)

            stage = Usd.Stage.CreateNew(file_path)

            root_prim = stage.DefinePrim("/root", "Xform")
            stage.SetDefaultPrim(root_prim)

            current_asset_info = root_prim.GetAssetInfo()
            current_asset_info['shotDescription'] = description
            root_prim.SetAssetInfo(current_asset_info)

            # Set Framerange of the shot.
            start_frame_str, end_frame_str = framerange.split('-')
            start_frame = int(start_frame_str)
            end_frame = int(end_frame_str)
            stage.SetStartTimeCode(start_frame)
            stage.SetEndTimeCode(end_frame)

            stage.GetRootLayer().Save()
            self.db.create_shot(seq_id, name, framerange, description, file_path)
        else:
            return print("entity_type format incorrect. Usage: 'asset', 'sequence', 'shot'")

    def edit_usd_entity(self, entity_type, name, mode, sublayer_path, seq_name=None):
        """
        Edits Usd asset and saves it to project path. 

        :param name: the name of the entity
        :param mode: "add", "delete", "move".
        :param sublayer_path: The path to the sublayer to perform actions on.
        """
        if entity_type == "asset":
            # Get the Asset USD path.
            entity_info = self.db.get_asset(name)
            entity_path = entity_info["usd_path"]

            # Construct Relative Path for Sublayer.
            entity_dir = os.path.dirname(entity_path)
            relative_sublayer_path = os.path.relpath(sublayer_path, entity_dir)
            relative_sublayer_path = relative_sublayer_path.replace('\\', '/')
            relative_sublayer_path = "./" + relative_sublayer_path

            # Open The USD Asset file.
            stage = Usd.Stage.Open(entity_path)
            root_layer = stage.GetRootLayer()

            # Add new Sublayer to Asset USD.
            if mode == "add":
                # Ensure the sublayer is not already part of the stage
                if relative_sublayer_path not in root_layer.subLayerPaths:
                    root_layer.subLayerPaths.insert(0, relative_sublayer_path)
                    root_layer.Save()
            elif mode == "delete":
                if relative_sublayer_path in root_layer.subLayerPaths:
                    root_layer.subLayerPaths.remove(relative_sublayer_path)
                    root_layer.Save()
                    
            elif mode == "move":
                pass

        elif entity_type == "sequence":
            # Get the Asset USD path.
            sequence_info = self.db.get_sequence(name)
            sequence_path = sequence_info["usd_path"]

            # Construct Relative Path for Sublayer.
            sequence_dir = os.path.dirname(sequence_path)
            relative_sublayer_path = os.path.relpath(sublayer_path, sequence_dir)
            relative_sublayer_path = relative_sublayer_path.replace('\\', '/')
            relative_sublayer_path = "./" + relative_sublayer_path

            # Open The USD Asset file.
            stage = Usd.Stage.Open(sequence_path)
            root_layer = stage.GetRootLayer()

            # Add new Sublayer to Asset USD.
            if mode == "add":
                # Ensure the sublayer is not already part of the stage
                if relative_sublayer_path not in root_layer.subLayerPaths:
                    root_layer.subLayerPaths.insert(0, relative_sublayer_path)
                    root_layer.Save()
            elif mode == "delete":
                if relative_sublayer_path in root_layer.subLayerPaths:
                    root_layer.subLayerPaths.remove(relative_sublayer_path)
                    root_layer.Save()
            elif mode == "move":
                pass

        elif entity_type == "shot":
            # Get the parent Sequence Id from db.
            sequence_info = self.db.get_sequence(seq_name)
            sequence_id = sequence_info["id"]

            # Get the Asset USD path from db
            shot_info = self.db.get_shot(sequence_id, name)
            shot_path = shot_info["usd_path"]

            # Construct Relative Path for Sublayer.
            shot_dir = os.path.dirname(shot_path)
            relative_sublayer_path = os.path.relpath(sublayer_path, shot_dir)
            relative_sublayer_path = relative_sublayer_path.replace('\\', '/')
            relative_sublayer_path = "./" + relative_sublayer_path

            # Open The USD Asset file.
            stage = Usd.Stage.Open(shot_path)
            root_layer = stage.GetRootLayer()

            # Add new Sublayer to Asset USD.
            if mode == "add":
                # Ensure the sublayer is not already part of the stage
                if relative_sublayer_path not in root_layer.subLayerPaths:
                    root_layer.subLayerPaths.insert(0, relative_sublayer_path)
                    root_layer.Save()
            elif mode == "delete":
                if relative_sublayer_path in root_layer.subLayerPaths:
                    root_layer.subLayerPaths.remove(relative_sublayer_path)
                    root_layer.Save()
            elif mode == "move":
                pass
        else:
            return print("entity_type format incorrect. Usage: 'asset', 'sequence', 'shot'")

    def delete_usd_entity(self, entity_type, name, seq_name=None):
        if entity_type == "asset":
            # Get the Asset USD path.
            entity_info = self.db.get_asset(name)
            entity_path = entity_info["usd_path"]
            entity_dir = os.path.dirname(entity_path)
            entity_dir = entity_dir.replace('\\', '/')

            try:
                shutil.rmtree(entity_dir)
                self.db.delete_asset(name)
                print(f"The folder at {entity_dir} has been successfully deleted.")
            except Exception as e:
                print(f"Error: {e}")

        elif entity_type == "sequence":
            # Get the Sequence path.
            entity_info = self.db.get_sequence(name)
            entity_path = entity_info["usd_path"]
            entity_dir = os.path.dirname(entity_path)
            entity_dir = entity_dir.replace('\\', '/')

            try:
                shutil.rmtree(entity_dir)
                self.db.delete_sequence(name)
                print(f"The folder at {entity_dir} has been successfully deleted.")
            except Exception as e:
                print(f"Error: {e}")

        elif entity_type == "shot":
            # Get the Sequence id from db.
            sequence_info = self.db.get_sequence(seq_name)
            sequence_id = sequence_info["id"]
            # Get the shot path from db.
            entity_info = self.db.get_shot(sequence_id, name)
            entity_path = entity_info["usd_path"]

            entity_dir = os.path.dirname(entity_path)
            entity_dir = entity_dir.replace('\\', '/')

            try:
                shutil.rmtree(entity_dir)
                self.db.delete_shot(name)
                print(f"The folder at {entity_dir} has been successfully deleted.")
            except Exception as e:
                print(f"Error: {e}")

        else:
            return print("entity_type format incorrect. Usage: 'asset', 'sequence', 'shot'")


    def create_usd_sublayer(self, entity_type, parent_name, sublayer_name, seq_name=None):
        """
        Creates a new usd file and sublayer's it to parent usd file (asset, seq or shot) 

        :param entity_type: either "asset", "sequence" or "shot".
        :param parent_name: The name of the entity in which the sublayer will be added.
        :param sublayer_name: The name of the sublayer file.
        """
        if entity_type == "asset":
            # Get Asset Id from db.
            entity_info = self.db.get_asset(parent_name)
            entity_id = entity_info["id"]
            
            # Construct file path for Sublayer usd.
            file_name = f"{parent_name}_{sublayer_name}.usda"
            file_path = os.path.join(self.usd_assets_folder, parent_name, sublayer_name, file_name)

            # Create the content of the sublayer usd.
            stage = Usd.Stage.CreateNew(file_path)

            root_prim = stage.DefinePrim("/root", "Xform")
            stage.SetDefaultPrim(root_prim)

            stage.GetRootLayer().Save()

            # Create new Department/sublayer in db.
            self.db.create_department(entity_type, entity_id, sublayer_name, file_path)

            # Add the new Sublayer created to the Specified Asset USD.
            self.edit_usd_entity(entity_type, parent_name, "add", file_path)

        elif entity_type == "sequence":
            # Get Sequence Id from db.
            entity_info = self.db.get_sequence(parent_name)
            entity_id = entity_info["id"]
            
            # Construct file path for Sublayer usd.
            file_name = f"{parent_name}_{sublayer_name}.usda"
            file_path = os.path.join(self.usd_sequence_folder, parent_name, sublayer_name, file_name)

            # Create the content of the sublayer usd.
            stage = Usd.Stage.CreateNew(file_path)

            root_prim = stage.DefinePrim("/root", "Xform")
            stage.SetDefaultPrim(root_prim)

            stage.GetRootLayer().Save()

            # Create new Department/sublayer in db.
            self.db.create_department(entity_type, entity_id, sublayer_name, file_path)

            # Add the new Sublayer created to the Specified Asset USD.
            self.edit_usd_entity(entity_type, parent_name, "add", file_path)
        
        elif entity_type == "shot":
            # Get Sequence Id from db.
            sequence_info = self.db.get_sequence(seq_name)
            sequence_id = sequence_info["id"]

            entity_info = self.db.get_shot(sequence_id, parent_name)
            entity_id = entity_info["id"]

            
            # Construct file path for Sublayer usd.
            file_name = f"{parent_name}_{sublayer_name}.usda"
            file_path = os.path.join(self.usd_shots_folder, parent_name, sublayer_name, file_name)

            # Create the content of the sublayer usd.
            stage = Usd.Stage.CreateNew(file_path)

            root_prim = stage.DefinePrim("/root", "Xform")
            stage.SetDefaultPrim(root_prim)

            stage.GetRootLayer().Save()

            # Create new Department/sublayer in db.
            self.db.create_department(entity_type, entity_id, sublayer_name, file_path)

            # Add the new Sublayer created to the Specified Asset USD.
            self.edit_usd_entity(entity_type, parent_name, "add", file_path, seq_name)
        else:
            return print("entity_type format incorrect. Usage: 'asset', 'sequence', 'shot'")

    def edit_usd_sublayer(self, entity_type, parent_name, sublayer_name, action, seq_name=None, new_sublayer_path=None):
        """
        Edits a USD sublayer by adding, removing, or updating it.

        :param entity_type: The type of the parent entity ('asset', 'sequence', 'shot').
        :param parent_name: The name of the parent entity.
        :param sublayer_name: The name of the sublayer to edit.
        :param action: The action to perform ('add', 'remove', 'update').
        :param seq_name: The name of the sequence, required if entity_type is 'shot'.
        :param new_sublayer_path: The new path for the sublayer, required if action is 'update'.
        """
        # Resolve the parent USD path based on entity_type and parent_name
        
        
        if entity_type == "asset":
            entity_info = self.db.get_asset(parent_name)
            entity_id = entity_info['id']

            department_info = self.db.get_department("asset", entity_id, sublayer_name) 
        elif entity_type == "sequence":
            entity_info = self.db.get_sequence(parent_name)
        elif entity_type == "shot" and seq_name:
            seq_info = self.db.get_sequence(seq_name)
            if not seq_info:
                print(f"Sequence '{seq_name}' not found.")
                return
            entity_info = self.db.get_shot(seq_info["id"], parent_name)
        else:
            print("Invalid entity_type or missing sequence name for 'shot'.")
            return

        if not entity_info:
            print(f"{entity_type.title()} '{parent_name}' not found.")
            return

        department_path = department_info["usd_path"]

        department_file_dir = os.path.dirname(department_path)
        relative_path = os.path.relpath(new_sublayer_path, department_file_dir)
        relative_path = relative_path.replace('\\', '/')
        relative_path = "./" + relative_path

        # Perform the specified action
        stage = Usd.Stage.Open(department_path)
        root_layer = stage.GetRootLayer()

        if action == "add":
            if sublayer_name not in root_layer.subLayerPaths:
                root_layer.subLayerPaths.append(relative_path)
        elif action == "remove":
            if sublayer_name in root_layer.subLayerPaths:
                root_layer.subLayerPaths.remove(relative_path)
        elif action == "update" and new_sublayer_path:
            try:
                index = root_layer.subLayerPaths.index(relative_path)
                root_layer.subLayerPaths[index] = relative_path
            except ValueError:
                print(f"Sublayer '{sublayer_name}' not found in '{parent_name}'.")
                return
        else:
            print("Invalid action or missing parameters.")

        root_layer.Save()

    def delete_usd_sublayer(self, entity_type, parent_name, sublayer_name, seq_name=None):
        if entity_type == "asset":
            # Get the Asset USD id.
            asset_info = self.db.get_asset(parent_name)
            asset_id = asset_info['id']

            # Get the Sublayer dir.
            sublayer_info = self.db.get_department("asset", asset_id, sublayer_name)
            sublayer_path = sublayer_info["usd_path"]
            sublayer_dir = os.path.dirname(sublayer_path)
            sublayer_dir = sublayer_dir.replace('\\', '/')

            try:
                shutil.rmtree(sublayer_dir)
                self.db.delete_department("asset", asset_id, sublayer_name)
                self.edit_usd_entity(entity_type, parent_name, "delete", sublayer_path)
                print(f"The folder at {sublayer_name} has been successfully deleted.")
            except Exception as e:
                print(f"Error: {e}")

        elif entity_type == "sequence":
            # Get the Sequence id.
            sequence_info = self.db.get_sequence(parent_name)
            sequence_id = sequence_info["id"]

            # Get the Sublayer dir.
            sublayer_info = self.db.get_department("sequence", sequence_id, sublayer_name)
            sublayer_path = sublayer_info["usd_path"]
            sublayer_dir = os.path.dirname(sublayer_path)
            sublayer_dir = sublayer_dir.replace('\\', '/')

            try:
                shutil.rmtree(sublayer_dir)
                self.db.delete_department("sequence", sequence_id, sublayer_name)
                self.edit_usd_entity(entity_type, parent_name, "delete", sublayer_path)
                print(f"The folder at {sublayer_name} has been successfully deleted.")
            except Exception as e:
                print(f"Error: {e}")

        elif entity_type == "shot":
            # Get the Sequence id.
            sequence_info = self.db.get_sequence(seq_name)
            sequence_id = sequence_info["id"]

            # Get the Shot id.
            shot_info = self.db.get_shot(sequence_id, parent_name)
            shot_id = shot_info["id"]

            # Get the sublayer dir.
            sublayer_info = self.db.get_department("shot", shot_id, sublayer_name)
            sublayer_path = sublayer_info["usd_path"]
            sublayer_dir = os.path.dirname(sublayer_path)
            sublayer_dir = sublayer_dir.replace('\\', '/')

            try:
                shutil.rmtree(sublayer_dir)
                self.db.delete_department("shot", shot_id, sublayer_name)
                self.edit_usd_entity(entity_type, parent_name, "delete", sublayer_path)
                print(f"The folder at {sublayer_name} has been successfully deleted.")
            except Exception as e:
                print(f"Error: {e}")
        else:
            return print("entity_type format incorrect. Usage: 'asset', 'sequence', 'shot'")    
        

    def create_usd_setVar(self, department_name, asset_name, name):
        file_name = f"{name}_{department_name}_{asset_name}.usda"
        file_path = os.path.join(self.usd_fragment_folder, name, department_name, asset_name, file_name)

        
        
        stage = Usd.Stage.CreateNew(file_path)

        root_prim = stage.DefinePrim("/root", "Xform")
        stage.SetDefaultPrim(root_prim)

        varSet_name = name
        variantSet = root_prim.GetVariantSets().AddVariantSet(varSet_name)

        stage.GetRootLayer().Save()

        asset_info = self.db.get_asset(asset_name)
        asset_id = asset_info['id']

        department_info = self.db.get_department("asset", id_value=asset_id, department_name=department_name)
        department_id = department_info['department_id']

        self.db.create_setVar(department_id, name, file_path)
        self.edit_usd_sublayer("asset", asset_name, department_name, "add", new_sublayer_path=file_path)

    def edit_usd_setVar(self, setVar_path, setVar_name, var_name, variantVersion_path=None):
        stage = Usd.Stage.Open(setVar_path)
        root_prim = stage.GetPrimAtPath('/root')
        variant_sets = root_prim.GetVariantSets()

        if variant_sets.HasVariantSet(setVar_name):
            varSet = variant_sets.GetVariantSet(setVar_name)

            if variantVersion_path is None:
                # Add variant to varSet without modifying payloads
                varSet.AddVariant(var_name)
            else:
                varSet.SetVariantSelection(var_name)

                with varSet.GetVariantEditContext():
                    # Construct the relative path for the payload
                    setVar_dir = os.path.dirname(setVar_path)
                    relative_var_path = os.path.relpath(variantVersion_path, setVar_dir)
                    relative_var_path = relative_var_path.replace('\\', '/')
                    relative_var_path = "./" + relative_var_path


                    root_prim.GetPayloads().ClearPayloads()
                    
                    # Add new payload pointing to the relative_var_path
                    root_prim.GetPayloads().AddPayload(relative_var_path)
                    
        stage.GetRootLayer().Save()

    def delete_usd_setVar(self, department_name, asset_name, setVar_name):
        """
        Deletes a USD SetVar including its file and database entry.

        :param department_name: Name of the department the SetVar belongs to.
        :param asset_name: Name of the asset the SetVar is associated with.
        :param setVar_name: Name of the SetVar to delete.
        """
        # Retrieve asset and department information
        asset_info = self.db.get_asset(asset_name)
        if not asset_info:
            print(f"No asset found with name {asset_name}")
            return
        asset_id = asset_info['id']

        department_info = self.db.get_department("asset", asset_id, department_name)
        if not department_info:
            print(f"No department found with name {department_name} for asset {asset_name}")
            return
        department_id = department_info['department_id']

        # Fetch SetVar to find the file path
        setVar_info = self.db.get_setVar(department_id, setVar_name)
        if not setVar_info:
            print(f"No SetVar found with name {setVar_name} in department {department_name}")
            return

        setVar_path = setVar_info['usd_path']
        setVar_dir = os.path.dirname(setVar_path)

        # Remove the directory and delete the database entry
        try:
            shutil.rmtree(setVar_dir)
            self.db.delete_setVar(setVar_name)
            print(f"SetVar {setVar_name} and its directory have been successfully deleted.")
        except Exception as e:
            print(f"Error deleting SetVar {setVar_name}: {e}")


    def create_variant(self, setVar_name, asset_name, name, department_name):
        asset_info = self.db.get_asset(asset_name)
        asset_id = asset_info['id']
        
        department_info = self.db.get_department("asset", id_value=asset_id, department_name=department_name)
        department_id = department_info['department_id']
        

        setVar_info = self.db.get_setVar(department_id, setVar_name)
        setVar_path = setVar_info['usd_path']
        setVar_id = setVar_info['setVar_id']

        self.db.create_variant(setVar_id, name)
        
        # edit setVar to add the new variant and the payload.
        self.edit_usd_setVar(setVar_path=setVar_path, setVar_name=setVar_name, var_name=name)
    
    def edit_variant(self, setVar_name, variant_name, action, new_payload_path=None):
        """
        Edits a USD variant within a SetVar.

        :param setVar_name: The name of the SetVar containing the variant.
        :param variant_name: The name of the variant to edit.
        :param action: The action to perform ('update_payload').
        :param new_payload_path: The new path for the variant's payload, required if action is 'update_payload'.
        """
        # Retrieve the SetVar and variant information
        setVar_info = self.db.get_setVar_by_name(setVar_name)
        if not setVar_info:
            print(f"SetVar '{setVar_name}' not found.")
            return

        setVar_path = setVar_info['usd_path']
        stage = Usd.Stage.Open(setVar_path)
        root_prim = stage.GetPrimAtPath('/root')
        variant_sets = root_prim.GetVariantSets()

        if not variant_sets.HasVariantSet(setVar_name):
            print(f"VariantSet '{setVar_name}' not found.")
            return

        variant_set = variant_sets.GetVariantSet(setVar_name)
        if action == "update_payload" and new_payload_path:
            if variant_set.HasVariant(variant_name):
                variant_set.SetVariantSelection(variant_name)
                with variant_set.GetVariantEditContext():
                    # Assuming the variant primarily uses a payload to reference content
                    root_prim.GetPayloads().ClearPayloads()
                    root_prim.GetPayloads().AddPayload(new_payload_path)
            else:
                print(f"Variant '{variant_name}' not found in SetVar '{setVar_name}'.")
        else:
            pass
            

        stage.GetRootLayer().Save()

    def delete_variant(self, setVar_name, variant_name):
        """
        Deletes a USD Variant, including its file and database entry.

        :param setVar_name: The SetVar name the variant belongs to.
        :param variant_name: The name of the variant to delete.
        """
        # Retrieve the SetVar and variant information
        # Assuming `get_setVar_by_name` and `get_variant_by_name` methods exist and return detailed information
        setVar_info = self.db.get_setVar_by_name(setVar_name)
        if not setVar_info:
            print(f"No SetVar found with name {setVar_name}")
            return
        
        variant_info = self.db.get_variant_by_name(variant_name, setVar_info['setVar_id'])
        if not variant_info:
            print(f"No variant found with name {variant_name} in SetVar {setVar_name}")
            return

        variant_path = variant_info['usd_path']
        variant_dir = os.path.dirname(variant_path)

        # Remove the directory and delete the database entry
        try:
            shutil.rmtree(variant_dir)
            self.db.delete_variant(variant_name)
            print(f"Variant {variant_name} and its directory have been successfully deleted.")
        except Exception as e:
            print(f"Error deleting variant {variant_name}: {e}")


    def create_usd_variantVersion(self, asset_name, department_name, setVar_name, var_name, comment):
        if running_in_maya:
            # Calculate Version.
            # Fetch all variants for the setVar_id from the database
            asset_info = self.db.get_asset(asset_name)
            asset_id = asset_info['id']
            
            department_info = self.db.get_department("asset", id_value=asset_id, department_name=department_name)
            department_id = department_info['department_id']

            setVar_info = self.db.get_setVar(department_id, setVar_name)
            setVar_id = setVar_info['setVar_id']
            setVar_path = setVar_info['usd_path']

            print("variant_info:", setVar_id, var_name)
            variant_info = self.db.get_variant(setVar_id, var_name)
            
            variant_id = variant_info['var_id']

            variantVersions = self.db.get_variantVersion(id_type="variant", id_value=variant_id, all=True)
            
            # Find the highest version
            highest_version = 0
            for variantVersion in variantVersions:
                version_int = int(variantVersion['version'])  # Convert version string to integer
                if version_int > highest_version:
                    highest_version = version_int
            
            # Assign the next number to version
            version = highest_version + 1
            version_str = f"{version:03}"
            
            file_name = f"{setVar_name}_{department_name}_{asset_name}_{var_name}_{version_str}.usda"
            file_path = os.path.join(self.usd_fragment_folder, setVar_name, department_name, asset_name, var_name, file_name)

            

            self.publish_variant.export_to_usd(file_path)

            if os.path.exists(file_path):
                        timestamp = os.path.getmtime(file_path)
                        timestamp_date = datetime.datetime.fromtimestamp(timestamp)
                        date = timestamp_date.strftime("%d-%m-%Y %H:%M:%S")

            snapshot = self.maya_utils.capture_snapshot()
            self.db.create_variantVersion(id_type="variant", id_value=variant_id, version=version, comment=comment, date=date, usd_path=file_path, snapshot=snapshot)

            self.edit_usd_setVar(setVar_path=setVar_path, setVar_name=setVar_name, var_name=var_name, variantVersion_path=file_path)

    def edit_usd_variantVersion(self):
        pass
    
    def delete_usd_variantVersion(self):
        pass


    def set_default_variant(self, default_variant, asset_name, department_name, setVar_name):
        asset_info = self.db.get_asset(asset_name)
        asset_id = asset_info['id']

        department_info = self.db.get_department("asset", asset_id, department_name)
        department_id = department_info['department_id']

        setVar_info = self.db.get_setVar(department_id, setVar_name)
        setVar_id = setVar_info['setVar_id']
        setVar_path = setVar_info['usd_path']

        stage = Usd.Stage.Open(setVar_path)
        
        root = stage.GetPrimAtPath("/root")
        variant_set = root.GetVariantSets().GetVariantSet(setVar_name)
        variant_set.SetVariantSelection(default_variant)

        stage.Save()
        return True