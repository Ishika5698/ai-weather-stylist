# AI Weather Stylist

A Flask-based web and CLI app that recommends personalized outfits based on city weather (via WeatherAPI), gender, occasion (casual, formal, work, party, date_night), mood (bold, minimal, cozy), and color preferences (12 options). Features 300+ outfit combinations, a favorites system, 3-day weather forecast, and vivid outfit descriptions.

## Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/ai-weather-stylist.git
   cd ai-weather-stylist
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up WeatherAPI key:
   - Get a key at [WeatherAPI](https://www.weatherapi.com).
   - Create a  file:
     ```bash
     echo "WEATHER_API_KEY=your-key" > .env
     ```
4. Run the app:
   ```bash
   python app.py
   ```
   - Web: Open 
   - CLI: usage: app.py [-h] [--occasion {casual,formal,work,party,date_night}]
              [--color {blue,red,black,white,green,yellow,purple,orange,pink,gray,navy,beige,default}]
              [--mood {bold,minimal,cozy}] [--city CITY]
              [--gender {male,female}] [--day {0,1,2,3}]

AI Stylist: Get outfit recommendations

options:
  -h, --help            show this help message and exit
  --occasion {casual,formal,work,party,date_night}
                        Occasion
  --color {blue,red,black,white,green,yellow,purple,orange,pink,gray,navy,beige,default}
                        Color preference
  --mood {bold,minimal,cozy}
                        Style mood
  --city CITY           City for weather-based recommendation
  --gender {male,female}
                        Gender
  --day {0,1,2,3}       Weather forecast day (0=today, 1-3=forecast)

## Features
- 300+ outfits across 5 occasions, 2 genders, 3 moods, 12 colors.
- Weather-based recommendations with 3-day forecast.
- Save favorite outfits to .
- Premium indigo-themed UI with animated dropdowns.

## License
MIT License
