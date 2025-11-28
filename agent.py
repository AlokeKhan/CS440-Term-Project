# agent.py
from typing import Dict, List, Any
from environment import HouseholdEnvironment, Appliance, HVACSystem


class EnergyAdvisorAgent:
    """
    Very first version of the energy advisor.
    Right now: just does a simple greedy assignment to cheap hours.
    """

    def __init__(self, env: HouseholdEnvironment):
        self.env = env

    def plan_day(self) -> Dict[str, Any]:
        """
        Produce:
          - a baseline schedule: run everything as soon as possible
          - a greedy schedule: run each appliance in cheapest available hours
        """
        baseline_schedule, baseline_hvac = self._baseline_policy()
        baseline_metrics = self.env.simulate_day(baseline_schedule, baseline_hvac)

        greedy_schedule, greedy_hvac = self._greedy_policy()
        greedy_metrics = self.env.simulate_day(greedy_schedule, greedy_hvac)

        return {
            "baseline_schedule": baseline_schedule,
            "baseline_hvac": baseline_hvac,
            "baseline_metrics": baseline_metrics,
            "greedy_schedule": greedy_schedule,
            "greedy_hvac": greedy_hvac,
            "greedy_metrics": greedy_metrics,
        }

    # ---------- Policies ----------

    def _baseline_policy(self) -> (Dict[int, List[str]], List[float]):
        """
        Baseline:
          - Run each appliance as soon as possible (starting at hour 0).
          - Keep HVAC setpoint constant all day.
        """
        schedule: Dict[int, List[str]] = {h: [] for h in range(24)}
        current_hour = 0

        for a in self.env.appliances:
            # schedule back-to-back from current_hour
            start_hour = current_hour
            end_hour = min(24, current_hour + a.duration_hours)
            if end_hour - start_hour < a.duration_hours:
                # Not enough time, but we still put what we can
                pass
            schedule[start_hour].append(a.name)
            current_hour = end_hour

        hvac_setpoints = [self.env.hvac.base_setpoint] * 24
        return schedule, hvac_setpoints

    def _greedy_policy(self) -> (Dict[int, List[str]], List[float]):
        """
        Simple greedy scheduler:
          - For each appliance, pick the cheapest available hours before its deadline.
          - HVAC: slightly relax during peak price hours.
        """
        prices = self.env.tou_prices
        schedule: Dict[int, List[str]] = {h: [] for h in range(24)}

        # For simplicity we assume no limit on how many appliances can run at once.
        # Later, you can add constraints if you want.

        # Sort appliances by deadline (earliest first)
        appliances_sorted = sorted(self.env.appliances, key=lambda a: a.deadline_hour)

        for a in appliances_sorted:
            # Candidate hours: from 0 up to and including deadline_hour
            latest_start = max(0, a.deadline_hour - a.duration_hours + 1)
            best_start = 0
            best_cost = float("inf")

            for start in range(0, latest_start + 1):
                end = start + a.duration_hours
                if end > 24:
                    continue
                # Cost of running this appliance from start to end-1
                cost = 0.0
                for h in range(start, end):
                    cost += a.power_kw * prices[h]
                if cost < best_cost:
                    best_cost = cost
                    best_start = start

            # Assign appliance at best_start
            schedule[best_start].append(a.name)

        # HVAC policy: relax comfort slightly during expensive hours
        hvac_setpoints: List[float] = []
        base = self.env.hvac.base_setpoint
        min_t = self.env.hvac.min_temp
        max_t = self.env.hvac.max_temp

        # Define "peak" as top 25% of prices
        sorted_prices = sorted(prices)
        peak_threshold = sorted_prices[int(0.75 * len(sorted_prices))]

        for h in range(24):
            p = prices[h]
            if p >= peak_threshold:
                # During peak, try to save a bit: slightly warmer if cooling
                setpoint = min(max_t, base + 2.0)
            else:
                setpoint = base
            hvac_setpoints.append(setpoint)

        return schedule, hvac_setpoints
    
