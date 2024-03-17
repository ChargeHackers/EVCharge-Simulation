import mesa
import numpy as np
from numpy import random
random.seed(189)
import threading
import time
import json
from threading import Event
import math
import csv

# At the start of your code, create an event object
stop_event = Event()


TIMESTEP = 15 # minutes = 1 tick
STATES = ['idle', 'charging', 'pickup', 'dropoff', 'going to recharge'] # car states
SPEED = 1 # miles per tick
CHARGING = 80 # kW outputted per hour by charging station
FUEL = 1 / 5 # kWh used to drive 1 mile

def manhattan_distance(pos1, pos2):
    # MANHATTAN DISTANCE from POS1 to POS2
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def random_pos(x, y):
    # RANDOM POSITION on the X by Y board
    return (random.randint(x - 1), random.randint(y - 1))

x, y = 25, 25
generate_pos = lambda : random_pos(x, y)

class Car(mesa.Agent):
    def __init__(self, id, model, pos, capacity = 80, battery = 1):
        # INITIALIZE CAR agent at position POS in MODEL, with battery capacity CAPACITY in kWh,
        # and battery level BATTERY
        super().__init__(id, model)
        model.place(self, pos)
        self.battery = battery
        self.capacity = capacity
        self.state = 'idle'
        self.dest = None
        self.pickup = None
        self.charging_time = 0 # minutes to finish charging to 100
        self.profit = 0

    def go_charge(self):
        self.state = 'going to recharge'
        self.dest = self.find_closest_station()

    def start_new_itinerary(self, pickup, dropoff):
        dist_to_pickup = manhattan_distance(self.pos, pickup)
        dist_to_dest = manhattan_distance(pickup, dropoff)
        closest_station = self.find_closest_station(dropoff)
        dist_to_charging = manhattan_distance(dropoff, closest_station)
        total_dist = dist_to_pickup + dist_to_dest + dist_to_charging
        battery_needed = total_dist * FUEL

        if self.battery * self.capacity >= battery_needed:
            self.state = 'pickup'
            self.pickup = pickup
            self.dest = dropoff
            self.profit += total_dist
        else:
            # print('RECHARGING!')
            self.go_charge()

    def step(self):
        if self.state == 'charging':
            self.battery += (80 * TIMESTEP / 60) / self.capacity
            self.battery = min(self.battery, 1)
            if self.battery == 1:
                self.state = 'idle'
        elif self.state == 'idle':
            self.start_new_itinerary(generate_pos(), generate_pos())
        else:
            dest = self.pickup if self.pickup else self.dest
            dx = abs(self.pos[0] - dest[0])
            dy = abs(self.pos[1] - dest[1])
            if SPEED >= dx + dy:
                self.move(dx, dy)
                self.update_state()
            elif SPEED <= dx:
                self.move(SPEED, 0)
            elif SPEED <= dy:
                self.move(0, SPEED)
            else:
                remainder = SPEED - dx
                assert remainder > 0, "remainder not greater than 0?!"
                self.move(dx, remainder)
                
    def update_state(self):
        # Updates the state once car is done with current state
        state = self.state
        match state:
            case 'pickup':
                self.state = 'dropoff'
                self.pickup = None
            case 'going to recharge':
                self.state = 'charging'
            case 'dropoff':
                self.state = 'idle'
            case 'charging':
                self.state = 'idle'

    def move(self, dx, dy):
        # MOVE DX units in the x axis towards destination, DY units in y axis towards destination
        # updates battery accordingly. DY, DX positive for simplicity.
        assert dx >= 0 and dy >= 0, "DX, DY not >= 0!"
        self.battery -= (dy + dx) * FUEL / self.capacity
        self.profit += dy + dx
        dest = self.pickup if self.pickup else self.dest
        dx *= -1 if self.pos[0] > dest[0] else 1
        dy *= -1 if self.pos[1] > dest[1] else 1
        new_pos = (self.pos[0] + dx, self.pos[1] + dy)
        self.model.grid.move_agent(self, new_pos)

    def find_closest_station(self, start = None):
        stations = list(self.model.charging_stations)
        pos = start if start else self.pos
        distances = [(manhattan_distance(pos, s), s) for s in stations]
        distances.sort(key = lambda x: x[0])
        return distances[0][1]

class Charger(mesa.Agent):
    def __init__(self, id, model, pos, capacity = 10000, rate = 1,):
        super().__init__(id, model)
        model.grid.place_agent(self, pos)
        model.charging_stations[pos] = self
        self.capacity = capacity
        self.rate = rate
        self.id = id
        self.charging_cars = 0
    
    def step( self ):
        self.hourly_cost = self.update_hourly_cost()

    def update_hourly_cost(self):
        # Constants for the sine wave and noise
        period = 24 * 4  # 24 hours, with each hour represented by 4 timesteps (15 min each)
        noise_mean = 0
        noise_variance = 0.05  # Adjust for more or less noise

        # Calculate the sine wave component based on the simulation time
        sine_component = math.sin(2 * math.pi * (self.model.schedule.time / period))

        # Add random noise
        noise = np.random.normal(noise_mean, noise_variance)

        # Increase cost if cars are charging, with a decay factor to return to base cost
        charging_increase = self.charging_cars * 0.1  # Increase cost by 0.1 per charging car
        decay_factor = 0.95  # Decay back to base cost

        # Update the hourly cost
        self.rate = (1 + sine_component + noise)  + charging_increase * decay_factor

        self.rate = round(self.rate,2)

    def add_charging_car(self):
        # Call this method when a car starts charging
        self.charging_cars += 1

    def remove_charging_car(self):
        # Call this method when a car stops charging
        self.charging_cars = max(0, self.charging_cars - 1)  # Ensure it doesn't go below 0


