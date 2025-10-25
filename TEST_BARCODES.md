# Test Barcodes for AI Nutrition Help

Since the barcode lookup API may not have all products or may have rate limits, we've included several common product barcodes in the mock database for testing.

## How It Works

1. **Barcode Detection**: The scanner can read ANY barcode from an image
2. **Product Lookup**: After detection, it tries to look up the product:
   - First tries the real barcode API (barcodelookup.com)
   - If not found or API fails, checks mock database
   - If not in mock database, returns "Product not found"

## Available Test Barcodes

### Beverages
- **012000161551** - Coca-Cola Classic (20 fl oz)
  - 240 calories, 65g sugar

- **078000113464** - Gatorade Thirst Quencher Fruit Punch (20 fl oz)
  - 140 calories, 34g sugar, 270mg sodium

### Snacks
- **028400047685** - Cheez-It Original Crackers (12.4 oz)
  - 150 calories per serving, 8g fat, 3g protein

- **028400013291** - Pringles Original Potato Crisps (5.5 oz)
  - 150 calories per serving, 10g fat

### Health Food
- **722252601025** - Quest Protein Bar - Chocolate Chip Cookie Dough (2.12 oz)
  - 200 calories, 21g protein, 14g fiber, 1g sugar
  - Great for fitness goals!

### Breakfast
- **016000275683** - Cheerios Cereal (18 oz)
  - 110 calories per serving, 3g protein, 3g fiber

## Testing Instructions

### Option 1: Enter Barcode Number
1. Go to the "Barcode Scanner" tab
2. Enter one of the barcodes above
3. Click "Scan Barcode Number"

### Option 2: Scan from Image
1. Find a product image with one of these barcodes online
2. Upload the image
3. The system will:
   - Detect the barcode automatically
   - Look it up in the database
   - Display the product info (if in mock database)

## Adding More Products

To add more test products, edit the `_get_mock_data()` method in:
`nutrition_agent/services/barcode_api.py`

Add entries in this format:
```python
"BARCODE_NUMBER": {
    "name": "Product Name",
    "brand": "Brand Name",
    "category": "category",
    "price": 2.99,
    "size": "size description",
    "nutrition": {
        "calories": 150,
        "protein": 10,
        "carbohydrates": 20,
        "sugar": 5,
        "fat": 3,
        "saturated_fat": 1,
        "sodium": 200,
        "fiber": 3
    },
    "ingredients": "ingredient list"
}
```

## Real API

If you have a valid API key from barcodelookup.com, set it in your environment:
```bash
export BARCODE_LOOKUP_API_KEY="your_api_key_here"
```

Then restart the server. The system will try the real API first before falling back to mock data.
