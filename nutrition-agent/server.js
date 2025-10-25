import express from 'express';
import { genkit } from 'genkit';
import { googleAI, gemini15Flash } from '@genkit-ai/googleai';
import dotenv from 'dotenv';
import axios from 'axios';

dotenv.config();

const app = express();
app.use(express.json());
app.use(express.static('public'));

// Initialize Genkit
const ai = genkit({
  plugins: [googleAI({ apiKey: process.env.GOOGLE_GENAI_API_KEY })]
});

// Simple barcode lookup function
async function lookupBarcode(barcode) {
  try {
    const response = await axios.get(
      `https://api.barcodelookup.com/v3/products?barcode=${barcode}&key=${process.env.BARCODE_LOOKUP_API_KEY}`
    );
    if (response.data.products?.[0]) {
      return response.data.products[0];
    }
    return null;
  } catch (error) {
    console.error('Barcode lookup error:', error);
    return null;
  }
}

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    // Check if message contains a barcode (numeric pattern)
    const barcodeMatch = message.match(/\b\d{8,13}\b/);
    let context = '';
    
    if (barcodeMatch) {
      const product = await lookupBarcode(barcodeMatch[0]);
      if (product) {
        context = `\n\nProduct Information:\nName: ${product.title}\nBrand: ${product.brand}\nCategory: ${product.category}\nIngredients: ${product.ingredients || 'Not available'}`;
      }
    }
    
    const systemPrompt = `You are a helpful nutrition and fitness assistant. Help users analyze products for their health and fitness goals.${context}`;
    
    const result = await ai.generate({
      model: gemini15Flash,
      prompt: message,
      system: systemPrompt,
      config: { temperature: 0.7 }
    });
    
    res.json({ response: result.text() });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});