class City(mesa.Model):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = mesa.space.MultiGrid(rows, cols, False)
        self.schedule = mesa.time.BaseScheduler(self)
        self.charging_stations = {}
        self.simulation_time = 0
    
    def place(self, car, pos):
        # Places a car on the grid
        self.grid.place_agent(car, pos)
        self.schedule.add(car)
    
    def step(self):
        self.schedule.step()
        for pos in self.charging_stations:
            self.charging_stations[pos].step()
        self.simulation_time += 1  # Increment simulation time
        # Update rates and export state if needed
        if self.simulation_time % (24*4) == 0:  # Reset every 24 hours
            self.simulation_time = 0

    def run_simulation(self, steps):
        while not stop_event.is_set():  # Check if the event is set
            self.step()
            self.print()
            self.export_state()
            self.export_charging_rates()
            time.sleep(0.4)

    def export_state(self):
        # Example structure, adapt as needed
        #print(self.charging_stations)
        data = {
            "cars": [{ "id": car.unique_id, "state": car.state, "pos": car.pos, "battery_cap": car.capacity, "battery_level_percentage": car.battery } for car in self.schedule.agents if isinstance(car, Car)],
            "stations": [{ "pos": pos, "price_per_kwh": self.charging_stations[pos].rate, "charger_id": self.charging_stations[pos].id, "power_budget": self.charging_stations[pos].capacity } for pos in self.charging_stations]
        }
        with open('current_state.json', 'w') as f:
            json.dump(data, f, indent=4)

        # Export cars to CSV
        with open('current_state_cars.csv', 'w', newline='') as csvfile:
            fieldnames = ['id', 'state', 'pos_x', 'pos_y', 'battery_cap', 'battery_level_percentage']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if csvfile.tell() == 0:
                writer.writeheader()

            for car in self.schedule.agents:
                if isinstance(car, Car):
                    writer.writerow({
                        'id': car.unique_id,
                        'state': car.state,
                        'pos_x': car.pos[0],
                        'pos_y': car.pos[1],
                        'battery_cap': car.capacity,
                        'battery_level_percentage': round(car.battery,2)
                    })
                
        # Export stations to CSV
        with open('current_state_stations.csv', 'w', newline='') as csvfile:
            fieldnames = ['pos_x', 'pos_y', 'price_per_kwh', 'charger_id', 'power_budget']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if csvfile.tell() == 0:
                writer.writeheader()

            for pos, charger in self.charging_stations.items():
                writer.writerow({
                    'pos_x': pos[0],
                    'pos_y': pos[1],
                    'price_per_kwh': charger.rate,
                    'charger_id': charger.id,
                    'power_budget': charger.capacity
                })

    def export_charging_rates(self):
        with open('charging_rates.csv', 'a', newline='') as csvfile:
            fieldnames = ['simulation_time', 'pos_x', 'pos_y', 'rate', 'charger_id', 'simulation_hour']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # If the file is new, write the header
            if csvfile.tell() == 0:
                writer.writeheader()

            for pos, charger in self.charging_stations.items():
                writer.writerow({
                    'simulation_time': self.simulation_time,
                    'pos_x': pos[0],
                    'pos_y': pos[1],
                    'rate': charger.rate,
                    'charger_id': charger.id,
                    'simulation_hour': (self.simulation_time * TIMESTEP) // 60
                })


    
    def print(self):
        header = list(range(self.cols))
        print('   ' + str(header.pop(0)) + ' ', end = '')
        [print(f' {x} ' if x < 10 else f'{x} ', end='') for x in header]
        print()
        for c in range(self.cols):
            s = str(c) + (' ' if c < 10 else '')
            for r in range(self.rows):
                agent = self.grid[r][c]
                if agent:
                    s += ' C ' if type(agent[0]) is Car else ' Ch'
                else:
                    s += ' . '
            print(s)

def start_simulation():
    num_cars = 10
    sf = City(x, y)
    charging_stations = [(18, 15), (15, 8), (21, 8), (9, 17), (17, 10)]
    cars = []
    for i in range(num_cars):
        pos = (0, 0) # generate_pos()
        cars.append(Car(i, sf, pos))
    for pos in charging_stations:
        charger_temp = Charger(num_cars + i, sf, pos)
        sf.charging_stations[pos] = charger_temp
    # Start the simulation in a separate thread
    simulation_thread = threading.Thread(target=sf.run_simulation)  # Run for 10 steps as an example
    simulation_thread.start()
    simulation_thread.join()

if __name__ == "__main__":
    # Set up the simulation environment
    # Your existing setup code...
    num_cars = 10
    sf = City(x, y)
    charging_stations = [(18, 15), (15, 8), (21, 8), (9, 17), (17, 10)]
    cars = []
    for i in range(num_cars):
        pos = (0, 0) # generate_pos()
        cars.append(Car(i, sf, pos))
    for pos in charging_stations:
        charger_temp = Charger(num_cars + i, sf, pos)
        sf.charging_stations[pos] = charger_temp
    # Start the simulation in a separate thread
    simulation_thread = threading.Thread(target=sf.run_simulation, args=(10,))  # Run for 10 steps as an example
    simulation_thread.start()

    # Assuming you want to stop the simulation at some condition or input
    input("Press Enter to stop the simulation...")  # Example stopping condition
    stop_event.set()  # Signal the thread to stop

    simulation_thread.join()  # Wait for the thread to finish
    print("Simulation ended.")