def should_charge(car, city):
    """
    Determines whether the car should go to charge or idle based on its battery level,
    the cost of the nearest charger, and the estimated cost of charging in the evening.
    """

    nearest_charger = car.find_closest_station()
 
    # Decide based on battery level and cost comparison
    if  nearest_charger.hourly_cost < ( nearest_charger.base_hourly_cost * 1.2 )  :
        return 'going to recharge'
    else:
        return 'idle'