import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta


# Has household class that holds states of houses, and appliance that can be added to house

class Appliance:
    name: str
    powerkW: float
    durationHours: float
    deadlineHour: int
    isFlexible: bool = True
    isScheduled: bool = False
    scheduledStart: Optional[int] = None  

    def energy_required(self) -> float:
        """Total energy required in kWh"""
        return self.powerkW * self.durationHours

    
class HVACSystem:
    """HVAC system with comfort constraints"""
    currentTemp: float = 72.0  # Fahrenheit
    setpoint: float = 72.0
    minTemp: float = 68.0  # Comfort lower bound
    maxTemp: float = 76.0  # Comfort upper bound
    powerkW: float = 3.5  # Average HVAC power
    
    def is_comfortable(self) -> bool:
        """Check if current temperature is within comfort bounds"""
        return self.minTemp <= self.currentTemp <= self.maxTemp


class TOUPricing:
    """Time-of-Use pricing structure"""
    
    def __init__(self, pricingType: str = "standard"):
        """
        Initialize TOU pricing
        
        Args:
            pricing_type: "standard", "summer", or "winter"
        """
        self.pricingType = pricingType
        self.prices = self._create_pricing_schedule()
    
    def _create_pricing_schedule(self) -> Dict[int, float]:
        """Create 24-hour pricing schedule"""
        if self.pricing_type == "standard":
            # Standard TOU: Peak 4pm-9pm, Off-peak midnight-6am
            prices = {}
            for hour in range(24):
                if 0 <= hour < 6:  # Off-peak 
                    prices[hour] = 0.08
                elif 16 <= hour < 21:  # Peak (4pm-9pm)
                    prices[hour] = 0.32
                else:  # Mid-peak
                    prices[hour] = 0.15
            return prices
        
        elif self.pricing_type == "summer":
            # Summer: Higher peak prices, longer peak hours
            prices = {}
            for hour in range(24):
                if 0 <= hour < 6:
                    prices[hour] = 0.09
                elif 14 <= hour < 22:  # Peak 2pm-10pm
                    prices[hour] = 0.38
                else:
                    prices[hour] = 0.17
            return prices
        
        else:  # winter
            prices = {}
            for hour in range(24):
                if 0 <= hour < 6:
                    prices[hour] = 0.07
                elif 17 <= hour < 20:  # Peak 5pm-8pm
                    prices[hour] = 0.28
                else:
                    prices[hour] = 0.14
            return prices
    
    def get_price(self, hour: int) -> float:
        """Get price for a specific hour"""
        return self.prices[hour % 24]
    
    def get_daily_schedule(self) -> pd.DataFrame:
        """Get full day pricing as DataFrame"""
        return pd.DataFrame({
            'hour': list(range(24)),
            'price': [self.prices[h] for h in range(24)]
        })


class Household:
    def __init__(self, monthlyBudget, pricingType: str = "standard", currentDay: int = 1, monthDays = 30):
        
        self.monthlyBudget = monthlyBudget
        self.currentDay = currentDay
        self.monthDays = monthDays
        self.currentHour = 0
        """Initialize Household environment"""

        self.energyUsedToday = 0.0
        self.energyUsedMonth = 0.0
        self.todayCost = 0.0
        self.monthCost = 0.0
        
        # TOU pricing
        self.tou_pricing = TOUPricing(pricingType)
        
        # HVAC system
        self.hvac = HVACSystem()
        
        # Appliances queue
        self.appliances: List[Appliance] = []
        
        # History for tracking
        self.hourly_usage = []
        self.hourly_costs = []


    def add_appliance(self, appliance: Appliance):
        """Add an appliance to the household queue"""
        self.appliances.append(appliance)
    
    def get_daily_budget(self) -> float:
        """Calculate remaining daily budget based on month progress"""
        days_remaining = self.monthDays - self.currentDay + 1
        budget_remaining = self.monthlyBudget - self.energyUsedMonth
        
        if days_remaining <= 0:
            return 0.0
        
        return budget_remaining / days_remaining
    
    def get_unscheduled_appliances(self) -> List[Appliance]:
        """Get list of appliances that haven't been scheduled yet"""
        return [a for a in self.appliances if not a.isScheduled]
    
    def schedule_appliance(self, appliance: Appliance, start_hour: int):
        """Schedule an appliance to start at a specific hour"""
        appliance.isScheduled = True
        appliance.scheduled_start = start_hour
    
