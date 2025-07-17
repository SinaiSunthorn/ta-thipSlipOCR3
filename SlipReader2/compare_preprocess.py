import os
import easyocr
import cv2

# สร้าง EasyOCR Reader
reader = easyocr.Reader(['th', 'en'])

# โฟลเดอร์ภาพและผลลัพธ์
input_folder = 'slip_images'
output_folder = 'result'
os.makedirs(output_folder, exist_ok=True)

def light_preprocess(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return resized

def ocr_and_export(image_path, output_txt_path):
    # Preprocess
    preprocessed = light_preprocess(image_path)

    # ใช้ detail=1 เพื่อให้ได้ตำแหน่งข้อความ (bounding box)
    results = reader.readtext(preprocessed, detail=1)

    # จัดเรียงข้อความตามแนวตั้ง (จากบนลงล่าง)
    results.sort(key=lambda x: x[0][0][1])  # x[0][0][1] = y บรรทัดบนของกล่อง

    # รวมข้อความตามลำดับจริง
    lines = [res[1].strip() for res in results if res[1].strip()]
    joined_text = '\n'.join(lines)

    # แสดงผลใน terminal
    print(joined_text)

    # บันทึกลงไฟล์
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(joined_text)
    print(f"✅ บันทึกที่: {output_txt_path}")

# วนลูปอ่านทุกภาพ
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")

        print(f"\n📄 กำลังประมวลผล: {filename}")
        try:
            ocr_and_export(image_path, output_file)
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดกับ {filename}: {e}")
