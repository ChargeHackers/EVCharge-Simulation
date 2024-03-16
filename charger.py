
import mesa
import numpy as np
from numpy import random
import math
import ai

class Charger(mesa.Agent):
    def __init__(self, id, model, pos, capacity = np.inf, rate = 1,):
        super().__init__(id, model)
        model.grid.place_agent(self, pos)
        model.charging_stations[pos] = self
        self.hourly_cost = 1
        self.capacity = capacity
        self.rate = rate

        self.base_hourly_cost = 1  # Base cost without any modifications
        self.hourly_cost = self.base_hourly_cost
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
        self.hourly_cost = (self.base_hourly_cost + sine_component + noise)  + charging_increase * decay_factor


    def add_charging_car(self):
        # Call this method when a car starts charging
        self.charging_cars += 1

    def remove_charging_car(self):
        # Call this method when a car stops charging
        self.charging_cars = max(0, self.charging_cars - 1)  # Ensure it doesn't go below 0
