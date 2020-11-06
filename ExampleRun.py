def run():
    import Model
    # get settings for HouseModel
    settings = Model.getSettings()

    # Create an instance of the HouseModel with given (or modified) settings
    HousePVModel = Model.HouseModel(settings)

    # The function sample_model() solves an instance of the HouseModel class returning the solved model and the
    # solvers termination status
    # Note, that the solver in Model.py line 156 needs to be changed to run with other solvers
    [Result, Status] = HousePVModel.sample_model()

    # The results can be read manually using the pyomo.environ class
    import pyomo.environ as pyo
    print("Demand at hour 123 of simulation: " + str(pyo.value(Result.Demand[123])) + " kWh")

    # read results via getKPI
    kpi_base = Model.getKPI([Result, Status])
    print("Capacity for the PV module: " + str(kpi_base["Cap_PV"]) + " kWh")

    # The sample_model function can use a dictionary to sample around the base settings by scaling inputs
    # The example below has 90% of the price originally set in the settings
    [cheaper_PV_cost_res, Status2] = HousePVModel.sample_model({"CostPV": 0.9, "CostBat": 1, "CostBuy": 1, "Demand": 1})

    # Given a dictionary containing KPI's the function getKPI() will give relative changes instead of absolute values
    relative_changes = Model.getKPI([cheaper_PV_cost_res, Status2], kpi_base)
    print("Reducing the price for PV has increased its installed capacity by " + str(
        round(relative_changes["Cap_PV"] * 100, 2)) + "%.")
    print("Reducing the price for PV has also increased the size of the installed battery by" + str(
        round(relative_changes["Cap_Bat"] * 100, 2)) + "%.")

    # Additional constraints can be activated when giving sample_model() a second argument
    # The example below again has 90% of the original PV cost but is forced to keep the PV capacity of the original
    [cheap_PV_same_size, Status3] = HousePVModel.sample_model({"CostPV": 0.9, "CostBat": 1, "CostBuy": 1, "Demand": 1},
                                                               {"PVFixed": kpi_base["Cap_PV"]})
    new_relative_changes = Model.getKPI([cheap_PV_same_size, Status3], kpi_base)
    print("The PV capacity changes by " + str(round(new_relative_changes["Cap_PV"]*100, 2)) + "% if the price is lowered" +
          " by 10% but the capacity of PV is kept fixed by a restriction.")
    print("The battery capacity changes by " + str(round(new_relative_changes["Cap_Bat"]*100, 2)) + "% if the price is lowered" +
          " by 10% but the capacity of PV is kept fixed by a restriction.")
    print("Under the same changes to the price of PV and the restriction of keeping the capacity fixed" +
          " the following changes happened.")
    print("The share of self produced energy changes by " + str(round(new_relative_changes["Own_Gen"]*100, 2)) + "%.")
    print("The total expenditures change by " + str(round(new_relative_changes["TOTEX"]*100, 2)) + "%.")
    print("The capital expenditures change by " + str(round(new_relative_changes["CAPEX"]*100, 2)) + "%.")

    if __name__ == '__main__':
        run()
