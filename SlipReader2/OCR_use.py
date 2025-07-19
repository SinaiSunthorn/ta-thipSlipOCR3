from pyzbar.pyzbar import decode
from PIL import Image
import os
import easyocr

reader = easyocr.Reader(['th', 'en'])  # OCR ไทย+อังกฤษ

def has_qr_code(image_path):
    try:
        img = Image.open(image_path)
        qr_codes = decode(img)
        return len(qr_codes) > 0
    except Exception as e:
        print(f"[ERROR] ตรวจ QR ไม่ได้ใน {image_path}: {e}")
        return False

def read_ocr_from_image(image_path):
    result = reader.readtext(image_path, detail=0)
    ocr_text = ' '.join(result)
    return ocr_text

def save_text_to_file(filename, text):
    result_folder = 'results2'
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    text_filename = os.path.join(result_folder, f"{filename}.txt")
    with open(text_filename, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"📄 บันทึกข้อความในไฟล์: {text_filename}")

def process_images_from_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            file_path = os.path.join(folder_path, filename)
            
            print(f"\n🖼️ ตรวจสอบภาพ: {filename}")

            if has_qr_code(file_path):
                print("✅ พบ QR → ดำเนินการ OCR")
                ocr_text = read_ocr_from_image(file_path)
                save_text_to_file(filename.split('.')[0], ocr_text)
            else:
                print("❌ ไม่พบ QR → เป็นสลิปปลอม")
                save_text_to_file(filename.split('.')[0], "[สลิปปลอม] ไม่พบ QR Code")

if __name__ == '__main__':
    folder_path = 'slip_images'
    process_images_from_folder(folder_path)