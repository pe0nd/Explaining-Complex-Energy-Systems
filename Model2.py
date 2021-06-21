# file  -- Module.py --

def getSettings():
    """Return settingsDict with default settings for usage in an HouseModel class object"""
    settingsDict = {
                    "lifetime": 10,  # Years
                    "cost_PV": 1000,  # €/kW
                    "cost_Battery": 300,  # €/kWh
                    "cost_buy": 0.25,  # €/kWh
                    "dem_tot": 3500,  # kWh/Year
                    }
    return settingsDict


class HouseModel:
    """Create an instance of the House model, setting its basic parameters"""

    def __init__(self, *settings_dict):
        if not settings_dict:
            self.Settings = getSettings()
        else:
            self.Settings = settings_dict[0]

    def sample_model(self, input_changes=None, fixed_outputs=None):
        import pyomo.environ as pyo
        from pyomo.opt import SolverFactory

        # Step 0: Create an instance of the model
        model = pyo.ConcreteModel()

        # Step 1: Define index sets
        time = range(3)

        # Input Changes
        Names = ["CostPV", "CostBat", "CostBuy", "Demand"]
        Scaling = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        if input_changes is not None:
            for i in range(Names.__len__()):
                try:
                    Scaling[i] = input_changes[Names[i]]
                except:
                    Scaling[i] = 1

        # Output Fixes
        Names = ["PVFixed", "BatteryFixed", "SelfProdRatioFixed", "TOTEXFixed", "CAPEXFixed"]
        Fixing = [-1, -1, -1, -1, -1, -1, -1, -1]
        if fixed_outputs is not None:
            for i in range(Names.__len__()):
                try:
                    Fixing[i] = fixed_outputs[Names[i]]
                except:
                    Fixing[i] = -1

        # Step 1.5: Parameters
        lifetime = self.Settings["lifetime"]  # years
        cost_PV = Scaling[0] * self.Settings["cost_PV"] / lifetime /8760 *3  # *((time[-1]+1)/8760) # € / (lifetime * kW)
        cost_Battery = Scaling[1] * self.Settings[
            "cost_Battery"] / lifetime /8760 *3  # *((time[-1]+1)/8760)  # € / (lifetime * kWh)
        cost_buy_ele = Scaling[2] * self.Settings["cost_buy"]  # €/kWh
        dem_tot = Scaling[3] * self.Settings["dem_tot"]  # kWh
        battery_in_eff = 1  # efficiency 100%

        import csv

        availability_pv = []  # create empty arrays
        DemandVal = []

        with open('TS_PVAvail.csv', 'r') as file:
            # next(file)
            reader = csv.reader(file, delimiter='\n')
            for row in reader:
                availability_pv.append(float(row[0]))

        with open('TS_Demand.csv', 'r') as file:
            # next(file)
            reader = csv.reader(file, delimiter='\n')
            for row in reader:
                DemandVal.append(float(row[0]))

        availability_pv = dict(enumerate(availability_pv))
        DemandVal = dict(enumerate(DemandVal))
        DemandVal = [0.03359699, 0.0235179, 0.2418983]
        availability_pv = [0.804, 0.791, 0.768]


        # Step 2: Define the decision

        # Electricity Sector
        model.EnergyPV = pyo.Var(time, within=pyo.NonNegativeReals)
        model.Demand = pyo.Var(time, within=pyo.NonNegativeReals)
        model.EnergyBattery = pyo.Var(time, within=pyo.NonNegativeReals)
        model.EnergyBattery_IN = pyo.Var(time, within=pyo.NonNegativeReals)
        model.EnergyBattery_OUT = pyo.Var(time, within=pyo.NonNegativeReals)
        model.EnergyBuy = pyo.Var(time, within=pyo.NonNegativeReals)
        model.CapacityPV = pyo.Var(within=pyo.NonNegativeReals)
        model.CapacityBattery = pyo.Var(within=pyo.NonNegativeReals)
        model.CostBuy = pyo.Var(within=pyo.Reals)
        model.CostPV = pyo.Var(within=pyo.Reals)
        model.CostBat = pyo.Var(within=pyo.Reals)

        # Step 3: Define Objective
        model.cost = pyo.Objective(expr=cost_PV * model.CapacityPV + cost_buy_ele * sum(
            model.EnergyBuy[i] for i in time) + cost_Battery * model.CapacityBattery, sense=pyo.minimize)

        # Step 4: Constraints
        model.limEQ = pyo.ConstraintList()

        for i in time:
            model.limEQ.add(model.EnergyPV[i] <= model.CapacityPV * availability_pv[i]) # PV Upper Limit

        for i in time:
            model.limEQ.add(model.EnergyBattery[i] <= model.CapacityBattery)  # Battery Upper Limit

        model.InitialBattery = pyo.Constraint(
            expr=model.EnergyBattery[0] == model.EnergyBattery[time[-1]] - model.EnergyBattery_OUT[0] +
                 model.EnergyBattery_IN[0])  # Battery level t=0 == t=T

        model.DemandEQ = pyo.ConstraintList()

        for i in time:
            model.DemandEQ.add(expr=model.Demand[i] == dem_tot * DemandVal[i])  # Electricity Demand

        model.batteryEQ = pyo.ConstraintList()

        for i in time[1:]:
            model.batteryEQ.add(
                expr=model.EnergyBattery[i] == model.EnergyBattery[i - 1] - model.EnergyBattery_OUT[i] +
                     model.EnergyBattery_IN[i])  # Battery Equation

        model.EnergyEQ = pyo.ConstraintList()
        for i in time:
            model.EnergyEQ.add(
                expr=model.Demand[i] == model.EnergyBuy[i] + model.EnergyBattery_OUT[i] - model.EnergyBattery_IN[
                    i] + model.EnergyPV[i])  # Energy Equation

        # Some equations that store input settings in a Variable
        model.ValueCostBuy = pyo.Constraint(expr=model.CostBuy == cost_buy_ele)
        model.ValueCostPV = pyo.Constraint(expr=model.CostPV == cost_PV)
        model.ValueCostBat = pyo.Constraint(expr=model.CostBat == cost_Battery)

        # Equations to fix outputs
        if Fixing[0] != -1:  # fixed PV Cap
            model.fixedPV = pyo.Constraint(expr=model.CapacityPV == Fixing[0])

        if Fixing[1] != -1:  # fixed Battery cap
            model.fixedBattery = pyo.Constraint(expr=model.CapacityBattery == Fixing[1])

        if Fixing[2] != -1:  # fixed Self Generation
            model.SelfProduction = pyo.Constraint(expr=sum(model.EnergyPV[i] for i in time) / dem_tot == Fixing[2])

        if Fixing[3] != -1:  # fixed TOTEX
            model.TOTEX = pyo.Constraint(expr=cost_PV * model.CapacityPV + cost_buy_ele * sum(
                model.EnergyBuy[i] for i in time) + cost_Battery * model.CapacityBattery == Fixing[3])

        if Fixing[4] != -1:  # fixed CAPEX
            model.CAPEX = pyo.Constraint(
                expr=cost_PV * model.CapacityPV + cost_Battery * model.CapacityBattery == Fixing[4])

        # Change lines below to use other solver
        solver_options = open("solverSettings.txt", "r").read().split("\n")
        for i in solver_options:
            if i.find('#') == 0 or i.__len__() == 0:
                val = 0  # comment or empty line: do nothing
            elif i.find('solver') == 0:
                val = i.split('=')
                val = val[1].strip()
                # set solver
                solver = SolverFactory(val)
            else:
                val = i.split('=')
                opt = val[0].strip()
                val = val[1].strip()
                try:
                    val2 = float(val)
                except ValueError:
                    val2 = val

                solver.options[opt] = val2

        results = solver.solve(model, tee=True, keepfiles=True)
        results.write()
        # Print full model to console. Only enable for debugging purpose
        # model.pprint()
        return model, results.solver.termination_condition