# ---------- Policies ----------

    def _baseline_policy(self) -> (Dict[int, List[str]], List[float]):
        """
        Baseline:
          - Run each appliance as soon as possible (starting at hour 0).
          - Keep HVAC setpoint constant all day.
        """
        schedule: Dict[int, List[str]] = {h: [] for h in range(24)}
        current_hour = 0

        for a in self.env.appliances:
            duration = max(1, int(a.duration_hours))
            start_hour = current_hour
            end_hour = min(24, current_hour + duration)
            schedule[start_hour].append(a.name)
            current_hour = end_hour

        hvac_setpoints = [self.env.hvac.base_setpoint] * 24
        return schedule, hvac_setpoints

    def _greedy_policy(self) -> (Dict[int, List[str]], List[float]):
        """
        Greedy scheduler:
          - For each appliance, pick the cheapest available hours before its deadline.
          - HVAC: slightly relax during expensive hours.
        """
        prices = self.env.tou_prices
        schedule: Dict[int, List[str]] = {h: [] for h in range(24)}

        # Sort appliances by deadline (earliest first)
        appliances_sorted = sorted(self.env.appliances, key=lambda a: int(a.deadline_hour))

        for a in appliances_sorted:
            duration = max(1, int(a.duration_hours))
            deadline = int(a.deadline_hour)

            latest_start = max(0, deadline - duration + 1)
            best_start = 0
            best_cost = float("inf")

            for start in range(0, latest_start + 1):
                end = start + duration
                if end > 24:
                    continue

                power = float(a.power_kw)
                cost = 0.0
                for h in range(start, end):
                    cost += power * prices[h]

                if cost < best_cost:
                    best_cost = cost
                    best_start = start

            schedule[best_start].append(a.name)

        # HVAC policy
        hvac_setpoints: List[float] = []
        base = self.env.hvac.base_setpoint
        min_t = self.env.hvac.min_temp
        max_t = self.env.hvac.max_temp

        sorted_prices = sorted(prices)
        peak_threshold = sorted_prices[int(0.75 * len(sorted_prices))]

        for h in range(24):
            p = prices[h]
            if p >= peak_threshold:
                setpoint = min(max_t, base + 2.0)
            else:
                setpoint = base
            hvac_setpoints.append(setpoint)

        return schedule, hvac_setpoints
    
# ---------- Explanations ----------

    def _build_explanations(
        self,
        greedy_schedule: Dict[int, List[str]],
        greedy_metrics: Dict[str, Any],
    ) -> List[str]:
        env = self.env
        explanations: List[str] = []

        prices: List[float] = list(env.tou_prices)
        sorted_prices = sorted(prices)
        peak_threshold = sorted_prices[int(0.75 * len(sorted_prices))] if sorted_prices else None

        daily_budget = None
        if hasattr(env, "get_daily_budget"):
            daily_budget = env.get_daily_budget()

        for a in env.appliances:
            start_hour = None
            for h in range(24):
                if a.name in greedy_schedule.get(h, []):
                    start_hour = h
                    break

            if start_hour is None:
                continue

            duration = max(1, int(a.duration_hours))
            end_hour = min(24, start_hour + duration)
            window_prices = prices[start_hour:end_hour]

            hits_peak = False
            if peak_threshold is not None:
                hits_peak = any(p >= peak_threshold for p in window_prices)

            if start_hour >= 22 or start_hour < 6:
                reason = "prices overnight are the lowest"
            elif peak_threshold is not None and not hits_peak:
                reason = "in low price mode to avoid peak rates"
            else:
                reason = "early enough to meet its deadline even if prices are higher"

            parts = [f"{a.name} was scheduled at hour {start_hour} {reason}."]

            if isinstance(greedy_metrics, dict) and daily_budget is not None:
                used = greedy_metrics.get("total_kwh")
                if isinstance(used, (int, float)):
                    if used <= daily_budget:
                        parts.append("This helps keep the budget witin the estimated value")
                    else:
                        parts.append("This steps over the daily budger to avaid comfort limits or dealines ")

            explanations.append(" ".join(parts))

        if peak_threshold is not None:
            explanations.append(
                "Hvac is set to slightly relaxed during the peak rates while staying within the comfort boundary"
            )

        return explanations
