# CS440-Term-Project
# Energy Consumption Advisor Agent

## Overview
The **Energy Consumption Advisor Agent** is an intelligent scheduling system that helps households manage electricity usage under **time-of-use (TOU)** pricing and monthly energy budgets. The agent combines ideas from *Artificial Intelligence: A Modern Approach (AIMA)* and CSU’s **CS440** curriculum, using **decision-theoretic planning**, **heuristic search**, and **explainable AI** methods to reduce energy costs while maintaining user comfort.

A **Streamlit dashboard** visualizes the optimized daily schedule, budget tracking, cost savings, and explanations that describe the reasoning behind each decision.

---

## Key Features
- **Day-Ahead Energy Planning:** Uses a 24-hour rolling planning horizon, reflecting common practice in the energy sector.
- **Decision-Theoretic Agent Model:** Implements a Markov Decision Process (MDP) to evaluate states, actions, and rewards.
- **Constraint Controller:** Enforces appliance deadlines and comfort bounds.
- **Heuristic Scheduler:** Uses local search strategies to find efficient, cost-aware schedules.
- **Budget Controller:** Tracks monthly kWh consumption and adjusts daily energy limits accordingly.
- **Reasoning and Explanation Module:** Generates clear, rule-based natural-language explanations for each action.
- **Streamlit Interface:** Provides an interactive visualization of schedules, consumption trends, and decision rationales.

---

## How It Works
1. **Perception:**  
   The agent reads relevant data such as appliance deadlines, TOU pricing, cumulative energy usage, and comfort ranges.

2. **Day-Ahead Planning:**  
   The system generates a 24-hour plan using a **rolling horizon** approach. After each day, new information is incorporated, and the next-day plan is recomputed. This method aligns with standard energy-sector scheduling practices and the **finite-horizon MDP models** covered in class.

3. **Decision-Making:**  
   The planner uses:
   - **States:** Representing the household’s energy context at each hour.
   - **Actions:** Scheduling appliance runs or adjusting HVAC settings.
   - **Rewards:** Combining electricity cost, comfort, and adherence to deadlines and budgets.
   The objective is to compute a policy that maximizes total expected utility over the next 24 hours.

4. **Explanation Generation:**  
   For each action, the system logs the factors influencing that decision (e.g., price levels, comfort constraints, or budget status). These logs are then mapped to concise natural-language templates, producing explanations such as  
   “The dishwasher was scheduled at 11 p.m. to avoid the 6–9 p.m. peak rate.”  
   These explanations appear directly in the Streamlit dashboard.

5. **Visualization:**  
   The dashboard presents the selected schedule, cumulative energy usage, estimated savings, and explanations for each action.

---

## System Architecture
- **Agent Type:** Utility-based, decision-theoretic agent  
- **Planning Framework:** Finite-horizon MDP with daily re-planning  
- **State Variables:** Time, TOU pricing tier, appliance status, HVAC conditions, kWh usage, comfort limits  
- **Actions:** Appliance start/stop times, HVAC setpoint adjustments, EV charging control  
- **Reward Function:** Balances minimized cost, comfort maintenance, and timing constraints  

---

## Dependencies
- Python 3.10+  
- `pandas` – data handling  
- `numpy` – numerical computation  
- `streamlit` – user interface  
- `matplotlib` or `plotly` – visualizations  
- `scikit-learn` (optional) – for any predictive components or heuristic tuning  

---

## Running the Project
Clone the repository:
```bash
git clone https://github.com/your-username/energy-advisor-agent.git
cd energy-advisor-agent
