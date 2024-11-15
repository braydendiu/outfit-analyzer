import aiohttp
from typing import List, Dict, Any
import traceback
import json
import asyncio
from .base_service import BaseFashionService

class SheinAPIService(BaseFashionService):
    def __init__(self):
        super().__init__()
        print("[DEBUG] Initializing SheinAPIService")
        self.base_url = "https://unofficial-shein.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": "d5e9dab93dmsh3371d8d2b83d55ep1207adjsn36f976d11a37",
            "X-RapidAPI-Host": "unofficial-shein.p.rapidapi.com"
        }

    async def search_products(self, category: str, color: str, gender: str = 'women', limit: int = 4) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/products/search"
            params = {
                "keywords": f"{gender} {color} {category}",
                "language": "en",
                "country": "US",
                "currency": "USD",
                "page": "1",
                "limit": str(limit),
                "sort": "7",
                "price_min": "0",
                "price_max": "200"
            }

            print(f"[DEBUG] Making request with params: {params}")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"[DEBUG] API Response: {json.dumps(data, indent=2)[:500]}...")
                        
                        if data.get("code") == "0" and data.get("msg") == "ok":
                            products = data.get("info", {}).get("products", [])
                            formatted_products = []
                            
                            for product in products[:limit]:
                                formatted = self._format_product(product, category, color, gender)
                                if formatted and formatted["price"]["current"] > 0:
                                    formatted_products.append(formatted)
                                    print(f"[DEBUG] Added product: {formatted['title']} - ${formatted['price']['current']}")
                            
                            if formatted_products:
                                return formatted_products

            return self._get_fallback_products(category, color, gender)

        except Exception as e:
            print(f"[ERROR] Search error: {str(e)}")
            print(traceback.format_exc())
            return self._get_fallback_products(category, color, gender)

    def _format_product(self, product: Dict, category: str, color: str, gender: str) -> Dict[str, Any]:
        try:
            # Get image URL
            image_url = product.get("goods_img", "")
            if image_url and not image_url.startswith(('http://', 'https://')):
                image_url = f"https:{image_url}"

            # Clean up the product title
            title = product.get("goods_name", "").strip()
            # Remove SHEIN and MOD from title and clean up
            title = title.replace("SHEIN", "").replace("MOD", "").replace("  ", " ").strip()
            if not title:
                title = f"{color.capitalize()} {category.capitalize()}"

            # Handle price
            try:
                price = None
                if "salePrice" in product:
                    price = float(product["salePrice"].get("amount", 0))
                elif "retailPrice" in product:
                    price = float(product["retailPrice"].get("amount", 0))
                elif "retail_price" in product:
                    price = float(product["retail_price"])
                elif "price" in product:
                    if isinstance(product["price"], dict):
                        price = float(product["price"].get("amount", 0))
                    else:
                        price = float(product["price"])
                
                if not price or price == 0:
                    default_prices = {
                        "tops": 19.99,
                        "bottoms": 24.99,
                        "dresses": 34.99,
                        "outerwear": 39.99,
                        "shoes": 29.99
                    }
                    price = default_prices.get(category.lower(), 29.99)
                
            except (ValueError, TypeError) as e:
                print(f"[ERROR] Price parsing error: {str(e)}")
                price = 29.99

            return {
                "title": title,
                "image_url": image_url,
                "price": {
                    "current": price,
                    "currency": "USD",
                    "color": self._get_color_hex(color)
                },
                "category": category.lower(),
                "type": category.capitalize(),
                "id": product.get("goods_id", ""),
                "product_url": product.get("detail_url", "")
            }

        except Exception as e:
            print(f"[ERROR] Product formatting error: {str(e)}")
            return None

    def _get_fallback_products(self, category: str, color: str, gender: str) -> List[Dict[str, Any]]:
        default_prices = {
            "tops": 19.99,
            "bottoms": 24.99,
            "dresses": 34.99,
            "outerwear": 39.99,
            "shoes": 29.99
        }
        
        return [{
            "title": f"{color.capitalize()} {category.capitalize()}",
            "image_url": f"https://via.placeholder.com/400x600.png?text={color}+{category}",
            "price": {
                "current": default_prices.get(category.lower(), 29.99),
                "currency": "USD",
                "color": self._get_color_hex(color)
            },
            "category": category.lower(),
            "type": category.capitalize()
        }]