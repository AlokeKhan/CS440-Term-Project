import streamlit as st

from agent import EnergyAdvisorAgent
from utils import make_default_env, compute_savings


def main() -> None:
    st.title("Energy Consumption Advisor Agent")

    st.sidebar.header("Household settings")
    monthly_budget = st.sidebar.number_input(
        "Monthly energy budget (kWh)",
        min_value=100.0,
        max_value=2000.0,
        value=600.0,
        step=50.0,
    )
    pricing_type = st.sidebar.selectbox(
        "TOU pricing type",
        options=["standard", "summer", "winter"],
        index=0,
    )

    if st.button("Generate day-ahead plan"):
        env = make_default_env(monthly_budget, pricing_type)
        agent = EnergyAdvisorAgent(env)
        result = agent.plan_day()

        baseline_metrics = result.get("baseline_metrics", {}) or {}
        greedy_metrics = result.get("greedy_metrics", {}) or {}

        savings = compute_savings(baseline_metrics, greedy_metrics)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Baseline")
            st.metric(
                "Daily energy (kWh)",
                f"{baseline_metrics.get('total_kwh', 0.0):.2f}",
            )
            st.metric(
                "Daily cost",
                f"{baseline_metrics.get('total_cost', 0.0):.2f}",
            )

        with col2:
            st.subheader("Greedy plan")
            st.metric(
                "Daily energy (kWh)",
                f"{greedy_metrics.get('total_kwh', 0.0):.2f}",
            )
            st.metric(
                "Daily cost",
                f"{greedy_metrics.get('total_cost', 0.0):.2f}",
            )
            st.metric(
                "Savings vs baseline",
                f"{savings['absolute']:.2f} ({savings['percent']:.1f}%)",
            )

        baseline_schedule = result.get("baseline_schedule", {}) or {}
        greedy_schedule = result.get("greedy_schedule", {}) or {}

        rows = []
        for h in range(24):
            rows.append(
                {
                    "hour": h,
                    "baseline": ", ".join(baseline_schedule.get(h, [])),
                    "greedy": ", ".join(greedy_schedule.get(h, [])),
                }
            )

        st.subheader("Schedules")
        st.dataframe(rows)

        hourly_usage = greedy_metrics.get("hourly_usage")
        hourly_costs = greedy_metrics.get("hourly_costs")

        if hourly_usage:
            st.subheader("Greedy hourly usage (kWh)")
            st.line_chart({"usage_kWh": hourly_usage})

        if hourly_costs:
            st.subheader("Greedy hourly cost")
            st.line_chart({"cost": hourly_costs})

        daily_budget = greedy_metrics.get("daily_budget_kwh")
        if isinstance(daily_budget, (int, float)):
            used = greedy_metrics.get("total_kwh", 0.0)
            st.subheader("Daily budget")
            st.write(
                f"Estimated daily budget: {daily_budget:.2f} kWh, "
                f"greedy plan uses {float(used):.2f} kWh."
            )

        explanations = result.get("explanations", [])
        if explanations:
            st.subheader("Explanation for decisions")
            for text in explanations:
                st.write(f"- {text}")


if __name__ == "__main__":
    main()
