from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify, make_response
from db import get_connection
from datetime import datetime, date, timedelta, time
from utils import generate_claim_inisiator, tambah_hari_kerja, mask_pan, log_activity, send_due_reminder_email
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_mail import Mail
from datetime import datetime,date
from init import mail, bcrypt
import pandas as pd
import io


klaim_bp = Blueprint('klaim', __name__)

# Parameter harus login untuk akses ke index
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please login first!', 'danger')
            return redirect(url_for('klaim.login'))
        return f(*args, **kwargs)
    return decorated_function

# Parameter khusus akses admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please login first!', 'danger')
            return redirect(url_for('klaim.login'))
        if session.get('role') != 'admin':
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('klaim.index'))
        return f(*args, **kwargs)
    return decorated_function

@klaim_bp.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Ambil total klaim per status
    cursor.execute("SELECT claim_status, COUNT(*) as total FROM tb_claim GROUP BY claim_status")
    status_counts = cursor.fetchall()
    status_counts = {row['claim_status']: row['total'] for row in status_counts}

    # Ambil total klaim per tipe
    cursor.execute("SELECT claim_type, COUNT(*) as total FROM tb_claim GROUP BY claim_type")
    type_counts = cursor.fetchall()
    type_counts = {row['claim_type']: row['total'] for row in type_counts}

    cursor.close()
    conn.close()

    # Default nilai 0 jika tidak ada status tersebut
    return render_template('index.html',
                           menu='home',
                           submenu='home',
                           active_count=status_counts.get("Active", 0),
                           notyet_count=status_counts.get("Not Yet Inputted", 0),
                           pending_count=status_counts.get("Pending", 0),
                           cancelled_count=status_counts.get("Cancelled", 0),
                           rejected_count=status_counts.get("Reject", 0),
                           onprocess_count=status_counts.get("On Process", 0),
                           closed_count=status_counts.get("Closed", 0),
                           wait_approval_count=status_counts.get("Waiting Approval", 0),
                           status_counts=status_counts)

@klaim_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("Username dan password wajib diisi.")
            return redirect(url_for('login'))
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, password, role FROM tb_user WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # print("Input password:", password)
        # print(bcrypt.generate_password_hash(password))
        # print("Stored hash:", user[2])
        # print("Cocok?:", bcrypt.check_password_hash(user[2], password))
        
        if user and bcrypt.check_password_hash(user[2], password):
            session.permanent = True
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            log_activity(user[0], user[1], "Login berhasil")
            return redirect(url_for('klaim.index'))
        else:
            flash('Username atau password salah', 'danger')
            return redirect(url_for('klaim.login'))
    
    return render_template('login.html')

def status_class(status):
    status_map = {
        "Solved": "bg-primary",
        "Reject": "bg-danger",
        "Rejected by Acq": "bg-danger",
        "Closed by Acquirer": "bg-secondary",
        "Closed Success": "bg-success",
        "Already Web Claim": "bg-info",
        "Already Email Claim": "bg-info",
        "Already Pro-Active": "bg-info",
        "Cancelled by Acq": "bg-dark",
        "Cancelled by ALTO": "bg-dark",
        "On Process": "bg-warning",
        "Not Yet Inputed": "bg-warning",
        "Process on Next Day": "bg-warning",
        "Change to be Re-Active": "bg-warning",
        "Pending Investigation": "bg-primary",
        "Waiting Approval": "bg-primary",
        "Waiting Reject": "bg-primary",
        "Duplicate/Double": "bg-light text-dark",
        "Crosscheck": "bg-warning",
        "Close by System": "bg-secondary",
        "Active": "bg-success",
        "admin": "bg-danger",
        "user": "bg-primary",
    }
    return status_map.get(status, "bg-light text-dark")

