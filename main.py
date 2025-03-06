import sqlite3
import hashlib
import datetime
from random import randrange
from string import ascii_letters
from getpass import getpass



transaction_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

my_conn = sqlite3.connect("bank_users.db")
my_cursor = my_conn.cursor()
my_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    transaction_pin INTEGER NOT NULL,
    account_number INTEGER NOT NULL UNIQUE,
    account_balance INTEGER NOT NULL
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
    return randrange(111111111111111, 999999999999999)

def register_user():
    def generate_acc_number():
        return randrange(10001, 99999)
    
    print("***************Register User***************")

    while True:
        full_name = input("Enter your full name: ")
        
        if not full_name:
            print("Full name field cannot be left blank")
            continue

        if not all(char in ascii_letters + " " for char in full_name):
            print("Invalid character in full name!")
            
            continue
        
        if len(full_name) < 4 or len(full_name) > 255:
            print("Invalid character length") 
            continue
        break

    while True:
        username = input("Enter your username: ")
        if not username:                
            print("Username field cannot be left blank")
            continue

        if len(username) < 3 or len(username) > 20:
            print("Invalid character length for username")
            continue
        
        if not all(char in ascii_letters + "0123456789_"for char in username):
            print("Invalid character used!")
            continue
        break

    while True:
        password = getpass("Set a password: ")
        if not password:
            print("Password field cannot be left blank")
            continue

        confirm_password = getpass("Confirm password: ")
        if not confirm_password:
            print("Confirm Password field cannot be left blank")
            continue


        if password != confirm_password:
            print("Those passwords don't match")
            continue

        break

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    while True:
        
        transaction_pin = (getpass("Set a transaction pin: "))
        if not transaction_pin:
            print("Transaction pin field cannot be left blank")
            continue
        if not all(char in "0123456789"for char in transaction_pin):
            print("Only digits 0-9 allowed!")
            continue
        if len(transaction_pin) != 4:
            print("Pin must contain 4 digits!")
            continue


        confirm_transaction_pin = (getpass("Confirm pin: "))
        if not confirm_transaction_pin:
            print("Confirm transaction pin cannot be left blank")
            continue
        if not all(char in "0123456789"for char in transaction_pin):
            print("Only digits 0-9 allowed!")
            continue
        if len(confirm_transaction_pin) != 4:
            print("Pin must contain 4 digits!")
            continue

        if transaction_pin != confirm_transaction_pin:
            print("Those transaction pins don't match")
            continue

        break

    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()


    while True:
        initial_deposit = int(input("Enter the value you want to deposit: "))

        if not initial_deposit:
            print("Enter a valid amount")
            continue
        if not type(initial_deposit) == int:
            print("Invalid Value!")
            continue
        if initial_deposit < 2000:
            print("Minimum of 2000 naira to open an account")
            continue

        break

    try:
        my_cursor.execute("""
        INSERT INTO users (full_name, username, password, transaction_pin, account_number, account_balance) VALUES
        (?, ?, ?, ?, ?, ?)
        """, (full_name, username, hashed_password, hashed_transaction_pin, generate_acc_number(), initial_deposit))
    except sqlite3.IntegrityError:
        print("Username already exists")
    else:
        my_conn.commit()
        print("Sign Up was successful")
        user = my_cursor.execute("""
        SELECT account_number, username FROM users WHERE username = ?""", (username,)).fetchone()
        print("Welcome", user[1])
        log_in()


