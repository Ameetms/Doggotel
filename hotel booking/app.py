from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# File paths
USERS_FILE = "users.xlsx"
BOOKINGS_FILE = "bookings.xlsx"

# Ensure Excel files exist
def create_excel_if_not_exists(file_path, columns):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_excel(file_path, index=False, engine='openpyxl')

# Create Excel files if they don't exist
create_excel_if_not_exists(USERS_FILE, ["Mobile", "Name", "Email", "Approved", "Can Bring Dog"])
create_excel_if_not_exists(BOOKINGS_FILE, ["Mobile", "Hotel", "Check-in", "Check-out"])

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        mobile = request.form['mobile']
        df_users = pd.read_excel(USERS_FILE, engine='openpyxl')

        if str(mobile) in df_users['Mobile'].astype(str).values:
            user = df_users[df_users["Mobile"].astype(str) == mobile].iloc[0]
            
            if user["Approved"] == "Yes":
                return redirect(url_for('booking', mobile=mobile))
            else:
                return "Your account is pending approval. Please wait for admin authorization."
        else:
            return redirect(url_for('register', mobile=mobile))
    
    return render_template('index.html')

@app.route('/register/<mobile>', methods=['GET', 'POST'])
def register(mobile):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        df_users = pd.read_excel(USERS_FILE, engine='openpyxl')

        new_user = pd.DataFrame({
            "Mobile": [mobile],
            "Name": [name],
            "Email": [email],
            "Approved": ["No"],  # Default: Not approved
            "Can Bring Dog": ["No"]  # Default: No dog allowed
        })
        df_users = pd.concat([df_users, new_user], ignore_index=True)
        df_users.to_excel(USERS_FILE, index=False, engine='openpyxl')

        return redirect(url_for('home'))  # Redirect to home after registration
    
    return render_template('register.html', mobile=mobile)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    df_users = pd.read_excel(USERS_FILE, engine='openpyxl')

    if request.method == 'POST':
        mobile = request.form['mobile']
        action = request.form['action']
        can_bring_dog = request.form['can_bring_dog']

        if mobile in df_users['Mobile'].astype(str).values:
            df_users.loc[df_users['Mobile'].astype(str) == mobile, 'Approved'] = action
            df_users.loc[df_users['Mobile'].astype(str) == mobile, 'Can Bring Dog'] = can_bring_dog
            df_users.to_excel(USERS_FILE, index=False, engine='openpyxl')
        
        return redirect(url_for('admin'))

    return render_template('admin.html', users=df_users.to_dict(orient='records'))

@app.route('/booking/<mobile>', methods=['GET', 'POST'])
def boo
