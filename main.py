from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'atmi'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_claim'
mysql = MySQL(app)

# Parameter harus login untuk akses ke index
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            flash('Please login first!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Parameter khusus akses admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin'):
            flash('Please login first!', 'danger')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM tb_user WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if username and password == user['password']:
            session['loggedin'] = True
            session['user'] = user['username']
            session['role'] = user['role']
            flash('Login Success!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Wrong username or password!', 'danger')
            return redirect(url_for('login'))
    else:
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

@app.route('/claim')
@login_required
def claim():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_claim")
    claim = cur.fetchall()
    cur.close()
    return render_template('claim.html', menu='master', submenu='claim', data=claim,  status_class=status_class)

@app.route('/update/<int:claim_id>', methods=['GET', 'POST'])
@login_required
def update(claim_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        # Ambil data dari form        
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
        cur.execute("""
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
        """, (
            claim_status, claim_number, claim_inisiator, claim_type, terminal,
            no_acq, no_pan, no_receipt, trx_date, trx_time, due_date, claim_date,
            trx_amount, description, user, reference, week_report, close_claim,
            bin, routing, claim_entry_boa, remarks, claim_id
        ))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('claim'))

    # GET method: Tampilkan data lama ke form
    cur.execute("SELECT * FROM tb_claim WHERE claim_id=%s", (claim_id,))
    claim = cur.fetchone()
    cur.close()
    
    if not claim:
        flash("Data not Found.")
        return redirect(url_for('claim'))
    
    from datetime import datetime, date
    for field in ['trx_date', 'due_date', 'claim_date', 'close_claim']:
        if isinstance(claim[field], (datetime, date)):
            claim[field] = claim[field].strftime('%Y-%m-%d')
    if claim['trx_time']:
        claim['trx_time'] = str(claim['trx_time'])[:5]

    return render_template('update.html', claim=claim)



@app.route('/deleteclaim/<int:claim_id>', methods=['GET'])
@login_required
def delete_claim(claim_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403 

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tb_claim WHERE claim_id=%s", (claim_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('pending'))



@app.route('/formclaim')
@login_required
def formclaim():
    cur = mysql.connection.cursor()
    
    current_user = session.get('user')

    # Ambil next claim ID
    cur.execute("SELECT MAX(claim_id) FROM tb_claim")
    last_id = cur.fetchone()[0] or 0
    next_id = last_id + 1

    # Ambil daftar user dari tabel user
    cur.execute("SELECT user FROM tb_user")
    users = [row[0] for row in cur.fetchall()]

    cur.close()

    # Ambil user yang login dari session
    current_user = session.get('user')

    return render_template(
        'formclaim.html',
        menu='master',
        submenu='formclaim',
        next_claim_id=next_id,
        users=users,
        current_user=current_user
    )


@app.route('/saveformclaim', methods=["POST"])
@login_required
def saveformclaim():
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
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tb_claim(claim_status,claim_number,claim_inisiator,claim_type,terminal,no_acq,no_pan,no_receipt,trx_date,trx_time,due_date,claim_date,trx_amount,description,user,reference,week_report,close_claim,bin,routing,claim_entry_boa,remarks) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (claim_status,claim_number,claim_inisiator,claim_type,terminal,no_acq,no_pan,no_receipt,trx_date,trx_time,due_date,claim_date,trx_amount,description,user,reference,week_report,close_claim,bin,routing,claim_entry_boa,remarks))
    mysql.connection.commit()
    cur.close()
    return redirect (url_for('formclaim', success='true'))

@app.route('/pending')
@login_required
def pending():
    cur = mysql.connection.cursor()
    
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
    query = """
        SELECT * FROM tb_claim
        WHERE LOWER(claim_status) NOT IN %s
    """

    cur.execute(query, (excluded_claim_status,))
    claim = cur.fetchall()
    cur.close()
    
    return render_template('pending.html', menu='master', submenu='pending', data=claim, status_class=status_class)


@app.route('/report')
@login_required
def report():
    return render_template('report.html', menu='master', submenu='report')

@app.route('/userlist')
@login_required
@admin_required
def userlist():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_user")
    user = cur.fetchall()
    cur.close()
    return render_template('userlist.html', menu='user', submenu='addusers', data=user, status_class=status_class)

@app.route('/adduser')
@login_required
@admin_required
def adduser():
    cur = mysql.connection.cursor()
    cur.execute("SELECT MAX(user_id) FROM tb_user")
    last_id = cur.fetchone()[0] or 0
    next_id = last_id + 1
    cur.close()
    return render_template('adduser.html', menu='user', submenu='adduser', next_user_id=next_id)

@app.route('/saveadduser', methods=["POST"])
@login_required
@admin_required
def saveadduser():
    print(request.form)
    user = request.form['user']
    password = request.form['password']
    role = request.form['role']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tb_user(user,password,role) VALUES (%s,%s,%s)", (user,password,role))
    mysql.connection.commit()
    cur.close()
    return redirect (url_for('adduser', success='true'))

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Youre Signout.', 'info')
    return redirect(url_for('login'))

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html', menu='master', submenu='contact')

if __name__ == '__main__':
    app.run(debug=True)