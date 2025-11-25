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
    