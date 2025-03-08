from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# File paths
USERS_FILE = "users.xlsx"
BOOKINGS_FILE = "bookings.xlsx"

# Ensure Excel files exist
def create_excel_if_not_exists(file_path, columns):
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=columns)
        df.to_excel(file_path, index=False, engine='openpyxl')

# Create files with new fields for approval and dog permission
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

        return "Registration successful! Wait for admin approval."
    
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
def booking(mobile):
    df_users = pd.read_excel(USERS_FILE, engine='openpyxl')
    user = df_users[df_users["Mobile"].astype(str) == mobile].iloc[0]

    if user["Approved"] != "Yes":
        return "Access denied. Your account is not approved."

    if request.method == 'POST':
        hotel = request.form['hotel']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        df_bookings = pd.read_excel(BOOKINGS_FILE, engine='openpyxl')

        new_booking = pd.DataFrame({
            "Mobile": [mobile],
            "Hotel": [hotel],
            "Check-in": [checkin],
            "Check-out": [checkout]
        })
        df_bookings = pd.concat([df_bookings, new_booking], ignore_index=True)
        df_bookings.to_excel(BOOKINGS_FILE, index=False, engine='openpyxl')

        return "Booking Successful!"

    return render_template('booking.html', mobile=mobile, can_bring_dog=user["Can Bring Dog"])

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
