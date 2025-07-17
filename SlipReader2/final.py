import os
import re
from openpyxl import Workbook
import pandas as pd

# Summary collector
summary_data = []

INPUT_FOLDER = 'results'

# Detect bank func

def detect_bank(text):
    """Detect bank from OCR text content."""
    text_lower = text.strip().lower()
    words = text.strip().lower().split()

    if words and words[0] == 'scb':
        return 'scb'
    
    elif words and words[0] == 'krungthai':
        return 'krungthai'
    
    elif re.search(r'\bgsb\b', text_lower) or 'ธนาคารออมสิน' in text_lower:
        return 'gsb'

    elif (
        (match_kbank_regex := re.search(r'(จาก|^)\s*[นสย]\.?\s*[\u0E00-\u0E7F\s\.]+ธ\.?กสิกรไทย', text)) or
        (has_kasikorn := 'กสิกรไทย' in text_lower) or
        (has_kbank := 'kbank' in text_lower) or
        (has_kplus := 'k+' in text_lower) or
        (has_make := 'ake' in text_lower)
    ):
        # 🔍 Show what matched
        # if match_kbank_regex:
        #     print("🔍 Matched regex: sender name + ธ.กสิกรไทย")
        #     print("→", match_kbank_regex.group())
        # elif has_kasikorn:
        #     print("🔍 Matched: 'กสิกรไทย' in text_lower")
        # elif has_kbank:
        #     print("🔍 Matched: 'kbank' in text_lower")
        # elif has_kplus:
        #     print("🔍 Matched: 'k+' in text_lower")
        # elif has_make:
        #     print("🔍 Matched: 'ake' in text_lower")

        return 'kbank'
    
    elif words and words[0] == 'bangkok':
        return 'bangkok'
    
    else:
        return 'unknown'
    
# Filter text
    
