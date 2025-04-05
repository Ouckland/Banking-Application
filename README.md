# 💳 Banking Application

A simple command-line banking application built using Python and SQLite. This project simulates core banking features such as account registration, login, deposit, withdrawal, transfers, and transaction history management — all secured with hashed passwords and PINs.

## 📦 Features

- **User Registration**  
  Secure sign-up with:
  - Username and password
  - Full name
  - Unique 10-digit account number
  - 4-digit transaction PIN (hashed)
  - Initial deposit (minimum ₦2000)

- **User Login**  
  - Authenticates via username and hashed password
  - Redirects to a secure banking dashboard

- **Banking Operations** (Post-login)
  - 💰 **Deposit**  
    Add funds to your account with PIN confirmation

  - 💸 **Withdraw**  
    Withdraw funds with PIN validation and balance check

  - 📊 **Balance Inquiry**  
    View current account balance with PIN authentication

  - 🧾 **Transaction History**  
    Review past deposits, withdrawals, and transfers

  - 🔁 **Fund Transfers**  
    Transfer money to other users using their account number with full validation

  - 👤 **Account Details**  
    View basic account details (name, username, account number)

  - 🚪 **Logout**  
    Exit to the main menu

## 🛠️ Tech Stack

- **Language:** Python 3
- **Database:** SQLite3
- **Security:** SHA-256 password & PIN hashing using `hashlib`
- **User Input:** `getpass` used for secure password and PIN entry

## 📂 Project Structure

```bash
banking_app/
│
├── bank.db               # SQLite3 database (auto-created on first run)
├── main.py               # Main application logic
└── README.md             # Project documentation
```

## 📋 How It Works

1. **Run the app**:  
   ```bash
   python main.py
   ```

2. **Choose from the main menu**:
   - Sign up as a new user
   - Log in to your account
   - Quit the application

3. **After login**:
   - Perform any of the available banking operations via menu

## 🔐 Security Considerations

- Passwords and transaction PINs are hashed using SHA-256 before being stored.
- Critical actions require PIN validation.
- Invalid input patterns are blocked with regex-based sanitization.

## ✅ Input Validations

- **Name:** Letters and spaces only  
- **Username:** 8-20 characters (letters, numbers, underscore)  
- **Password:** At least 8 characters, with letters and digits  
- **Transaction PIN:** Exactly 4 digits  
- **Initial Deposit:** Minimum ₦2000

## 💡 Future Improvements

- Add GUI or web frontend
- Implement user roles (admin, customer)
- Add email/SMS notification system
- Upgrade to PostgreSQL or MySQL
- OTP or 2FA for added security

---
