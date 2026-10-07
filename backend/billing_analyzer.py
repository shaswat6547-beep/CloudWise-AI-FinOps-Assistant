import pandas as pd


def analyze_billing(file_path):
    # Read the billing CSV file
    df = pd.read_csv(file_path)

    # Calculate total cloud cost
    total_cost = df["cost"].sum()

    # Calculate cost for each cloud service
    service_cost = (
        df.groupby("service")["cost"]
        .sum()
        .sort_values(ascending=False)
    )

    # Find potentially wasteful resources
    idle_resources = df[
        (df["cpu_usage"] < 10) |
        (df["resource_status"] == "unattached")
    ]

    return {
        "total_cost": round(total_cost, 2),
        "service_cost": service_cost.to_dict(),
        "idle_resources": idle_resources.to_dict("records")
    }