from typing import Dict, List, Any
from .shein_service import SheinAPIService

class LocalFashionService:
    def __init__(self):
        self.shein_service = SheinAPIService()

    async def find_matching_items(self, category: str, color: str) -> List[Dict[str, Any]]:
        try:
            return await self.shein_service.search_products(category, color)
        except Exception as e:
            print(f"Error finding matching items: {str(e)}")
            return []

    def get_all_categories(self) -> List[str]:
        return ["tops", "bottoms", "outerwear", "shoes"]