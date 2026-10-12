from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from werkzeug.utils import secure_filename
from PIL import Image
import imagehash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lostfound_db'

# Uploads folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# Helper function for image comparison
def compare_images(img1_path, img2_path):
    hash1 = imagehash.average_hash(Image.open(img1_path))
    hash2 = imagehash.average_hash(Image.open(img2_path))
    return hash1 - hash2

# Home → redirect to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session['username'] = account['username']
            session['role'] = account['role']
            session['user_id'] = account['id']
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password"
            return render_template('index.html', error=error)
    return render_template('index.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO user (fullname, email, username, password, role) VALUES (%s, %s, %s, %s, %s)',
            (fullname, email, username, password, role)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))
    return render_template('signup.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Total Lost Items
        cursor.execute("SELECT COUNT(*) AS total_lost FROM lost_items")
        total_lost = cursor.fetchone()['total_lost']

        # Total Found Items
        cursor.execute("SELECT COUNT(*) AS total_found FROM found_items")
        total_found = cursor.fetchone()['total_found']

        # Total Claims (lost items na claimed)
        cursor.execute("SELECT COUNT(*) AS total_claims FROM lost_items WHERE claim_status = 'claimed'")
        total_claims = cursor.fetchone()['total_claims']

        # Pending Approvals (lost + found na pending)
        cursor.execute("SELECT COUNT(*) AS pending_lost FROM lost_items WHERE status = 'pending'")
        pending_lost = cursor.fetchone()['pending_lost']

        cursor.execute("SELECT COUNT(*) AS pending_found FROM found_items WHERE status = 'pending'")
        pending_found = cursor.fetchone()['pending_found']

        pending_items = pending_lost + pending_found

        cursor.close()

        return render_template('dashboard.html',
                               total_lost=total_lost,
                               total_found=total_found,
                               total_claims=total_claims,
                               pending_items=pending_items)
    return redirect(url_for('login'))


# Report Lost route
@app.route('/report-lost', methods=['GET', 'POST'])
def report_lost():
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        date_lost = request.form['date_lost']
        file = request.files['picture']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO lost_items (item_name, description, date_lost, picture, status, user_id, claim_status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (item_name, description, date_lost, filename, 'pending', session['user_id'], 'unclaimed'))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('dashboard'))
    return render_template('report_lost.html')

# Report Found route
@app.route('/report-found', methods=['GET', 'POST'])
def report_found():
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        date_found = request.form['date_found']
        file = request.files['picture']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO found_items (item_name, description, date_found, picture, status, user_id, claim_status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (item_name, description, date_found, filename, 'pending', session['user_id'], 'unclaimed'))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('dashboard'))
    return render_template('report_found.html')

# Matches route with image comparison
@app.route('/matches')
def matches():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Lost items with owner info
    cursor.execute("""
        SELECT l.*, u.fullname AS lost_owner
        FROM lost_items l
        JOIN user u ON l.user_id = u.id
        WHERE l.status = 'approved'
    """)
    lost_items = cursor.fetchall()

    # Found items with finder info
    cursor.execute("""
        SELECT f.*, u.fullname AS found_owner
        FROM found_items f
        JOIN user u ON f.user_id = u.id
        WHERE f.status = 'approved'
    """)
    found_items = cursor.fetchall()

    matches = []
    seen_pairs = set()

    for lost in lost_items:
        for found in found_items:
            lost_img = os.path.join(app.config['UPLOAD_FOLDER'], lost['picture'])
            found_img = os.path.join(app.config['UPLOAD_FOLDER'], found['picture'])
            if os.path.exists(lost_img) and os.path.exists(found_img):
                diff = compare_images(lost_img, found_img)

                if diff < 10 or lost['item_name'].lower() == found['item_name'].lower() \
                   or lost['description'].lower() == found['description'].lower():

                    pair_key = (lost['id'], found['id'])
                    if pair_key not in seen_pairs:
                        matches.append((lost, found))
                        seen_pairs.add(pair_key)

    cursor.close()
    return render_template('matches.html', matches=matches)



@app.route('/admin')
def admin():
    # Check kung naka-login at role = admin
    if 'role' in session and session['role'] == 'admin':
        # 👉 Hardcoded check: only allow one admin account
        if session['username'] != 'arjeeh':  # palitan mo ng username/email ng main admin mo
            return redirect(url_for('dashboard'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT * FROM lost_items")
        lost_items = cursor.fetchall()

        cursor.execute("SELECT * FROM found_items")
        found_items = cursor.fetchall()

        # Fetch notifications
        cursor.execute("SELECT * FROM notifications ORDER BY created_at DESC")
        notifications = cursor.fetchall()
        cursor.close()

        return render_template('admin.html',
                               lost_items=lost_items,
                               found_items=found_items,
                               notifications=notifications)
    return redirect(url_for('dashboard'))


@app.route('/approve/<string:item_type>/<int:item_id>')
def approve(item_type, item_id):
    #Check kung naka-login at admin lang ang puwedeng mag-approve
    if 'role' in session and session['role'] == 'admin':
        #Hardcoded check: only allow one admin account
        if session['username'] != 'arjeeh':  # palitan mo ng main admin username/email mo
            return redirect(url_for('dashboard'))

        cursor = mysql.connection.cursor()
        if item_type == 'lost':
            cursor.execute("UPDATE lost_items SET status = 'approved' WHERE id = %s", (item_id,))
        elif item_type == 'found':
            cursor.execute("UPDATE found_items SET status = 'approved' WHERE id = %s", (item_id,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('admin'))

    # Kung hindi admin, balik sa dashboard
    return redirect(url_for('dashboard'))

# Reject route
@app.route('/reject/<string:item_type>/<int:item_id>')
def reject(item_type, item_id):
    #Check kung naka-login at admin lang ang puwedeng mag-reject
    if 'role' in session and session['role'] == 'admin':
        #Hardcoded check: only allow one admin account
        if session['username'] != 'arjeeh':  # palitan mo ng main admin username/email mo
            return redirect(url_for('dashboard'))

        cursor = mysql.connection.cursor()
        if item_type == 'lost':
            cursor.execute("UPDATE lost_items SET status = 'rejected' WHERE id = %s", (item_id,))
        elif item_type == 'found':
            cursor.execute("UPDATE found_items SET status = 'rejected' WHERE id = %s", (item_id,))
        mysql.connection.commit()
    cursor.close()
    return redirect(url_for('admin'))

@app.route('/mark_read/<int:notif_id>')
def mark_read(notif_id):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE notifications SET status = 'read' WHERE id = %s", (notif_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('admin'))

# Claim route (with admin notification entry)
@app.route('/claim/<int:lost_id>/<int:found_id>')
def claim(lost_id, found_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Update claim status
    cursor.execute("UPDATE lost_items SET claim_status = 'claimed' WHERE id = %s", (lost_id,))
    cursor.execute("UPDATE found_items SET claim_status = 'claimed' WHERE id = %s", (found_id,))

    # Get item details
    cursor.execute("SELECT item_name, description FROM lost_items WHERE id = %s", (lost_id,))
    lost_item = cursor.fetchone()

    cursor.execute("SELECT item_name, description FROM found_items WHERE id = %s", (found_id,))
    found_item = cursor.fetchone()

    # Build message with item details
    message = f"Claim processed: Lost '{lost_item['item_name']}' ({lost_item['description']}) " \
              f"matched with Found '{found_item['item_name']}' ({found_item['description']})."

    # Insert notification
    cursor.execute("INSERT INTO notifications (message, status) VALUES (%s, %s)", (message, "unread"))

    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('matches'))

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