# Make Appliance easier to construct.
def _appliance_init(self, name, powerkW, durationHours, deadlineHour, isFlexible=True):
    self.name = name
    self.powerkW = float(powerkW)
    self.durationHours = float(durationHours)
    self.deadlineHour = int(deadlineHour)
    self.isFlexible = bool(isFlexible)
    self.isScheduled = False
    self.scheduledStart = None
    self.scheduled_start = None


Appliance.__init__ = _appliance_init


def _get_duration_hours(self):
    return self.durationHours


def _set_duration_hours(self, value):
    self.durationHours = float(value)


Appliance.duration_hours = property(_get_duration_hours, _set_duration_hours)


def _get_deadline_hour(self):
    return self.deadlineHour


def _set_deadline_hour(self, value):
    self.deadlineHour = int(value)


Appliance.deadline_hour = property(_get_deadline_hour, _set_deadline_hour)


def _get_power_kw(self):
    return self.powerkW


def _set_power_kw(self, value):
    self.powerkW = float(value)


Appliance.power_kw = property(_get_power_kw, _set_power_kw)


# HVAC compatibility aliases used by the agent.
def _get_base_setpoint(self):
    return self.setpoint


def _set_base_setpoint(self, value):
    self.setpoint = float(value)


HVACSystem.base_setpoint = property(_get_base_setpoint, _set_base_setpoint)


def _get_min_temp(self):
    return self.minTemp


def _set_min_temp(self, value):
    self.minTemp = float(value)


HVACSystem.min_temp = property(_get_min_temp, _set_min_temp)


def _get_max_temp(self):
    return self.maxTemp


def _set_max_temp(self, value):
    self.maxTemp = float(value)


HVACSystem.max_temp = property(_get_max_temp, _set_max_temp)


# TOUPricing alias for pricing_type used inside _create_pricing_schedule.
def _get_pricing_type(self):
    return getattr(self, "pricingType", "standard")


def _set_pricing_type(self, value):
    self.pricingType = value


TOUPricing.pricing_type = property(_get_pricing_type, _set_pricing_type)


class HouseholdEnvironment(Household):
    def __init__(self, monthlyBudget, pricingType: str = "standard", currentDay: int = 1, monthDays=30):
        super().__init__(monthlyBudget, pricingType, currentDay, monthDays)

    @property
    def tou_prices(self):
        return [self.tou_pricing.get_price(h) for h in range(24)]

    def simulate_day(self, schedule, hvac_setpoints):
        self.energyUsedToday = 0.0
        self.todayCost = 0.0
        self.hourly_usage = [0.0] * 24
        self.hourly_costs = [0.0] * 24

        for a in self.appliances:
            a.isScheduled = False
            if hasattr(a, "scheduled_start"):
                a.scheduled_start = None
            if hasattr(a, "scheduledStart"):
                a.scheduledStart = None

        for hour, names in schedule.items():
            for name in names:
                for a in self.appliances:
                    if a.name == name:
                        a.isScheduled = True
                        a.scheduled_start = hour
                        a.scheduledStart = hour
                        break

        comfort_violations = 0

        for h in range(24):
            if hvac_setpoints and h < len(hvac_setpoints):
                self.hvac.setpoint = float(hvac_setpoints[h])
                self.hvac.currentTemp = float(hvac_setpoints[h])

            if not self.hvac.is_comfortable():
                comfort_violations += 1

            usage = 0.0
            for a in self.appliances:
                start = getattr(a, "scheduled_start", getattr(a, "scheduledStart", None))
                duration = getattr(a, "durationHours", 0)
                if start is None or not duration:
                    continue
                if start <= h < start + duration:
                    usage += float(getattr(a, "powerkW", 0.0))

            usage += float(getattr(self.hvac, "powerkW", 0.0))

            price = self.tou_pricing.get_price(h)
            cost = usage * price

            self.hourly_usage[h] = usage
            self.hourly_costs[h] = cost

            self.energyUsedToday += usage
            self.todayCost += cost

        self.energyUsedMonth += self.energyUsedToday
        self.monthCost += self.todayCost

        missed_deadlines = 0
        for a in self.appliances:
            start = getattr(a, "scheduled_start", getattr(a, "scheduledStart", None))
            duration = getattr(a, "durationHours", 0)
            deadline = getattr(a, "deadlineHour", 23)
            if start is None or not duration:
                continue
            finish = start + duration
            if finish > deadline:
                missed_deadlines += 1

        daily_budget = self.get_daily_budget()

        return {
            "total_kwh": self.energyUsedToday,
            "total_cost": self.todayCost,
            "hourly_usage": self.hourly_usage,
            "hourly_costs": self.hourly_costs,
            "comfort_violations": comfort_violations,
            "missed_deadlines": missed_deadlines,
            "daily_budget_kwh": daily_budget,
        }   