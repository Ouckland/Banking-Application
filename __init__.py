import sqlite3
import hashlib
import datetime
import re
from time import sleep
from random import randint
from getpass import getpass

my_conn = sqlite3.connect("bank.db")
my_cursor = my_conn.cursor()

my_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    transaction_pin TEXT NOT NULL,
    account_number INTEGER NOT NULL UNIQUE,
    account_balance NUMERIC NOT NULL
)
""")

my_cursor.execute("""
CREATE TABLE IF NOT EXISTS transaction_history (
    transaction_id INTEGER PRIMARY KEY,
    transaction_type TEXT NOT NULL,
    amount INTEGER,
    account_number INTEGER,
    transaction_time TEXT,
    FOREIGN KEY(account_number) REFERENCES users(account_number)
)""")

def generate_transaction_id():
    while True:
        transaction_id = randint(111111111111111, 999999999999999)
        exists = my_cursor.execute("SELECT transaction_id FROM transaction_history WHERE transaction_id = ?", (transaction_id,)).fetchone()
        if not exists:
            return transaction_id

def generate_acc_number():
    while True:
        acc_number = randint(1000000001, 9999999999)
        exists = my_cursor.execute("SELECT account_number FROM users WHERE account_number = ?", (acc_number,)).fetchone()
        if not exists:
            return acc_number

def validate_input(pattern, prompt, error_message):
    while True:
        user_input = input(prompt).strip()
        if re.fullmatch(pattern, user_input):
            return user_input
        print(error_message)

def register_user():
    print("*************** Register User ***************")
    full_name = validate_input(r"^[A-Za-z]+( [A-Za-z]+)*$", "Enter your full name: ", "Invalid name! Use only letters and spaces.")
    username = validate_input(r"^[A-Za-z0-9_]{8,20}$", "Enter your username: ", "Invalid username! Use 8-20 letters, numbers, or underscores.")
    password = validate_input(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", "Set a password: ", "Password must be at least 8 characters, containing letters and numbers.")
    confirm_password = getpass("Confirm password: ")
    if password != confirm_password:
        print("Passwords do not match!")
        return register_user()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    transaction_pin = validate_input(r"^\d{4}$", "Set a 4-digit transaction pin: ", "Transaction pin must be exactly 4 digits.")
    confirm_transaction_pin = getpass("Confirm transaction pin: ")
    if transaction_pin != confirm_transaction_pin:
        print("Transaction pins do not match!")
        return register_user()
    
    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
    initial_deposit = float(validate_input(r"^[2-9]\d{3,}$", "Enter initial deposit (min 2000): ", "Minimum deposit is 2000."))
    
    try:
        my_cursor.execute("""
        INSERT INTO users (full_name, username, password, transaction_pin, account_number, account_balance) VALUES
        (?, ?, ?, ?, ?, ?)""",
        (full_name, username, hashed_password, hashed_transaction_pin, generate_acc_number(), initial_deposit))
        my_conn.commit()
        print("Sign Up was successful!")
    except sqlite3.IntegrityError:
        print("Username already exists!")
        return register_user()

def transfer(user):
    sender_account_number = user[2]
    recipient_account_number = int(validate_input(r"^\d{10}$", "Enter recipient account number: ", "Invalid account number! Must be 10 digits."))
    if sender_account_number == recipient_account_number:
        print("Transaction INVALID! You cannot transfer money to yourself.")
        return transfer(user)
    
    recipient = my_cursor.execute("SELECT full_name FROM users WHERE account_number = ?", (recipient_account_number,)).fetchone()
    if not recipient:
        print("Invalid recipient account number!")
        return transfer(user)
    
    print(f"Confirm account holder: {recipient[0]}")
    if input("Yes or No: ").strip().lower() != "yes":
        print("Transfer cancelled!")
        return
    
    amount = float(validate_input(r"^\d+(\.\d{1,2})?$", "Enter transfer amount: ", "Invalid amount! Enter a valid number."))
    sender_balance = my_cursor.execute("SELECT account_balance FROM users WHERE account_number = ?", (sender_account_number,)).fetchone()[0]
    if sender_balance < amount:
        print("Insufficient funds!")
        return transfer(user)
    
    my_cursor.execute("UPDATE users SET account_balance = account_balance - ? WHERE account_number = ?", (amount, sender_account_number))
    my_cursor.execute("UPDATE users SET account_balance = account_balance + ? WHERE account_number = ?", (amount, recipient_account_number))
    transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_id = generate_transaction_id()
    
    my_cursor.execute("""
    INSERT INTO transaction_history (transaction_id, transaction_type, amount, account_number, transaction_time) 
    VALUES (?, 'Transfer', ?, ?, ?)""", (transaction_id, amount, sender_account_number, transaction_time))
    my_cursor.execute("""
    INSERT INTO transaction_history (transaction_id, transaction_type, amount, account_number, transaction_time) 
    VALUES (?, 'Received Transfer', ?, ?, ?)""", (transaction_id, amount, recipient_account_number, transaction_time))
    my_conn.commit()
    print(f"Successfully transferred {amount} Naira to {recipient[0]}!")

main_menu()
