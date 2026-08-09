import cv2
import requests


BACKEND_URL = "http://127.0.0.1:8000/interview/face"


def start_camera():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        return

    print("EDITH camera started.")
    print("Backend connection: ACTIVE")
    print("Press Q to close.")
    print("Press S to send a frame to backend.")

    while True:

        success, frame = camera.read()

        if not success:
            print("ERROR: Could not read camera frame.")
            break

        # Display camera
        cv2.imshow(
            "EDITH - Camera",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        # Send current frame to FastAPI
        if key == ord("s"):

            success, encoded_image = cv2.imencode(
                ".jpg",
                frame
            )

            if not success:
                print("ERROR: Could not encode frame.")
                continue

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

                print("\n-----------------------------")
                print("Backend Status:", response.status_code)

                if response.status_code == 200:

                    result = response.json()

                    print("Backend Response:")
                    print(result)

                    face_analysis = result.get(
                        "face_analysis",
                        {}
                    )

                    print(
                        "Face detected:",
                        face_analysis.get("face_detected")
                    )

                    print(
                        "Face count:",
                        face_analysis.get("face_count")
                    )

                else:

                    print(
                        "Backend Error:",
                        response.text
                    )

                print("-----------------------------\n")

            except requests.exceptions.RequestException as error:

                print(
                    "ERROR: Backend connection failed:",
                    error
                )

        # Q = quit
        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_camera()