@klaim_bp.route('/claim')
@login_required
def claim():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    # ambil parameter dari URL
    selected_status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 10  # jumlah klaim per halaman
    # search = request.args.get('search', '').lower()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil semua status unik untuk dropdown
    cursor.execute("SELECT DISTINCT claim_status FROM tb_claim")
    all_status = [row['claim_status'] for row in cursor.fetchall()]

    if selected_status:
        cursor.execute("SELECT * FROM tb_claim WHERE(claim_status) = %s ORDER BY claim_id DESC", 
                       (selected_status,))
    else:
        cursor.execute("SELECT * FROM tb_claim ORDER BY claim_id DESC")

    claims = cursor.fetchall()


    # Mask PAN
    for claim_row in claims: # Ganti 'claim' dengan 'claim_row' untuk menghindari konflik nama variabel
        if 'no_pan' in claim_row and claim_row['no_pan'] is not None:
            claim_row['no_pan'] = mask_pan(claim_row['no_pan'])
        
        for field in ['trx_date', 'due_date', 'claim_date', 'close_claim']:
            if field in claim_row and isinstance(claim_row[field], (datetime, date)):
                claim_row[field] = claim_row[field].strftime('%Y-%m-%d')
            elif field in claim_row and claim_row[field] is None:
                claim_row[field] = "" # Ganti None dengan string kosong untuk konsistensi

        if 'trx_time' in claim_row and claim_row['trx_time'] is not None:
            if isinstance(claim_row['trx_time'], time):
                claim_row['trx_time'] = claim_row['trx_time'].strftime('%H:%M:%S')
            elif isinstance(claim_row['trx_time'], timedelta): # <--- TANGANI TIMEDELTA DI SINI
                # Konversi timedelta menjadi HH:MM:SS string
                total_seconds = int(claim_row['trx_time'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                claim_row['trx_time'] = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                # Fallback jika sudah string tapi tidak sesuai format
                claim_row['trx_time'] = str(claim_row['trx_time'])
        elif 'trx_time' in claim_row and claim_row['trx_time'] is None:
            claim_row['trx_time'] = "" # Ganti None dengan string kosong

        # Untuk approved_at (jika ada dan mungkin juga datetime object)
        if 'approved_at' in claim_row and isinstance(claim_row['approved_at'], datetime):
            claim_row['approved_at'] = claim_row['approved_at'].strftime('%Y-%m-%d %H:%M:%S')
        elif 'approved_at' in claim_row and claim_row['approved_at'] is None:
            claim_row['approved_at'] = ""
            
    # Pagination
    total_claims = len(claims)
    start_page = (page - 1) * per_page
    end = start_page + per_page
    claims_paginated = claims[start_page:end]
    
    cursor.close()
    conn.close()
    
    return render_template('claim.html', 
                           data = claims_paginated,
                           all_status = all_status,
                           selected_status = selected_status,
                           page = page,
                           per_page = per_page,
                           total_claims = total_claims,
                           status_class = status_class,
                           mask_pan = mask_pan)
                           

@klaim_bp.route('/update_claim/<int:claim_id>', methods=['GET', 'POST'])
@login_required
def update(claim_id):
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tb_claim WHERE claim_id = %s", (claim_id,))
    claim = cursor.fetchone()
    
    if not claim:
        flash("Data not found", "danger")
        return redirect(url_for('klaim.claim'))

    # Daftar status yang tidak bisa di-update/diedit oleh non-admin atau jika sedang menunggu approval
    restricted_statuses_for_edit = ["Not Yet Inputted", "On Process", "Waiting Reject", "Waiting Approval"]

    # Logika untuk GET request (saat menampilkan form update)
    if request.method == 'GET':
        # Jika bukan admin DAN status klaim ada di daftar restricted
        if session['role'] != 'admin' and claim['claim_status'] in restricted_statuses_for_edit:
            flash(f"Klaim dengan status '{claim['claim_status']}' tidak dapat diedit sebelum disetujui admin.", 'danger')
            return redirect(url_for('klaim.claim')) # Atau tampilkan halaman detail read-only

        # ... sisa kode GET request seperti sebelumnya ...
        # Pastikan Anda mengirimkan `claim` yang diformat ke `update.html`
        for field in ['trx_date', 'due_date', 'claim_date', 'close_claim']:
            if isinstance(claim[field], (datetime, date)):
                claim[field] = claim[field].strftime('%Y-%m-%d')
        if claim['trx_time']:
            if isinstance(claim['trx_time'], time):
                claim['trx_time'] = claim['trx_time'].strftime('%H:%M:%S')
            else:
                claim['trx_time'] = str(claim['trx_time'])

        routing_options = ["ALTO", "ARTAJASA"]
        cursor.execute("SELECT DISTINCT error_code FROM tb_claim WHERE error_code IS NOT NULL ORDER BY error_code ASC")
        # Menggunakan list comprehension untuk mendapatkan nilai saja
        db_error_codes = [str(row['error_code']) for row in cursor.fetchall()]
        
        # Tambahkan error codes statis jika ada yang tidak ada di DB tapi ingin tetap muncul
        static_error_codes = [
            "E*2 M-00", "E*2 M-10", "E*2 M-13", "E*3 M-13", "E*3 M-14",
            "E*4 M-00", "E*4 M-13", "E*4 M-19", "E*5 M-00, PRESENTER ERROR",
            "Host Timeout", "D*0 M-18, D*2 M-18, Host Timeout",
            "D*0 M-13, D*2 M-13, Host Timeout", "Power Interruption"
        ]
        
        error_code_options = sorted(list(set(db_error_codes + static_error_codes)))
        type_klaim_options = ["Pro-active Claim", "Web Claim AJ", "Web Claim"]
        boa_entry_options = ["Solved", "On Process", "Rejected"]
        status_options = ["Solved", "Reject", "Closed by Acquirer", "Already Web Claim", "Closed Success",
                          "Active", "Close by System", "Already Email Claim", "Already Pro-Active", "Cancelled by Acq",
                          "On Process", "Not Yet Inputed", "Process on Next Day", "Change to be Re-Active",
                          "Rejected by Acq", "Pending Investigation", "Waiting Approval", "Waiting Reject",
                          "Cancelled by ALTO", "Duplicate/Double", "Crosscheck"]

        log_activity(session['user_id'], session['username'], f"Melihat form update klaim ID {claim_id}")

        return render_template('update.html', claim=claim, routing_options=routing_options,error_code_options=error_code_options,
                               boa_entry_options=boa_entry_options, status_options=status_options, type_klaim_options=type_klaim_options)

    elif request.method == 'POST':
        # Re-fetch claim status to ensure it's current before processing update
        cursor.execute("SELECT claim_status FROM tb_claim WHERE claim_id = %s", (claim_id,))
        current_claim_status_from_db = cursor.fetchone()['claim_status']

        if session['role'] != 'admin' and current_claim_status_from_db in restricted_statuses_for_edit:
            flash(f"Tidak dapat mengubah klaim dengan status '{current_claim_status_from_db}'. Mohon tunggu persetujuan admin.", 'danger')
            return redirect(url_for('klaim.claim'))
        # Jika klaim sudah dalam status Waiting Approval, tidak bisa diubah
        # Ambil semua input
        claim_status = request.form['claim_status']
        claim_number = request.form['claim_number']
        claim_inisiator = request.form['claim_inisiator']
        claim_type = request.form['claim_type']
        terminal = request.form['terminal']
        no_acq = request.form['no_acq']
        no_pan = request.form['no_pan']
        no_receipt = request.form['no_receipt']
        trx_date = request.form['trx_date']
        trx_time = request.form['trx_time']
        due_date = request.form['due_date']
        claim_date = request.form['claim_date']
        trx_amount = request.form['trx_amount']
        description = request.form['description']
        user_id = session.get('user_id')  # Ambil user_id dari session
        user = request.form['user']
        reference = request.form['reference']
        week_report = request.form['week_report']
        close_claim = request.form['close_claim']
        bin = request.form['bin']
        error_code = request.form['error_code']
        routing = request.form['routing']
        claim_entry_boa = request.form['claim_entry_boa']
        remarks = request.form['remarks']
        current_claim_status = claim['claim_status'] # Ambil status klaim saat ini dari database
        new_claim_status = request.form['claim_status'] # Ambil status dari form
        
        # Anda perlu mendefinisikan status mana yang eligible untuk berubah ke Waiting Approval
        # Contoh: Jika status sebelumnya bukan yang sudah final/ditolak, dan deskripsi diisi
        if description and description.strip() != "": # Pastikan deskripsi tidak kosong
             # Anda bisa menambahkan kondisi peran di sini jika hanya user tertentu yang memicu 'Waiting Approval'
            if session['role'] == 'user': # Contoh: Hanya user biasa yang memicu Waiting Approval
                 # Asumsi admin bisa langsung set status final
                new_claim_status = "Waiting Approval"
            # else: # Jika admin, biarkan status dari form
            #     new_claim_status = request.form['claim_status']

        cursor.execute("""
            UPDATE tb_claim SET 
                claim_status=%s,
                claim_number=%s,
                claim_inisiator=%s,
                claim_type=%s,
                terminal=%s,
                no_acq=%s,
                no_pan=%s,
                no_receipt=%s,
                trx_date=%s,
                trx_time=%s,
                due_date=%s,
                claim_date=%s,
                trx_amount=%s,
                description=%s,
                user_id=%s,
                user=%s,
                reference=%s,
                week_report=%s,
                close_claim=%s,
                bin=%s,
                error_code=%s,
                routing=%s,
                claim_entry_boa=%s,
                remarks=%s
            WHERE claim_id=%s
        """, (
            new_claim_status, claim_number, claim_inisiator, claim_type, terminal,
            no_acq, no_pan, no_receipt, trx_date, trx_time, due_date, claim_date,
            trx_amount, description, user_id, user, reference, week_report, close_claim,
            bin,error_code, routing, claim_entry_boa, remarks, claim_id
        ))
        conn.commit()
        flash('Claim updated successfully!', 'success')
        log_activity(session['user_id'], session['username'], f"Update klaim ID {claim_id} menjadi status {new_claim_status}")

        # Refresh data claim lagi setelah update
        cursor.execute("SELECT * FROM tb_claim WHERE claim_id = %s", (claim_id,))
        claim = cursor.fetchone()

        # Format tanggal dan waktu
        for field in ['trx_date', 'due_date', 'claim_date', 'close_claim']:
            if isinstance(claim[field], (datetime, date)):
                claim[field] = claim[field].strftime('%Y-%m-%d')
        if claim['trx_time']:
            claim['trx_time'] = str(claim['trx_time'])[:5]

        # List tambahan jika ada
        routing_options = ["ALTO", "ARTAJASA"]
        boa_entry_options = ["Solved", "On Process", "Rejected"]
        status_options = ["Solved", "Reject", "Closed by Acquirer", "Already Web Claim", "Closed Success",
                          "Active", "Close by System", "Already Email Claim", "Already Pro-Active", "Cancelled by Acq",
                          "On Process", "Not Yet Inputed", "Process on Next Day", "Change to be Re-Active", 
                          "Rejected by Acq", "Pending Investigation", "Waiting Approval", "Waiting Reject", 
                          "Cancelled by ALTO", "Duplicate/Double", "Crosscheck"]
        type_klaim_options = ["Pro-active Claim", "Web Claim AJ", "Web Claim"]

        return render_template('update.html', claim=claim, routing_options=routing_options, type_klaim_options=type_klaim_options,
                               boa_entry_options=boa_entry_options, status_options=status_options)

    cursor.close()
    conn.close()

    # GET (pertama kali buka halaman)
    if not claim:
        flash("Data not found", "danger")
        return redirect(url_for('klaim.claim'))

    for field in ['trx_date', 'due_date', 'claim_date', 'close_claim']:
        if isinstance(claim[field], (datetime, date)):
            claim[field] = claim[field].strftime('%Y-%m-%d')
    if claim['trx_time']:
    # Jika trx_time adalah datetime.time object, gunakan strftime
        if isinstance(claim['trx_time'],time):
            claim['trx_time'] = claim['trx_time'].strftime('%H:%M:%S')
        else: # Jika sudah string, pastikan formatnya benar atau tidak diubah
            claim['trx_time'] = str(claim['trx_time']) # Contoh: '09:31:00'

    routing_options = ["ALTO", "ARTAJASA"]
    type_klaim_options = ["Pro-active Claim", "Web Claim AJ", "Web Claim"]
    boa_entry_options = ["Solved", "On Process", "Rejected"]
    status_options = ["Solved", "Reject", "Closed by Acquirer", "Already Web Claim", "Closed Success",
                      "Active", "Close by System", "Already Email Claim", "Already Pro-Active", "Cancelled by Acq",
                      "On Process", "Not Yet Inputed", "Process on Next Day", "Change to be Re-Active", 
                      "Rejected by Acq", "Pending Investigation", "Waiting Approval", "Waiting Reject", 
                      "Cancelled by ALTO", "Duplicate/Double", "Crosscheck"]

    log_activity(session['user_id'], session['username'], f"Update klaim ID {claim_id}")

    return render_template('update.html', claim=claim, routing_options=routing_options,
                           boa_entry_options=boa_entry_options, status_options=status_options, type_klaim_options=type_klaim_options)


@klaim_bp.route('/delete_claim/<int:claim_id>', methods=['POST'])
@login_required
def delete_claim(claim_id):
    if session.get('role') != 'admin':
        return "Unauthorized access!", 403
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tb_claim WHERE claim_id = %s", (claim_id,))
    conn.commit()
    cursor.close()
    conn.close()
    log_activity(session['user_id'], session['username'], f"Hapus klaim ID {claim_id}")
    flash('Claim deleted successfully!', 'success')
    return redirect(url_for('klaim.claim'))

@klaim_bp.route('/formclaim')
@login_required
def formclaim():
    conn = get_connection()
    cursor = conn.cursor()
    current_user = session.get('username')
    cursor.execute("SELECT MAX(claim_id) FROM tb_claim")
    last_id = cursor.fetchone()[0] or 0
    next_id = last_id + 1

    cursor.execute("SELECT * FROM tb_user")
    users = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    tipe_klaim_options = ["Pro-active Claim", "Web Claim AJ", "Web Claim", "Web Claim CCTV", "Web Claim CCTV AJ"]
    status_options = ["Closed by Acquirer", "Reject", "Already Web Claim", "Closed Success", "Active", "Closed by System", "Already Email Claim", "Already Pro-active", "Cancelled by Acquirer", "On Process", "Not Yet Inputted","Process on Next Day","Change to be re-active","Rejected by Acquirer", "Pending Investigastion", "Waiting Approval", "Cancelled by ALTO", "Cross Check"]

    return render_template(
        'formclaim.html',
        menu='master',
        submenu='formclaim',
        next_id=next_id,
        tipe_klaim_options=tipe_klaim_options,
        users=users,
        claim=claim,
        current_user=current_user,
        status_options=status_options
    )

@klaim_bp.route('/saveformclaim', methods=['POST'])
@login_required
def saveformclaim():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    tipe_klaim_options = ["Pro-active Claim", "Web Claim AJ", "Web Claim", "Web Claim CCTV", "Web Claim CCTV AJ"]
    status_options = ["Closed by Acquirer", "Reject", "Already Web Claim", "Closed Success", "Active", "Closed by System", "Already Email Claim", "Already Pro-active", "Cancelled by Acquirer", "On Process", "Not Yet Inputted","Process on Next Day","Change to be re-active","Rejected by Acquirer", "Pending Investigastion", "Waiting Approval", "Cancelled by ALTO", "Cross Check"]
    
    print(request.form)
    claim_id = request.form['claim_id']
    claim_status = request.form['claim_status']
    claim_number = request.form['claim_number']
    claim_inisiator = request.form['claim_inisiator']
    claim_type = request.form['claim_type']
    terminal = request.form['terminal']
    no_acq = request.form['no_acq']
    no_pan = request.form['no_pan']
    no_receipt = request.form['no_receipt']
    trx_date = request.form['trx_date']
    trx_time = request.form['trx_time']
    due_date = request.form['due_date']
    claim_date = request.form['claim_date']
    trx_amount = request.form['trx_amount']
    description = request.form['description']
    user_id = session['user_id']
    user = request.form['user']
    reference = request.form['reference']
    week_report = request.form['week_report']
    close_claim = request.form['close_claim']
    bin = request.form['bin']
    error_code = request.form['error_code']
    routing = request.form['routing']
    claim_entry_boa = request.form['claim_entry_boa']
    remarks = request.form['remarks']
    
    if session['role'] == 'user':
        if claim_type == "Pro-active Claim":
            claim_status = "Not Yet Inputted"
        elif claim_type in ["Web Claim", "Web Claim AJ"]:
            claim_status = "On Process"
    else: 
        # Fallback jika claim_type tidak cocok dengan aturan di atas
        # Anda bisa mempertahankan nilai dari form jika tidak ada aturan khusus,
        # atau set default lain jika ingin lebih ketat.
        claim_status = request.form['claim_status'] # Ambil dari form jika tidak ada aturan otomatis

    if claim_type == "Pro-active Claim":
        claim_inisiator = generate_claim_inisiator(claim_type, claim_date)
        due_date = tambah_hari_kerja(claim_date, 3)
    else:
        claim_inisiator = request.form['claim_inisiator']
        # Pastikan due_date juga dihandle untuk non-Pro-active claim
        # Anda mungkin perlu mengambil due_date dari form jika tidak otomatis
        due_date = request.form['due_date'] # Pastikan Anda punya input 'due_date' di formclaim.html

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tb_claim(claim_status, claim_number, claim_inisiator, claim_type, terminal, no_acq, no_pan, no_receipt, trx_date, trx_time, due_date, claim_date, trx_amount, description, user_id, user, reference, week_report, close_claim, bin, error_code, routing, claim_entry_boa, remarks)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            claim_status, claim_number, claim_inisiator, claim_type, terminal,
            no_acq, no_pan, no_receipt, trx_date, trx_time, due_date, claim_date,
            trx_amount, description, user_id, user, reference, week_report,
            close_claim, bin, error_code, routing, claim_entry_boa, remarks
        )
    )
    log_activity(session['user_id'], session['username'], f"Menambah klaim baru ID {claim_id} dengan status {claim_status}") # Perbarui pesan log
    conn.commit()
    cursor.close()
    conn.close()
    flash('Claim added successfully!', 'success') # Ubah pesan flash
    return redirect (url_for('klaim.formclaim', success='true'))

