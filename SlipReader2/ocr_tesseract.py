import pytesseract
import cv2
import os

# ✅ ตั้ง path ไปยัง tesseract.exe (เฉพาะบน Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"ไม่สามารถเปิดภาพ: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5)  # ขยายภาพให้ชัดขึ้น
    _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)  # เพิ่ม contrast
    return thresh

def read_text_from_image(image_path):
    image = preprocess_image(image_path)
    text = pytesseract.image_to_string(image, lang='tha+eng')  # รองรับไทย+อังกฤษ
    return text

def read_images_from_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, filename)
            print(f"\n📄 อ่านสลิป: {filename}")
            print("=" * 50)
            try:
                text = read_text_from_image(image_path)
                print(text.strip())
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")
            print("=" * 50)

if __name__ == '__main__':
    print("📌 เริ่ม OCR ด้วย Tesseract...")
    read_images_from_folder('slip_images')
