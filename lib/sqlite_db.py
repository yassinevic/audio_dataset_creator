import json
import sqlite3
from typing import Any, Dict, List, Optional

class SQLiteDBHelper:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Allows access to columns by name
        self.cursor = self.connection.cursor()

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

    def insert(self, table: str, data: dict):
        """Insert a record into a table."""
        self.connect()
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(data.values()))
        self.connection.commit()
        self.close()

    def flag(self, table: str, is_recorded: int, id:int):
        """Insert a record into a table."""
        self.connect()
        sql = f"UPDATE {table} set recorded  = ? where id = ?"
        self.cursor.execute(sql, (is_recorded,id))
        self.connection.commit()
        self.close()

    def read_sentences(self, table, recorded = -1, dataset=-1, sub_dataset="", page=1, page_size=10):
        """Read paginated key-value pairs from the database."""
        self.connect()
    
        # Calculate the offset for the given page and page_size
        offset = (page - 1) * page_size
    
        # SQL query with LIMIT and OFFSET for pagination
        sql = f"SELECT * FROM {table} WHERE dataset = {dataset} AND sub_dataset = '{sub_dataset}' LIMIT {page_size} OFFSET {offset}"
        if recorded>-1:
            sql = f"SELECT * FROM {table} WHERE recorded = {recorded} AND dataset = {dataset} AND sub_dataset = '{sub_dataset}' LIMIT {page_size} OFFSET {offset}"

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
    
        sql = f"SELECT count(1)  as total FROM {table}"
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


    def execute_query(self, query: str):
        """Execute a custom query (use with caution for SELECT queries only)."""
        self.connect()
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.close()
        return results
