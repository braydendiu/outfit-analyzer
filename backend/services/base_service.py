from typing import List, Dict, Any

class BaseFashionService:
    def _get_color_hex(self, color: str) -> str:
        color_map = {
            "black": "#000000",
            "white": "#FFFFFF",
            "gray": "#808080",
            "red": "#FF0000",
            "blue": "#0000FF",
            "green": "#008000",
            "yellow": "#FFD700",
            "purple": "#800080",
            "pink": "#FFC0CB",
            "brown": "#A0522D",
            "beige": "#F5F5DC"
        }
        return color_map.get(color.lower(), "#808080")