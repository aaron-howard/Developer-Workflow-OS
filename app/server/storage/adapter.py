from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

class StorageAdapter(ABC):
    @abstractmethod
    def insert(self, collection: str, data: Dict[str, Any]) -> str:
        """Insert a document and return its ID."""
        pass
        
    @abstractmethod
    def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID."""
        pass
        
    @abstractmethod
    def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update a document by ID."""
        pass

class ConvexStorageAdapter(StorageAdapter):
    # In a real implementation, this would import the convex client
    def __init__(self, client_url: str):
        self.url = client_url
        
    def insert(self, collection: str, data: Dict[str, Any]) -> str:
        # Mock implementation for Convex mutation
        return f"convex_id_{collection}"
        
    def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        # Mock implementation for Convex query
        return {"id": doc_id, "mock": True}
        
    def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        # Mock implementation for Convex mutation
        return True