def log_in():
    print("***************Log In***************")
    while True:
        username = input("Enter your username: ").strip()
        if not username:
            print("Username field cannot be left blank")
            continue
        
        if not all(char in ascii_letters + "0123456789_"for char in username):
            print("Invalid character used!")
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
    SELECT full_name, username FROM users WHERE username = ? AND password = ?
    """, (username, hashed_password)).fetchone()

    
    if user is None:
        print("Invalid username or password!")
        log_in()
    else:    
        print(f"Log In Successful\nWelcome to the Dashboard, {user[1]}")
        login_menu(user)
                

def deposit():
    while True:
        try:
            account_number = int(input("Enter your account number: ").strip())
        except ValueError as e:
            print(e)
        else:
            if not account_number:
                print("Enter your account number!")
                continue
            break
    my_cursor.execute("""SELECT * FROM users WHERE account_number = ?""", (account_number,))
    user_data = my_cursor.fetchone()
    if user_data is None:
        print("Invalid Account number!")
    else:
        while True:
            try:
                amount = int(input("Enter the amount you want to deposit: ").strip())
            except ValueError as e:
                print(e)
            else:
                if not amount:
                    print("You have to enter a valid amount. Minimum of 1 naira")
                    continue
                if amount < 10:
                    print("Minimum deposit is 10 naira!")
                    continue

                if amount >= 100000000:
                    print("Max deposit is 99999990!")
                else:
                    my_cursor.execute("""
                    UPDATE users
                    SET 
                    account_balance = account_balance + ?""", (amount,))
                    my_cursor.execute("""
                    INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?,?)
                                      """, (generate_transaction_id(), "Deposit", amount, account_number, transaction_time)) 
                    my_conn.commit()
                    print(f"{amount} Succesfully deposited!")
                break

def withdraw():
    while True:
        try:
            account_number = int(input("Enter your account number: ").strip())
        except ValueError as e:
            print(e)
        else:
            if not account_number:
                print("Enter your account number!")
                continue
            break
    my_cursor.execute("""SELECT * FROM users WHERE account_number = ?""", (account_number,))
    user_data = my_cursor.fetchone()
    if user_data is None:
        print("Invalid Account number!")
    else:
        while True:
            try:
                amount = int(input("Enter the amount you want to withdraw: ").strip())
            except ValueError as e:
                print(e)
            else:
                if not amount:
                    print("You have to enter a valid amount. Minimum of 1 naira")
                    continue
                if amount < 10:
                    print("Minimum withdrawal is 10 naira!")
                    continue
                account_balance = my_cursor.execute("""SELECT account_balance FROM users WHERE account_number = ?""", (account_number,)).fetchone()
                if account_balance[0] <= amount:
                    print("Insufficient Funds Available!")
                else:
                    

                    while True:
                        transaction_pin = getpass("Enter your transaction pin: ")
                        hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
                        pin_validity = my_cursor.execute("""SELECT account_number FROM users WHERE transaction_pin = ?""", (hashed_transaction_pin,)).fetchone()
                        if pin_validity is None:
                            print("Invalid Pin!Try again")
                            tries -= 1
                            continue
                        break
                    
                    my_cursor.execute("""
                    UPDATE users
                    SET account_balance = account_balance - ?""", (amount,))
                    my_cursor.execute("""
                    INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?,?)
                                      """,(generate_transaction_id(), "Withdrawal", amount, account_number, transaction_time))
                    my_conn.commit()
                    print(f"{amount} Succesfully withdrawn!")
                    break

def balance_inquiry():
    while True:
        transaction_pin = getpass("Enter your transaction pin: ")
        hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
        pin_data = my_cursor.execute("""SELECT account_balance FROM users WHERE transaction_pin = ?""", (hashed_transaction_pin,)).fetchone()
        if pin_data is None:
            print("Invalid Pin!Try again")
            continue
        break
    print(f"""Account Balance : {pin_data[0]}
""")
                    
    
    
    # my_cursor.execute(""""")

def transaction_history():
    while True:
        
        transaction_pin = (getpass("Enter transaction pin: "))
        if not transaction_pin:
            print("Transaction pin field cannot be left blank")
            continue

        
        break

    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
    
    account_number = my_cursor.execute("""
    SELECT account_number FROM users WHERE transaction_pin = ?""", (hashed_transaction_pin,)).fetchone()
    if account_number is None:
       print("Account number not found!")
    else:

        transaction_history = my_cursor.execute("""
        SELECT * FROM transaction_history WHERE account_number = ?""", (account_number[0],)).fetchall()
        # print(transaction_history)
        if bool(transaction_history) is False:
            print("No Transactions records yet!")
        
        else:
            for (id, type, amount, account_number, transaction_time) in transaction_history:
                print(f"""Transaction ID: {id}
        Transaction type: {type}
        Amount: {amount} naira
        Account Number: {account_number}
        Time: {transaction_time}

            """)
            
    
