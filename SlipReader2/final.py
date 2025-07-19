import os
import easyocr

import re
from openpyxl import Workbook
import pandas as pd

# Initialize OCR reader
reader = easyocr.Reader(['th', 'en'])  # รองรับภาษาไทยและอังกฤษ

def read_ocr_from_image(image_path):
    # ใช้ OCR เพื่อแปลงข้อความจากภาพ
    result = reader.readtext(image_path, detail=0)  # detail=0 ทำให้ได้แค่ข้อความ
    ocr_text = ' '.join(result)
    return ocr_text

def save_text_to_file(filename, text):
    # สร้างโฟลเดอร์ result หากยังไม่มี
    result_folder = 'results'
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    
    # สร้างชื่อไฟล์ .txt จากชื่อไฟล์ภาพ
    text_filename = os.path.join(result_folder, f"{filename}.txt")
    
    with open(text_filename, 'w', encoding='utf-8') as file:
        file.write(text)
    
    print(f"📄 บันทึกข้อความในไฟล์: {text_filename}")

def process_images_from_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):  # รองรับไฟล์ .jpg, .png, .jpeg
            file_path = os.path.join(folder_path, filename)
            
            # OCR to extract text from image
            ocr_text = read_ocr_from_image(file_path)
            
            # ตรวจสอบว่า OCR ได้ข้อความหรือไม่
            if not ocr_text:
                print(f"📄 ไม่สามารถอ่านภาพ: {filename}")
            else:
                # บันทึกข้อความ OCR ลงในไฟล์ .txt
                save_text_to_file(filename.split('.')[0], ocr_text)

if __name__ == '__main__':
    folder_path = 'slip_images'  # โฟลเดอร์ที่เก็บไฟล์ภาพสลิป
    process_images_from_folder(folder_path)
