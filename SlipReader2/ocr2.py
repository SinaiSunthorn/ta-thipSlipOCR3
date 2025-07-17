import os
import re

# --- Config --- #
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
         # ใช้ re เพื่อแยกบรรทัดที่ไม่ว่าง
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ใช้ re เพื่อจับชื่อผู้โอนและเลขบัญชีจากคำว่า "จาก"
    sender_name_match = re.search(r'จาก\s*((?:[นรสยจล]\.?\s*)?(?:[\u0E00-\u0E7F\.]+\s*){1,4}?)(?=\s*(กสิกรไทย|กรุงไทย|ไทยพาณิชย์|ออมสิน|กรุงเทพ|tmb|ธนาคาร|xxx|x-))',text)
    sender_name = sender_name_match.group(1).strip() if sender_name_match else 'ไม่พบชื่อผู้โอน'

    
    # ใช้ re เพื่อจับเลขบัญชีผู้โอนจากคำว่า "จาก" (เลขบัญชีอาจจะมีช่องว่างหรือขีดกลาง)
    sender_acc_match = re.search(r'\d{3}-\d{1,4}', text.replace(' ', ''))
    sender_acc = sender_acc_match.group() if sender_acc_match else 'ไม่พบเลขบัญชี'
    
    # ใช้ re เพื่อจับชื่อผู้รับและเลขบัญชีผู้รับจากคำว่า "ไปยัง"
    # ชื่อผู้รับ (รองรับคำนำหน้า เช่น น.ส. / นาย / นาง)
    receiver_name_match = re.search(r'ไปยัง\s*((?:[นสย]\.?\s*)?(?:[\u0E00-\u0E7F\.]+\s*){1,4}?)(?=\s*(กสิกรไทย|กรุงไทย|ไทยพาณิชย์|ออมสิน|กรุงเทพ|tmb|ธนาคาร|xxx|x-))',text)
    receiver_name = receiver_name_match.group(1).strip() if receiver_name_match else 'ไม่พบชื่อผู้รับ'


    # ใช้ re เพื่อจับเลขบัญชีผู้รับจากคำว่า "ไปยัง" (เลขบัญชีผู้รับก็อาจมีช่องว่างหรือขีดกลาง)
    receiver_acc_match = re.search(r'ไปยัง.*?((?:\d{3}-?\d{1,4})|(?:\d{9,12}))', text)
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

    
def handle_scb(text):
    print("🔁 ไทยพาณิชย์ (SCB)")

        # ใช้ re เพื่อแยกบรรทัดที่ไม่ว่าง
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ใช้ re เพื่อจับชื่อผู้โอนและเลขบัญชีจากคำว่า "จาก"
    sender_name_match = re.search(r'จาก\s*([\u0E00-\u0E7F]+\s[\u0E00-\u0E7F]+\s?[\u0E00-\u0E7F]+)', text)
    sender_name = sender_name_match.group(1) if sender_name_match else 'ไม่พบชื่อผู้โอน'
    
    # ใช้ re เพื่อจับเลขบัญชีผู้โอนจากคำว่า "จาก" (เลขบัญชีอาจจะมีช่องว่างหรือขีดกลาง)
    sender_acc_match = re.search(r'\d{3}-\d{1,4}', text.replace(' ', ''))
    sender_acc = sender_acc_match.group() if sender_acc_match else 'ไม่พบเลขบัญชี'
    
    # ใช้ re เพื่อจับชื่อผู้รับและเลขบัญชีผู้รับจากคำว่า "ไปยัง"
    # ชื่อผู้รับ (รองรับคำนำหน้า เช่น น.ส. / นาย / นาง)
    receiver_name_match = re.search(  r'ไปยัง\s*((?:[นสย]\.?\s*)?(?:[\u0E00-\u0E7F\.]+(?:\s+[\u0E00-\u0E7F]+)*))', text)
    receiver_name = receiver_name_match.group(1).strip() if receiver_name_match else 'ไม่พบชื่อผู้รับ'

    # ใช้ re เพื่อจับเลขบัญชีผู้รับจากคำว่า "ไปยัง" (เลขบัญชีผู้รับก็อาจมีช่องว่างหรือขีดกลาง)
    receiver_acc_match = re.search(r'ไปยัง.*?((?:\d{3}-?\d{1,4})|(?:\d{9,12}))', text)
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

def handle_bangkok(text): 
    print("🔁 ธ.กรุงเทพ")
    # ใช้ re เพื่อแยกบรรทัดที่ไม่ว่าง
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ใช้ re เพื่อจับชื่อผู้โอนและเลขบัญชีจากคำว่า "จาก"
    sender_name_match = re.search(r'จาก\s*((?:[น]\.?\s*)?(?:[\u0E00-\u0E7F\.]+\s*){1,4}?)(?=\s*(กสิกรไทย|กรุงไทย|ไทยพาณิชย์|ออมสิน|กรุงเทพ|tmb|ธนาคาร|xxx|x-))',text)
    sender_name = sender_name_match.group(1).strip() if sender_name_match else 'ไม่พบชื่อผู้โอน'

    
    # ใช้ re เพื่อจับเลขบัญชีผู้โอนจากคำว่า "จาก" (เลขบัญชีอาจจะมีช่องว่างหรือขีดกลาง)
    sender_acc_match = re.search(r'[\dXx]{2,4}[-\s]?[\dXx]{2,4}[-\s]?[\dXx]{2,4}', text.replace(' ', ''))
    sender_acc = sender_acc_match.group() if sender_acc_match else 'ไม่พบเลขบัญชี'
    
    # ใช้ re เพื่อจับชื่อผู้รับและเลขบัญชีผู้รับจากคำว่า "ไปยัง"
    # ชื่อผู้รับ (รองรับคำนำหน้า เช่น น.ส. / นาย / นาง)
    receiver_name_match = re.search(r'ไปที่\s*((?:[นสย]\.?\s*)?(?:[\u0E00-\u0E7F\.]+\s*){1,4}?)(?=\s*(กสิกรไทย|กรุงไทย|ไทยพาณิชย์|ออมสิน|กรุงเทพ|tmb|ธนาคาร|xxx|x-))',text)
    receiver_name = receiver_name_match.group(1).strip() if receiver_name_match else 'ไม่พบชื่อผู้รับ'


    # ใช้ re เพื่อจับเลขบัญชีผู้รับจากคำว่า "ไปยัง" (เลขบัญชีผู้รับก็อาจมีช่องว่างหรือขีดกลาง)
    receiver_acc_match = re.search(r'ไปที่.*?((?:\d{3}-?\d{1,4})|(?:\d{9,12}))', text)
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

            # Route to handler using if-elif
            if bank == 'kbank':
                handle_kbank(text)
            elif bank == 'krungthai':
                handle_krungthai(text)
            elif bank == 'scb':
                handle_scb(text)
            elif bank == 'bangkok':
                handle_bangkok(text)
            elif bank == 'gsb':
                handle_gsb(text)
            else:
                handle_unknown(text)

if __name__ == '__main__':
    main()
