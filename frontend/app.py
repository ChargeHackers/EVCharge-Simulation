from flask import Flask, render_template
import random

app = Flask(__name__)

# Simulate your data generation
def simulate_ev_charging():
    chargers = [{"power_budget": 100, "price_per_kwh": random.uniform(0.1, 0.5), "charger_id": i, "x": random.randint(0, 9), "y": random.randint(0, 9), "alone": True} for i in range(5)]
    
    evs = []
    for _ in range(10):
        battery_cap = random.randint(10, 100)  # Randomize battery capacity between 20 and 100
        battery_level_percentage = random.randint(1, 100)  # Randomize battery level percentage
        evs.append({
            "battery_cap": battery_cap, 
            "miles": battery_cap,  # Assuming 1 mile per unit of battery capacity for simplicity
            "state": random.choice(["idle", "charging", "driving"]), 
            "x": random.randint(0, 9), 
            "y": random.randint(0, 9),
            "battery_level_percentage": battery_level_percentage
        })
    # Determine if a charger is alone
    for charger in chargers:
        for ev in evs:
            if charger["x"] == ev["x"] and charger["y"] == ev["y"]:
                charger["alone"] = False
                break

    platform = {
        "chargers_occupied": len([c for c in chargers if not c["alone"]]),
        "ev_state_counts": {"idle": len([ev for ev in evs if ev["state"] == "idle"]),
                            "charging": len([ev for ev in evs if ev["state"] == "charging"]),
                            "driving": len([ev for ev in evs if ev["state"] == "driving"])}
    }
    return chargers, evs, platform



@app.route('/')
def index():
    chargers, evs, platform = simulate_ev_charging()
    return render_template('index.html', chargers=chargers, evs=evs, platform=platform)

@app.route('/compare')
def compare():
    return render_template('compare.html')


if __name__ == '__main__':
    app.run(debug=True)
