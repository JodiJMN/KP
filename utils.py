from datetime import datetime, timedelta
import os
from db import get_connection

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
        cursor.execute(
            "SELECT claim_inisiator FROM tb_claim WHERE claim_inisiator LIKE %s ORDER BY id DESC LIMIT 1",
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
    if len(pan) >= 10:
        return pan[:6] + '*' * (len(pan) - 10) + pan[-4:]
    return pan

