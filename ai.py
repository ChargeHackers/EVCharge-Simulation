def should_charge(car, city):
    """
    Determines whether the car should go to charge or idle based on its battery level,
    the cost of the nearest charger, and the estimated cost of charging in the evening.
    """
    # Constants (these could be dynamic or based on real data)
    evening_charge_discount = 0.8  # Assume 20% cheaper to charge in the evening
    normal_charge_cost = 1  # Cost per kWh for charging now


    nearest_charger = city.find_closest_station()
 
    nearest_charger_cost =nearest_charger.hourly_cost
    # Calculate the cost of charging now vs. in the evening
    battery_needed = car.capacity - (car.battery * car.capacity)
    cost_now = battery_needed * nearest_charger_cost
    cost_evening = battery_needed * normal_charge_cost * evening_charge_discount

    # Decide based on battery level and cost comparison
    if  nearest_charger.hourly_cost < ( nearest_charger.base_hourly_cost * 1.2 )  :
        return 'going to recharge'
    else:
        return 'idle'