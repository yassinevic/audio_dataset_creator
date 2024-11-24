import json
import sqlite3
from typing import Any, Dict, List, Optional

class SQLiteDBHelper:
    def __init__(self, db_path: str, sql_file: str):
        self.db_path = db_path
        self.sql_file = sql_file
        self.connection = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Allows access to columns by name
        self.cursor = self.connection.cursor()
        print(f"Connected to database: {self.db_path}")
        
        # Ensure all tables exist
        self.ensure_tables_exist()

    def ensure_tables_exist(self):
        """Check if the main table exists, and if not, execute the SQL script."""
        try:
            # Check if any table exists by checking the `sentence` table (assumes it's crucial)
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sentence';
            """)
            table_exists = self.cursor.fetchone()

            if not table_exists:
                print("Required tables do not exist. Executing SQL script to create them...")
                
                # Read and execute the entire SQL file
                with open(self.sql_file, 'r') as f:
                    sql_script = f.read()
                self.cursor.executescript(sql_script)
                self.connection.commit()
                print("All tables created successfully.")
            else:
                print("Tables already exist.")
        except sqlite3.Error as e:
            print(f"Error while ensuring table existence: {e}")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    def create_table(self, table_sql: str):
        """Create a table using a provided SQL command."""
        self.connect()
        self.cursor.execute(table_sql)
        self.connection.commit()
        self.close()

    def insert(self, table: str, data: dict):
        """Insert a record into a table."""
        self.connect()
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(data.values()))
        self.connection.commit()
        self.close()

    def update(self, table: str, data: dict, condition: str, condition_params: tuple):
        """
        Update a record in a table.
        
        Args:
            table (str): Name of the table.
            data (dict): Dictionary of columns and their new values.
            condition (str): SQL condition for the update (e.g., "id = ?").
            condition_params (tuple): Parameters to safely fill in the condition placeholders.
        """
        self.connect()
        set_clause = ', '.join(f"{key} = ?" for key in data.keys())
        sql = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        self.cursor.execute(sql, tuple(data.values()) + condition_params)
        self.connection.commit()
        self.close()

    def read_sentences(self, table, recorded = -1, dataset=-1, sub_dataset="", page=1, page_size=10):
        """Read paginated key-value pairs from the database."""
        self.connect()
    
        # Calculate the offset for the given page and page_size
        offset = (page - 1) * page_size
    
        # SQL query with LIMIT and OFFSET for pagination
        sql = f"SELECT s.*, sp.name as speaker_name FROM {table} as s  , speaker as sp WHERE s.speaker = sp.id AND dataset = {dataset} AND sub_dataset = '{sub_dataset}' ORDER BY id DESC LIMIT {page_size} OFFSET {offset}"
        if recorded>-1:
            sql = f"SELECT s.*, sp.name as speaker_name FROM {table} as s  , speaker as sp WHERE s.speaker = sp.id AND recorded = {recorded} AND dataset = {dataset} AND sub_dataset = '{sub_dataset}' ORDER BY id DESC LIMIT {page_size} OFFSET {offset}"

        print(sql)

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        self.close()

        # Convert rows to a list of dictionaries
        data = [dict(row) for row in rows]
        # Convert the list of dictionaries to JSON
        json_data = json.dumps(data, indent=4)
        return json_data
    

    def read_paginated_data(self, table, filter = -1, page=1, page_size=10):
        """Read paginated key-value pairs from the database."""
        self.connect()
    
        # Calculate the offset for the given page and page_size
        offset = (page - 1) * page_size
    
        # SQL query with LIMIT and OFFSET for pagination
        sql = f"SELECT * FROM {table} LIMIT {page_size} OFFSET {offset}"
        if filter>-1:
            sql = f"SELECT * FROM {table} WHERE recorded = {filter} LIMIT {page_size} OFFSET {offset}"

        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        self.close()

        # Convert rows to a list of dictionaries
        data = [dict(row) for row in rows]
        # Convert the list of dictionaries to JSON
        json_data = json.dumps(data, indent=4)
        return json_data

    def count_sentences(self, table, recorded = -1, dataset=-1, sub_dataset=""):
        """Read paginated key-value pairs from the database."""
        self.connect()
    
        sql = f"SELECT count(1)  as total FROM {table} WHERE dataset = {dataset} AND sub_dataset = '{sub_dataset}'"
        if recorded>-1:
            sql = f"SELECT count(1)  as total FROM {table} WHERE recorded = {recorded} AND dataset = {dataset} AND sub_dataset = '{sub_dataset}'"

        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        self.close()

        if row:
            # Convert the row to a dictionary and then to JSON
            data = dict(row)
            return data["total"]
        else:
            return None  # Return None if no record was found
         
    def count(self, table, filter = -1):
        """Read paginated key-value pairs from the database."""
        self.connect()
    
        sql = f"SELECT count(1) as total FROM {table}"
        if filter>-1:
            sql = f"SELECT count(1)  as total FROM {table} WHERE recorded = {filter}"

        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        self.close()

        if row:
            # Convert the row to a dictionary and then to JSON
            data = dict(row)
            return data["total"]
        else:
            return None  # Return None if no record was found
    
    def read_by_key(self, table: str, key: str, value: Any) -> Optional[dict]:
        """Read a record by a specified key and return it as a dictionary."""
        self.connect()
        sql = f"SELECT * FROM {table} WHERE {key} = ?"
        self.cursor.execute(sql, (value,))
        row = self.cursor.fetchone()
        self.close()
        if row:
            # Convert the row to a dictionary and then to JSON
            data = dict(row)
            json_data = json.dumps(data, indent=4)
            return json_data
        else:
            return None  # Return None if no record was found

    def read_all(self, table: str) -> Optional[dict]:
        """Read a record by a specified key and return it as a dictionary."""
        self.connect()
        sql = f"SELECT * FROM {table}"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        self.close()
        # Convert rows to a list of dictionaries
        data = [dict(row) for row in rows]
        # Convert the list of dictionaries to JSON
        json_data = json.dumps(data, indent=4)
        return json_data
        
    def save_json_data(self, table: str, json_data: list, dataset: int, sub_dataset: str):
        if not all(isinstance(item, dict) for item in json_data):
            raise ValueError("json_data must be a list of JSON objects")
        self.connect()
        for item in json_data:
            columns = ', '.join(item.keys())
            placeholders = ', '.join('?' for _ in item)
            sql = f"INSERT INTO {table} ({columns}, dataset, sub_dataset) VALUES ({placeholders},{dataset},'{sub_dataset}')"
            self.cursor.execute(sql, tuple(item.values()))
        self.connection.commit()
        self.close()
        
    def delete(self, table: str, key: str, value: Any):
        """Delete a key-value pair from the database."""
        self.connect()
        sql = f"DELETE FROM {table} WHERE {key} = ?"
        self.cursor.execute(sql, (value,))
        self.connection.commit()
        self.close()
        return self.cursor.rowcount > 0  # Returns True if a row was deleted

    def delete_sub_data_set(self, table: str, dataset: str, dataset_value: Any, sub_dataset: str, sub_dataset_value: Any):
        """Delete a key-value pair from the database."""
        self.connect()
        sql = f"DELETE FROM {table} WHERE {dataset} = ? and  {sub_dataset} = ?"
        self.cursor.execute(sql, (dataset_value, sub_dataset_value))
        self.connection.commit()
        self.close()
        return self.cursor.rowcount > 0  # Returns True if a row was deleted

    def execute_query(self, query: str):
        """Execute a custom query (use with caution for SELECT queries only)."""
        self.connect()
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.close()
        return results
