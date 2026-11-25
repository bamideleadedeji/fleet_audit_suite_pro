"""
Commercial Fleet & Last-Mile Delivery Cost-Per-Mile (CPM) Audit Engine (v2.0)
Computes Cost Per Mile, Revenue Per Mile, MPG Fuel Variance/Theft Alerts, and PM Service Countdown.
"""

import pandas as pd

DEFAULT_FLEET = [
    {"Unit_ID": "TRK-101", "Vehicle_Type": "26ft Box Truck", "Route_Corridor": "I-95 Northeast", "Miles_Driven": 6420, "Fuel_Gallons": 845.0, "Benchmark_MPG": 7.8, "Fuel_Spend_USD": 3295.50, "Maint_And_Tires_USD": 980.00, "Driver_And_Ins_USD": 4850.00, "Gross_Freight_Rev_USD": 11420.00, "Miles_Until_Next_PM": 950},
    {"Unit_ID": "TRK-102", "Vehicle_Type": "26ft Box Truck", "Route_Corridor": "I-10 Sunbelt", "Miles_Driven": 7150, "Fuel_Gallons": 1140.0, "Benchmark_MPG": 7.8, "Fuel_Spend_USD": 4389.00, "Maint_And_Tires_USD": 1420.00, "Driver_And_Ins_USD": 5100.00, "Gross_Freight_Rev_USD": 12350.00, "Miles_Until_Next_PM": 3200},
    {"Unit_ID": "VAN-201", "Vehicle_Type": "Sprinter Last-Mile", "Route_Corridor": "Metro Hub A", "Miles_Driven": 4180, "Fuel_Gallons": 245.0, "Benchmark_MPG": 17.5, "Fuel_Spend_USD": 931.00, "Maint_And_Tires_USD": 390.00, "Driver_And_Ins_USD": 3450.00, "Gross_Freight_Rev_USD": 6890.00, "Miles_Until_Next_PM": 1100},
    {"Unit_ID": "VAN-202", "Vehicle_Type": "Sprinter Last-Mile", "Route_Corridor": "Metro Hub B", "Miles_Driven": 3960, "Fuel_Gallons": 288.0, "Benchmark_MPG": 17.5, "Fuel_Spend_USD": 1094.40, "Maint_And_Tires_USD": 610.00, "Driver_And_Ins_USD": 3400.00, "Gross_Freight_Rev_USD": 6210.00, "Miles_Until_Next_PM": 4400},
    {"Unit_ID": "SEM-301", "Vehicle_Type": "53ft Dry Van Semi", "Route_Corridor": "I-80 Midwest", "Miles_Driven": 9450, "Fuel_Gallons": 1390.0, "Benchmark_MPG": 6.9, "Fuel_Spend_USD": 5351.50, "Maint_And_Tires_USD": 1680.00, "Driver_And_Ins_USD": 6900.00, "Gross_Freight_Rev_USD": 17850.00, "Miles_Until_Next_PM": 600},
]


def audit_delivery_fleet(df: pd.DataFrame) -> dict:
    work = df.copy()
    actual_mpg_list, mpg_var_list, fuel_alert_list = [], [], []
    tot_cost_list, cpm_list, rpm_list, net_profit_list, net_cpm_list, pm_alert_list = [], [], [], [], [], []

    for _, row in work.iterrows():
        miles = max(float(row.get("Miles_Driven", 1.0)), 1.0)
        gallons = max(float(row.get("Fuel_Gallons", 1.0)), 0.1)
        bench_mpg = max(float(row.get("Benchmark_MPG", 8.0)), 0.1)
        fuel_usd = float(row.get("Fuel_Spend_USD", 0.0))
        maint_usd = float(row.get("Maint_And_Tires_USD", 0.0))
        driver_usd = float(row.get("Driver_And_Ins_USD", 0.0))
        rev_usd = float(row.get("Gross_Freight_Rev_USD", 0.0))
        next_pm = float(row.get("Miles_Until_Next_PM", 5000.0))

        act_mpg = round(miles / gallons, 2)
        mpg_var = round((act_mpg - bench_mpg) / bench_mpg * 100.0, 1)
        fuel_flag = "FUEL / MPG ANOMALY (<-12%)" if mpg_var <= -12.0 else "NORMAL FUEL EFFICIENCY"

        tot_cost = round(fuel_usd + maint_usd + driver_usd, 2)
        cpm = round(tot_cost / miles, 3)
        rpm = round(rev_usd / miles, 3)
        profit = round(rev_usd - tot_cost, 2)
        net_cpm = round(rpm - cpm, 3)
        pm_flag = "SERVICE DUE SOON (<=1,500 mi)" if next_pm <= 1500 else "OK"

        actual_mpg_list.append(act_mpg)
        mpg_var_list.append(mpg_var)
        fuel_alert_list.append(fuel_flag)
        tot_cost_list.append(tot_cost)
        cpm_list.append(cpm)
        rpm_list.append(rpm)
        net_profit_list.append(profit)
        net_cpm_list.append(net_cpm)
        pm_alert_list.append(pm_flag)

    work["Actual_MPG"] = actual_mpg_list
    work["MPG_Variance_Pct"] = mpg_var_list
    work["Fuel_Audit_Status"] = fuel_alert_list
    work["Total_Op_Cost_USD"] = tot_cost_list
    work["Cost_Per_Mile_USD"] = cpm_list
    work["Revenue_Per_Mile_USD"] = rpm_list
    work["Net_Profit_USD"] = net_profit_list
    work["Net_Margin_Per_Mile_USD"] = net_cpm_list
    work["PM_Service_Alert"] = pm_alert_list

    tot_miles = max(float(work["Miles_Driven"].sum()), 1.0)
    tot_cost_all = float(work["Total_Op_Cost_USD"].sum())
    tot_rev_all = float(work["Gross_Freight_Rev_USD"].sum())

    return {
        "df": work,
        "total_miles": int(tot_miles),
        "fleet_cpm": round(tot_cost_all / tot_miles, 3),
        "fleet_rpm": round(tot_rev_all / tot_miles, 3),
        "total_profit": round(tot_rev_all - tot_cost_all, 2),
        "fuel_anomalies": int((work["Fuel_Audit_Status"] != "NORMAL FUEL EFFICIENCY").sum()),
        "pm_due_count": int((work["PM_Service_Alert"] != "OK").sum()),
    }