@klaim_bp.route('/pending')
@login_required
def pending():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True) # Sudah benar

    page = int(request.args.get('page', 1))
    per_page = 10
    selected_status = request.args.get('status', '')

    excluded_statuses = [
        'solved', 'reject', 'close by acq', 'close by system',
        'close success', 'rejected by acq', 'cancelled by alto'
    ]
    
    status_options = [
        "Solved", "Reject", "Closed by Acquirer", "Already Web Claim", "Closed Success", "Active",
        "Close by System", "Already Email Claim", "Already Pro-Active", "Cancelled by Acq", "On Process",
        "Not Yet Inputed", "Process on Next Day", "Change to be Re-Active", "Rejected by Acq",
        "Pending Investigation", "Waiting Approval", "Waiting Reject", "Cancelled by ALTO", "Duplicate/Double", "Crosscheck"
    ]

    # Bangun query dasar
    base_query = """
        SELECT * FROM tb_claim
        WHERE LOWER(claim_status) NOT IN ({})
    """.format(', '.join(['%s'] * len(excluded_statuses)))
    base_params = [s.lower() for s in excluded_statuses] # Pastikan parameter juga lowercase

    # Tambahkan filter status jika ada
    if selected_status:
        # Jika ada selected_status, kita ingin menampilkan HANYA status itu
        # Jadi, kita tidak perlu lagi mengecualikan status yang sudah solved/rejected
        query_for_data = "SELECT * FROM tb_claim WHERE LOWER(claim_status) = %s"
        params_for_data = [selected_status.lower()]
    else:
        # Jika tidak ada selected_status, gunakan query dasar untuk 'pending'
        query_for_data = base_query
        params_for_data = base_params

    # Tambahkan ORDER BY
    query_for_data += " ORDER BY due_date ASC"

    cursor.execute(query_for_data, params_for_data)
    all_claims_for_pagination = cursor.fetchall() # Ambil semua data untuk paginasi dan highlight

    # --- Proses `due_date` dan `highlight_rows` di SINI ---
    today = date.today()
    tomorow = today + timedelta(days=1)
    highlight_rows = {}
    for row in all_claims_for_pagination: # Iterasi data yang sudah diambil
        # Konversi due_date jika masih string atau datetime.datetime
        if isinstance(row['due_date'], str):
            row['due_date'] = datetime.strptime(row['due_date'], '%Y-%m-%d').date()
        elif isinstance(row['due_date'], datetime):
            row['due_date'] = row['due_date'].date() # Ubah datetime object menjadi date object

        if row['due_date'] <= today:
            highlight_rows[row['claim_id']] = 'table-danger'
        elif row['due_date'] == tomorow:
            highlight_rows[row['claim_id']] = 'table-warning'
        else:
            highlight_rows[row['claim_id']] = ''

    # --- End Process Highlight ---

    # Ambil semua status unik untuk dropdown (ini bisa tetap terpisah atau juga difilter)
    # Anda sudah memiliki all_status dari tb_claim, ini baik
    cursor.execute("SELECT DISTINCT claim_status FROM tb_claim")
    all_status = [row['claim_status'] for row in cursor.fetchall()]

    # Pagination
    total = len(all_claims_for_pagination)
    start_page = (page - 1) * per_page
    end = start_page + per_page
    claims_paginated = all_claims_for_pagination[start_page:end]

    cursor.close()
    conn.close()

    return render_template(
        'pending.html',
        menu='master',
        submenu='pending',
        data=claims_paginated,
        page=page,
        per_page=per_page,
        total=total,
        all_status=all_status,
        selected_status=selected_status,
        status_class=status_class, # Pastikan fungsi ini tersedia di scope
        status_options=status_options,
        highlight_rows=highlight_rows,
    )

