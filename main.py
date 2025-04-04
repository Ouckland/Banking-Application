import re
import sqlite3
import hashlib
import datetime
from time import sleep
from random import randint
from string import ascii_letters
from getpass import getpass

my_conn = sqlite3.connect("bank.db")
my_cursor = my_conn.cursor()

my_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    transaction_pin INTEGER NOT NULL,
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
        transaction_id_exists = my_cursor.execute("SELECT transaction_id FROM transaction_history WHERE transaction_id = ?", (transaction_id,)).fetchone()
        if not transaction_id_exists:
            return transaction_id

def generate_acc_number():
    while True:
        acc_number = randint(1000000001, 9999999999)
        acc_number_exists = my_cursor.execute("SELECT account_number FROM users WHERE account_number = ?", (acc_number,)).fetchone()
        if not acc_number_exists:
            return acc_number
        
def validate_input(pattern, prompt, error_message):
    while True:
        user_input = input(prompt).strip()
        if re.fullmatch(pattern, user_input):
            return user_input
        print(error_message)

def validate_getpass(pattern, prompt, error_message):
    while True:
        user_input = getpass(prompt).strip()
        if re.fullmatch(pattern, user_input):
            return user_input
        print(error_message)

def register_user():

    print("***************Register User***************")

    full_name = validate_input(r"^[A-Za-z]+( [A-Za-z]+)*$", "Enter your full name: ", "Invalid name! Use only letters and spaces.")
    username = validate_input(r"^[A-Za-z0-9_]{8,20}$", "Enter your username: ", "Invalid username! Use 8-20 letters, numbers, or underscores.")
    password = validate_getpass(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", "Set a password: ", "Password must be at least 8 characters, containing letters and numbers.")
    confirm_password = getpass("Confirm password: ")
    if password != confirm_password:
        print("Passwords do not match!")
        return register_user()        
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    transaction_pin = validate_getpass(r"^\d{4}$", "Set a 4-digit transaction pin: ", "Transaction pin must be exactly 4 digits.")
    confirm_transaction_pin = getpass("Confirm transaction pin: ")
    if transaction_pin != confirm_transaction_pin:
        print("Transaction pins do not match!")
        return register_user()

    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
    initial_deposit = float(validate_input(r"^[2-9]\d{3,}$", "Enter initial deposit (min 2000): ", "Minimum deposit is 2000."))

    try:
        my_cursor.execute("""
        INSERT INTO users (full_name, username, password, transaction_pin, account_number, account_balance) VALUES
        (?, ?, ?, ?, ?, ?)
        """, (full_name, username, hashed_password, hashed_transaction_pin, generate_acc_number(), initial_deposit))
        my_conn.commit()
        sleep(randint(1, 4))
        print("Sign Up was successful!")
        user = my_cursor.execute("""
        SELECT account_number, username FROM users WHERE username = ?""", (username,)).fetchone()
        print("Welcome", user[1])
        log_in()
        
    except sqlite3.IntegrityError as e:
        print("Username already exists", e)
        return register_user()    


def log_in():
    print("***************Log In***************")
    while True:
        username = input("Enter your username: ").strip()
        if not username:
            print("Username field cannot be left blank")
            continue
        break  


    while True:
        password = getpass("Enter your password: ").strip()
        if not password:
            print("Password field cannot be left blank")
            continue
        break

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = my_cursor.execute("""
    SELECT full_name, username, account_number, transaction_pin FROM users WHERE username = ? AND password = ?
    """, (username, hashed_password)).fetchone()

    sleep(randint(1,4))
    if not user:
        print("Invalid username or password!")
        log_in()
    else:    
        print(f"Log In Successful\nWelcome to the Dashboard, {user[1]}")
        sleep(randint(1,4))
        login_menu(user)
                

def deposit(user):
    while True:
        try:
            amount = float(input("Enter the amount you want to deposit: "))
        except ValueError:
            print("Enter a valid amount", )
        else:
            if amount < 10:
                print("Minimum deposit is 10 naira!")
                continue

            if amount >= 100000000:
                print("Max deposit is 99999990!")
            else:
                while True:
                    transaction_pin = getpass("Enter your transaction pin: ")
                    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
                    pin_validity = my_cursor.execute("""SELECT account_number FROM users WHERE transaction_pin = ?""", (hashed_transaction_pin,)).fetchone()
                    if not pin_validity:
                        print("Invalid Pin!Try again")
                        continue
                    break
                
                while True:
                    confirmation = input(f"Are you sure you want to deposit {amount} Naira into your account?\nYes or No: ").lower()
                    if confirmation == "yes":
                        my_cursor.execute("""
                        UPDATE users
                        SET 
                        account_balance = account_balance + ?""", (amount,))
                        transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                        my_cursor.execute("""
                            INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?,?)
                            """, (generate_transaction_id(), "Deposit", amount, user[2], transaction_time))
                        my_conn.commit()
                        sleep(randint(1,4))
                        print(f"{amount} Naira Succesfully deposited!")
                    elif confirmation == "no":
                        pass
                    else:
                        continue
                    break
            break

def withdraw(user):
    while True:
        try:
            amount = float(input("Enter the amount you want to withdraw: "))
            if amount < 10:
                print("Minimum withdrawal is 10 naira!")
                continue
            if amount > 999_999:
                print("Max withdrawal is 999,999 naira")
                continue
            account_balance = my_cursor.execute("""SELECT account_balance FROM users WHERE username = ?""", (user[1],)).fetchone()
            if account_balance[0] <= amount:
                print("Insufficient Funds Available!")
                sleep(randint(1,4))
                continue
        except ValueError as e:
            print("Enter a valid amount!")
            continue
        break

    while True:
        transaction_pin = getpass("Enter your transaction pin: ")
        hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
        pin_validity = my_cursor.execute("""SELECT account_number FROM users WHERE transaction_pin = ?""", (hashed_transaction_pin,)).fetchone()
        if not pin_validity:
            print("Invalid Pin!Try again")
            continue
        break
                
    while True:
        confirmation = input(f"Are you sure you want to withdraw {amount} Naira from your account?\nYes or No: ").lower()
        if confirmation == "yes":
            my_cursor.execute("""
            UPDATE users
            SET account_balance = account_balance - ?""", (amount,))
            
            transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            my_cursor.execute("""
            INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?,?)
            """, (generate_transaction_id(), "Withdrawal", amount, user[2], transaction_time))  
            my_conn.commit()
            sleep(randint(1,5))
            print(f"{amount} Naira Succesfully withdrawn!")
        elif confirmation == "no":
            pass
        else:
            continue
        break

def balance_inquiry(user):
    while True:
        transaction_pin = getpass("Enter your transaction pin: ")
        hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
        pin_data = my_cursor.execute("""SELECT account_balance FROM users WHERE (transaction_pin, username) = (?, ?)""", (hashed_transaction_pin, user[1])).fetchone()
        if not pin_data:
            print("Invalid Pin!Try again")
            continue
        break
    sleep(randint(1,4))
    print(f"""Account Balance : {pin_data[0]} Naira""")
                    

def transaction_history(user):
    while True:
        transaction_pin = (getpass("Enter transaction pin: "))
        if not transaction_pin:
            print("Transaction pin field cannot be left blank")
            continue
        break

    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
    
    account_number = my_cursor.execute("""
    SELECT account_number FROM users WHERE (transaction_pin, username) = (?, ?)""", (hashed_transaction_pin, user[1])).fetchone()
    if not account_number:
       print("Account number not found!")
    else:
        transaction_history = my_cursor.execute("""
        SELECT * FROM transaction_history WHERE account_number = ?""", (account_number[0],)).fetchall()
        if not transaction_history:
            print("No Transactions records yet!")
        else:
            for (id, type, amount, account_number, transaction_time) in transaction_history:
                sleep(randint(1,4))
                print(f"""Transaction ID: {id}
                Transaction type: {type}
                Amount: {amount} Naira
                Account Number: {account_number}
                Time: {transaction_time}
                """)
            
    
def account_details(user):
    while True:
        transaction_pin = getpass("Enter your transaction pin: ")
        hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
        pin_data = my_cursor.execute("""SELECT * FROM users WHERE username = ? AND transaction_pin = ?""", (user[1], hashed_transaction_pin)).fetchone()
        if not pin_data:
            print("Invalid Pin!Try again")
            continue
        break
    sleep(randint(1,4))
    print(f"""Full name : {pin_data[1]}
        User name : {pin_data[2]}
        Account Number : {pin_data[5]}
        """)

def transfer(user):
    while True:
        try:
            recipient_account_number = int(input("Enter recipient account number: ").strip())
            account_number = my_cursor.execute("""
            SELECT account_number FROM users WHERE (username) = (?)""", (user[1],)).fetchone()
        
            if not account_number:
                print("Invalid account number provided!")
                continue
            if account_number[0] == recipient_account_number:
                print("Transaction INVALID! You cannot transfer money to yourself")
                continue
          
        except ValueError:
            print("Enter a valid account number")
            continue
        break    
    
    while True:
        recipient_user_data = my_cursor.execute("""SELECT full_name FROM users WHERE account_number = ?""", (recipient_account_number,)).fetchone()
        if not recipient_user_data:
            print("Invalid Account number!")
            transfer(user)
        else:
            print(f"Confirm account holder name as: {recipient_user_data[0]}")
            confirmation = input("Yes or no: ").strip()
            if confirmation.lower() == "no":
                break
            elif confirmation.lower() == "yes":
                while True:
                    try:
                        amount = float(input("Enter the amount you want to deposit: ").strip())
                    except ValueError:
                        print("Enter a valid amount!")
                        continue
                    else:
                        if amount < 10:
                            print("Minimum transfer is 10 naira!")
                            continue

                        if amount >= 100000000:
                            print("Max transfer is 99_999_990 naira!")
                        account_balance = my_cursor.execute("""SELECT account_balance FROM users WHERE account_number = ? """, (account_number[0],)).fetchone()
                        if account_balance[0] <= amount:
                            print("Insufficient Funds Available!")
                        else:
                            while True:
                                transaction_pin = (getpass("Enter transaction pin: "))
                                if not transaction_pin:
                                    print("Transaction pin field cannot be left blank")
                                    continue 
                                
                                hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
                                pin_validity = my_cursor.execute("""
                                    SELECT * FROM users WHERE (transaction_pin, account_number) = (?,?)
                                    """, (hashed_transaction_pin, account_number[0])).fetchone()
                                if not pin_validity:
                                    print("Invalid pin entered!")
                                    continue

                                while True:
                                    confirmation = input(f"Are you sure you want to transfer {amount} Naira to {recipient_user_data[0]}?\nYes or No: ").lower()
                                    if confirmation == "yes":
                                        my_cursor.execute(f"""
                                        UPDATE users
                                        SET account_balance = account_balance + ?
                                        WHERE account_number = ?""", (amount, recipient_account_number,))
                                        my_cursor.execute(f"""
                                        UPDATE users
                                        SET account_balance = account_balance - ?
                                        WHERE account_number = ?""", (amount, account_number[0]))
                                        transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    
                                        my_cursor.execute("""
                                        INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?,?)
                                        """, (generate_transaction_id(), f"Transfer to {recipient_account_number} - {recipient_user_data[0]}", amount, account_number[0], transaction_time)) 
                                    
                                        my_cursor.execute("""
                                        INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?, ?)
                                                    """, (generate_transaction_id(), f"Recieved Transfer from {account_number[0]} - {user[0]}", amount, recipient_account_number, transaction_time))
                                        my_conn.commit()
                                        sleep(randint(1,4))
                                        print(f"{amount} Naira transferred Succesfully to {recipient_user_data[0]}!")
                                    elif confirmation == "no":
                                        print("Tranfer cancelled!")    
                                        pass
                                    else:
                                        continue
                                    break
                                break            
                    break                   
            else:
                continue
        break


def login_menu(user):
    login_menu = """
    1.  Deposit
    2.  Withdraw
    3.  Balance inquiry
    4.  Transaction history
    5.  Transfer
    6.  Account Details
    7.  Log Out
    """
    while True:
        print(login_menu)
        choice = input("Choose an option from the menu above: ").strip()
        sleep(randint(1,4))
        if choice == "1":
            deposit(user)
        elif choice == "2":
            withdraw(user)
        elif choice == "3":
            balance_inquiry(user)
        elif choice == "4":
            transaction_history(user)
        elif choice == "5":
            transfer(user)
        elif choice == "6":
            account_details(user)
            
        elif choice == "7":
            main_menu()
            break    

def main_menu():

    menu = """
    ***************Menu***************"
    Welcome to the Bank of Astute People

    1. Sign Up.
    2. Log In
    3. Quit
    """

    while True:

        print(menu)
        choice = input("Choose an option from the menu above: ").strip()
        if choice == "1":
            register_user()
        elif choice == "2":
            log_in()
        elif choice == "3":
            print("Thank you for banking with us!")
            break
        else:
            print("Option Invalid. Choose an option from the menu above!")
            # continue
        break

main_menu()
