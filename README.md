#  Banking Management System

A web-based Banking Management System to manage customer accounts, transactions, and administrative banking operations.



##  Project Overview

The Banking Management System is a software application designed to automate and manage core banking operations such as customer account management, transactions, and loan processing. The system aims to reduce manual effort, improve accuracy, and provide secure and efficient banking services. It serves as a centralized platform for administrators, bank staff, and customers to interact with banking data digitally. This project is developed as part of a **Software Engineering academic requirement**.



##  Problem It Solves

Traditional banking processes often rely on manual record keeping, which can lead to errors, data inconsistency, and delays.

Key problems addressed:
- Manual record maintenance
- Time-consuming transaction processing
- Higher chances of human error
- Difficulty for customers to access account information quickly

This system provides a digital solution that ensures faster processing, better data management, and improved user experience.



##  Target Users (Personas)

###  Admin
- Manages the overall system
- Monitors transactions and reports
- Controls user access and system security

###  Bank Staff
- Creates and manages customer accounts
- Performs deposits and withdrawals
- Processes fund transfers and loan-related activities

###  Customer
- Securely logs in to the system
- Views account balance and transaction history
- Performs basic banking operations such as fund transfers



##  Vision Statement

To build a **secure, reliable, and user-friendly digital banking system** that simplifies banking operations and enhances efficiency for both banks and customers.


##  Key Features / Goals

- User authentication and role-based access
- OTP based email verification via Gmail SMTP
- Customer account management
- Deposit and withdrawal operations
- Fund transfer between accounts
- Transaction history tracking
- Loan application and management with EMI calculator
- Administrative monitoring and reporting
- Role based dashboards (Admin / Staff / Customer)
- Staff dashboard with customer and account management

##  Success Metrics

- Accurate and error-free transaction processing
- Secure storage of customer and transaction data
- Users can complete tasks with minimal errors
- Fast and reliable system response


##  Assumptions & Constraints

- The system requires an active internet connection
- This is an academic project with limited time and scope
- The system uses a relational database (e.g., MySQL)
- Real-world banking regulations are simplified
- Security features are implemented at a basic academic level

## MoSCoW Prioritization

| Priority | Features |
|---------|----------|
| Must Have | User login, Account creation, Deposit money, Withdraw money |
| Should Have | Fund transfer, Transaction history |
| Could Have | Loan management, Staff dashboard, EMI calculator |
| Won’t Have | Mobile application, Advanced analytics, Reports |

## Local Development Tools

The following tools were used to develop and run the Banking Management System locally:

- **Operating System:** Windows 10 / Windows 11  
- **Version Control:** Git & GitHub  
- **Containerization:** Docker Desktop  
- **Backend Framework:** Python (Flask)  
- **Frontend:**  HTML + CSS (Professional Banking Theme)  
- **Database:**  MySQL 8.0 (fully integrated via Docker) 
- **Code Editor:** Visual Studio Code
- **Email Service:** Gmail SMTP (for OTP verification)
- **Terminal:** Windows Command Prompt  

Docker is used to ensure a consistent local development environment without manually installing dependencies.


##  Quick Start – Local Development

This project uses Docker to run the Banking Management System locally without installing dependencies manually.
### Prerequisites

- Docker Desktop installed
- Git installed
- Web browser (Chrome / Edge / Firefox)
- Gmail account with App Password (for OTP)
- Python 3.11 (inside Docker, no manual install needed)

## Gmail Setup for OTP
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Create app password with name BMS
5. Copy the 16 character password
6. Paste it in .env file as MAIL_PASSWORD

## Software Design

The Banking Management System follows a modular layered architecture that separates the user interface, backend services, and database. The system is designed with high cohesion and low coupling to improve maintainability and scalability.

Key design choices include role-based access control, a separate authentication module, and containerized deployment using Docker, which improve system organization, security, and ease of deployment.

### Architecture Diagram

![Architecture](Diagrams/architecture.png)
## Steps to Run the Backend Locally

### Step 1: Clone the repository

git clone https://github.com/pranay2686/Banking-Management-System.git


### Step 2: Navigate to the backend folder

cd Banking-Management-System

**Step 3: Create a .env file in the root folder with:**
```bash
SECRET_KEY=bms_super_secret_key_2024
FLASK_ENV=development
DB_HOST=db
DB_PORT=3306
DB_NAME=bms_db
DB_USER=bms_user
DB_PASSWORD=bms_password123
MAIL_USERNAME=yourgmail@gmail.com
MAIL_PASSWORD=your16charapppassword
MAIL_DEFAULT_SENDER=yourgmail@gmail.com
```

**Step 4: Start the application**
```bash
docker-compose up --build
```

**Step 5: Setup the database (run once only)**
```bash
docker exec -it bms_web flask db upgrade
```

**Step 6: Create admin user (run once only)**
```bash
docker exec -it bms_web python create_admin.py
```

**Step 7: Open the application in your browser**
```bash
http://localhost:5000
```
## Default Roles
After running create_admin.py, you can:
- Login and register as a Customer (default role)
- Admin can change any user's role to Staff or Admin
- Admin Dashboard: Manage users, approve/reject loans
- Staff Dashboard: View customers, accounts, transactions
- Customer Dashboard: Manage accounts, deposit, withdraw, transfer, apply loans
