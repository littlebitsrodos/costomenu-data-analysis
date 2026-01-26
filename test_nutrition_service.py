"""
Test Nutrition Service - Verify Open Food Facts API Integration
Tests the nutrition service without requiring database connection
"""

from nutrition_service import OpenFoodFactsAPI, NutritionData
import json


def test_search_greek_products():
    """Test searching for Greek products"""
    print("\n" + "="*60)
    print("TEST 1: Searching for Greek Products")
    print("="*60)
    
    api = OpenFoodFactsAPI()
    
    test_queries = [
        "ντομάτα",      # Tomato
        "φέτα",         # Feta
        "αγγούρι",      # Cucumber
        "ελιές",        # Olives
        "πιπεριά",      # Pepper
    ]
    
    results = {}
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        products = api.search_product(query, country_code="gr")
        
        if products:
            first = products[0]
            print(f"  ✅ Found: {first.get('product_name', 'N/A')}")
            print(f"  📦 Code: {first.get('code', 'N/A')}")
            
            nutrition = api.extract_nutrition(first)
            print(f"  🥗 Nutrition (per 100g):")
            print(f"     Calories: {nutrition.calories or 'N/A'} kcal")
            print(f"     Protein: {nutrition.protein or 'N/A'}g")
            print(f"     Carbs: {nutrition.carbohydrates or 'N/A'}g")
            print(f"     Fat: {nutrition.fat or 'N/A'}g")
            print(f"     Confidence: {nutrition.confidence_score:.0%}")
            
            results[query] = {
                'product_name': first.get('product_name'),
                'nutrition': {
                    'calories': nutrition.calories,
                    'protein': nutrition.protein,
                    'carbohydrates': nutrition.carbohydrates,
                    'fat': nutrition.fat,
                    'confidence': nutrition.confidence_score
                }
            }
        else:
            print(f"  ❌ No products found")
            results[query] = None
    
    return results


def test_barcode_lookup():
    """Test looking up products by barcode"""
    print("\n" + "="*60)
    print("TEST 2: Barcode Lookup")
    print("="*60)
    
    api = OpenFoodFactsAPI()
    
    # Example Greek product barcodes (these may or may not exist)
    test_barcodes = [
        "5201007009336",  # Example Greek barcode
        "3017620422003",  # Nutella (international)
    ]
    
    for barcode in test_barcodes:
        print(f"\n🔍 Looking up barcode: {barcode}")
        product = api.get_product_by_barcode(barcode)
        
        if product:
            print(f"  ✅ Found: {product.get('product_name', 'N/A')}")
            nutrition = api.extract_nutrition(product)
            print(f"  Calories: {nutrition.calories or 'N/A'} kcal/100g")
        else:
            print(f"  ❌ Product not found")


def test_fresh_greek_salad():
    """Test calculating nutrition for the Fresh Greek Salad from the image"""
    print("\n" + "="*60)
    print("TEST 3: Fresh Greek Salad Nutrition")
    print("="*60)
    
    api = OpenFoodFactsAPI()
    
    # Ingredients from the uploaded image
    ingredients = [
        {"name": "Tomato", "grams": 150.0},
        {"name": "Cucumber", "grams": 70.0},
        {"name": "Green Pepper", "grams": 30.0},
        {"name": "Feta", "grams": 80.0},
        {"name": "Black Olive", "grams": 20.0},
        {"name": "Oregano", "grams": 2.0},
        {"name": "Red Onion", "grams": 20.0},
        {"name": "Cherry Tomato", "grams": 10.0},
    ]
    
    total_nutrition = {
        'calories': 0,
        'protein': 0,
        'carbohydrates': 0,
        'fat': 0,
    }
    
    print("\n📋 Ingredient Breakdown:")
    print("-" * 60)
    
    for ing in ingredients:
        # Search for the ingredient
        products = api.search_product(ing['name'])
        
        if products:
            nutrition = api.extract_nutrition(products[0])
            
            # Calculate for the specific portion (nutrition is per 100g)
            factor = ing['grams'] / 100.0
            
            ing_cal = (nutrition.calories or 0) * factor
            ing_prot = (nutrition.protein or 0) * factor
            ing_carbs = (nutrition.carbohydrates or 0) * factor
            ing_fat = (nutrition.fat or 0) * factor
            
            total_nutrition['calories'] += ing_cal
            total_nutrition['protein'] += ing_prot
            total_nutrition['carbohydrates'] += ing_carbs
            total_nutrition['fat'] += ing_fat
            
            print(f"\n{ing['name']} ({ing['grams']}g):")
            print(f"  Calories: {ing_cal:.1f} kcal")
            print(f"  Protein: {ing_prot:.1f}g")
            print(f"  Carbs: {ing_carbs:.1f}g")
            print(f"  Fat: {ing_fat:.1f}g")
        else:
            print(f"\n{ing['name']} ({ing['grams']}g): ⚠️  No data found")
    
    print("\n" + "="*60)
    print("TOTAL NUTRITION (Fresh Greek Salad):")
    print("="*60)
    print(f"Calories:       {total_nutrition['calories']:.1f} kcal")
    print(f"Protein:        {total_nutrition['protein']:.1f}g")
    print(f"Carbohydrates:  {total_nutrition['carbohydrates']:.1f}g")
    print(f"Fat:            {total_nutrition['fat']:.1f}g")
    print("="*60 + "\n")
    
    return total_nutrition


def main():
    """Run all tests"""
    print("\n🧪 NUTRITION SERVICE TEST SUITE")
    print("Testing Open Food Facts API Integration\n")
    
    # Test 1: Search Greek products
    search_results = test_search_greek_products()
    
    # Test 2: Barcode lookup
    test_barcode_lookup()
    
    # Test 3: Calculate Fresh Greek Salad
    salad_nutrition = test_fresh_greek_salad()
    
    # Save results
    output = {
        'search_results': search_results,
        'fresh_greek_salad': salad_nutrition
    }
    
    with open('nutrition_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("✅ Test results saved to: nutrition_test_results.json")


if __name__ == "__main__":
    main()
