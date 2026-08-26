import cv2
import face_recognition

# 1. Image load aur details set karein
my_image = face_recognition.load_image_file("my_photo.jpg")
my_encoding = face_recognition.face_encodings(my_image)[0]

known_face_encodings = [my_encoding]
known_face_names = ["Name: Rahul | Mobile: 9876543210"] # Aapka naam aur number

# 2. Camera kholne ke liye
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Processing speed badhane ke liye frame ko chota karein
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Face detect aur encode karein
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        text = "UNKNOWN DETECTED"
        color = (0, 0, 255) # Red color for Unknown

        if True in matches:
            first_match_index = matches.index(True)
            text = known_face_names[first_match_index]
            color = (0, 255, 0) # Green color for Match

        # Original frame size par scale karein
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Face ke aas-paas Box banayein
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Bottom bar me Name & Number likhein
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, text, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    # Live Feed Dikhayein
    cv2.imshow('Traffic CCTV - Identity Monitor', frame)

    # Keyboard par 'q' dabane par program band hoga
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()