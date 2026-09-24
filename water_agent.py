import math


def water_quality_agent(
    ph,
    turbidity,
    tds,
    dissolved_oxygen,
):
    try:
        ph = float(ph)
        turbidity = float(turbidity)
        tds = float(tds)
        dissolved_oxygen = float(dissolved_oxygen)

    except (ValueError, TypeError):
        return {
            "agent": "Water Quality Agent",
            "status": "Unknown",
            "risk_points": 0,
            "message": "Invalid water parameter values.",
        }

    values = [ph, turbidity, tds, dissolved_oxygen]

    if not all(math.isfinite(value) for value in values):
        return {
            "agent": "Water Quality Agent",
            "status": "Unknown",
            "risk_points": 0,
            "message": "Water parameters contain invalid numeric values.",
        }

    issues = []

    # pH
    if ph < 6.5:
        issues.append(f"pH is too low ({ph})")
    elif ph > 8.5:
        issues.append(f"pH is too high ({ph})")

    # Turbidity
    if turbidity > 5:
        issues.append(f"Turbidity is high ({turbidity})")

    # TDS
    if tds > 500:
        issues.append(f"TDS is high ({tds})")

    # Dissolved oxygen
    if dissolved_oxygen < 5:
        issues.append(f"Dissolved oxygen is low ({dissolved_oxygen})")

    risk_points = len(issues)

    if risk_points == 0:
        risk = "Low"
        message = (
            "All configured water parameters are within "
            "the configured thresholds."
        )
    elif risk_points <= 2:
        risk = "Moderate"
        message = (
            f"{risk_points} water parameter(s) are outside "
            "the configured thresholds."
        )
    else:
        risk = "High"
        message = (
            f"{risk_points} water parameter(s) are outside "
            "the configured thresholds."
        )

    return {
    "agent": "Water Quality Agent",
    "status": risk,
    "ph": ph,
    "turbidity": turbidity,
    "tds": tds,
    "dissolved_oxygen": dissolved_oxygen,
    "risk_points": risk_points,
    "issues": issues,
    "message": message
}