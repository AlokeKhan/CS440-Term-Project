from typing import List, Dict

from environment import HouseholdEnvironment, Appliance


def default_appliances() -> List[Appliance]:
    appliances: List[Appliance] = [
        Appliance("Dishwasher", 1.2, 2, 23),
        Appliance("Washer/Dryer", 2.0, 3, 21),
        Appliance("EV Charger", 7.0, 4, 7, isFlexible=True),
    ]
    return appliances


def make_default_env(monthly_budget_kwh: float, pricingType: str = "standard") -> HouseholdEnvironment:
    env = HouseholdEnvironment(monthly_budget_kwh, pricingType)
    for appliance in default_appliances():
        env.add_appliance(appliance)
    return env


def compute_savings(baseline_metrics: Dict[str, float], greedy_metrics: Dict[str, float]) -> Dict[str, float]:
    bc = baseline_metrics.get("total_cost")
    gc = greedy_metrics.get("total_cost")

    if not isinstance(bc, (int, float)) or not isinstance(gc, (int, float)) or bc <= 0:
        return {"absolute": 0.0, "percent": 0.0}

    diff = bc - gc
    return {"absolute": diff, "percent": (diff / bc) * 100.0}
