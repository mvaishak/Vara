# Vara

An intelligent personal styling application powered by AI that helps users get outfit recommendations based on their closet and occasion.

## Features

- 👗 **Outfit Recommendations**: Get AI-powered styling suggestions for any occasion
- 📸 **Closet Management**: Upload and organize your clothing items
- 🎨 **Visual Styling**: View outfit combinations with your actual clothing images
- 🔍 **Clothing Analysis**: Automatic analysis of clothing attributes
- 💾 **Persistent Storage**: Save and manage your closet data

## Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: OpenAI API with LangChain
- **Image Processing**: Pillow
- **Data Management**: JSON-based storage
- **Environment Management**: Python-dotenv

## Project Structure

```
ai-personal-stylist/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── assets/
│   └── style.css         # Custom styling
├── core/
│   ├── analyzer.py       # Clothing analysis logic
│   ├── database.py       # Data persistence
│   ├── stylist.py        # AI stylist recommendations
│   └── __init__.py
├── data/
│   ├── my_closet.json    # Closet data storage
│   └── closet_images/    # Stored clothing images
└── utils/
    ├── helpers.py        # Utility functions
    └── __init__.py
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-personal-stylist
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   VARIATION_COUNT=3
   ```

## Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Access the app**
   Open your browser and navigate to `http://localhost:8501`

3. **Build your closet**
   - Upload clothing items with descriptions
   - The app will analyze and categorize them

4. **Get recommendations**
   - Describe an occasion or style preference
   - Receive AI-powered outfit suggestions
   - View combinations with your actual clothing

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `VARIATION_COUNT`: Number of outfit variations to generate (default: 3)

## API Keys

This application requires an OpenAI API key to function. Get one at [platform.openai.com](https://platform.openai.com)

