import sqlite3
from typing import List, Optional, Tuple
import pandas as pd
from .models import Family, Client, Holding

class DatabaseManager:
    def __init__(self, db_path: str = 'portfolio.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            # Create tables if they don't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS families (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    family_id INTEGER,
                    FOREIGN KEY (family_id) REFERENCES families (id),
                    UNIQUE(name, family_id)
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    ticker TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    buy_price REAL NOT NULL,
                    buy_date DATE NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            conn.commit()

    def execute_query(self, query: str, params: tuple = (), fetch: bool = True) -> Optional[pd.DataFrame]:
        with self.get_connection() as conn:
            if fetch:
                return pd.read_sql_query(query, conn, params=params)
            conn.execute(query, params)
            conn.commit()
            return None

    # Family operations
    def add_family(self, name: str) -> Tuple[bool, str]:
        try:
            self.execute_query(
                "INSERT INTO families (name) VALUES (?)",
                (name,),
                fetch=False
            )
            return True, f"Family '{name}' added successfully"
        except sqlite3.IntegrityError:
            return False, "Family already exists"

    def get_all_families(self) -> pd.DataFrame:
        return self.execute_query("SELECT * FROM families")

    # Client operations
    def add_client(self, name: str, family_id: int) -> Tuple[bool, str]:
        try:
            self.execute_query(
                "INSERT INTO clients (name, family_id) VALUES (?, ?)",
                (name, family_id),
                fetch=False
            )
            return True, f"Client '{name}' added successfully"
        except sqlite3.IntegrityError:
            return False, "Client already exists in this family"

    def get_all_clients(self) -> pd.DataFrame:
        return self.execute_query("""
            SELECT clients.id, clients.name, families.name as family_name 
            FROM clients 
            JOIN families ON clients.family_id = families.id
        """)

    def get_client_holdings(self, client_id: int) -> pd.DataFrame:
        return self.execute_query("""
            SELECT ticker, quantity, buy_price, buy_date
            FROM holdings
            WHERE client_id = ?
        """, (client_id,))