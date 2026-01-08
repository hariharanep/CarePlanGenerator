from abc import ABC, abstractmethod
from typing import Dict, List

class DataStore(ABC):
    CONFLICT_KEY = "conflict"
    ERROR_MESSAGE_KEY = "message"

    @abstractmethod
    def validate_order(self, data: Dict) -> List:
        pass

    @abstractmethod
    def validate_provider(self, npi: str, name: str) -> Dict:
        pass

    @abstractmethod
    def add_provider(self, npi: str, name: str):
        pass

    @abstractmethod
    def validate_patient(self, mrn: str, first_name: str, last_name: str) -> Dict:
        pass

    @abstractmethod
    def add_patient(self, mrn: str, first_name: str, last_name: str):
        pass

    @abstractmethod
    def check_duplicate_order(self, mrn: str, medication: str) -> bool:
        pass

    @abstractmethod
    def add_order(self, order_data: Dict):
        pass

    @abstractmethod
    def export_orders(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_stats(self) -> Dict:
        pass
