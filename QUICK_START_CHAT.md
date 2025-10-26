# Quick Start Guide - AI Chat Interface

## 🚀 Getting Started in 3 Steps

### Step 1: Start the Backend

```bash
cd /home/charlie/Documents/CS_Projects/AINutritionHelp
python backend/api_simple.py
```

**Expected output:**
```
======================================================================
AI Nutrition Help API - HACKATHON DEMO MODE
======================================================================

⚠️  NO AUTHENTICATION - For demo purposes only!

API Endpoints (all use demo user):
  Profile:
    GET    http://localhost:5000/api/profile
    PUT    http://localhost:5000/api/profile

  Nutrition & AI:
    POST   http://localhost:5000/api/barcode/scan
    POST   http://localhost:5000/api/agent/evaluate
    POST   http://localhost:5000/api/agent/chat    👈 NEW!

  Weight Tracking:
    POST   http://localhost:5000/api/weight
    GET    http://localhost:5000/api/weight/history
======================================================================
```

---

### Step 2: Open the Frontend

```bash
# Option 1: Firefox
firefox frontend/nutriscan_zen.html

# Option 2: Chrome
google-chrome frontend/nutriscan_zen.html

# Option 3: Any browser
open frontend/nutriscan_zen.html
```

---

### Step 3: Test the Chat

**Login:** Use `demo_user` / `demo123` (or any credentials)

**You should see:**
```
┌─────────────────────────────────────────────────────────────┐
│ Left Side: Scanner                Right Side: AI Chat       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Barcode Input]                  🤖 AI Nutrition Companion │
│  [Upload Image]                   ────────────────────────  │
│                                   👋 Hi! I'm your AI...     │
│  [Product Details]                                          │
│                                   💪 Quick Actions:         │
│  [Get AI Analysis]                - Pre-workout meal?       │
│                                   - Protein needs?          │
│  [Analysis Results]               - Healthy snacks?         │
│                                                              │
│                                   ────────────────────────  │
│                                   [Type a message...]  [➤]  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 What Changed?

### BEFORE ❌
```
Right Sidebar:
┌──────────────────────────────┐
│ 🧪 Test Products             │
├──────────────────────────────┤
│ Try these sample barcodes:   │
│                              │
│ [Quest Protein Bar]          │
│ 722252601025                 │
│                              │
│ [Coca-Cola Classic]          │
│ 012000161551                 │
│                              │
│ [Gatorade]                   │
│ 078000113464                 │
│                              │
│ [Cheerios]                   │
│ 016000275683                 │
│                              │
│ 💡 Tip                       │
│ AI recommendations are       │
│ personalized...              │
└──────────────────────────────┘
```

### AFTER ✅
```
Right Sidebar:
┌──────────────────────────────┐
│ 🤖 AI Nutrition Companion    │
│ Your personal health asst.   │
├──────────────────────────────┤
│                              │
│ 🤖 Hey there! I just looked  │
│    at the Quest Protein Bar  │
│    you scanned...            │
│                              │
│ 👤 What should I eat after   │
│    my workout?               │
│                              │
│ 🤖 Great question! Based on  │
│    your muscle building...   │
│    [typing...]               │
│                              │
├──────────────────────────────┤
│ [Ask me anything...]     [➤] │
└──────────────────────────────┘
```

---

## 💬 Example Conversations

### Scenario 1: Scanning a Product

**User Action:** Scans barcode `722252601025` (Quest Protein Bar)

**Chat Response (Automatic):**
```
🤖 Hey! I just looked at the Quest Chocolate Chip Cookie Dough
   Protein Bar you scanned.

   This is an excellent choice for muscle building! With 21g of
   protein and only 1g of sugar, it aligns perfectly with your
   high-protein goals.

   Best consumed: Within 30 minutes post-workout

   Overall Score: 85/100 ✅
```

---

### Scenario 2: Asking a Question

**User Types:** "What should I eat before a workout?"

**Chat Response:**
```
🤖 Great question! For your pre-workout meal, I recommend:

   1. Complex carbs for energy (oatmeal, sweet potato)
   2. Moderate protein (20-30g)
   3. Low fat to avoid digestive issues

   Timing: 1-2 hours before exercise

   Example meal:
   - Banana with peanut butter
   - Greek yogurt with berries
   - Whole grain toast with turkey

   This will fuel your moderately active lifestyle!
