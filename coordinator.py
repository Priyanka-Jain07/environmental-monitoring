# Risk values accepted from all environmental agents.
VALID_STATUSES = {
    "Low",
    "Moderate",
    "High",
    "Very High",
}


def risk_value(status):
    values = {
        "Low": 1,
        "Moderate": 2,
        "High": 3,
        "Very High": 4,
    }

    return values.get(status, 0)


def coordinator_agent(air_result, water_result, waste_result):
    results = [
        air_result,
        water_result,
        waste_result,
    ]

    valid_results = []

    for result in results:
        if not isinstance(result, dict):
            continue

        status = str(result.get("status", "")).strip()

        if status in VALID_STATUSES:
            valid_results.append(result)

    if not valid_results:
        return {
            "agent": "Coordinator Agent",
            "status": "Unknown",
            "overall_risk": "Unknown",
            "message": (
                "No valid environmental agent results are available."
            ),
            "reason": (
                "No valid environmental agent results are available."
            ),
            "conflict": False,
            "freshness_flag": True,
            "agents_analyzed": 0,
            "average_risk": None,
        }

    total = sum(
        risk_value(result.get("status"))
        for result in valid_results
    )

    average = total / len(valid_results)

    if average <= 1.5:
        overall = "Low"
    elif average <= 2.3:
        overall = "Moderate"
    else:
        overall = "High"

    statuses = [
        result.get("status")
        for result in valid_results
    ]

    conflict = (
        "Low" in statuses
        and (
            "High" in statuses
            or "Very High" in statuses
        )
    )

    freshness_flag = len(valid_results) < len(results)

    reason = (
        f"{len(valid_results)} of {len(results)} environmental "
        f"agents returned valid analysis. "
        f"Average risk score: {average:.2f}."
    )

    if freshness_flag:
        reason += (
            " One or more agents were unavailable or not analyzed."
        )

    if conflict:
        reason += (
            " Different agents reported substantially different "
            "risk levels."
        )

    return {
        "agent": "Coordinator Agent",

        # IMPORTANT:
        # app.py expects 'status' and 'message'.
        "status": overall,
        "overall_risk": overall,

        "message": reason,
        "reason": reason,
        "conflict": conflict,
        "freshness_flag": freshness_flag,
        "agents_analyzed": len(valid_results),
        "average_risk": round(average, 2),
    }
