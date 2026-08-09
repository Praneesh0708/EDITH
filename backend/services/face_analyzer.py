import cv2


# Load OpenCV's built-in Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def analyze_face(image):
    """
    Analyze a single image/frame.

    Returns:
        face_count
        face_detected
        faces
    """

    if image is None:
        return {
            "status": "error",
            "message": "Invalid image"
        }

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    detected_faces = []

    for (x, y, w, h) in faces:
        detected_faces.append({
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h)
        })

    return {
        "status": "success",
        "face_detected": len(detected_faces) > 0,
        "face_count": len(detected_faces),
        "faces": detected_faces
    }