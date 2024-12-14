from typing import Tuple
import pandas as pd
from database.db_manager import DatabaseManager

class FamilyService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def create_family(self, name: str) -> Tuple[bool, str]:
        """Create a new family"""
        if not name.strip():
            return False, "Family name cannot be empty"
        return self.db.add_family(name)

    def get_all_families(self) -> pd.DataFrame:
        """Get all families"""
        return self.db.get_all_families()

    def get_family_details(self, family_id: int) -> pd.DataFrame:
        """Get family details including all clients"""
        query = """
            SELECT f.name as family_name, 
                   COUNT(DISTINCT c.id) as total_clients,
                   COUNT(DISTINCT h.id) as total_holdings
            FROM families f
            LEFT JOIN clients c ON f.id = c.family_id
            LEFT JOIN holdings h ON c.id = h.client_id
            WHERE f.id = ?
            GROUP BY f.id
        """
        return self.db.execute_query(query, (family_id,))