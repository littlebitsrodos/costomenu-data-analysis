"""
Nutrition Service - Open Food Facts API Integration
Fetches and caches nutritional data for ingredients from Open Food Facts.
"""

import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NutritionData:
    """Nutritional information per 100g"""
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    saturated_fat: Optional[float] = None
    sugars: Optional[float] = None
    source: str = "openfoodfacts"
    external_id: Optional[str] = None
    confidence_score: float = 0.0


class OpenFoodFactsAPI:
    """
    Open Food Facts API Client
    Documentation: https://openfoodfacts.github.io/openfoodfacts-server/api/
    """
    
    BASE_URL = "https://world.openfoodfacts.org"
    USER_AGENT = "CostoMenu/1.0 (https://costo.menu; contact@costo.menu)"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT
        })
    
    def search_product(self, query: str, country_code: str = "gr") -> List[Dict[str, Any]]:
        """
        Search for products by name
        
        Args:
            query: Product name to search for (e.g., "ντομάτα", "feta cheese")
            country_code: ISO 2-letter country code (default: "gr" for Greece)
        
        Returns:
            List of product dictionaries
        """
        url = f"{self.BASE_URL}/cgi/search.pl"
        params = {
            "search_terms": query,
            "countries": country_code,
            "json": 1,
            "page_size": 10,
            "fields": "code,product_name,nutriments,nutrition_grades"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("products", [])
        except Exception as e:
            logger.error(f"Error searching Open Food Facts: {e}")
            return []
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Get product details by barcode
        
        Args:
            barcode: Product barcode (EAN-13, UPC, etc.)
        
        Returns:
            Product dictionary or None if not found
        """
        url = f"{self.BASE_URL}/api/v0/product/{barcode}.json"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == 1:
                return data.get("product")
            return None
        except Exception as e:
            logger.error(f"Error fetching product {barcode}: {e}")
            return None
    
    def extract_nutrition(self, product: Dict[str, Any]) -> NutritionData:
        """
        Extract nutritional data from Open Food Facts product
        
        Args:
            product: Product dictionary from API
        
        Returns:
            NutritionData object
        """
        nutriments = product.get("nutriments", {})
        
        # Open Food Facts uses different keys for per 100g values
        # Keys ending in _100g are normalized per 100g
        nutrition = NutritionData(
            calories=nutriments.get("energy-kcal_100g"),
            protein=nutriments.get("proteins_100g"),
            carbohydrates=nutriments.get("carbohydrates_100g"),
            fat=nutriments.get("fat_100g"),
            fiber=nutriments.get("fiber_100g"),
            sodium=nutriments.get("sodium_100g"),  # in mg
            saturated_fat=nutriments.get("saturated-fat_100g"),
            sugars=nutriments.get("sugars_100g"),
            external_id=product.get("code"),
            source="openfoodfacts"
        )
        
        # Calculate confidence score based on completeness
        fields = [nutrition.calories, nutrition.protein, 
                  nutrition.carbohydrates, nutrition.fat]
        filled_fields = sum(1 for f in fields if f is not None)
        nutrition.confidence_score = filled_fields / len(fields)
        
        return nutrition


class NutritionService:
    """
    High-level service for managing nutritional data
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: MySQL database connection
        """
        self.db = db_connection
        self.api = OpenFoodFactsAPI()
    
    def fetch_nutrition_for_ingredient(
        self, 
        ingredient_name: str,
        force_refresh: bool = False
    ) -> Optional[NutritionData]:
        """
        Fetch nutritional data for an ingredient
        
        Args:
            ingredient_name: Name of ingredient (e.g., "Tomato", "Feta")
            force_refresh: If True, bypass cache and fetch fresh data
        
        Returns:
            NutritionData object or None if not found
        """
        # Search Open Food Facts
        products = self.api.search_product(ingredient_name)
        
        if not products:
            logger.warning(f"No products found for '{ingredient_name}'")
            return None
        
        # Take the first result (best match)
        best_match = products[0]
        nutrition = self.api.extract_nutrition(best_match)
        
        logger.info(
            f"Found nutrition for '{ingredient_name}': "
            f"{nutrition.calories} kcal, "
            f"confidence={nutrition.confidence_score:.2f}"
        )
        
        return nutrition
    
    def save_nutrition_to_db(
        self, 
        ingredient_id: int, 
        nutrition: NutritionData
    ) -> bool:
        """
        Save nutritional data to database
        
        Args:
            ingredient_id: ID from ingredients table
            nutrition: NutritionData object
        
        Returns:
            True if successful, False otherwise
        """
        cursor = self.db.cursor()
        
        query = """
            INSERT INTO ingredient_nutrition (
                ingredient_id, calories, protein, carbohydrates, fat,
                fiber, sodium, saturated_fat, sugars,
                source, external_id, confidence_score, last_synced
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE
                calories = VALUES(calories),
                protein = VALUES(protein),
                carbohydrates = VALUES(carbohydrates),
                fat = VALUES(fat),
                fiber = VALUES(fiber),
                sodium = VALUES(sodium),
                saturated_fat = VALUES(saturated_fat),
                sugars = VALUES(sugars),
                source = VALUES(source),
                external_id = VALUES(external_id),
                confidence_score = VALUES(confidence_score),
                last_synced = VALUES(last_synced),
                updated_at = CURRENT_TIMESTAMP
        """
        
        try:
            cursor.execute(query, (
                ingredient_id,
                nutrition.calories,
                nutrition.protein,
                nutrition.carbohydrates,
                nutrition.fat,
                nutrition.fiber,
                nutrition.sodium,
                nutrition.saturated_fat,
                nutrition.sugars,
                nutrition.source,
                nutrition.external_id,
                nutrition.confidence_score,
                datetime.now()
            ))
            self.db.commit()
            logger.info(f"Saved nutrition data for ingredient_id={ingredient_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving nutrition data: {e}")
            self.db.rollback()
            return False
    
    def get_nutrition_from_db(self, ingredient_id: int) -> Optional[NutritionData]:
        """
        Retrieve cached nutritional data from database
        
        Args:
            ingredient_id: ID from ingredients table
        
        Returns:
            NutritionData object or None if not found
        """
        cursor = self.db.cursor(dictionary=True)
        
        query = """
            SELECT * FROM ingredient_nutrition 
            WHERE ingredient_id = %s
        """
        
        cursor.execute(query, (ingredient_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return NutritionData(
            calories=row["calories"],
            protein=row["protein"],
            carbohydrates=row["carbohydrates"],
            fat=row["fat"],
            fiber=row["fiber"],
            sodium=row["sodium"],
            saturated_fat=row["saturated_fat"],
            sugars=row["sugars"],
            source=row["source"],
            external_id=row["external_id"],
            confidence_score=row["confidence_score"]
        )


if __name__ == "__main__":
    # Example usage
    api = OpenFoodFactsAPI()
    
    # Test search
    print("Searching for 'ντομάτα'...")
    products = api.search_product("ντομάτα")
    
    if products:
        print(f"Found {len(products)} products")
        first = products[0]
        print(f"First result: {first.get('product_name')}")
        
        nutrition = api.extract_nutrition(first)
        print(f"Nutrition: {nutrition}")
    else:
        print("No products found")
