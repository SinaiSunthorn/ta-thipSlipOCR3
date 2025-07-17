import os
import re

# --- Config ---
INPUT_FOLDER = 'results'  # Folder containing all .txt files
# ---------------

def detect_bank(text):
    """Detect bank from OCR text content."""
    text_lower = text.lower()

    if 'krungthai' in text_lower or 'กรุงไทย' in text_lower:
        return 'krungthai'
    elif 'kbank' in text_lower or 'กสิกรไทย' in text_lower or 'k+' in text_lower or 'ake' in text_lower:
        return 'kbank'
    elif 'scb' in text_lower or 'ไทยพาณิชย์' in text_lower:
        return 'scb'
    elif 'bangkok bank' in text_lower or 'ธนาคารกรุงเทพ' in text_lower:
        return 'bangkok'
    elif 'gsb' in text_lower or 'ออมสิน' in text_lower or 'mymo' in text_lower:
        return 'gsb'
    else:
        return 'unknown'

# Example handlers (replace with real pipelines later)
def handle_kbank(text): 
    print("🔁 กสิกรไทย (KBank)")

def handle_krungthai(text): 
    print("🔁 กรุงไทย")

def handle_scb(text):
    print("🔁 ไทยพาณิชย์ (SCB)")

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    sender_name = sender_acc = receiver_name = receiver_acc = amount = None

    for i, line in enumerate(lines):
        if not sender_name and 'จาก' in line:
            sender_name = lines[i + 1] if i + 1 < len(lines) else "ไม่พบชื่อผู้โอน"
            sender_acc = lines[i + 2] if i + 2 < len(lines) else "ไม่พบเลขบัญชีผู้โอน"

        elif not receiver_name and 'ไปยัง' in line:
            receiver_name = lines[i + 1] if i + 1 < len(lines) else "ไม่พบชื่อผู้รับ"
            receiver_acc = lines[i + 2] if i + 2 < len(lines) else "ไม่พบเลขบัญชีผู้รับ"

        elif not amount and 'จำนวนเงิน' in line:
            if i + 1 < len(lines):
                amt = lines[i + 1].replace(',', '').replace('บาท', '').strip()
                if any(c.isdigit() for c in amt):
                    amount = amt

    # Fallbacks
    sender_name = sender_name or "ไม่พบชื่อผู้โอน"
    sender_acc = sender_acc or "ไม่พบเลขบัญชีผู้โอน"
    receiver_name = receiver_name or "ไม่พบชื่อผู้รับ"
    receiver_acc = receiver_acc or "ไม่พบเลขบัญชีผู้รับ"
    amount = amount or "ไม่พบจำนวนเงิน"

    # Output
    print("👤 ผู้โอน:", sender_name)
    print("   เลขบัญชี:", sender_acc)
    print("👤 ผู้รับ:", receiver_name)
    print("   เลขบัญชี:", receiver_acc)
    print("💰 จำนวนเงิน:", amount)

def handle_bangkok(text): 
     print("🔁 ธ.กรุงเทพ")

#     lines = [line.strip() for line in text.split('\n') if line.strip()]
    
#     sender_name = sender_acc = receiver_name = receiver_acc = amount = None

#     for i, line in enumerate(lines):
#         if not amount and 'จำนวนเงิน' in line:
#             if i + 1 < len(lines):
#                 amt = lines[i + 1].replace(',', '').replace('บาท', '').replace('thb', '').strip()
#                 amt = re.sub(r'[^\d.]', '', amt)
#                 if amt:
#                     amount = amt

#         elif not sender_name and 'จาก' in line:
#             sender_name = lines[i + 1] if i + 1 < len(lines) else "ไม่พบชื่อผู้โอน"
#             sender_acc = lines[i + 2] if i + 2 < len(lines) else "ไม่พบเลขบัญชีผู้โอน"

#         elif not receiver_name and ('ไปที่' in line or 'ไปยัง' in line):
#             receiver_name = lines[i + 1] if i + 1 < len(lines) else "ไม่พบชื่อผู้รับ"
#             receiver_acc = lines[i + 2] if i + 2 < len(lines) else "ไม่พบเลขบัญชีผู้รับ"

#     # Fallbacks
#     sender_name = sender_name or "ไม่พบชื่อผู้โอน"
#     sender_acc = sender_acc or "ไม่พบเลขบัญชีผู้โอน"
#     receiver_name = receiver_name or "ไม่พบชื่อผู้รับ"
#     receiver_acc = receiver_acc or "ไม่พบเลขบัญชีผู้รับ"
#     amount = amount or "ไม่พบจำนวนเงิน"

#     # Output
#     print("👤 ผู้โอน:", sender_name)
#     print("   เลขบัญชี:", sender_acc)
#     print("👤 ผู้รับ:", receiver_name)
#     print("   เลขบัญชี:", receiver_acc)
#     print("💰 จำนวนเงิน:", amount)

def handle_gsb(text): 
    print("🔁 ออมสิน (GSB)")
    
def handle_unknown(text): 
    print("⚠️ ไม่สามารถระบุธนาคารได้")

# --- Main Script ---
def main():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith('.txt'):
            path = os.path.join(INPUT_FOLDER, filename)
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()

            bank = detect_bank(text)
            print(f"\n📄 File: {filename} → Bank: {bank}")

            # Route to handler
            match bank:
                case 'kbank': handle_kbank(text)
                case 'krungthai': handle_krungthai(text)
                case 'scb': handle_scb(text)
                case 'bangkok': handle_bangkok(text)
                case 'gsb': handle_gsb(text)
                case _: handle_unknown(text)

if __name__ == '__main__':
    main()