import cv2
import requests
import time


BASE_URL = "http://127.0.0.1:8000"


def start_camera():

    # --------------------------------------------------------
    # Start Interview Session
    # --------------------------------------------------------

    try:
        response = requests.post(
            f"{BASE_URL}/interview/start",
            timeout=10
        )

        if response.status_code != 200:
            print("ERROR: Could not start interview.")
            print(response.text)
            return

        session_data = response.json()

        session_id = session_data["session_id"]

        print("--------------------------------")
        print("EDITH Interview Session Started")
        print("Session ID:", session_id)
        print("Question:", session_data["question"])
        print("--------------------------------")

    except requests.exceptions.RequestException as error:

        print("ERROR: Backend connection failed.")
        print(error)
        return

    # --------------------------------------------------------
    # Open Camera
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")
        return

    print("EDITH camera started.")
    print("Automatic face analysis: ACTIVE")
    print("Press Q to close.")

    last_send_time = 0

    # Send approximately one frame every 2 seconds
    SEND_INTERVAL = 2

    # --------------------------------------------------------
    # Camera Loop
    # --------------------------------------------------------

    while True:

        success, frame = camera.read()

        if not success:

            print("ERROR: Could not read camera frame.")
            break

        # ----------------------------------------------------
        # Display Camera
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "EDITH - Face Analysis ACTIVE",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "EDITH - Interview Camera",
            frame
        )

        # ----------------------------------------------------
        # Automatically Send Frame
        # ----------------------------------------------------

        current_time = time.time()

        if current_time - last_send_time >= SEND_INTERVAL:

            success, encoded_image = cv2.imencode(
                ".jpg",
                frame
            )

            if success:

                try:

                    response = requests.post(
                        f"{BASE_URL}/interview/face",
                        params={
                            "session_id": session_id
                        },
                        files={
                            "image_file": (
                                "camera.jpg",
                                encoded_image.tobytes(),
                                "image/jpeg"
                            )
                        },
                        timeout=10
                    )

                    if response.status_code == 200:

                        result = response.json()

                        face_analysis = result.get(
                            "face_analysis",
                            {}
                        )

                        face_detected = face_analysis.get(
                            "face_detected",
                            False
                        )

                        face_count = face_analysis.get(
                            "face_count",
                            0
                        )

                        print(
                            f"Face detected: {face_detected} | "
                            f"Face count: {face_count}"
                        )

                    else:

                        print(
                            "Backend error:",
                            response.status_code,
                            response.text
                        )

                except requests.exceptions.RequestException as error:

                    print(
                        "ERROR: Could not send frame:",
                        error
                    )

                last_send_time = current_time

        # ----------------------------------------------------
        # Quit
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    print("EDITH camera stopped.")
    print("Session ID:", session_id)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":

    start_camera()

