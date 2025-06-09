from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from db import get_connection
from datetime import datetime, date
from utils import generate_claim_inisiator, tambah_hari_kerja, mask_pan
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
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
    
    return render_template('index.html', menu='home', submenu='home')

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
        cursor.execute("SELECT * FROM tb_user WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and password == user[2]:
            # if check_password_hash(user[2], password):
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash('Login successful!', 'success')
            return redirect(url_for('klaim.index'))
        else:
            flash('Invalid username or password', 'danger')
    
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
        "Waiting Approve": "bg-primary",
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
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_claim")
    claims = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('claim.html', menu='master', submenu='claim' , data=claims, status_class=status_class)


@klaim_bp.route('/update_claim/<int:claim_id>', methods=['GET', 'POST'])
@login_required
def update(claim_id):
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tb_claim WHERE claim_id = %s", (claim_id,))
    claim = cursor.fetchone()
    
    if request.method == 'POST':
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
        user = request.form['user']
        reference = request.form['reference']
        week_report = request.form['week_report']
        close_claim = request.form['close_claim']
        bin = request.form['bin']
        routing = request.form['routing']
        claim_entry_boa = request.form['claim_entry_boa']
        remarks = request.form['remarks']

        # Update query
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
                user=%s,
                reference=%s,
                week_report=%s,
                close_claim=%s,
                bin=%s,
                routing=%s,
                claim_entry_boa=%s,
                remarks=%s
            WHERE claim_id=%s
        """, 
            (claim_status, claim_number, claim_inisiator, claim_type, terminal,
            no_acq, no_pan, no_receipt, trx_date, trx_time, due_date, claim_date,
            trx_amount, description, user, reference, week_report, close_claim,
            bin, routing, claim_entry_boa, remarks, claim_id
            ))
        conn.commit()
        
        flash('Claim updated successfully!', 'success')
        return redirect(url_for('klaim.claim'))
    
    cursor.close()
    conn.close()

    if not claim:
        flash("Data not Found.")
        return redirect(url_for('claim'))
    
    for field in ['trx_date', 'due_date', 'claim_date', 'close_claim']:
        if isinstance(claim[field], (datetime, date)):
            claim[field] = claim[field].strftime('%Y-%m-%d')
    if claim['trx_time']:
        claim['trx_time'] = str(claim['trx_time'])[:5]

    return render_template('update.html', claim=claim)


@klaim_bp.route('/delete_claim/<int:claim_id>', methods=['POST'])
@login_required
def delete_claim(claim_id):
    if session.get('role') != 'admin':
        return "Unauthorized access!", 403
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tb_claim WHERE id = %s", (claim_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Claim deleted successfully!', 'success')
    return redirect(url_for('pending'))

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

    # # Masking Pan jika Closed saja
    # for klaim in form_claim:
    #     if klaim['status_klaim'] in ['Closed by Acquirer', 'Reject', 'Closed Success']:
    #         klaim['no_pan'] = mask_pan(klaim['no_pan'])

    return render_template(
        'formclaim.html',
        menu='master',
        submenu='formclaim',
        next_claim_id=next_id,
        users=users,
        current_user=current_user
    )

@klaim_bp.route('/saveformclaim', methods=['POST'])
@login_required
def saveformclaim():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    tipe_klaim_options = ["Pro-active Claim", "Web Claim AJ", "Web Claim", "Web Claim CCTV", "Web Claim CCTV AJ"]
    status_options = ["Closed by Acquirer", "Reject", "Already Web Claim", "Closed Success", "Active", "Closed by System", "Already Email Claim", "Already Pro-active", "Cancelled by Acquirer", "On Process", "Not Yet Inputted","Process on Next Day","Change to be re-active","Rejected by Acquirer", "Pending Investigastion", "Waiting Approve", "Cancelled by ALTO", "Cross Check"]
    
    print(request.form)
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
    user = request.form['user']
    reference = request.form['reference']
    week_report = request.form['week_report']
    close_claim = request.form['close_claim']
    bin = request.form['bin']
    routing = request.form['routing']
    claim_entry_boa = request.form['claim_entry_boa']
    remarks = request.form['remarks']

    if claim_type == "Pro-active Claim":
        claim_inisiator = generate_claim_inisiator(claim_type, claim_date)
        due_date = tambah_hari_kerja(claim_date, 3)
    else:
        claim_inisiator = request.form['claim_inisiator']

    conn = get_connection()
    cursor = conn.cursor()
    # Check if the claim number already exists
    cursor.execute("INSERT INTO tb_claim(claim_status,claim_number,claim_inisiator,claim_type,terminal,no_acq,no_pan,no_receipt,trx_date,trx_time,due_date,claim_date,trx_amount,description,user,reference,week_report,close_claim,bin,routing,claim_entry_boa,remarks) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (claim_status,claim_number,claim_inisiator,claim_type,terminal,no_acq,no_pan,no_receipt,trx_date,trx_time,due_date,claim_date,trx_amount,description,user,reference,week_report,close_claim,bin,routing,claim_entry_boa,remarks))
    conn.commit()
    cursor.close()
    return redirect (url_for('klaim.formclaim', success='true', tipe_klaim_options=tipe_klaim_options, status_options=status_options))

@klaim_bp.route('/pending')
@login_required
def pending():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    conn = get_connection()
    cursor = conn.cursor()
    excluded_claim_status = (
        'solved',
        'reject',
        'close by acq',
        'close by system',
        'close success',
        'rejected by acq',
        'cancelled by alto'
    )

    # query SQL dengan kondisi NOT IN
    placeholders = ', '.join(['%s'] * len(excluded_claim_status))
    query = f"""
        SELECT * FROM tb_claim
        WHERE LOWER(claim_status) NOT IN ({placeholders})
    """

    cursor.execute(query, excluded_claim_status)
    claim = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('pending.html', menu='master', submenu='pending', data=claim, status_class=status_class)

@klaim_bp.route('/report')
@login_required
def report():
    if 'logged_in' not in session:
        return redirect(url_for('klaim.login'))
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_claim")
    claim = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('report.html', menu='master', submenu='report', data=claim, status_class=status_class)

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
    
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tb_user (username, password, role) VALUES (%s, %s, %s)", (username, generate_password_hash(password), role))
    conn.commit()
    cursor.close()
    conn.close()

    flash('User added successfully!', 'success')
    return redirect(url_for('klaim.add_user'))


@klaim_bp.route('/logout')
@login_required 
def logout():
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
    df = pd.read_sql("SELECT * FROM tb_claim", conn)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
    output.seek(0)
    conn.close()
    return send_file(output, attachment_filename=f'klaim_data.xlsx', as_attachment=True)