def handle_scb(text):
    print("🔁 ไทยพาณิชย์ (SCB)")

    # ใช้ re เพื่อแยกบรรทัดที่ไม่ว่าง
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ใช้ re เพื่อจับชื่อผู้โอนและเลขบัญชีจากคำว่า "จาก"
    sender_name_match = re.search(r'จาก\s*([\u0E00-\u0E7F]+\s[\u0E00-\u0E7F]+\s?[\u0E00-\u0E7F]+)', text)
    sender_name = sender_name_match.group(1) if sender_name_match else 'ไม่พบชื่อผู้โอน'
    
    # ใช้ re เพื่อจับเลขบัญชีผู้โอนจากคำว่า "จาก" (เลขบัญชีอาจจะมีช่องว่างหรือขีดกลาง)
    sender_acc_match = re.search(r'((?:x{1,3}[\s-]?){1,2}\d{3,4}-?\d?)', text.lower())
    sender_acc = sender_acc_match.group(1) if sender_acc_match else 'ไม่พบเลขบัญชี'
    
    # ใช้ re เพื่อจับชื่อผู้รับและเลขบัญชีผู้รับจากคำว่า "ไปยัง"
    # ชื่อผู้รับ (รองรับคำนำหน้า เช่น น.ส. / นาย / นาง)
    receiver_name_match = re.search(  r'ไปยัง\s*((?:[นสย]\.?\s*)?(?:[\u0E00-\u0E7F\.]+(?:\s+[\u0E00-\u0E7F]+)*))', text)
    receiver_name = receiver_name_match.group(1).strip() if receiver_name_match else 'ไม่พบชื่อผู้รับ'

    # ใช้ re เพื่อจับเลขบัญชีผู้รับจากคำว่า "ไปยัง" (เลขบัญชีผู้รับก็อาจมีช่องว่างหรือขีดกลาง)
    receiver_acc_match = re.search(r'ไปยัง.*?((?:x{1,3}[\s-]?){1,2}\d{3,4}-?\d?)', text.lower())
    receiver_acc = receiver_acc_match.group(1) if receiver_acc_match else "ไม่พบเลขบัญชีผู้รับ"
    
    # ใช้ re เพื่อจับจำนวนเงินจากคำว่า "จำนวนเงิน"
    amount_match = re.search(r'จำนวนเงิน\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
    amount = amount_match.group(1) if amount_match else "ไม่พบจำนวนเงิน"

    # Output ข้อมูลที่แยกออกจาก OCR
    print("👤 ผู้โอน:", sender_name)
    print("   เลขบัญชี:", sender_acc)
    print("👤 ผู้รับ:", receiver_name)
    print("   เลขบัญชี:", receiver_acc)
    print("💰 จำนวนเงิน:", amount)

    return {
        "sender_name": sender_name,
        "sender_bank": "ไทยพาณิชย์",
        "sender_acc": sender_acc,
        "receiver_name": receiver_name,
        "receiver_bank": "ไม่ระบุ",  # SCB slip มักไม่มีชื่อธนาคารผู้รับ
        "receiver_acc": receiver_acc,
        "amount": amount
    }

def handle_krungthai(text):
    print("🔁 กรุงไทย")

    # ใช้ re เพื่อแยกบรรทัดที่ไม่ว่าง
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ดึงข้อความตั้งแต่ "จาก" เป็นต้นไป
    sender_segment = text[text.find("จาก"):text.find("ไปยัง") if "ไปยัง" in text else len(text)]
    # ชื่อผู้โอน
    sender_name_match = re.search(r'จาก\s*((?:[นสย]\.?\s*)?(?:[\u0E00-\u0E7F\.]+))', sender_segment)
    sender_name = sender_name_match.group(1).strip() if sender_name_match else 'ไม่พบชื่อผู้โอน'
    # ธนาคารผู้โอน
    sender_bank_match = re.search(r'จาก\s+[\u0E00-\u0E7F\s.]+?\s+([\u0E00-\u0E7F]+)', sender_segment)
    sender_bank = sender_bank_match.group(1) if sender_bank_match else 'ไม่พบชื่อธนาคารผู้โอน'
    # เลขบัญชีผู้โอน
    sender_acc_match = re.search(r'(?:x{1,3}[\s-]?){1,2}\d{3,4}-?\d?', sender_segment.lower())
    sender_acc = sender_acc_match.group() if sender_acc_match else 'ไม่พบเลขบัญชี'

    # ดึงข้อความตั้งแต่ "ไปยัง" เป็นต้นไป
    receiver_segment = text[text.find("ไปยัง"):text.find("จำนวน") if "จำนวน" in text else len(text)]
    # ชื่อผู้รับ
    receiver_name_match = re.search(
        r'ไปยัง\s*((?:น\.ส\.|นางสาว|นาย|นาง)?\s*[\u0E00-\u0E7F]+(?:\s[\u0E00-\u0E7F]+)?)',receiver_segment
    )
    receiver_name = receiver_name_match.group(1).strip() if receiver_name_match else 'ไม่พบชื่อผู้รับ'
    # ธนาคารผู้รับ
    receiver_bank_match = re.search(r'ไปยัง\s+[\u0E00-\u0E7F\s.]+?\s+([\u0E00-\u0E7F]+)?\s+([\u0E00-\u0E7F]+)?\s+([\u0E00-\u0E7F]+)', receiver_segment)
    receiver_bank = receiver_bank_match.group(3) if receiver_bank_match else 'ไม่พบชื่อธนาคารผู้รับ'
    # เลขบัญชีผู้รับ
    receiver_acc_match = re.search(r'(?:x{1,3}[\s-]?){1,2}\d{3,4}-?\d?', receiver_segment.lower())
    receiver_acc = receiver_acc_match.group() if receiver_acc_match else 'ไม่พบเลขบัญชี'

    # จำนวนเงิน
    amount_match = re.search(r'จำนวนเงิน\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
    amount = amount_match.group(1) if amount_match else "ไม่พบจำนวนเงิน"

    # Output แสดงผล
    print("sender_segment:", sender_segment)
    print("receiver_segment:", receiver_segment)
    print("👤 ผู้โอน:", sender_name)
    print("   ธนาคาร:", sender_bank)
    print("   เลขบัญชี:", sender_acc)
    print("👤 ผู้รับ:", receiver_name)
    print("   ธนาคาร:", receiver_bank)
    print("   เลขบัญชี:", receiver_acc)
    print("💰 จำนวนเงิน:", amount)

    # Return ข้อมูล
    return {
        'sender_name': sender_name,
        'sender_bank': sender_bank,
        'sender_acc': sender_acc,
        'receiver_name': receiver_name,
        'receiver_bank': receiver_bank,
        'receiver_acc': receiver_acc,
        'amount': amount
    }

def handle_gsb(text):
    print("🔁 ออมสิน (GSB)")

    # Sender name
    sender_name_match = re.search(r'จาก\s+([นาย|นาง|น.ส.|นางสาว]*[\u0E00-\u0E7F\s]+?)\s+ธนาคารออมสิน', text)
    sender_name = sender_name_match.group(1).strip() if sender_name_match else "ไม่พบชื่อผู้โอน"

    # Sender bank
    sender_bank = "ธนาคารออมสิน" if "ธนาคารออมสิน" in text else "ไม่พบชื่อธนาคารผู้โอน"

    # Sender account
    sender_acc_match = re.search(r'ธนาคารออมสิน\s+(\d{4}x{4,}[\d]+)', text)
    sender_acc = sender_acc_match.group(1) if sender_acc_match else "ไม่พบเลขบัญชีผู้โอน"

    # Receiver name: รองรับ "เติมเงินพร้อมเพย์" และมี . หรือ ~ คั่น
    receiver_name_match = re.search(
        r'ถึง\s+([นาย|นาง|น\.ส\.|นางสาว]*[\u0E00-\u0E7F\s.]+?)\s+(?:เติมเงิน)?\s*(?:พร้อมเพย์|พร้อมจ่าย)',
        text
    )
    receiver_name = receiver_name_match.group(1).strip() if receiver_name_match else "ไม่พบชื่อผู้รับ"

    # Receiver bank
    receiver_bank_match = re.search(r'(เติมเงิน)?\s*(พร้อมเพย์|พร้อมจ่าย)', text)
    receiver_bank = receiver_bank_match.group(0).strip() if receiver_bank_match else "ไม่พบช่องทางผู้รับ"

    # Receiver account: รองรับช่องว่าง, 'เาง', หรือไม่มี space ระหว่าง
    receiver_acc_match = re.search(
        r'(?:พร้อมเพย์|พร้อมจ่าย)[\s\w]*?(\d{4}x{4,}[\d]+)', text
    )
    receiver_acc = receiver_acc_match.group(1) if receiver_acc_match else "ไม่พบเลขบัญชีผู้รับ"

    # Amount
    amount_match = re.search(r'จำนวนเงิน\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
    amount = amount_match.group(1) if amount_match else "ไม่พบจำนวนเงิน"

    # Output ข้อมูลที่แยกออกจาก OCR
    print("👤 ผู้โอน:", sender_name)
    print("   เลขบัญชี:", sender_acc)
    print("👤 ผู้รับ:", receiver_name)
    print("   เลขบัญชี:", receiver_acc)
    print("💰 จำนวนเงิน:", amount)

    return {
        "sender_name": sender_name,
        "sender_bank": "ธนาคารออมสิน",
        "sender_acc": sender_acc,
        "receiver_name": receiver_name,
        "receiver_bank": receiver_bank,
        "receiver_acc": receiver_acc,
        "amount": amount
    }

def handle_kbank(text): 
    print("🔁 กสิกรไทย (KBank)")
    # Sender name
    sender_name_match = re.search(
        r'(?:น\.ส\.|นางสาว|นาย|นาง)\s*[\u0E00-\u0E7F]+\s[\u0E00-\u0E7F\.]+',
        text
    )
    sender_name = sender_name_match.group() if sender_name_match else "ไม่พบชื่อผู้โอน"

    # Sender bank (assume first ธ.กสิกรไทย after sender name)
    sender_bank_match = re.search(
        r'{}[\s.]*ธ\.กสิกรไทย'.format(re.escape(sender_name)),
        text
    )
    sender_bank = "ธ.กสิกรไทย" if sender_bank_match else "ไม่พบชื่อธนาคารผู้โอน"

    # Sender account (first masked pattern)
    sender_acc_match = re.search(
        r'(?:x{1,3}[\s\-]?){1,3}\d{3,4}-?(?:\d|x)?',
        text.lower()
    )
    sender_acc = sender_acc_match.group() if sender_acc_match else "ไม่พบเลขบัญชีผู้โอน"

    # Receiver name (second name after first account)
    receiver_name_match = re.findall(
        r'(?:น\.ส\.|นางสาว|นาย|นาง)\s*[\u0E00-\u0E7F]+\s[\u0E00-\u0E7F\.]+',
        text
    )
    receiver_name = receiver_name_match[1] if len(receiver_name_match) > 1 else "ไม่พบชื่อผู้รับ"

    # Receiver bank (second ธ.กสิกรไทย)
    receiver_bank_match = re.findall(
        r'ธ\.กสิกรไทย',
        text
    )
    receiver_bank = receiver_bank_match[1] if len(receiver_bank_match) > 1 else "ไม่พบชื่อธนาคารผู้รับ"

    # Receiver account (second masked pattern)
    receiver_acc_match = re.findall(
        r'(?:x{1,3}[\s\-]?){1,3}\d{3,4}-?(?:\d|x)?',
        text.lower()
    )
    receiver_acc = receiver_acc_match[1] if len(receiver_acc_match) > 1 else "ไม่พบเลขบัญชีผู้รับ"

    # Amount
    amount_match = re.search(
        r'จำนวน:\s*([\d,]+\.\d{2})',
        text
    )
    amount = amount_match.group(1) if amount_match else "ไม่พบจำนวนเงิน"

    # Output
    print("👤 ผู้โอน:", sender_name)
    print("   ธนาคาร:", sender_bank)
    print("   เลขบัญชี:", sender_acc)
    print("👤 ผู้รับ:", receiver_name)
    print("   ธนาคาร:", receiver_bank)
    print("   เลขบัญชี:", receiver_acc)
    print("💰 จำนวนเงิน:", amount)

    return {
        "sender_name": sender_name,
        "sender_bank": "ธนาคารกสิกรไทย",
        "sender_acc": sender_acc,
        "receiver_name": receiver_name,
        "receiver_bank": receiver_bank,
        "receiver_acc": receiver_acc,
        "amount": amount
    }

def handle_bangkok(text): 
    print("🔁 กรุงเทพ")
    # Sender name
    sender_name_match = re.search(r'จาก\s+(น\.ส\.|นางสาว|นาย|นาง)\s*([\u0E00-\u0E7F]+)', text)
    sender_name = f"{sender_name_match.group(1)} {sender_name_match.group(2)}" if sender_name_match else "ไม่พบชื่อผู้โอน"

    # Sender account (look for 3-digit + dash + masked)
    sender_acc_match = re.search(r'จาก.*?(\d{3}-\d(?:[\s\-]?[x\d]{3,6}))', text.lower())
    sender_acc = sender_acc_match.group(1) if sender_acc_match else 'ไม่พบเลขบัญชี'

    # Sender bank
    sender_bank = "ธนาคารกรุงเทพ" if "ธนาคารกรุงเทพ" in text else "ไม่พบชื่อธนาคารผู้โอน"

    # Receiver name (match first Thai full name after 'ไปที่')
    receiver_name_match = re.search(r'ไปที่.*?(น\.ส\.|นางสาว|นาย|นาง)?\s*([\u0E00-\u0E7F\s]+?)\s+\d{3}', text)
    receiver_name = f"{receiver_name_match.group(1)} {receiver_name_match.group(2).strip()}" if receiver_name_match else "ไม่พบชื่อผู้รับ"

    # Receiver account
    receiver_acc_match = re.search(r'จาก.*?(\d{3}-\d(?:[\s\-]?[x]{1,3}){0,2}[\s\-]?\d{2,4})', text.lower())
    receiver_acc = receiver_acc_match.group(1) if receiver_acc_match else "ไม่พบเลขบัญชีผู้รับ"

    # Receiver bank
    receiver_bank_match = re.search(r'ไปที่.*?(ธนาคาร[\u0E00-\u0E7F]+)', text)
    receiver_bank = receiver_bank_match.group(1) if receiver_bank_match else ("พร้อมเพย์" if "พร้อมเพย์" in text else "ไม่พบชื่อธนาคารผู้รับ")

    # Amount
    amount_match = re.search(r'จำนวนเงิน\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
    amount = amount_match.group(1) if amount_match else "ไม่พบจำนวนเงิน"

    # Output
    print("👤 ผู้โอน:", sender_name)
    print("   ธนาคาร:", sender_bank)
    print("   เลขบัญชี:", sender_acc)
    print("👤 ผู้รับ:", receiver_name)
    print("   ช่องทาง:", receiver_bank)
    print("   เลขบัญชี:", receiver_acc)
    print("💰 จำนวนเงิน:", amount)

    return {
        "sender_name": sender_name,
        "sender_bank": "กรุงเทพ",
        "sender_acc": sender_acc,
        "receiver_name": receiver_name,
        "receiver_bank": receiver_bank,
        "receiver_acc": receiver_acc,
        "amount": amount
    }

def handle_unknown(text): 
    print("⚠️ ไม่สามารถระบุธนาคารได้")

# Additional Functions
def log_data(file_name, bank, sender_name, sender_bank, sender_acc, receiver_name, receiver_bank, receiver_acc, amount):
    summary_data.append([
        file_name,
        bank,
        sender_name,
        sender_bank,
        sender_acc,
        receiver_name,
        receiver_bank,
        receiver_acc,
        amount
    ])

def write_to_excel(data, filename="output_summary.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"

    headers = [
        "Filename", "Bank",
        "Sender Name", "Sender Bank", "Sender Account",
        "Receiver Name", "Receiver Bank", "Receiver Account",
        "Amount"
    ]
    ws.append(headers)

    for row in data:
        ws.append(row)

    wb.save(filename)
    print(f"\n📁 Exported summary to {filename}")

# Main Script

def main():
    data_rows = []

    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith('.txt'):
            path = os.path.join(INPUT_FOLDER, filename)
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()

            bank = detect_bank(text)
            print(f"\n📄 File: {filename} → Bank: {bank}")

            row = {
                "file": filename,
                "bank": bank,
                "sender_name": "-",
                "sender_bank": "-",
                "sender_acc": "-",
                "receiver_name": "-",
                "receiver_bank": "-",
                "receiver_acc": "-",
                "amount": "-"
            }

            if bank == 'scb':
                data = handle_scb(text)
            elif bank == 'krungthai':
                data = handle_krungthai(text)
            elif bank == 'kbank':
                data = handle_kbank(text)
            elif bank == 'bangkok':
                data = handle_bangkok(text)
            elif bank == 'gsb':
                data = handle_gsb(text)
            else:
                handle_unknown(text)
                data = {}

            # อัปเดตข้อมูลใน row ถ้ามี data คืนมา
            if data:
                row.update(data)

            data_rows.append(row)

    # Export เป็น .xlsx
    df = pd.DataFrame(data_rows)
    df.to_excel("output.xlsx", index=False)
    print("\n✅ Exported to output.xlsx")

if __name__ == '__main__':
    main()