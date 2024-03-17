import fire

from metagpt.roles.di.data_interpreter import DataInterpreter

WINE_REQ = "Run data analysis on data stored in data/charging_rates.csv. The data shows historical data of charging rates throughout the region and location of the charger. Do data analys and train some models to predict the cheapest rates patterns"

DATA_DIR = "data/"
# sales_forecast data from https://www.kaggle.com/datasets/aslanahmedov/walmart-sales-forecast/data
SALES_FORECAST_REQ = f"""The live data is displayed on current_state_cars.csv and current_state_stations.csv. Historical charging rates are stored in data/charging_rates.csv. These files hold the live information about position of the EV car, the charging station location, price per kwh, battery level, etc. while historical data holds the variation of charging price information. Your target is to come up with a live routine which fetches all this data and then use that to determine for any individual EV that it is optimum time to charge the car or not. Your aim is to find the cheapest rate to charge car at. Explore the files in the directory and see how you can use the trained model with the data being generated live and write a python utility which will run along the simulator to optimize ev charging to reduce the cost. Run the code to see if it works as expected or not.
"""

REQUIREMENTS = {"wine": SALES_FORECAST_REQ, "sales_forecast": SALES_FORECAST_REQ}


async def main(use_case: str = "wine"):
    mi = DataInterpreter()
    requirement = REQUIREMENTS[use_case]
    await mi.run(requirement)


if __name__ == "__main__":
    fire.Fire(main)
