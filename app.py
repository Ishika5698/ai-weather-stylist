import requests
import argparse
from flask import Flask, request, render_template
import time
import json
import os
from requests.exceptions import RequestException
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_CITY = "London"
FALLBACK_WEATHER = {"temp": 15, "condition": "partly cloudy"}
FAVORITES_FILE = "favorites.json"

def validate_city(city):
    """Validate city using WeatherAPI's autocomplete endpoint."""
    try:
        response = requests.get(f"http://api.weatherapi.com/v1/search.json?key={API_KEY}&q={city}", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Autocomplete Response for {city}: {data}")
        return (True, None) if data else (False, "City not found. Please select a valid city.")
    except RequestException as e:
        print(f"City validation error: {str(e)}")
        return False, f"Network error: {str(e)}. Check your connection."

def get_weather(city, day=0):
    """Get current or forecast weather for city using WeatherAPI."""
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days={day+1}&aqi=no"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if day == 0:
            weather = {"temp": data["current"]["temp_c"], "condition": data["current"]["condition"]["text"].lower()}
        else:
            weather = {"temp": data["forecast"]["forecastday"][day]["day"]["avgtemp_c"], "condition": data["forecast"]["forecastday"][day]["day"]["condition"]["text"].lower()}
        print(f"Weather Response for {city}, day {day}: {weather}")
        return weather, None
    except RequestException as e:
        print(f"Weather fetch error for {city}: {str(e)}")
        return FALLBACK_WEATHER, f"Network error: {str(e)}."
    except Exception as e:
        print(f"Unexpected error for {city}: {str(e)}")
        return FALLBACK_WEATHER, f"API error: {str(e)}."

def recommend_outfit(occasion, color, temp, condition, mood, city, gender, day):
    """Generate outfit recommendation with description based on inputs."""
    valid_colors = ["blue", "red", "black", "white", "green", "yellow", "purple", "orange", "pink", "gray", "navy", "beige"]
    color = color.lower() if color else "default"
    if color not in valid_colors:
        color = "default"
    gender = gender.lower() if gender else "male"
    if gender not in ["male", "female"]:
        gender = "male"

    outfits = {
        "casual": {
            "male": {
                "blue": {
                    "bold": {"items": "Blue leather jacket, black jeans, sneakers", "description": "This bold blue look screams confidence with a sleek leather jacket, perfect for a night out."},
                    "minimal": {"items": "Blue chinos, white tee, loafers", "description": "A clean, minimalist blue outfit that’s effortlessly stylish for any casual day."},
                    "cozy": {"items": "Blue hoodie, gray joggers, slip-ons", "description": "Stay comfy yet cool with this cozy blue hoodie ensemble, ideal for lounging or errands."}
                },
                "red": {"bold": {"items": "Red bomber jacket, black pants, boots", "description": "Make a statement with this vibrant red bomber jacket."}, "minimal": {"items": "Red shirt, khaki shorts, sneakers", "description": "Casual and cool red look."}, "cozy": {"items": "Red sweatshirt, black joggers, slippers", "description": "Warm and relaxed red outfit."}},
                "black": {"bold": {"items": "Black denim jacket, gray tee, combat boots", "description": "Edgy black denim vibe."}, "minimal": {"items": "Black jeans, white shirt, sneakers", "description": "Simple black and white classic."}, "cozy": {"items": "Black hoodie, sweatpants, slippers", "description": "Ultimate black comfort."}},
                "white": {"bold": {"items": "White graphic tee, cargo pants, high-tops", "description": "Bold white street style."}, "minimal": {"items": "White linen shirt, beige shorts, loafers", "description": "Crisp white summer look."}, "cozy": {"items": "White sweater, gray sweats, sneakers", "description": "Cozy white warmth."}},
                "green": {"bold": {"items": "Green parka, black jeans, boots", "description": "Rugged green adventure style."}, "minimal": {"items": "Green polo, khaki pants, sneakers", "description": "Fresh green casual."}, "cozy": {"items": "Green hoodie, joggers, slip-ons", "description": "Relaxed green comfort."}},
                "yellow": {"bold": {"items": "Yellow jacket, black shorts, sneakers", "description": "Bright yellow energy."}, "minimal": {"items": "Yellow tee, denim jeans, loafers", "description": "Sunny yellow simplicity."}, "cozy": {"items": "Yellow sweatshirt, gray pants, sneakers", "description": "Warm yellow coziness."}},
                "purple": {"bold": {"items": "Purple blazer, black tee, jeans", "description": "Vibrant purple flair."}, "minimal": {"items": "Purple shirt, gray shorts, sneakers", "description": "Subtle purple charm."}, "cozy": {"items": "Purple hoodie, black joggers, slippers", "description": "Cozy purple retreat."}},
                "orange": {"bold": {"items": "Orange windbreaker, black pants, boots", "description": "Bold orange adventure."}, "minimal": {"items": "Orange tee, khaki shorts, sneakers", "description": "Playful orange casual."}, "cozy": {"items": "Orange sweater, joggers, slip-ons", "description": "Warm orange comfort."}},
                "pink": {"bold": {"items": "Pink jacket, white tee, jeans", "description": "Striking pink confidence."}, "minimal": {"items": "Pink shirt, beige pants, loafers", "description": "Soft pink elegance."}, "cozy": {"items": "Pink hoodie, gray sweats, sneakers", "description": "Cozy pink vibes."}},
                "gray": {"bold": {"items": "Gray graphic tee, black cargo pants, sneakers", "description": "Urban gray edge."}, "minimal": {"items": "Gray polo, denim jeans, oxfords", "description": "Classic gray polish."}, "cozy": {"items": "Gray sweatshirt, joggers, slippers", "description": "Relaxed gray comfort."}},
                "navy": {"bold": {"items": "Navy bomber jacket, black jeans, boots", "description": "Sleek navy cool."}, "minimal": {"items": "Navy shirt, khaki chinos, sneakers", "description": "Crisp navy casual."}, "cozy": {"items": "Navy hoodie, gray joggers, slip-ons", "description": "Cozy navy warmth."}},
                "beige": {"bold": {"items": "Beige jacket, black pants, sneakers", "description": "Modern beige flair."}, "minimal": {"items": "Beige tee, denim shorts, loafers", "description": "Light beige ease."}, "cozy": {"items": "Beige sweater, joggers, sneakers", "description": "Warm beige comfort."}},
                "default": {"bold": {"items": "Gray tee, cargo pants, high-tops", "description": "Versatile gray street style."}, "minimal": {"items": "Gray polo, jeans, oxfords", "description": "Timeless gray simplicity."}, "cozy": {"items": "Gray sweatshirt, joggers, sneakers", "description": "Ultimate gray coziness."}}
            },
            "female": {
                "blue": {
                    "bold": {"items": "Blue denim skirt, crop top, ankle boots", "description": "This bold blue outfit radiates trendy vibes with a chic denim skirt, perfect for a stylish day out."},
                    "minimal": {"items": "Blue midi dress, white sneakers", "description": "A sleek blue midi dress for a minimalist, effortless look that shines anywhere."},
                    "cozy": {"items": "Blue knit sweater, leggings, fuzzy boots", "description": "Wrap yourself in cozy blue comfort with this soft sweater and fuzzy boots combo."}
                },
                "red": {"bold": {"items": "Red jumpsuit, black heels", "description": "Fiery red jumpsuit for a bold statement."}, "minimum": {"items": "Red blouse, white jeans, flats", "description": "Elegant red and white simplicity."}, "cozy": {"items": "Red cardigan, black leggings, slippers", "description": "Cozy red warmth."}},
                "black": {"bold": {"items": "Black leather pants, graphic tee, boots", "description": "Edgy black leather look."}, "minimal": {"items": "Black shift dress, ballet flats", "description": "Classic black dress elegance."}, "cozy": {"items": "Black oversized sweater, joggers, sneakers", "description": "Relaxed black comfort."}},
                "white": {"bold": {"items": "White blazer, ripped jeans, heels", "description": "Chic white blazer style."}, "minimal": {"items": "White sundress, sandals", "description": "Breezy white summer dress."}, "cozy": {"items": "White hoodie, sweatpants, fuzzy socks", "description": "Cozy white lounge wear."}},
                "green": {"bold": {"items": "Green maxi skirt, crop top, sandals", "description": "Vibrant green boho chic."}, "minimal": {"items": "Green blouse, beige pants, flats", "description": "Fresh green elegance."}, "cozy": {"items": "Green sweater, leggings, boots", "description": "Warm green coziness."}},
                "yellow": {"bold": {"items": "Yellow dress, statement necklace, heels", "description": "Sunny yellow glamour."}, "minimal": {"items": "Yellow top, denim skirt, sneakers", "description": "Playful yellow casual."}, "cozy": {"items": "Yellow hoodie, joggers, slippers", "description": "Cozy yellow comfort."}},
                "purple": {"bold": {"items": "Purple jumpsuit, gold earrings, boots", "description": "Regal purple flair."}, "minimal": {"items": "Purple blouse, black jeans, flats", "description": "Subtle purple charm."}, "cozy": {"items": "Purple cardigan, leggings, sneakers", "description": "Cozy purple retreat."}},
                "orange": {"bold": {"items": "Orange skirt, white top, heels", "description": "Bold orange vibrancy."}, "minimal": {"items": "Orange dress, sandals", "description": "Bright orange simplicity."}, "cozy": {"items": "Orange sweater, black joggers, boots", "description": "Warm orange comfort."}},
                "pink": {"bold": {"items": "Pink blazer, black dress, heels", "description": "Striking pink sophistication."}, "minimal": {"items": "Pink top, white shorts, flats", "description": "Soft pink casual."}, "cozy": {"items": "Pink hoodie, gray leggings, slippers", "description": "Cozy pink vibes."}},
                "gray": {"bold": {"items": "Gray jumpsuit, statement belt, boots", "description": "Modern gray edge."}, "minimal": {"items": "Gray blouse, black skirt, flats", "description": "Classic gray polish."}, "cozy": {"items": "Gray sweatshirt, leggings, sneakers", "description": "Relaxed gray comfort."}},
                "navy": {"bold": {"items": "Navy dress, silver accessories, heels", "description": "Elegant navy glamour."}, "minimal": {"items": "Navy top, beige pants, sneakers", "description": "Crisp navy casual."}, "cozy": {"items": "Navy cardigan, black leggings, boots", "description": "Cozy navy warmth."}},
                "beige": {"bold": {"items": "Beige trench coat, black dress, boots", "description": "Sophisticated beige style."}, "minimal": {"items": "Beige blouse, denim jeans, flats", "description": "Light beige ease."}, "cozy": {"items": "Beige hoodie, joggers, sneakers", "description": "Warm beige comfort."}},
                "default": {"bold": {"items": "Gray jumpsuit, necklace, boots", "description": "Versatile gray chic."}, "minimal": {"items": "Gray blouse, black jeans, flats", "description": "Timeless gray simplicity."}, "cozy": {"items": "Gray sweatshirt, leggings, sneakers", "description": "Ultimate gray coziness."}}
            }
        },
        "formal": {
            "male": {
                "blue": {"bold": {"items": "Navy suit, patterned blue tie, brogues", "description": "Sharp navy suit for a bold formal presence."}, "minimal": {"items": "Navy suit, white shirt, no tie", "description": "Clean navy suit elegance."}, "cozy": {"items": "Navy blazer, white shirt, wool scarf", "description": "Warm navy formal style."}},
                "default": {"bold": {"items": "Gray suit, colorful tie, wingtips", "description": "Classic gray suit flair."}, "minimal": {"items": "Gray suit, white shirt, black shoes", "description": "Timeless gray suit."}, "cozy": {"items": "Gray suit, turtleneck, overcoat", "description": "Cozy gray formal."}}
            },
            "female": {
                "blue": {"bold": {"items": "Navy gown, statement earrings, heels", "description": "Elegant navy gown for a stunning entrance."}, "minimal": {"items": "Navy pencil dress, nude pumps", "description": "Sleek navy dress sophistication."}, "cozy": {"items": "Navy wrap dress, warm shawl", "description": "Cozy navy elegance."}},
                "default": {"bold": {"items": "Gray gown, pearl necklace, heels", "description": "Regal gray gown."}, "minimal": {"items": "Gray dress, black pumps", "description": "Simple gray elegance."}, "cozy": {"items": "Gray blazer, turtleneck, trousers", "description": "Warm gray formal."}}
            }
        },
        "work": {
            "male": {
                "blue": {"bold": {"items": "Blue blazer, white shirt, khaki pants, loafers", "description": "Professional blue blazer for a confident office look."}, "minimal": {"items": "Blue dress shirt, gray slacks, oxfords", "description": "Crisp blue shirt for a polished workday."}, "cozy": {"items": "Blue sweater, chinos, boots", "description": "Comfortable blue sweater for a relaxed office vibe."}},
                "default": {"bold": {"items": "Gray blazer, white shirt, navy pants, loafers", "description": "Sharp gray office style."}, "minimal": {"items": "Gray shirt, black slacks, oxfords", "description": "Simple gray work look."}, "cozy": {"items": "Gray sweater, chinos, boots", "description": "Cozy gray office comfort."}}
            },
            "female": {
                "blue": {"bold": {"items": "Blue pantsuit, white blouse, heels", "description": "Powerful blue pantsuit for a commanding office presence."}, "minimal": {"items": "Blue blouse, pencil skirt, flats", "description": "Elegant blue blouse for a professional day."}, "cozy": {"items": "Blue cardigan, trousers, boots", "description": "Cozy blue cardigan for a comfortable workday."}},
                "default": {"bold": {"items": "Gray blazer, white dress, heels", "description": "Chic gray office style."}, "minimal": {"items": "Gray blouse, black skirt, flats", "description": "Simple gray work look."}, "cozy": {"items": "Gray cardigan, trousers, boots", "description": "Cozy gray office comfort."}}
            }
        },
        "party": {
            "male": {
                "blue": {"bold": {"items": "Blue velvet blazer, black shirt, jeans, loafers", "description": "Sleek blue velvet for a standout party vibe."}, "minimal": {"items": "Blue shirt, black pants, sneakers", "description": "Cool blue party casual."}, "cozy": {"items": "Blue sweater, chinos, boots", "description": "Relaxed blue party comfort."}},
                "default": {"bold": {"items": "Gray blazer, black shirt, jeans, loafers", "description": "Stylish gray party look."}, "minimal": {"items": "Gray tee, black pants, sneakers", "description": "Simple gray party style."}, "cozy": {"items": "Gray hoodie, jeans, boots", "description": "Cozy gray party vibe."}}
            },
            "female": {
                "blue": {"bold": {"items": "Blue sequin dress, heels", "description": "Dazzling blue sequins to light up the party."}, "minimal": {"items": "Blue top, black jeans, flats", "description": "Chic blue party casual."}, "cozy": {"items": "Blue sweater, skirt, boots", "description": "Cozy blue party comfort."}},
                "default": {"bold": {"items": "Gray party dress, heels", "description": "Sparkling gray party glamour."}, "minimal": {"items": "Gray top, black jeans, flats", "description": "Simple gray party look."}, "cozy": {"items": "Gray cardigan, jeans, boots", "description": "Cozy gray party style."}}
            }
        },
        "date_night": {
            "male": {
                "blue": {"bold": {"items": "Blue blazer, black shirt, jeans, loafers", "description": "Suave blue blazer for a romantic evening."}, "minimal": {"items": "Blue shirt, gray pants, sneakers", "description": "Effortless blue date-night charm."}, "cozy": {"items": "Blue sweater, chinos, boots", "description": "Warm blue outfit for a cozy date."}},
                "default": {"bold": {"items": "Gray blazer, black shirt, jeans, loafers", "description": "Sleek gray date-night style."}, "minimal": {"items": "Gray shirt, navy pants, sneakers", "description": "Simple gray date look."}, "cozy": {"items": "Gray sweater, jeans, boots", "description": "Cozy gray date comfort."}}
            },
            "female": {
                "blue": {"bold": {"items": "Blue wrap dress, heels", "description": "Elegant blue wrap dress for a stunning date night."}, "minimal": {"items": "Blue blouse, black jeans, flats", "description": "Chic blue date-night casual."}, "cozy": {"items": "Blue sweater, skirt, boots", "description": "Cozy blue outfit for a romantic evening."}},
                "default": {"bold": {"items": "Gray dress, black heels", "description": "Romantic gray date-night glamour."}, "minimal": {"items": "Gray blouse, black jeans, flats", "description": "Simple gray date look."}, "cozy": {"items": "Gray cardigan, jeans, boots", "description": "Cozy gray date comfort."}}
            }
        }
    }
    mood = mood.lower() if mood else "minimal"
    if mood not in ["bold", "minimal", "cozy"]:
        mood = "minimal"
    
    outfit_data = outfits.get(occasion.lower(), outfits["casual"]).get(gender).get(color, outfits[occasion.lower()][gender]["default"]).get(mood)
    base_outfit = outfit_data["items"]
    description = outfit_data["description"]
    
    # Weather-based adjustments
    day_text = "Today" if day == 0 else f"In {day} day{'s' if day > 1 else ''}"
    if temp is not None:
        if temp < 5:
            base_outfit += ", heavy winter coat, scarf"
        elif temp < 10:
            base_outfit += ", warm coat"
        elif temp < 18:
            base_outfit += ", light jacket"
        elif temp > 30:
            base_outfit += ", lightweight scarf"
        elif temp > 25:
            base_outfit += ", breathable hat"
    
    if condition:
        if any(w in condition.lower() for w in ["rain", "shower", "drizzle"]):
            base_outfit += ", and an umbrella"
        elif "snow" in condition.lower():
            base_outfit += ", and snow boots"
        elif "clear" in condition.lower() and temp > 20:
            base_outfit += ", and sunglasses"
    
    return f"Recommended outfit for {occasion} in {color} (Mood: {mood}, Gender: {gender}, Weather: {temp}°C, {condition}, City: {city}, {day_text}): {base_outfit}\n\n{description}"

def run_cli():
    """Run CLI mode with argparse."""
    parser = argparse.ArgumentParser(description="AI Stylist: Get outfit recommendations")
    parser.add_argument("--occasion", type=str, default="casual", choices=["casual", "formal", "work", "party", "date_night"], help="Occasion")
    parser.add_argument("--color", type=str, default="default", choices=["blue", "red", "black", "white", "green", "yellow", "purple", "orange", "pink", "gray", "navy", "beige", "default"], help="Color preference")
    parser.add_argument("--mood", type=str, default="minimal", choices=["bold", "minimal", "cozy"], help="Style mood")
    parser.add_argument("--city", type=str, default=DEFAULT_CITY, help="City for weather-based recommendation")
    parser.add_argument("--gender", type=str, default="male", choices=["male", "female"], help="Gender")
    parser.add_argument("--day", type=int, default=0, choices=[0, 1, 2, 3], help="Weather forecast day (0=today, 1-3=forecast)")
    args = parser.parse_args()

    is_valid, error = validate_city(args.city)
    if not is_valid:
        print(f"Error: Invalid city - {error}. Using {DEFAULT_CITY}")
        args.city = DEFAULT_CITY

    weather, error = get_weather(args.city, args.day)
    if error:
        print(f"Warning: {error}")
    recommendation = recommend_outfit(args.occasion, args.color, weather["temp"], weather["condition"], args.mood, args.city, args.gender, args.day)
    print(recommendation)

@app.route("/", methods=["GET", "POST"])
def index():
    """Handle web app requests."""
    recommendation = None
    error = None
    defaults = {"occasion": "casual", "color": "default", "mood": "minimal", "city": DEFAULT_CITY, "gender": "male", "day": "0"}
    if request.method == "POST":
        occasion = request.form.get("occasion", defaults["occasion"])
        color = request.form.get("color", defaults["color"])
        mood = request.form.get("mood", defaults["mood"])
        city = request.form.get("city", defaults["city"]).strip()
        gender = request.form.get("gender", defaults["gender"])
        day = int(request.form.get("day", defaults["day"]))
        if not city:
            error = "City name cannot be empty."
        else:
            is_valid, city_error = validate_city(city)
            if not is_valid:
                error = f"Invalid city: {city_error}. Using {DEFAULT_CITY}."
                city = DEFAULT_CITY
            if not error:
                weather, weather_error = get_weather(city, day)
                if weather_error:
                    error = weather_error
                else:
                    recommendation = recommend_outfit(occasion, color, weather["temp"], weather["condition"], mood, city, gender, day)
        defaults.update({"occasion": occasion, "color": color, "mood": mood, "city": city, "gender": gender, "day": str(day)})
    return render_template("index.html", recommendation=recommendation, error=error, defaults=defaults, timestamp=int(time.time()))

@app.route("/save_favorite", methods=["POST"])
def save_favorite():
    """Save an outfit to favorites."""
    outfit = request.form.get("outfit")
    if not os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "w") as f:
            json.dump([], f)
    with open(FAVORITES_FILE, "r+") as f:
        favorites = json.load(f)
        favorites.append(outfit)
        f.seek(0)
        json.dump(favorites, f, indent=2)
    return {"status": "success"}

@app.route("/favorites")
def view_favorites():
    """View saved favorite outfits."""
    try:
        with open(FAVORITES_FILE, "r") as f:
            favorites = json.load(f)
    except FileNotFoundError:
        favorites = []
    return render_template("favorites.html", favorites=favorites)

@app.route("/validate_city", methods=["GET"])
def validate_city_endpoint():
    """Validate city via API for client-side requests."""
    city = request.args.get("city")
    is_valid, error = validate_city(city)
    return {"valid": is_valid, "error": error}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_cli()
    else:
        app.run(debug=True, port=5001)