"""
Recipe Nutrition Calculator
Calculates nutritional values for recipes based on ingredient data
"""

import mysql.connector
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
from nutrition_service import NutritionService, NutritionData
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RecipeNutrition:
    """Nutritional information for a complete recipe"""
    recipe_id: int
    recipe_name: str
    servings: int
    
    # Total nutrition for entire recipe
    total_calories: float = 0.0
    total_protein: float = 0.0
    total_carbohydrates: float = 0.0
    total_fat: float = 0.0
    total_fiber: float = 0.0
    total_sodium: float = 0.0
    
    # Per serving
    calories_per_serving: float = 0.0
    protein_per_serving: float = 0.0
    carbs_per_serving: float = 0.0
    fat_per_serving: float = 0.0
    fiber_per_serving: float = 0.0
    sodium_per_serving: float = 0.0
    
    # Metadata
    ingredients_analyzed: int = 0
    ingredients_total: int = 0
    coverage_percent: float = 0.0


@dataclass
class IngredientNutritionBreakdown:
    """Nutritional breakdown for a single ingredient in a recipe"""
    ingredient_id: int
    ingredient_name: str
    portion_grams: float
    calories: float
    protein: float
    carbohydrates: float
    fat: float


class RecipeNutritionCalculator:
    """
    Calculates nutritional values for recipes
    """
    
    def __init__(self):
        self.db = self._connect_db()
        self.nutrition_service = NutritionService(self.db)
    
    def _connect_db(self):
        """Connect to MySQL database"""
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "costomenu")
        )
    
    def get_recipe_ingredients(self, recipe_id: int) -> List[Tuple]:
        """
        Get all ingredients for a recipe with their portions
        
        Returns:
            List of (ingredient_id, ingredient_name, portion, unit_name)
        """
        cursor = self.db.cursor()
        
        query = """
            SELECT 
                ri.ingredient_id,
                i.name as ingredient_name,
                ri.portion,
                u.name as unit_name,
                i.base_unit_id
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            LEFT JOIN units u ON ri.portion_unit_id = u.id
            WHERE ri.recipe_id = %s
            ORDER BY ri.ordinal
        """
        
        cursor.execute(query, (recipe_id,))
        return cursor.fetchall()
    
    def convert_to_grams(
        self, 
        portion: float, 
        unit_name: str, 
        ingredient_id: int
    ) -> float:
        """
        Convert ingredient portion to grams
        
        Args:
            portion: Amount of ingredient
            unit_name: Unit of measurement (e.g., 'kg', 'ml', 'piece')
            ingredient_id: ID to look up conversions
        
        Returns:
            Weight in grams
        """
        # Common conversions
        conversions = {
            'kg': 1000,
            'g': 1,
            'ml': 1,  # Assume 1ml = 1g for liquids (water density)
            'l': 1000,
            'τεμ': 100,  # Default piece weight
            'piece': 100,
        }
        
        if unit_name in conversions:
            return portion * conversions[unit_name]
        
        # TODO: Look up ingredient-specific conversions from ingredient_units table
        # For now, assume grams
        return portion
    
    def calculate_recipe_nutrition(
        self, 
        recipe_id: int
    ) -> Optional[RecipeNutrition]:
        """
        Calculate complete nutritional breakdown for a recipe
        
        Args:
            recipe_id: ID of recipe to analyze
        
        Returns:
            RecipeNutrition object with complete breakdown
        """
        # Get recipe info
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, serving FROM recipes WHERE id = %s", 
            (recipe_id,)
        )
        recipe = cursor.fetchone()
        
        if not recipe:
            print(f"Recipe {recipe_id} not found")
            return None
        
        servings = recipe['serving'] or 1
        
        # Initialize result
        result = RecipeNutrition(
            recipe_id=recipe_id,
            recipe_name=recipe['name'],
            servings=servings
        )
        
        # Get all ingredients
        ingredients = self.get_recipe_ingredients(recipe_id)
        result.ingredients_total = len(ingredients)
        
        breakdown = []
        
        for ing_id, ing_name, portion, unit_name, base_unit_id in ingredients:
            # Get or fetch nutrition data
            nutrition = self.nutrition_service.get_nutrition_from_db(ing_id)
            
            if not nutrition:
                print(f"Fetching nutrition for '{ing_name}'...")
                nutrition = self.nutrition_service.fetch_nutrition_for_ingredient(ing_name)
                
                if nutrition:
                    self.nutrition_service.save_nutrition_to_db(ing_id, nutrition)
            
            if not nutrition or not nutrition.calories:
                print(f"⚠️  No nutrition data for '{ing_name}'")
                continue
            
            # Convert portion to grams
            portion_grams = self.convert_to_grams(portion, unit_name or 'g', ing_id)
            
            # Calculate nutrition for this portion (nutrition is per 100g)
            factor = portion_grams / 100.0
            
            ing_calories = (nutrition.calories or 0) * factor
            ing_protein = (nutrition.protein or 0) * factor
            ing_carbs = (nutrition.carbohydrates or 0) * factor
            ing_fat = (nutrition.fat or 0) * factor
            ing_fiber = (nutrition.fiber or 0) * factor
            ing_sodium = (nutrition.sodium or 0) * factor
            
            # Add to totals
            result.total_calories += ing_calories
            result.total_protein += ing_protein
            result.total_carbohydrates += ing_carbs
            result.total_fat += ing_fat
            result.total_fiber += ing_fiber
            result.total_sodium += ing_sodium
            
            result.ingredients_analyzed += 1
            
            breakdown.append(IngredientNutritionBreakdown(
                ingredient_id=ing_id,
                ingredient_name=ing_name,
                portion_grams=portion_grams,
                calories=ing_calories,
                protein=ing_protein,
                carbohydrates=ing_carbs,
                fat=ing_fat
            ))
        
        # Calculate per serving
        if servings > 0:
            result.calories_per_serving = result.total_calories / servings
            result.protein_per_serving = result.total_protein / servings
            result.carbs_per_serving = result.total_carbohydrates / servings
            result.fat_per_serving = result.total_fat / servings
            result.fiber_per_serving = result.total_fiber / servings
            result.sodium_per_serving = result.total_sodium / servings
        
        # Calculate coverage
        if result.ingredients_total > 0:
            result.coverage_percent = (
                result.ingredients_analyzed / result.ingredients_total * 100
            )
        
        return result, breakdown
    
    def print_nutrition_report(
        self, 
        nutrition: RecipeNutrition, 
        breakdown: List[IngredientNutritionBreakdown]
    ):
        """Print formatted nutrition report"""
        print("\n" + "="*60)
        print(f"📊 NUTRITIONAL ANALYSIS: {nutrition.recipe_name}")
        print("="*60)
        
        print(f"\n🍽️  Servings: {nutrition.servings}")
        print(f"📈 Coverage: {nutrition.coverage_percent:.1f}% "
              f"({nutrition.ingredients_analyzed}/{nutrition.ingredients_total} ingredients)")
        
        print("\n" + "-"*60)
        print("PER SERVING:")
        print("-"*60)
        print(f"  Calories:       {nutrition.calories_per_serving:>8.1f} kcal")
        print(f"  Protein:        {nutrition.protein_per_serving:>8.1f} g")
        print(f"  Carbohydrates:  {nutrition.carbs_per_serving:>8.1f} g")
        print(f"  Fat:            {nutrition.fat_per_serving:>8.1f} g")
        print(f"  Fiber:          {nutrition.fiber_per_serving:>8.1f} g")
        print(f"  Sodium:         {nutrition.sodium_per_serving:>8.1f} mg")
        
        print("\n" + "-"*60)
        print("TOTAL RECIPE:")
        print("-"*60)
        print(f"  Calories:       {nutrition.total_calories:>8.1f} kcal")
        print(f"  Protein:        {nutrition.total_protein:>8.1f} g")
        print(f"  Carbohydrates:  {nutrition.total_carbohydrates:>8.1f} g")
        print(f"  Fat:            {nutrition.total_fat:>8.1f} g")
        
        if breakdown:
            print("\n" + "-"*60)
            print("INGREDIENT BREAKDOWN:")
            print("-"*60)
            for ing in breakdown:
                print(f"\n  {ing.ingredient_name} ({ing.portion_grams:.0f}g):")
                print(f"    Calories: {ing.calories:.1f} kcal")
                print(f"    Protein:  {ing.protein:.1f}g")
                print(f"    Carbs:    {ing.carbohydrates:.1f}g")
                print(f"    Fat:      {ing.fat:.1f}g")
        
        print("\n" + "="*60 + "\n")


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python recipe_nutrition_calculator.py <recipe_id>")
        print("Example: python recipe_nutrition_calculator.py 123")
        sys.exit(1)
    
    recipe_id = int(sys.argv[1])
    
    calculator = RecipeNutritionCalculator()
    result = calculator.calculate_recipe_nutrition(recipe_id)
    
    if result:
        nutrition, breakdown = result
        calculator.print_nutrition_report(nutrition, breakdown)
        
        # Save to JSON
        output_file = f"recipe_{recipe_id}_nutrition.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'nutrition': asdict(nutrition),
                'breakdown': [asdict(b) for b in breakdown]
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved detailed report to: {output_file}")
    else:
        print(f"❌ Could not calculate nutrition for recipe {recipe_id}")


if __name__ == "__main__":
    main()