def account_details(user):
    while True:
        transaction_pin = getpass("Enter your transaction pin: ")
        hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
        pin_data = my_cursor.execute("""SELECT * FROM users WHERE username = ? AND transaction_pin = ?""", (user[1], hashed_transaction_pin)).fetchone()
        if pin_data is None:
            print("Invalid Pin!Try again")
            continue
        break
    print(f"""Full name : {pin_data[1]}
User name : {pin_data[2]}
Account Number : {pin_data[5]}
Account Balance : {pin_data[6]}
""")

def transfer():
    while True:
        try:
            recipient_account_number = int(input("Enter your account number: ").strip())
        except ValueError as e:
            print(e)
        else:
            if not recipient_account_number:
                print("Enter your account number!")
                continue
            while True:
        
                transaction_pin = (getpass("Enter transaction pin: "))
                if not transaction_pin:
                    print("Transaction pin field cannot be left blank")
                    continue 
                break

            hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
            
            account_number = my_cursor.execute("""
            SELECT account_number FROM users WHERE transaction_pin = ?""", (hashed_transaction_pin,)).fetchone()
            if bool(account_number) is False:
                    print("The pin is incorrect!")
                    continue
            else:
                if account_number == recipient_account_number:
                    print("Transaction INVALID! You cannot transfer money to yourself")

                break
    my_cursor.execute("""SELECT full_name FROM users WHERE account_number = ?""", (recipient_account_number,))
    user_data = my_cursor.fetchone()
    if user_data is None:
        print("Invalid Account number!")
    else:
        print(f"Confirm account holder name as: {user_data[0]}")
        confirmation = input("Yes or no: ").strip()
        if confirmation.lower() == "yes":

            while True:
                try:
                    amount = int(input("Enter the amount you want to deposit: ").strip())
                except ValueError as e:
                    print(e)
                else:
                    if not amount:
                        print("You have to enter a valid amount. Minimum of 1 naira")
                        continue
                    if amount < 10:
                        print("Minimum transfer is 10 naira!")
                        continue

                    if amount >= 100000000:
                        print("Max deposit is 99999990!")
                    account_balance = my_cursor.execute("""SELECT account_balance FROM users WHERE account_number = ? """, (account_number[0],)).fetchone()
                    if account_balance[0] <= amount:
                        print("Insufficient Funds Available!")

                    else:
                        my_cursor.execute(f"""
                        UPDATE users
                        SET account_balance = account_balance + ?
                        WHERE account_number = {recipient_account_number}""", (amount,))
                        my_cursor.execute(f"""
                        UPDATE users
                        SET account_balance = account_balance - ?
                        WHERE account_number = ?""", (amount, account_number[0]))
                        my_cursor.execute("""
                        INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?,?)
                                        """, (generate_transaction_id(), "Transfer", amount, account_number[0], transaction_time)) 
                        my_cursor.execute("""
                        INSERT INTO transaction_history(transaction_id, transaction_type, amount, account_number, transaction_time) VALUES (?,?,?,?, ?)
                                    """, (generate_transaction_id(), "Recieved Transfer", amount, recipient_account_number, transaction_time))
                        my_conn.commit()
                        print(f"{amount} Succesfull!")
                        break
        else:
            print("Tranfer cancelled!")    



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
        if choice == "1":
            deposit()
        elif choice == "2":
            withdraw()
        elif choice == "3":
            balance_inquiry()
        elif choice == "4":
            transaction_history()
        elif choice == "5":
            transfer()
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