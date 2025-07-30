import cv2
from cvzone.HandTrackingModule import HandDetector
import math

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8)


class DragRect():
    def __init__(self, posCentre, size=[200, 200]):
        self.posCentre = posCentre
        self.size = size
        self.color = (255, 0, 255)  # Default purple color

    def update(self, cursor):
        cx, cy = self.posCentre
        w, h = self.size

        # If the index finger tip is in the rectangle region
        if cx - w // 2 < cursor[0] < cx + w // 2 and cy - h // 2 < cursor[1] < cy + h // 2:
            self.posCentre = cursor[0], cursor[1]
            self.color = (0, 255, 0)  # Green when being dragged
            return True  # Return True if this rectangle is being dragged
        else:
            self.color = (255, 0, 255)  # Purple when not being dragged
            return False


# Create multiple rectangles
rectList = []
for x in range(5):
    rectList.append(DragRect([x * 250 + 150, 150]))

while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)

    # Reset all rectangles to default color first
    for rect in rectList:
        rect.color = (255, 0, 255)

    # Find hands
    hands, img = detector.findHands(img)
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]

        if lmList and len(lmList) > 12:  # Make sure we have enough landmarks
            # Calculate distance between index finger (8) and middle finger (12)
            x1, y1 = lmList[8][0], lmList[8][1]
            x2, y2 = lmList[12][0], lmList[12][1]
            l = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            # Display distance for debugging
            cv2.putText(img, f'Distance: {int(l)}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # If fingers are close together (pinch gesture)
            if l < 50:  # Increased threshold for easier use
                cursor = lmList[8]  # Index finger tip landmark

                # Update rectangles - only one at a time
                for rect in rectList:
                    if rect.update(cursor):
                        break  # Stop after finding the first rectangle being dragged

    # Draw all rectangles
    for rect in rectList:
        cx, cy = rect.posCentre
        w, h = rect.size
        cv2.rectangle(img, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), rect.color, cv2.FILLED)
        # Add a border for better visibility
        cv2.rectangle(img, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), (255, 255, 255), 3)

    cv2.imshow('Image', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()