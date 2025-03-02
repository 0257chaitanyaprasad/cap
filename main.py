import cv2
import mediapipe as mp
from pymongo import MongoClient
import time
from datetime import datetime
import requests

client = MongoClient("mongodb+srv://chaitanyamsd77:Kunda123@happinessdb.9zok7.mongodb.net/")
db = client["HappinessDB"]
collection = db["HappinessRatings"]

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

EMAIL_API_URL = "https://happiness-email-validation.onrender.com/validate-email?email="

def validate_email(email):
    response = requests.get(EMAIL_API_URL + email)
    result = response.json()
    return result['is_email_valid']

def count_fingers(hand_landmarks):
    fingers = [
        (hand_landmarks[8].y < hand_landmarks[6].y),
        (hand_landmarks[12].y < hand_landmarks[10].y),
        (hand_landmarks[16].y < hand_landmarks[14].y),
        (hand_landmarks[20].y < hand_landmarks[18].y)
    ]
    thumb_condition = (hand_landmarks[4].x > hand_landmarks[3].x) if hand_landmarks[17].x < hand_landmarks[5].x else (hand_landmarks[4].x < hand_landmarks[3].x)
    fingers.append(thumb_condition)
    return sum(fingers)

questions = [
    "How was your day?",
    "Did you get enough sleep?",
    "Are you feeling stressed?",
    "Are you enjoying your work?",
    "Did you eat healthy today?"
]
question_interval = 5

while True:
    user_name = input("Enter your Name: ")
    age = input("Enter your Age: ")
    gender = input("Enter your Gender (male/female/others): ")

    while True:
        email = input("Enter your Email: ")
        if validate_email(email):
            print("✅ Email is Valid")
            break
        else:
            print("❌ Invalid Email! Try Again")

    cap = cv2.VideoCapture(0)
    happiness_responses = {}
    question_index = 0
    start_time = time.time()

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)

            cv2.putText(frame, questions[question_index], (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = hand_landmarks.landmark
                    finger_count = count_fingers(landmarks)
                    happiness_responses[questions[question_index]] = finger_count
                    cv2.putText(frame, f"Happiness Rating: {finger_count}/5", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.imshow("Happiness Index Monitor", frame)

            if time.time() - start_time >= question_interval:
                question_index += 1
                start_time = time.time()
                if question_index >= len(questions):
                    break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    total_fingers = sum(happiness_responses.values())
    happiness_percentage = (total_fingers / (len(questions) * 5)) * 100
    now = datetime.now()
    user_data = {
        "Name": user_name,
        "Age": age,
        "Gender": gender,
        "Email": email,
        "Date": now.strftime("%d-%m-%Y"),
        "Time": now.strftime("%H:%M:%S"),
        "Happiness Score": round(happiness_percentage, 2),
        "Answers": happiness_responses
    }

    collection.insert_one(user_data)
    print(f"😊 Your Overall Happiness Score: {round(happiness_percentage, 2)}%")

    again = input("Do you want to continue? (yes/no): ")
    if again.lower() != "yes":
        break

client.close()
print("Program Terminated")
