# EnviroMonitor - Fixed Version

## Files
- app.py
- air_agent.py
- water_agent.py
- waste_agent.py
- coordinator.py

## Main fixes

1. Air Agent
   - `status` is always one of: Low, Moderate, High, Very High.
   - `aqi_category` is kept separately for labels such as Very Unhealthy.
   - Example: AQI 232 -> `status = Very High`, `aqi_category = Very Unhealthy`.

2. Water Agent
   - Returns `ph` because the Streamlit UI reads `ph`.
   - Also returns `pH` as a compatibility alias.
   - A normal input such as pH 7.2, turbidity 2, TDS 350, DO 7 gives `status = Low`.

3. Waste Agent
   - No image means `status = Unknown`; it is not treated as Low.
   - The default `yolov8n.pt` is a generic model and must NOT be interpreted as a waste classifier.
   - For actual waste classification, set `WASTE_MODEL_PATH` to your waste-trained `best.pt`.

4. Coordinator
   - Accepts only the shared risk statuses.
   - Returns BOTH `status`/`message` and `overall_risk`/`reason`, so old and new UI code work.
   - Unanalyzed agents are excluded from the average instead of being treated as safe.

## Run

Open PowerShell in the project folder:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

If your virtual environment has a different name, activate that environment instead.

## Environment variables

Your `.env` should contain:

```text
WAQI_TOKEN=your_waqi_token
WASTE_MODEL_PATH=path\to\best.pt
WASTE_CONFIDENCE=0.15
```

`WASTE_MODEL_PATH` is optional. Without it, `yolov8n.pt` can detect generic COCO objects but cannot reliably classify them as waste.
