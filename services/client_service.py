from typing import Tuple, Optional
import pandas as pd
from database.db_manager import DatabaseManager

class ClientService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_client(self, name: str, family_id: int) -> Tuple[bool, str]:
        """Create a new client"""
        if not name.strip():
            return False, "Client name cannot be empty"
        return self.db.add_client(name, family_id)

    def get_all_clients(self) -> pd.DataFrame:
        """Get all clients with their family information"""
        return self.db.get_all_clients()

    def get_client_details(self, client_id: int) -> Optional[pd.DataFrame]:
        """Get detailed information about a specific client"""
        query = """
            SELECT c.id, c.name as client_name, 
                   f.name as family_name,
                   COUNT(h.id) as num_holdings,
                   SUM(h.quantity * h.buy_price) as total_investment
            FROM clients c
            JOIN families f ON c.family_id = f.id
            LEFT JOIN holdings h ON c.id = h.client_id
            WHERE c.id = ?
            GROUP BY c.id
        """
        return self.db.execute_query(query, (client_id,))