def getKPI(model, *base_model):
    from pyomo.opt import TerminationCondition as TC
    if model[1] == TC.infeasible:
        KPIdict = {"Cap_PV": -2, "Cap_Bat": -2, "Own_Gen": -2, "TOTEX": -2, "CAPEX": -2}
    else:
        # read the values from a solved model
        model = model[0]
        import pyomo.environ as pyo

        # get some key information from the model
        time_steps = range(model.Demand.__len__())
        demand_tot = sum(pyo.value(model.Demand[i]) for i in time_steps)
        cost_buy_ele = pyo.value(model.CostBuy)
        cost_PV = pyo.value(model.CostPV)
        cost_Battery = pyo.value(model.CostBat)

        Value_PV = pyo.value(model.CapacityPV)
        Value_Bat = pyo.value(model.CapacityBattery)
        Value_OwnGen = sum(pyo.value(model.EnergyPV[i]) for i in time_steps) / demand_tot
        Value_TOTEX = cost_buy_ele * sum(pyo.value(model.EnergyBuy[i]) for i in time_steps) + cost_PV * pyo.value(
            model.CapacityPV) + cost_Battery * pyo.value(model.CapacityBattery)
        Value_CAPEX = cost_PV * pyo.value(model.CapacityPV) + cost_Battery * pyo.value(model.CapacityBattery)

        if not base_model:
            KPIdict = {
                "Cap_PV": Value_PV,
                "Cap_Bat": Value_Bat,
                "Own_Gen": Value_OwnGen,
                "TOTEX": Value_TOTEX,
                "CAPEX": Value_CAPEX
            }
        else:
            base_model = base_model[0]
            KPIdict = {  # % difference to base model
                "Cap_PV": (Value_PV - base_model["Cap_PV"]) / (base_model["Cap_PV"] + 1e-8),
                "Cap_Bat": (Value_Bat - base_model["Cap_Bat"]) / (base_model["Cap_Bat"] + 1e-8),
                "Own_Gen": (Value_OwnGen - base_model["Own_Gen"]) / (base_model["Own_Gen"] + 1e-8),
                "TOTEX": (Value_TOTEX - base_model["TOTEX"]) / (base_model["TOTEX"] + 1e-8),
                "CAPEX": (Value_CAPEX - base_model["CAPEX"]) / (base_model["CAPEX"] + 1e-8)
            }
    return KPIdict