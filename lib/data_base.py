import sqlite3
import os

class ProjectDataBase:
    # Tables
    create_assets_sql = """
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        name TEXT,
        description TEXT,
        usd_path TEXT
    );
    """

    create_sequences_sql = """
    CREATE TABLE IF NOT EXISTS sequences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        usd_path TEXT,
        description TEXT
    );
    """

    create_shots_sql = """
    CREATE TABLE IF NOT EXISTS shots (
        id INTEGER PRIMARY KEY,
        seq_id INTEGER,
        name TEXT,
        usd_path TEXT,
        framerange TEXT,
        description TEXT,
        FOREIGN KEY(seq_id) REFERENCES sequences(id)
    );
    """

    create_departments_sql = """
    CREATE TABLE IF NOT EXISTS departments (
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        seq_id INTEGER,
        shot_id INTEGER,
        asset_id INTEGER,
        usd_path TEXT,
        name TEXT,
        FOREIGN KEY(seq_id) REFERENCES sequences(id),
        FOREIGN KEY(shot_id) REFERENCES shots(id),
        FOREIGN KEY(asset_id) REFERENCES assets(id)
    );
    """

    create_tasks_sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_id INTEGER,
        name TEXT,
        FOREIGN KEY(department_id) REFERENCES departments(department_id)
    );
    """

    create_setVar_sql = """
    CREATE TABLE IF NOT EXISTS setVar (
        setVar_id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_id INTEGER,
        name TEXT,
        usd_path TEXT,
        FOREIGN KEY(department_id) REFERENCES departments(department_id)
    );
    """

    create_variant_sql = """
    CREATE TABLE IF NOT EXISTS variant (
        var_id INTEGER PRIMARY KEY AUTOINCREMENT,
        setVar_id INTEGER,
        name TEXT,
        FOREIGN KEY(setVar_id) REFERENCES setVar(setVar_id)
    );
    """
    
    create_variantVersion_sql = """
    CREATE TABLE IF NOT EXISTS variantVersion (
        variantVersion_id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_id INTEGER,
        var_id INTEGER,
        version INTEGER,
        comment TEXT,
        date TEXT,
        usd_path TEXT,
        pinned BOOLEAN,
        snapshot BLOB,
        FOREIGN KEY(var_id) REFERENCES variant(var_id),
        FOREIGN KEY(department_id) REFERENCES departments(department_id)
    );
    """

    trigger_insert_variantVersion_sql = """
    CREATE TRIGGER IF NOT EXISTS SetOnlyOnePinnedAfterInsert
    AFTER INSERT ON variantVersion
    FOR EACH ROW
    WHEN NEW.pinned = 1
    BEGIN
        UPDATE variantVersion SET pinned = 0 WHERE variantVersion_id != NEW.variantVersion_id;
    END;
    """

    trigger_update_variantVersion_sql = """
    CREATE TRIGGER IF NOT EXISTS SetOnlyOnePinnedBeforeUpdate
    BEFORE UPDATE ON variantVersion
    FOR EACH ROW
    WHEN NEW.pinned = 1 AND OLD.pinned != 1
    BEGIN
        UPDATE variantVersion SET pinned = 0 WHERE variantVersion_id != NEW.variantVersion_id;
    END;
    """

    create_files_sql = """
    CREATE TABLE IF NOT EXISTS files (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        version INTEGER,
        comment TEXT,
        date TEXT,
        file_path TEXT,
        file_type TEXT,
        snapshot BLOB,
        FOREIGN KEY(task_id) REFERENCES tasks(task_id)
    );
    """
    

    # Initialization
    def __init__(self, db_path):
        self.db_path = db_path
        self.initialize_db()  # Call the initialize_db method

    def initialize_db(self):
        # Ensure the folder exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute(self.create_assets_sql)
            cursor.execute(self.create_sequences_sql)
            cursor.execute(self.create_shots_sql)
            cursor.execute(self.create_departments_sql)
            cursor.execute(self.create_setVar_sql)
            cursor.execute(self.create_variant_sql)
            cursor.execute(self.create_variantVersion_sql)
            cursor.execute(self.create_tasks_sql)
            cursor.execute(self.create_files_sql)
            cursor.execute(self.trigger_insert_variantVersion_sql)
            cursor.execute(self.trigger_update_variantVersion_sql)
            
            # Commit the changes
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e.args[0]}")
        finally:
            # Close the connection
            conn.close()
    
    # Asset CRUD        
    def create_asset(self, type, name, usd_path, description):
        """
        Add a new asset to the database.

        :param type: The type of the asset.
        :param name: The name of the asset.
        :param usd_path: The filesystem path to the asset's USD file.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO assets (type, name, usd_path, description) 
                VALUES (?, ?, ?, ?)
            """, (type, name, usd_path, description))
            conn.commit()
            return cursor.lastrowid  # Returns the id of the newly created asset

    def get_asset(self, name=None, all=False):
        """
        Retrieve all assets or a specific asset by name.
        
        :param name: The name of the asset to retrieve (optional).
        :param all: Boolean indicating whether to retrieve all assets.
        :return: A list of assets if all=True, or a single asset if all=False and name is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            
            if all:
                cursor.execute("SELECT * FROM assets")
                return cursor.fetchall()  # Returns a list of Row objects
            else:
                cursor.execute("SELECT * FROM assets WHERE name = ?", (name,))
                result = cursor.fetchone()
                return dict(result) if result else None  # Returns a dictionary or None

    def update_asset(self, asset_id, name, usd_path, type, description):
        """
        Update an asset details.

        :param asset_id: The ID of the asset to update.
        :param name: The new name of the asset.
        :param usd_path: The new filesystem path to the asset's USD file.
        :param description: The new text description of the asset.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE assets
                SET name = ?, usd_path = ?, type = ?, description = ?,
                WHERE id = ?
            """, (name, usd_path, type, asset_id, description))
            conn.commit()

    def delete_asset(self, name):
        """
        Delete an Asset from the database by its name.

        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM assets WHERE name = ?
            """, (name,))
            conn.commit()

    # Sequence CRUD     
    def create_sequence(self, name, usd_path, description):
        """
        Add a new sequence to the database.

        :param name: The name of the sequence.
        :param usd_path: The filesystem path to the sequence's USD file.
        :param description: A text description of the sequence.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sequences (name, usd_path, description) 
                VALUES (?, ?, ?)
            """, (name, usd_path, description))
            conn.commit()
            return cursor.lastrowid  # Returns the id of the newly created sequence

    def get_sequence(self, name=None, all=False):
        """
        Rretrieve all sequences or a specific sequence by name.
        
        :param name: The name of the sequence to retrieve (optional).
        :param all: Boolean indicating whether to retrieve all sequences.
        :return: A list of sequences if all=True, or a single sequence if all=False and name is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            
            if all:
                cursor.execute("SELECT * FROM sequences")
                return cursor.fetchall()  # Returns a list of Row objects
            else:
                cursor.execute("SELECT * FROM sequences WHERE name = ?", (name,))
                result = cursor.fetchone()
                return dict(result) if result else None  # Returns a dictionary or None

    def update_sequence(self, seq_id, name, usd_path, description):
        """
        Update a sequence's details in the database.

        :param seq_id: The ID of the sequence to update.
        :param name: The new name of the sequence.
        :param usd_path: The new filesystem path to the sequence's USD file.
        :param description: The new text description of the sequence.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sequences
                SET name = ?, usd_path = ?, description = ?
                WHERE id = ?
            """, (name, usd_path, description, seq_id))
            conn.commit()

    def delete_sequence(self, name):
        """
        Delete a sequence from the database by its name.

        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM sequences WHERE name = ?
            """, (name,))
            conn.commit()

    # Shot CRUD
    def create_shot(self, seq_id, name, framerange, description, usd_path):
        """
        Add a new shot to the database.
        
        :param seq_id: The ID of the sequence this shot belongs to.
        :param name: The name of the shot.
        :param framerange: The frame range of the shot.
        :param description: A text description of the shot.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO shots (seq_id, name, framerange, description, usd_path)
                VALUES (?, ?, ?, ?, ?)
            """, (seq_id, name, framerange, description, usd_path))
            conn.commit()
            return cursor.lastrowid  # Returns the id of the newly created shot

    def get_shot(self, seq_id, shot_name=None, all=False):
        """
        Retrieve all shots for the sequence or a specific shot by name within the sequence.
        
        :param seq_id: The ID of the sequence to retrieve shots for.
        :param shot_name: The name of the shot to retrieve (optional).
        :param all: Boolean indicating whether to retrieve all shots for the sequence.
        :return: A list of shots if all=True, or a single shot if all=False and shot_name is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            
            if all:
                cursor.execute("SELECT * FROM shots WHERE seq_id = ?", (seq_id,))
                return cursor.fetchall()  # Returns a list of Row objects
            else:
                cursor.execute("SELECT * FROM shots WHERE seq_id = ? AND name = ?", (seq_id, shot_name,))
                result = cursor.fetchone()
                return dict(result) if result else None  # Returns a dictionary or None

    def update_shot(self, shot_id, seq_id, name, framerange, description):
        """
        Update a shot's details in the database.

        :param shot_id: The ID of the shot to update.
        :param seq_id: The new ID of the sequence this shot belongs to.
        :param name: The new name of the shot.
        :param framerange: The new frame range of the shot.
        :param description: The new text description of the shot.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE shots
                SET seq_id = ?, name = ?, framerange = ?, description = ?
                WHERE id = ?
            """, (seq_id, name, framerange, description, shot_id))
            conn.commit()

    def delete_shot(self, name):
        """
        Delete a shot from the database by its name.

        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM shots WHERE name = ?
            """, (name,))
            conn.commit()
    
    # Department CRUD
    def create_department(self, id_type, id_value, name, usd_path):
        """
        Add a new department, which can be linked either to a sequence, a shot, or an asset.
        
        :param id_type: A string indicating the type of entity ('sequence', 'shot', or 'asset') the department is associated with.
        :param id_value: The ID of the entity to which the department is linked.
        :param name: The name of the department.
        """
        # Validate id_type to ensure it's one of the expected values
        if id_type not in ['sequence', 'shot', 'asset']:
            raise ValueError("Invalid id_type specified. Use 'sequence', 'shot', or 'asset'.")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Initialize all potential foreign keys with NULL
            seq_id = shot_id = asset_id = None
            
            # Depending on the id_type, assign the id_value to the appropriate variable
            if id_type == 'sequence':
                seq_id = id_value
            elif id_type == 'shot':
                shot_id = id_value
            elif id_type == 'asset':
                asset_id = id_value

            cursor.execute("""
                INSERT INTO departments (seq_id, shot_id, asset_id, name, usd_path)
                VALUES (?, ?, ?, ?, ?)
            """, (seq_id, shot_id, asset_id, name, usd_path))
            conn.commit()
            return cursor.lastrowid  # Returns the id of the newly created department

    def get_department(self, id_type, id_value, department_name=None, all=False):
        """
        Retrieve all departments linked to a sequence, shot or asset. Or a specific department by name within that linkage.
        
        :param id_type: A string specifying the type of linkage ('sequence', 'shot' or 'asset').
        :param id_value: The ID of the linkage element.
        :param department_name: The name of the department (optional).
        :param all: Boolean indicating whether to retrieve all departments linked to the sequence, shot or asset.
        :return: A list of departments if all=True, or a single department if all=False and department_name is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            if id_type == "sequence":
                id_column = "seq_id"
            elif id_type == "shot":
                id_column = "shot_id"
            else:
                id_column = "asset_id"
            if all:
                cursor.execute(f"""
                    SELECT * FROM departments WHERE {id_column} = ?
                """, (id_value,))
                return cursor.fetchall()  # Returns a list of Row objects
            else:
                cursor.execute(f"""
                    SELECT * FROM departments WHERE {id_column} = ? AND name = ?
                """, (id_value, department_name,))
                result = cursor.fetchone()
                return dict(result) if result else None  # Returns a dictionary or None

    def update_department(self, id_type, department_id, id_value, name):
        """
        Update a department's details in the database, allowing linkage to either a sequence, shot or asset.

        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if id_type == "sequence":
                id_column = "seq_id"
            elif id_type == "shot":
                id_column = "shot_id"
            else:
                id_column = "asset_id"
            cursor.execute(f"""
                UPDATE departments
                SET {id_column} = ?, name = ?
                WHERE department_id = ?
            """, (id_value, name, department_id))
            conn.commit()

    def delete_department(self, id_type, id_value, name):
        """
        Delete a department from the database by its name and associated sequence, shot or asset.

        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if id_type == "sequence":
                id_column = "seq_id"
            elif id_type == "shot":
                id_column = "shot_id"
            else:
                id_column = "asset_id"
            cursor.execute(f"""
                DELETE FROM departments WHERE name = ? AND {id_column} = ?
            """, (name, id_value))
            conn.commit()

    # Task CRUD
    def create_task(self, department_id, task_name):
        """
        Add a new task to the database, which can be linked either to a department or a variant.
        
        :param department_id: The ID of the department to which the task is associated.
        :param task_name: The name of the task.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (department_id, name)
                VALUES (?, ?)
            """, (department_id, task_name))
            conn.commit()
            return cursor.lastrowid  # Returns the id of the newly created task

    def get_task(self, department_id, task_name=None, all=False):
        """
        Retrieve all departments linked to a department, or a specific task by name within that linkage.
        
        :param id_value: The ID of the department.
        :param task_name: The name of the task (optional).
        :param all: Boolean indicating whether to retrieve all tasks linked to the department.
        :return: A list of tasks if all=True, or a single task if all=False and task_name is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            if all:
                cursor.execute(f"""
                    SELECT * FROM tasks WHERE department_id = ?
                """, (department_id,))
                return cursor.fetchall()  # Returns a list of Row objects
            else:
                cursor.execute(f"""
                    SELECT * FROM tasks WHERE department_id = ? AND name = ?
                """, (department_id, task_name,))
                result = cursor.fetchone()
                return dict(result) if result else None  # Returns a dictionary or None

    def update_task(self, task_id, task_name):
        """
        Update a task's details in the database.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE tasks
                SET name = ?
                WHERE task_id = ?
            """, (task_name, task_id))
            conn.commit()

    def delete_task(self, task_id, task_name):
        """
        Delete a task from the database by its name and associated department or variant.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                DELETE FROM departments WHERE name = ? AND task_id = ?
            """, (task_name, task_id))
            conn.commit()

    # SetVar CRUD
    def create_setVar(self, department_id, name, usd_path):
        """
        Add a new setVar to a specific department.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO setVar (department_id, name, usd_path)
                VALUES (?, ?, ?)
            """, (department_id, name, usd_path))
            conn.commit()
            return cursor.lastrowid  # Returns the id of the newly created task

    def get_setVar(self, department_id, setVar_name=None, all=False):
        """
        Retrieve all setVars in a department or a specific setVar by name within that department.
        
        :param department_id: The ID of the department.
        :param setVar_name: The name of the setVar (optional).
        :param all: Boolean indicating whether to retrieve all setVars in the department.
        :return: A list of setVars if all=True, or a single setVar if all=False and setVar_name is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            
            if all:
                # Retrieve all tasks for the specified department
                cursor.execute("""
                    SELECT * FROM setVar WHERE department_id = ?
                """, (department_id,))
                return cursor.fetchall()  # Returns a list of Row objects
            else:
                # Retrieve a specific task by name within the specified department
                cursor.execute("""
                    SELECT * FROM setVar WHERE department_id = ? AND name = ?
                """, (department_id, setVar_name,))
                return cursor.fetchone()  # Returns a single Row object or None

    def update_setVar(self, setVar_id, department_id, name):
        """
        Update a setVar's details in the database.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE setVar
                SET department_id = ?, name = ?
                WHERE setVar_id = ?
            """, (department_id, name, setVar_id))
            conn.commit()

    def delete_setVar(self, name):
        """
        Delete a setVar from the database by its name.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM setVar WHERE name = ?
            """, (name,))
            conn.commit()

    # Variant CRUD
    def create_variant(self, setVar_id, name):
        """
        Add a new variant to a specific setVar.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO variant (setVar_id, name)
                VALUES (?, ?)
            """, (setVar_id, name))
            conn.commit()
            return cursor.lastrowid

    def get_variant(self, setVar_id, var_name=None, all=False):
        """
        Retrieve all variants in a setVar or a specific variant by name within that setVar.
        
        :param setVar_id: The ID of the setVar.
        :param var_name: The name of the variant (optional).
        :param all: Boolean indicating whether to retrieve all variants in the setVar.
        :return: A list of variants if all=True, or a single variant if all=False and var_name is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            
            if all:
                # Retrieve all tasks for the specified department
                cursor.execute("""
                    SELECT * FROM variant WHERE setVar_id = ?
                """, (setVar_id,))
                return cursor.fetchall()  # Returns a list of Row objects
            else:
                # Retrieve a specific task by name within the specified department
                cursor.execute("""
                    SELECT * FROM variant WHERE setVar_id = ? AND name = ?
                """, (setVar_id, var_name,))
                return cursor.fetchone()  # Returns a single Row object or None

    def update_variant(self, var_id, setVar_id, name):
        """
        Update a variant details in the database.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE variant
                SET setVar_id = ?, name = ?
                WHERE var_id = ?
            """, (setVar_id, name, var_id))
            conn.commit()

    def delete_variant(self, name):
        """
        Delete a variant from the database by its name.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM variant WHERE name = ?
            """, (name,))
            conn.commit()

    # File CRUD
    def create_file(self, task_id, version, comment, date, file_path, file_type, snapshot):
        """
        Add a new file associated with a specific task.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files (task_id, version, comment, date, file_path, file_type, snapshot)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task_id, version, comment, date, file_path, file_type, snapshot))
            conn.commit()
            return cursor.lastrowid  # Returns the ID of the newly created file

    def get_file(self, task_id, file_id=None, all=False):
        """
        Retrieve all files in a task or a specific file by file_id within that task.
        
        :param task_id: The ID of the task.
        :param file_id: The ID of the file (optional).
        :param all: Boolean indicating whether to retrieve all files in the task.
        :return: A list of files if all=True, or a single file if all=False and file_id is provided.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Makes the fetch return a dictionary-like Row object
            cursor = conn.cursor()
            
            if all:
                # Retrieve all files for the specified task
                cursor.execute("""
                    SELECT * FROM files WHERE task_id = ?
                """, (task_id,))
                return cursor.fetchall()  # Returns a list of Row objects
            elif file_id is not None:
                # Retrieve a specific file by file_id within the specified task
                cursor.execute("""
                    SELECT * FROM files WHERE task_id = ? AND file_id = ?
                """, (task_id, file_id))
                return cursor.fetchone()  # Returns a single Row object or None
            else:
                # No valid identifier provided; return None or handle as appropriate
                return None

    def update_file(self, file_id, version, task_id, comment, date, file_path, file_type):
        """
        Update details of an existing file.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE files
                SET task_id = ?, version = ?, comment = ?, date = ?, file_path = ?, file_type = ?
                WHERE file_id = ?
            """, (task_id, version, comment, date, file_path, file_type, file_id))
            conn.commit()

    def delete_file(self, file_id):
        """
        Delete a file from the database by its file ID.
        
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files WHERE file_id = ?", (file_id,))
            conn.commit()

    # usdVersion CRUD
    def create_variantVersion(self, id_type, id_value, version, comment, date, usd_path, snapshot):
        """
        Add a new USD version associated with a specific variant.
        
        :param id_type: Either "department" or "variant".
        :param id_value: The ID of the variant/department the USD version is associated with.
        :param comment: A comment or note about the USD version.
        :param date: The date the USD version was added or modified.
        :param usd_path: The filesystem path to the USD file.
        """
        if id_type == "variant":
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO variantVersion (var_id, version, comment, date, usd_path, snapshot, pinned, department_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (id_value, version, comment, date, usd_path, snapshot, False, None))
                conn.commit()
                return cursor.lastrowid  # Returns the ID of the newly created USD version
        else:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO variantVersion (department_id, version, comment, date, usd_path, snapshot, pinned, var_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (id_value, version, comment, date, usd_path, snapshot, False, None))
                conn.commit()
                return cursor.lastrowid  # Returns the ID of the newly created USD version
    
    def get_variantVersion(self, id_type, id_value, variantVersion_version=None, all=False):
        """
        Retrieve all USD versions for a variant/department or a specific USD version by its ID.
        
        :param id_type: Either "department" or "variant".
        :param id_value: The ID of the variant/department the USD version is associated with.
        :param usdVersion_id: The ID of the USD version (optional).
        :param all: Boolean indicating whether to retrieve all USD versions for the variant.
        :return: A list of USD versions if all=True, or a single USD version if all=False and usdVersion_id is provided.
        """
        if id_type == "variant":
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if all:
                    cursor.execute("SELECT * FROM variantVersion WHERE var_id = ?", (id_value,))
                    return cursor.fetchall()  # Returns a list of Row objects
                elif variantVersion_version is not None:
                    cursor.execute("SELECT * FROM variantVersion WHERE var_id = ? AND version = ?", (id_value, variantVersion_version))
                    return cursor.fetchone()  # Returns a single Row object or None
                else:
                    return None
        else:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if all:
                    cursor.execute("SELECT * FROM variantVersion WHERE department_id = ?", (id_value,))
                    return cursor.fetchall()  # Returns a list of Row objects
                elif variantVersion_version is not None:
                    cursor.execute("SELECT * FROM variantVersion WHERE department_id = ? AND version = ?", (id_value, variantVersion_version))
                    return cursor.fetchone()  # Returns a single Row object or None
                else:
                    return None

    def update_variantVersion(self, variantVersion_id, **kwargs):
        """
        Dynamically update details of an existing USD version based on provided keyword arguments.

        :param variantVersion_id: The ID of the USD version to update.
        :param kwargs: Keyword arguments corresponding to the column names and their new values.
        """
        # Construct the SET part of the SQL query dynamically based on kwargs
        set_clause = ', '.join([f"{key} = ?" for key in kwargs])
        parameters = list(kwargs.values()) + [variantVersion_id]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE variantVersion
                SET {set_clause}
                WHERE variantVersion_id = ?
            """, parameters)
            conn.commit()

    def delete_usdVersion(self, variantVersion_id):
        """
        Delete a USD version from the database by its ID.
        
        :param usdVersion_id: The ID of the USD version to delete.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM variantVersion WHERE variantVersion_id = ?", (variantVersion_id,))
            conn.commit()
        

    # Utility functions
    @staticmethod
    def initialize_database(db_path):
        db = ProjectDataBase(db_path)