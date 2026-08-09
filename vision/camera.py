import cv2
import requests
import time

BACKEND_URL = "http://127.0.0.1:8000/interview/face"

SEND_INTERVAL = 3  # send one frame every 3 seconds


def send_frame_to_backend(frame):

    success, encoded_image = cv2.imencode(
        ".jpg",
        frame
    )

    if not success:
        print("ERROR: Could not encode frame.")
        return

    try:

        response = requests.post(
            BACKEND_URL,
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
                f"[EDITH] Face detected: {face_detected} | "
                f"Faces: {face_count}"
            )

        else:

            print(
                "Backend Error:",
                response.status_code,
                response.text
            )

    except requests.exceptions.RequestException as error:

        print(
            "ERROR: Backend connection failed:",
            error
        )


def start_camera():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")
        return

    print("EDITH automatic face monitoring started.")
    print("Backend:", BACKEND_URL)
    print("Press Q to close.")

    last_sent_time = 0

    while True:

        success, frame = camera.read()

        if not success:

            print(
                "ERROR: Could not read camera frame."
            )

            break

        # Display camera
        cv2.imshow(
            "EDITH - Face Monitoring",
            frame
        )

        # Automatically send frame
        current_time = time.time()

        if current_time - last_sent_time >= SEND_INTERVAL:

            send_frame_to_backend(frame)

            last_sent_time = current_time

        # Q = quit
        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    start_camera()