import pytest
from unittest.mock import patch, MagicMock
from api.models.food_analysis import FoodAnalysisResult, NutritionInfo
from api.services.fatsecret_scraper.scraper import search_and_scrape_as_analysis_result


@patch("api.services.fatsecret_scraper.scraper.create_browser")
def test_positive_valid_food_scrape(mock_create_browser):
    mock_driver = MagicMock()
    mock_create_browser.return_value = mock_driver

    mock_driver.page_source = '''
    <html>
        <body>
            <h1>Nasi Goreng</h1>
            <div class="nutrition_facts international">
                <div class="serving_size_value">100 gram</div>
                <div class="nutrient black left">Energi</div>
                <div class="nutrient black right">168 kkal</div>
                <div class="nutrient black left">Lemak</div>
                <div class="nutrient black right">5g</div>
                <div class="nutrient black left">Protein</div>
                <div class="nutrient black right">6g</div>
            </div>
        </body>
    </html>
    '''

    mock_link = MagicMock()
    mock_link.get_attribute.return_value = "https://www.fatsecret.co.id/kalori-gizi/umum/nasi-goreng"
    mock_driver.find_elements.return_value = [mock_link]

    result = search_and_scrape_as_analysis_result("nasi goreng")

    assert result.food_name.lower() == "nasi goreng"
    assert result.nutrition_info is not None
    assert result.nutrition_info.calories == 168.0
    assert result.nutrition_info.fat == 5.0
    assert result.nutrition_info.protein == 6.0

@patch("api.services.fatsecret_scraper.scraper.create_browser")
def test_negative_food_not_found(mock_create_browser):
    mock_driver = MagicMock()
    mock_create_browser.return_value = mock_driver

    # Simulate no links found
    mock_driver.find_elements.return_value = []

    result = search_and_scrape_as_analysis_result("nonexistentfood123")

    assert result.nutrition_info is None
    assert result.error is not None
    assert "No valid result found" in result.error

@patch("api.services.fatsecret_scraper.scraper.create_browser")
def test_corner_empty_keyword(mock_create_browser):
    mock_driver = MagicMock()
    mock_create_browser.return_value = mock_driver

    # Simulate no links found
    mock_driver.find_elements.return_value = []

    result = search_and_scrape_as_analysis_result("")

    assert result.nutrition_info is None
    assert result.error is not None
    assert "No valid result found" in result.error