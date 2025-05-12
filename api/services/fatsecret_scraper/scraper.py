from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import quote
from uuid import uuid4
from datetime import datetime
from time import sleep

from api.models.food_analysis import FoodAnalysisResult, NutritionInfo


def create_browser(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def parse_float(s: str) -> float:
    """Parse a string to float, handling various formats including comma as decimal separator."""
    # Remove all non-numeric characters except decimal separators
    cleaned = ''.join(c for c in s if c.isdigit() or c in '.,')
    # Replace comma with dot for decimal
    return float(cleaned.replace(',', '.')) if cleaned else 0.0


def search_and_scrape_as_analysis_result(keyword: str) -> FoodAnalysisResult:
    driver = create_browser()
    try:
        print(f"🔍 Searching for: {keyword}")
        search_url = f"https://www.fatsecret.co.id/kalori-gizi/search?q={quote(keyword)}"
        driver.get(search_url)
        sleep(2)

        all_links = driver.find_elements(By.CSS_SELECTOR, "a")
        first_link = next(
            (a for a in all_links
             if (href := a.get_attribute("href"))
             and "/kalori-gizi/umum/" in href
             and not href.rstrip("/").endswith("/umum")),
            None
        )

        if not first_link:
            raise Exception("No valid result found.")

        # Dismiss cookie if needed
        try:
            driver.execute_script("""
                const btn = document.querySelector('.cc-btn.cc-allow');
                if (btn) { btn.click(); }
            """)
            sleep(1)
        except:
            pass

        driver.execute_script("arguments[0].click();", first_link)
        sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Extract food name from h1
        food_name = soup.select_one("h1").text.strip() if soup.select_one("h1") else keyword
        print(f"📋 Food name: {food_name}")

        # Find the nutrition facts div
        nutrition_facts = soup.select_one("div.nutrition_facts.international")
        if not nutrition_facts:
            raise Exception("Nutrition facts section not found.")

        # Extract serving size
        serving_size_el = nutrition_facts.select_one(".serving_size_value")
        serving_size = serving_size_el.text.strip() if serving_size_el else "Not specified"
        print(f"🍽️ Serving size: {serving_size}")

        # Initialize nutrition data structure
        nutrition_data = {
            "food_name": food_name,
            "calories": 0.0,
            "fat": 0.0,
            "saturated_fat": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fiber": 0.0,
            "sugar": 0.0,
            "sodium": 0.0,
            "cholesterol": 0.0,
            "vitamins_and_minerals": {}
        }

        # Process each nutrient row in the table
        nutrient_rows = nutrition_facts.find_all(["div"], class_=lambda c: c and "nutrient" in c and ("left" in c or "right" in c))
        
        # Group rows together for processing
        i = 0
        while i < len(nutrient_rows):
            # Skip header rows
            if "header" in nutrient_rows[i].get("class", []):
                i += 1
                continue
                
            # Get the label (left side)
            if "left" in nutrient_rows[i].get("class", []):
                label = nutrient_rows[i].text.strip().lower()
                
                # Find the corresponding value (right side)
                value_el = None
                if i + 1 < len(nutrient_rows) and "right" in nutrient_rows[i+1].get("class", []):
                    value_el = nutrient_rows[i+1]
                    value_text = value_el.text.strip()
                    
                    try:
                        # Extract numeric value and unit
                        value = parse_float(value_text)
                        unit = ''.join(c for c in value_text if not c.isdigit() and c not in '., ').strip()
                        
                        print(f"📊 {label} → {value_text} → {value} {unit}")
                        
                        # Handle each nutrient type
                        if "energi" in label:
                            if "kj" in value_text.lower():
                                # Store kJ value but don't convert to kcal yet - look for direct kcal value
                                nutrition_data["vitamins_and_minerals"]["energy_kj"] = value
                            elif "kkal" in value_text.lower():
                                nutrition_data["calories"] = value
                        elif label == "":  # Empty label usually follows Energi (kJ) with a kcal value
                            if "kkal" in value_text.lower() and nutrition_data["calories"] == 0.0:
                                nutrition_data["calories"] = value
                        elif "lemak jenuh" in label:
                            nutrition_data["saturated_fat"] = value
                        elif "lemak tak jenuh ganda" in label:
                            nutrition_data["vitamins_and_minerals"]["polyunsaturated_fat"] = value
                        elif "lemak tak jenuh tunggal" in label:
                            nutrition_data["vitamins_and_minerals"]["monounsaturated_fat"] = value
                        elif "lemak" in label and "tak jenuh" not in label and "jenuh" not in label:
                            nutrition_data["fat"] = value
                        elif "karbohidrat" in label:
                            nutrition_data["carbs"] = value
                        elif "protein" in label:
                            nutrition_data["protein"] = value
                        elif "serat" in label:
                            nutrition_data["fiber"] = value
                        elif "gula" in label:
                            nutrition_data["sugar"] = value
                        elif "natrium" in label or "sodium" in label:
                            nutrition_data["sodium"] = value
                        elif "kolesterol" in label:
                            nutrition_data["cholesterol"] = value
                        elif "kalium" in label:
                            nutrition_data["vitamins_and_minerals"]["potassium"] = value
                    except Exception as e:
                        print(f"❌ Error parsing {label}: {e}")
                
                # Move to the next label
                i += 2
            else:
                i += 1

        # If no direct kcal value was found, convert from kJ if available
        if nutrition_data["calories"] == 0.0 and "energy_kj" in nutrition_data["vitamins_and_minerals"]:
            nutrition_data["calories"] = nutrition_data["vitamins_and_minerals"]["energy_kj"] / 4.184
            print(f"🔄 Converted {nutrition_data['vitamins_and_minerals']['energy_kj']} kJ to {nutrition_data['calories']} kcal")

        # Create NutritionInfo object
        nutrition_info = NutritionInfo(
            calories=nutrition_data["calories"],
            protein=nutrition_data["protein"],
            carbs=nutrition_data["carbs"],
            fat=nutrition_data["fat"],
            saturated_fat=nutrition_data["saturated_fat"],
            sodium=nutrition_data["sodium"],
            fiber=nutrition_data["fiber"],
            sugar=nutrition_data["sugar"],
            cholesterol=nutrition_data["cholesterol"],
            nutrition_density=0.0,  # Calculate this based on your formula if needed
            vitamins_and_minerals=nutrition_data["vitamins_and_minerals"]
        )

        # Create and return the result
        return FoodAnalysisResult(
            food_name=nutrition_data["food_name"],  # Changed from foodName to food_name
            nutrition_info=nutrition_info,
            ingredients=[],
            additionalInformation={"serving_size": serving_size},
            warnings=[],
            foodImageUrl=None,
            timestamp=datetime.utcnow(),
            id=str(uuid4()),
            userId="anonymous",
            healthScore=0.0  # Calculate this based on your formula if needed
        )

    except Exception as e:
        print(f"❌ Error scraping '{keyword}': {e}")
        return FoodAnalysisResult(
            food_name=keyword,  # Changed from foodName to food_name
            error=str(e),
            nutrition_info=None,
            ingredients=[],
            additionalInformation={},
            warnings=[],
            foodImageUrl=None,
            timestamp=datetime.utcnow(),
            id=str(uuid4()),
            userId="anonymous",
            healthScore=0.0
        )
    finally:
        driver.quit()


if __name__ == "__main__":
    keyword = input("Enter food to search: ")
    result = search_and_scrape_as_analysis_result(keyword)
    print(result.model_dump_json(indent=2))