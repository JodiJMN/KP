from datetime import datetime, timedelta, date
from db import get_connection
from flask_mail import Message
from flask import current_app
import locale

def get_due_reminder_claims():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    today = date.today()
    besok = today + timedelta(days=1)

    query = """
        SELECT claim_number, due_date
        FROM tb_claim
        WHERE due_date <= %s
        AND claim_status NOT IN ('Solved', 'Closed', 'Close Success', 'Rejected by ACQ', 'Cancelled by ALTO')
        ORDER BY due_date ASC
    """
    cursor.execute(query, (besok,))
    results = cursor.fetchall()
    
    # Pastikan due_date adalah objek date sebelum dikembalikan
    for row in results:
        if isinstance(row['due_date'], str):
            row['due_date'] = datetime.strptime(row['due_date'], '%Y-%m-%d').date() # Konversi jika string
        elif isinstance(row['due_date'], datetime):
            row['due_date'] = row['due_date'].date()

    cursor.close()
    conn.close()
    return results

def send_due_reminder_email(mail, recipients):
    with current_app.app_context():
        claims = get_due_reminder_claims()
        if not claims:
            return

        body = "🔔 Berikut daftar klaim yang akan due besok atau sudah lewat:\n\n"
        for claim_data in claims:
            claim_number = claim_data['claim_number']
            due_date = claim_data['due_date']
            
            status = "TERLEWAT" if due_date < date.today() else "H-1"
            body += f"- {claim_number} (Due: {due_date}, Status: {status})\n"

        msg = Message(subject="⚠️ Reminder Klaim Due Date",
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=recipients)
        msg.body = body
        mail.send(msg)
        

def generate_claim_inisiator(claim_type, claim_date):
    if claim_type != "Pro-active Claim":
        return ""

    # Pastikan claim_date adalah datetime.date
    if isinstance(claim_date, str):
        try:
            claim_date_obj = datetime.strptime(claim_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Format claim_date harus 'YYYY-MM-DD'")
    elif isinstance(claim_date, datetime):
        claim_date_obj = claim_date.date()
    else:
        claim_date_obj = claim_date  # diasumsikan sudah date

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Lock table untuk mencegah race condition saat generate nomor urut
        cursor.execute("LOCK TABLES tb_claim WRITE;")

        # Ambil claim_inisiator terakhir secara global (bukan per tanggal)
        # prefix = claim_date_obj.strftime("%y/%m/%d")
        cursor.execute(
            "SELECT claim_inisiator FROM tb_claim WHERE claim_inisiator LIKE %s ORDER BY claim_id DESC LIMIT 1",
            ('%/ATMi-Klaim/%',)
        )
        last = cursor.fetchone()

        if last:
            last_claim_inisiator = last[0]  # contoh: '004204/ATMi-Klaim/22/05/25'
            last_number_str = last_claim_inisiator.split('/')[0]
            last_number = int(last_number_str)
            next_number = last_number + 1
        else:
            next_number = 1

        nomor_urut_str = str(next_number).zfill(6)
        tanggal = claim_date_obj.strftime("%y/%m/%d")
        claim_inisiator = f"{nomor_urut_str}/ATMi-Klaim/{tanggal}"

        cursor.execute("UNLOCK TABLES;")
    finally:
        cursor.close()
        conn.close()

    return claim_inisiator

def tambah_hari_kerja(tanggal, hari_kerja):
    if isinstance(tanggal, str):
        tanggal = datetime.strptime(tanggal, '%Y-%m-%d').date()

    hasil = tanggal
    while hari_kerja > 0:
        hasil += timedelta(days=1)
        if hasil.weekday() < 5:
            hari_kerja -= 1
    return hasil

def mask_pan(pan):
    pan = str(pan)
    if len(pan) >= 10:
        return pan[:6] + '*' * (len(pan) - 10) + pan[-4:]
    return pan

def log_activity(user_id, username, action):
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO tb_log (user_id, username, action, timestamp) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (user_id, username, action, datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()
    
def get_due_soon_claims():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    today = date.today()
    besok = today + timedelta(days=1)

    # Cek klaim yang due hari ini atau H-1 (besok)
    cursor.execute("""
        SELECT claim_id, claim_number, due_date, claim_status
        FROM tb_claim
        WHERE due_date IN (%s, %s)
        AND claim_status NOT IN ('Solved', 'Closed', 'Close Success', 'Reject', 'Cancelled by ALTO', 'Rejected by ACQ')
        ORDER BY due_date ASC
    """, (today, besok))

    data = cursor.fetchall()
    for row in data:
        if isinstance(row['due_date'], str):
            row['due_date'] = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
        elif isinstance(row['due_date'], datetime):
            row['due_date'] = row['due_date'].date()
    cursor.close()
    conn.close()

    return data

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
def format_rupiah(amount):
    if amount is None:
        return "Rp 0" # Atau string kosong jika Anda prefer
    try:
        # Cek apakah angka memiliki bagian desimal non-nol
        if amount == int(amount): # Jika angka bulat (misal 200000.0 atau 200000)
            return f"Rp {int(amount):,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
        else: # Jika memiliki desimal (misal 12345.67)
            # Anda bisa tentukan berapa digit desimal yang diinginkan
            return f"Rp {amount:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
    except Exception as e:
        print(f"Error formatting rupiah: {e}")
        return f"Rp {str(amount)}" # Fallback