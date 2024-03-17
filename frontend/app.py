from flask import Flask, render_template
import random
import json
import jsonify

app = Flask(__name__)

# Simulate your data generation
def get_simulation_data():
    #print('hey')
    with open('../current_state.json', 'r') as f:  # Adjust the path if necessary
        data = json.load(f)
    
    # Assuming the JSON structure from components.py, adjust as needed
    chargers = data["stations"]
    evs = data["cars"]
    # You might need to adjust the following logic based on your actual data structure and requirements
    for charger in chargers:
        charger["alone"] = True  # Initialize every charger as alone
        print(charger["price_per_kwh"])
        charger["x"], charger["y"] = charger["pos"]  # Assuming 'pos' holds the x, y coordinates
        del charger["pos"]  # Remove 'pos' if not needed in the Flask app

    for ev in evs:
        ev["x"], ev["y"] = ev["pos"]
        ev["battery_level_percentage"] = round(ev["battery_level_percentage"]*100,2)
        del ev["pos"]  # Adjust according to your template needs

    # Determine if a charger is alone
    for charger in chargers:
        for ev in evs:
            if (charger["x"], charger["y"]) == (ev["x"], ev["y"]):
                charger["alone"] = False
                break

    platform = {
        "chargers_occupied": len([c for c in chargers if not c["alone"]]),
        "ev_state_counts": {
            "idle": len([ev for ev in evs if ev["state"] == "idle"]),
            "charging": len([ev for ev in evs if ev["state"] == "charging"]),
            "driving": len([ev for ev in evs if ev["state"] == "driving"]),
        }
    }
    return chargers, evs, platform


@app.route('/')
def index():
    chargers, evs, platform = get_simulation_data()
    return render_template('index.html', chargers=chargers, evs=evs, platform=platform)

@app.route('/update-data')
def update_data():
    chargers, evs, platform = get_simulation_data()
    return ({'chargers': chargers, 'evs': evs, 'platform': platform})

@app.route('/compare')
def compare():
    return render_template('compare.html')


if __name__ == '__main__':
    #start_simulation()
    app.run(debug=True, host='0.0.0.0')
