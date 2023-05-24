import sqlite3

from flask import Flask, render_template, request, redirect, session

import os
import csv

from werkzeug.utils import secure_filename



app = Flask(__name__)
app.secret_key = 'secret_key'  # Change this to your own secret key



# Database connection
conn = sqlite3.connect('users.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Perform any necessary logout actions (e.g., clear session data)

    # Redirect the user to the login page
    return redirect('/')
# @app.route('/logout', methods=['GET'])
# def logout():
#     # Check if the user is authenticated
#     if 'username' in session:
#         # Clear the session data, including the user's login status
#         session.clear()
#
#     # Redirect the user to the login page
#     return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('register.html', error=error)
        else:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect('/')

    return render_template('register.html')

# @app.route('/dashboard', methods=['GET'])
# @login_required
# def dashboard():
#     # Retrieve the logged-in user's username
#     username = session['username']
#
#     # Retrieve the path to the user's uploaded CSV file from the database
#     cursor.execute("SELECT csv_path FROM users WHERE username = ?", (username,))
#     result = cursor.fetchone()
#     if result is None or result[0] is None:
#         flash('No CSV file uploaded.', 'info')
#         return redirect(url_for('dashboard'))
#
#     csv_path = result[0]
#
#     # Read the CSV file and convert it to a list of dictionaries
#     csv_data = []
#     with open(csv_path, 'r') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             csv_data.append(row)
#
#     return render_template('dashboard.html', username=username, csv_data=csv_data)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        if request.method == 'POST':
            # Get the uploaded file
            file = request.files['file']

            # Check if the file is allowed
            if file and allowed_file(file.filename):
                # Save the file to the upload folder
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))

                # Store the uploaded file path in the session
                session['uploaded_file'] = os.path.join(UPLOAD_FOLDER, filename)

        # Display the uploaded CSV file (if any)
        uploaded_file = session.get('uploaded_file')
        if uploaded_file and os.path.isfile(uploaded_file):
            # Read and process the CSV file
            csv_data = read_csv_file(uploaded_file)
            return render_template('dashboard.html', username=session['username'], csv_data=csv_data)
        else:
            return render_template('dashboard.html', username=session['username'], csv_data=None)
    else:
        return redirect('/')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_csv_file(file_path):
    csv_data = []

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            csv_data.append(row)

    return csv_data

if __name__ == '__main__':
    app.run(debug=True)
