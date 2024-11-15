from services.shein_service import SheinAPIService
from services.base_service import BaseFashionService
import asyncio
import json

async def test_service():
    print("Starting SHEIN service test...")
    service = SheinAPIService()
    
    # Test cases
    tests = [
        ("dress", "pink"),
        ("tops", "black"),
        ("shoes", "white")
    ]
    
    for category, color in tests:
        print(f"\nTesting search for {color} {category}")
        try:
            products = await service.search_products(category, color, limit=2)
            
            if products:
                print(f"\nFound {len(products)} products:")
                for idx, product in enumerate(products, 1):
                    print(f"\nProduct {idx}:")
                    print(f"Title: {product.get('title', 'No title')}")
                    print(f"Image: {product.get('image_url', 'No image')}")
                    print(f"Price: ${product.get('price', {}).get('current', 'No price')}")
                    print(f"Category: {product.get('category', 'No category')}")
            else:
                print("No products found")
                
        except Exception as e:
            print(f"Error testing {color} {category}: {str(e)}")

if __name__ == "__main__":
    print("Running test script...")
    asyncio.run(test_service())
    print("\nTest complete.")