@klaim_bp.route('/report')
@login_required
def report():
    conn = get_connection()
    cursor = conn.cursor()

    selected_status = request.args.get("status", "")
    selected_type = request.args.get("type", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    query = "SELECT * FROM tb_claim WHERE 1=1"
    params = []

    if selected_status:
        query += " AND claim_status = %s"
        params.append(selected_status)

    if selected_type:
        query += " AND claim_type = %s"
        params.append(selected_type)

    if start_date and end_date:
        query += " AND claim_date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    cursor.execute(query, tuple(params))
    claim = cursor.fetchall()

    # ambil daftar status dan tipe unik untuk dropdown
    cursor.execute("SELECT DISTINCT claim_status FROM tb_claim")
    all_status = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT claim_type FROM tb_claim")
    all_types = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('report.html',
                           data=claim,
                           menu='master',
                           submenu='report',
                           all_status=all_status,
                           all_types=all_types,
                           selected_status=selected_status,
                           selected_type=selected_type,
                           start_date=start_date,
                           end_date=end_date,
                           status_class=status_class)

@klaim_bp.route('/userlist')
@login_required
@admin_required
def userlist():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tb_user")
    user = cur.fetchall()
    cur.close()
    return render_template('userlist.html', menu='user', submenu='addusers', data=user, status_class=status_class)

@klaim_bp.route('/adduser')
@login_required
@admin_required
def add_user():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(user_id) FROM tb_user")
    last_id = cursor.fetchone()[0] or 0
    next_id = last_id + 1
    cursor.close()
    conn.close()

    return render_template('adduser.html', menu='user', submenu='adduser', next_user_id=next_id)

@klaim_bp.route('/saveadduser', methods=['POST'])
@login_required
@admin_required
def saveadduser():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    user_id = request.form['user_id']
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute("INSERT INTO tb_user (user_id, username, password, role) VALUES (%s, %s, %s, %s)",
                   (user_id, username, hashed_password, role))

    conn.commit()
    cursor.close()
    conn.close()

    flash('User added successfully!', 'success')
    return redirect(url_for('klaim.add_user'))


@klaim_bp.route('/logout')
@login_required 
def logout():
    log_activity(session['user_id'], session['username'], "Logout")
    session.clear()
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('klaim.login'))

