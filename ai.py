def should_charge(car, nearest_charger):
    """
    Determines whether the car should go to charge or idle based on its battery level,
    the cost of the nearest charger, and the estimated cost of charging in the evening.
    """
    print(nearest_charger.rate, car.battery)
    #nearest_charger = car.find_closest_station()
 
    # Decide based on battery level and cost comparison
    if  nearest_charger.rate < 0.8 and car.battery < 0.6 :
        return True
    else:
        return False