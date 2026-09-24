import os
from functools import lru_cache

import numpy as np
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# MODEL SETTINGS
# ============================================================

MODEL_PATH = os.getenv(
    "WASTE_MODEL_PATH",
    "yolov8n.pt"
).strip()


try:

    CONFIDENCE = float(
        os.getenv(
            "WASTE_CONFIDENCE",
            "0.15"
        )
    )

except ValueError:

    CONFIDENCE = 0.15


CONFIDENCE = max(
    0.0,
    min(
        1.0,
        CONFIDENCE
    )
)


# ============================================================
# LOAD YOLO MODEL
# ============================================================

@lru_cache(maxsize=1)
def get_model():

    try:

        # YOLO automatically downloads
        # yolov8n.pt if it is not present.

        model = YOLO(
            MODEL_PATH
        )

        return model


    except Exception as e:

        raise RuntimeError(
            f"Unable to load YOLO model "
            f"'{MODEL_PATH}': {str(e)}"
        )


# ============================================================
# WASTE DETECTION AGENT
# ============================================================

def waste_detection_agent(
    uploaded_file
):

    if uploaded_file is None:

        return {

            "agent": "Waste Detection Agent",

            "status": "Unknown",

            "detections": [],

            "message": (
                "No waste image uploaded."
            )

        }


    try:

        # ----------------------------------------------------
        # OPEN IMAGE
        # ----------------------------------------------------

        uploaded_file.seek(0)

        image = Image.open(
            uploaded_file
        ).convert("RGB")


        image_array = np.array(
            image
        )


        # ----------------------------------------------------
        # LOAD MODEL
        # ----------------------------------------------------

        model = get_model()


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        results = model.predict(

            source=image_array,

            conf=CONFIDENCE,

            iou=0.5,

            imgsz=640,

            verbose=False

        )


        detections = []


        # ----------------------------------------------------
        # EXTRACT DETECTIONS
        # ----------------------------------------------------

        for result in results:

            if result.boxes is None:
                continue


            names = result.names


            for box in result.boxes:

                try:

                    class_id = int(
                        box.cls[0].item()
                    )


                    confidence = float(
                        box.conf[0].item()
                    )


                    if isinstance(
                        names,
                        dict
                    ):

                        class_name = names.get(

                            class_id,

                            f"class_{class_id}"

                        )

                    else:

                        class_name = str(
                            class_id
                        )


                    detections.append({

                        "object": class_name,

                        "confidence": round(
                            confidence,
                            3
                        )

                    })


                except Exception:

                    continue


        # ----------------------------------------------------
        # NO OBJECTS
        # ----------------------------------------------------

        if not detections:

            return {

                "agent":
                    "Waste Detection Agent",

                "status":
                    "Unknown",

                "detections":
                    [],

                "message":
                    (
                        "No detectable objects "
                        "were found."
                    ),

                "model":
                    MODEL_PATH,

                "confidence_threshold":
                    CONFIDENCE

            }


        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        # yolov8n.pt is a GENERAL object model.
        # It is NOT a waste-trained model.
        #
        # Therefore we should NOT call generic objects
        # "waste".

        custom_waste_model = (

            MODEL_PATH.lower()
            not in (
                "yolov8n.pt",
                "yolo11n.pt"
            )

        )


        if custom_waste_model:

            count = len(
                detections
            )


            if count <= 3:

                risk = "Low"

            elif count <= 7:

                risk = "Moderate"

            else:

                risk = "High"


            message = (

                f"{count} waste object(s) "
                f"detected."

            )


        else:

            risk = "Unknown"


            message = (

                f"{len(detections)} "
                f"generic object(s) detected. "

                "A waste-trained YOLO model "
                "is required for actual waste "
                "classification."

            )


        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {

            "agent":
                "Waste Detection Agent",

            "status":
                risk,

            "detections":
                detections,

            "message":
                message,

            "model":
                MODEL_PATH,

            "confidence_threshold":
                CONFIDENCE

        }


    # --------------------------------------------------------
    # INVALID IMAGE
    # --------------------------------------------------------

    except UnidentifiedImageError:

        return {

            "agent":
                "Waste Detection Agent",

            "status":
                "Unknown",

            "detections":
                [],

            "message":
                "The uploaded file is not a valid image."

        }


    # --------------------------------------------------------
    # MODEL / DETECTION ERROR
    # --------------------------------------------------------

    except Exception as e:

        return {

            "agent":
                "Waste Detection Agent",

            "status":
                "Unknown",

            "detections":
                [],

            "message":
                f"Detection error: {str(e)}"

        }