@klaim_bp.route('/contact')
@login_required
def contact():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    return render_template('contact.html', menu='master', submenu='contact')

@klaim_bp.route('/export')
def export_klaim():
    conn = get_connection()
    
    
    selected_status = request.args.get("status", "")
    selected_type = request.args.get("type", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    query = "SELECT * FROM tb_claim WHERE 1=1"
    params = []

    if selected_status:
        query += " AND claim_status = %s"
        params.append(selected_status)

    if selected_type:
        query += " AND claim_type = %s"
        params.append(selected_type)

    if start_date and end_date:
        query += " AND claim_date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    # Gunakan pd.read_sql dengan query dan params
    df = pd.read_sql(query, conn, params=params) # Sediakan params ke read_sql

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    output.seek(0)
    conn.close()

    return send_file(
        output,
        download_name='klaim_data_filtered.xlsx', # Ubah nama file agar jelas hasil filter
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@klaim_bp.route('/send_due_email')
def send_due_email():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('klaim.login'))

    from utils import send_due_reminder_email
    from init import mail

    try:
        # Daftar penerima email (ganti sesuai kebutuhan)
        recipients = ['jodijmn@email.com']
        send_due_reminder_email(mail, recipients)
        flash("Email berhasil dikirim!", "success")
    except Exception as e:
        flash(f"Gagal mengirim email: {str(e)}", "danger")

    return redirect(url_for('klaim.dashboard'))


@klaim_bp.route('/dashboard')
@login_required
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    if session['role'] == 'admin':
        # Email ke admin saja (bisa kamu sesuaikan)
        send_due_reminder_email(mail, ['jodijmn@gmail.com'])
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Ambil total klaim per status
    cursor.execute("SELECT claim_status, COUNT(*) as total FROM tb_claim GROUP BY claim_status")
    status_counts_result = cursor.fetchall()

    # Ubah ke bentuk dictionary
    status_counts = {row['claim_status']: row['total'] for row in status_counts_result}

    # Ambil total klaim per tipe untuk grafik pie / bar
    cursor.execute("SELECT claim_type, COUNT(*) as total FROM tb_claim GROUP BY claim_type")
    type_counts_result = cursor.fetchall()
    type_counts = {row['claim_type']: row['total'] for row in type_counts_result}

    cursor.close()
    conn.close()

    # Definisikan warna dan label box dashboard
    boxes = [
        ("Active", status_counts.get("Active", 0), "#00C853"),
        ("Not Yet Inputted", status_counts.get("Not Yet Inputted", 0), "#00BFA5"),
        ("Pending", status_counts.get("Pending", 0), "#FFEB3B"),
        ("Waiting Approval", status_counts.get("Waiting Approval", 0), "#F2BF26"),
        ("Cancelled", status_counts.get("Cancelled", 0), "#FF0000"),
        ("Rejected", status_counts.get("Reject", 0), "#0DC7B7"),
        ("On Process", status_counts.get("On Process", 0), "#F44336"),
        ("Closed", status_counts.get("Closed", 0), "#D605D2")
    ]

    # Untuk Chart
    chart_labels = list(type_counts.keys())
    chart_values = list(type_counts.values())
    active_count = status_counts.get("Active", 0)
    notyet_count = status_counts.get("Not Yet Inputted", 0)
    pending_count = status_counts.get("Pending", 0)
    wait_approval_count = status_counts.get("Waiting Approval", 0)
    cancelled_count = status_counts.get("Cancelled", 0)
    rejected_count = status_counts.get("Rejected", 0) or status_counts.get("Reject", 0)
    onprocess_count = status_counts.get("On Process", 0)
    closed_count = status_counts.get("Closed", 0)
    claims = []
    for label, count, color in boxes:
        try:
            claims.append({
                "label": str(label or "Unknown"),
                "count": int(count or 0),
                "color": str(color or "#CCCCCC")
            })
        except Exception as e:
            print(f"[WARNING] Gagal menambahkan ke claims: {label}, {count}, {color} ({e})")


    return render_template(
    'index.html',
    boxes=boxes,
    chart_labels=chart_labels,
    chart_values=chart_values,
    claims=claims,
    active_count=active_count,
    notyet_count=notyet_count,
    pending_count=pending_count,
    wait_approval_count=wait_approval_count,
    cancelled_count=cancelled_count,
    rejected_count=rejected_count,
    onprocess_count=onprocess_count,
    closed_count=closed_count,
    menu='home',
    submenu='home'
)
    
@klaim_bp.route('/status/<status>')
@login_required
def tickets_by_status(status):
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    selected_status = request.args.get('status', '')
    
    status_options = [
    "Solved", "Reject", "Closed by Acquirer", "Already Web Claim", "Closed Success", "Active",
    "Close by System", "Already Email Claim", "Already Pro-Active", "Cancelled by Acq", "On Process",
    "Not Yet Inputed", "Process on Next Day", "Change to be Re-Active", "Rejected by Acq",
    "Pending Investigation", "Waiting Approval", "Waiting Reject", "Cancelled by ALTO", "Duplicate/Double", "Crosscheck"
    ]
    
    cursor.execute("SELECT * FROM tb_claim WHERE claim_status = %s", (status,))
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template(
        'status_list.html', 
        data=data, 
        status_filter=status, 
        status_class=status_class, 
        selected_status=selected_status,
        status_options=status_options,
        menu='master',
        submenu='status_list'
        )

@klaim_bp.route('/generate_inisiator', methods=['POST'])
@login_required
def generate_inisiator():
    claim_type = request.json.get('claim_type')
    claim_date = request.json.get('claim_date')

    if not claim_type or not claim_date:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        nomor = generate_claim_inisiator(claim_type, claim_date)
        return jsonify({'claim_inisiator': nomor})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@klaim_bp.route('/update_pending_ajax', methods=['POST'])
@login_required
def update_pending_ajax():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tb_claim SET 
                claim_status=%s,
                claim_number=%s,
                description=%s,
                close_claim=%s,
                bin=%s,
                error_code=%s,
                claim_entry_boa=%s,
                remarks=%s
            WHERE claim_id=%s
        """, (
            request.form['claim_status'],
            request.form['claim_number'],
            request.form['description'],
            request.form['close_claim'],
            request.form['bin'],
            request.form['error_code'],
            request.form['claim_entry_boa'],
            request.form['remarks'],
            request.form['claim_id']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@klaim_bp.route('/log')
def view_log():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('klaim.login'))

    username_filter = request.args.get('username', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 🧠 Query dinamis
    query = "SELECT * FROM tb_log WHERE 1=1"
    params = []

    if username_filter:
        query += " AND username LIKE %s"
        params.append(f"%{username_filter}%")
    
    if start_date:
        query += " AND DATE(timestamp) >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND DATE(timestamp) <= %s"
        params.append(end_date)

    query += " ORDER BY timestamp DESC"

    cursor.execute(query, tuple(params))
    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('log.html', logs=logs,
                           username_filter=username_filter,
                           start_date=start_date,
                           end_date=end_date,
                           menu='admin', submenu='log')
    
    
@klaim_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pass = request.form['old_password']
        new_pass = request.form['new_password']
        confirm_pass = request.form['confirm_password']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM tb_user WHERE user_id = %s", (session['user_id'],))
        user = cursor.fetchone()

        if not user or not bcrypt.check_password_hash(user[0], old_pass):
            flash('Password lama salah', 'danger')
            return redirect(url_for('klaim.change_password'))

        if new_pass != confirm_pass:
            flash('Password baru tidak cocok', 'danger')
            return redirect(url_for('klaim.change_password'))

        hashed = bcrypt.generate_password_hash(new_pass).decode('utf-8')
        cursor.execute("UPDATE tb_user SET password = %s WHERE user_id = %s", (hashed, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Password berhasil diubah', 'success')
        return redirect(url_for('klaim.change_password'))

    return render_template('profile.html', menu='user', submenu='profile')

@klaim_bp.route('/approval')
@login_required
def approval_list():
    if session['role'] != 'admin':
        return redirect(url_for('klaim.dashboard'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tb_claim WHERE claim_status = 'Waiting Approval'")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('approval.html', data=data, menu='master', submenu='approval')

@klaim_bp.route('/approve_claim/<int:claim_id>', methods=['POST'])
@login_required
def approve_claim(claim_id):
    if session['role'] != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('klaim.dashboard'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tb_claim
        SET claim_status = 'Active',
            approved_by = %s,
            approved_at = NOW()
        WHERE claim_id = %s
    """, (session['username'], claim_id))

    conn.commit()
    cursor.close()
    conn.close()
    flash("Klaim berhasil di-approve", "success")
    return redirect(url_for('klaim.approval_list'))

@klaim_bp.route('/reject_claim/<int:claim_id>', methods=['POST'])
@login_required
@admin_required # Pastikan hanya admin yang bisa reject
def reject_claim(claim_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tb_claim
        SET claim_status = 'Reject',
            approved_by = %s,
            approved_at = NOW()
        WHERE claim_id = %s
    """, (session['username'], claim_id))

    conn.commit()
    cursor.close()
    conn.close()
    flash("Klaim berhasil di-reject.", "success")
    log_activity(session['user_id'], session['username'], f"Reject klaim ID {claim_id}")
    return redirect(url_for('klaim.approval_list'))