```

---

### Scenario 3: Follow-up Question

**Context:** Just scanned a Coca-Cola

**User Types:** "Is this bad for me?"

**Chat Response:**
```
🤖 Looking at the Coca-Cola you just scanned - I'll be honest
   with you.

   It contains 39g of sugar, which is close to your entire
   daily recommended limit. For your general health goals,
   this isn't ideal as a regular choice.

   Healthier alternatives:
   - Sparkling water with lemon
   - Unsweetened iced tea
   - Coconut water (for electrolytes)

   Occasional treat? Sure! Just balance it with your other meals.
```

---

## 🧪 Test Commands

### Test the Chat API Directly

```bash
curl -X POST http://localhost:5000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is a healthy breakfast?"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "A healthy breakfast should include..."
}
```

---

### Test with Product Context

```bash
curl -X POST http://localhost:5000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Is this good for me?",
    "product": {
      "name": "Quest Protein Bar",
      "barcode": "722252601025",
      "nutrition": {
        "calories": 190,
        "protein": 21,
        "sugar": 1
      }
    }
  }'
```

---

## 🎨 UI Features to Try

### 1. Quick Action Buttons
Click any of the pre-defined questions:
- 💪 "What should I eat before a workout?"
- 🥗 "How much protein do I need daily?"
- 🍎 "What are healthy snack options?"

### 2. Typing Animation
Watch the three animated dots while AI thinks:
```
🤖 [• • •]  (animated)
```

### 3. Auto-Scroll
Messages automatically scroll to bottom

### 4. Enter Key
Press Enter instead of clicking send button

### 5. Context Awareness
The AI remembers:
- Your user profile (goals, activity level)
- Recently scanned products
- Your dietary restrictions

---

## 🔧 Troubleshooting

### Issue: Chat not responding

**Check:**
1. Backend is running: `curl http://localhost:5000/api/health`
2. Browser console for errors: F12 → Console tab
3. Network tab shows successful API calls

**Fix:**
```bash
# Restart backend
Ctrl+C
python backend/api_simple.py
```

---

### Issue: "Nutrition agent not available"

**Check:**
1. Environment variable: `GOOGLE_API_KEY` is set
2. File exists: `agent/.env`

**Fix:**
```bash
cd agent
cat .env  # Should show GOOGLE_API_KEY=...

# If missing:
echo "GOOGLE_API_KEY=your_key_here" > .env
```

---

### Issue: Chat appears but messages don't send

**Check:**
1. Browser console (F12)
2. Network tab → look for `/api/agent/chat` request
3. Check response status

**Common causes:**
- CORS error (backend not running on localhost:5000)
- JavaScript error (check console)
- API timeout (increase timeout in code)

---

## 📱 Mobile View

The chat is fully responsive! Try resizing your browser:

**Desktop (>968px):**
- Chat height: 600px
- Message bubbles: 75% max-width
- Side-by-side layout

**Mobile (<968px):**
- Chat height: 500px
- Message bubbles: 85% max-width
- Stacked layout

---

## 🎯 Success Indicators

✅ **It's working if you see:**
- Welcome message with 👋 icon
- Quick action buttons are clickable
- Typing indicator appears when sending
- AI responses show in white bubbles
- Your messages show in green bubbles
- Auto-scroll to latest message

❌ **Something's wrong if:**
- Chat area is blank
- Messages don't appear
- Send button stays disabled
- Network errors in console
- "Nutrition agent not available" error

---

## 🚀 Next Steps

1. **Customize quick actions:** Edit the button text in `nutriscan_zen.html` (lines 1332-1340)

2. **Change chat styling:** Modify CSS variables in `nutriscan_zen.html` (lines 639-907)

3. **Add more context:** Enhance the `sendChatMessage()` function to include more user data

4. **Implement persistence:** Save chat history to `localStorage` or database

5. **Add markdown support:** Use a markdown parser for formatted AI responses

---

## 📚 Related Files

- **Full Documentation:** [AI_CHAT_INTEGRATION.md](AI_CHAT_INTEGRATION.md)
- **Frontend Code:** [frontend/nutriscan_zen.html](frontend/nutriscan_zen.html)
- **Backend API:** [backend/api_simple.py](backend/api_simple.py)
- **Agent Service:** [agent/service.py](agent/service.py)
- **Main Agent:** [agent/main_agent.py](agent/main_agent.py)

---

**Happy Chatting! 🎉**
