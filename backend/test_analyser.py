from billing_analyzer import analyze_billing


result = analyze_billing("sample_billing.csv")

print("\n===== CLOUDWISE ANALYSIS =====")

print("\nTotal Cloud Cost:")
print("$", result["total_cost"])

print("\nCost By Service:")
for service, cost in result["service_cost"].items():
    print(service, "→ $", cost)

print("\nPotentially Wasteful Resources:")

for resource in result["idle_resources"]:
    print(
        resource["resource_id"],
        "→ CPU:",
        resource["cpu_usage"],
        "% | Status:",
        resource["resource_status"]
    )