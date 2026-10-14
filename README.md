# Women Safety & Safe Route Finder Using Cloud Computing

A full-stack, cloud-native Women Safety web application powered by **AWS (EC2, RDS, S3)**, **Python Flask**, and **Interactive Safety-Scored Maps**.

---

## 🛠️ Technology Stack

- **Application Hosting (Compute)**: Amazon EC2 (Linux Ubuntu / Amazon Linux)
- **Cloud Database**: Amazon Relational Database Service (RDS) for MySQL
- **Object Storage**: Amazon Simple Storage Service (S3) for incident photos
- **Backend Framework**: Python 3.13 Flask REST API
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5, FontAwesome)
- **Mapping & Routing**: Leaflet / OpenStreetMap with transparent safety scoring (and Google Maps API support)
- **Emergency Notifications**: SOS broadcast with GPS coordinate tracking & Google Maps deep links

---

## 📁 Project Architecture & Files

```text
D:\DAV\cloud-project/
├── app.py                      # Core Flask web server & API routes
├── config.py                   # Configuration & AWS environment parameters
├── requirements.txt            # Python dependencies (Flask, PyMySQL, boto3, etc.)
├── schema.sql                  # MySQL database schema for AWS RDS
├── test_app.py                 # Automated unit tests for all modules
├── .env.example                # Sample environment variables for AWS
├── services/
│   ├── database.py             # Dual-engine DB (Amazon RDS MySQL + local SQLite fallback)
│   ├── maps_service.py         # Multi-route alternative path generator
│   ├── safety_score.py         # Transparent safety score algorithm (lighting, crime, time)
│   ├── location_service.py     # Live GPS tracking & journey recorder
│   ├── sos_service.py          # Emergency distress signal & guardian dispatcher
│   └── storage_service.py      # Amazon S3 photo uploader with local fallback
├── templates/
│   ├── base.html               # Shared navbar, SOS quick button, & cloud status badges
│   ├── login.html              # Sign-in page with 1-click test credentials
│   ├── register.html           # User registration
│   ├── dashboard.html          # Main hub with prominent SOS button & alerts
│   ├── safe_route.html         # Interactive map, safety scores & color-coded routes
│   ├── contacts.html           # Emergency guardians management
│   ├── reports.html            # Community unsafe area reporting & photo evidence
│   └── admin.html              # Cloud verification console (EC2, RDS, S3 status)
└── static/
    ├── css/style.css           # Custom animations, SOS pulse, and layout styles
    └── js/
        ├── map.js              # Leaflet mapping and route rendering
        ├── sos.js              # Emergency trigger and GPS extraction
        └── location.js         # Real-time periodic GPS ping
```

---

## 🚀 Step 1: Run Locally on Your Computer

1. Open PowerShell or Command Prompt in `D:\DAV\cloud-project`:
   ```powershell
   cd D:\DAV\cloud-project
   ```
2. Start the application:
   ```powershell
   python app.py
   ```
3. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```
4. **Pre-seeded Accounts for instant testing**:
   - **Demo User**: `priya@example.com` / Password: `demo123`
   - **Cloud Admin**: `admin@cloudsafety.org` / Password: `admin123`

---

## ☁️ Step 2: Deploy to AWS EC2 (Public Cloud)

### 1. Launch EC2 Instance (Free Tier)
1. Sign in to your [AWS Management Console](https://console.aws.amazon.com/).
2. Select your preferred region (e.g., **ap-south-1 Mumbai** or **us-east-1 N. Virginia**).
3. Search for **EC2** &rarr; click **Launch Instance**:
   - **Name**: `women-safety-server`
   - **OS**: Ubuntu 24.04 LTS (Free tier eligible)
   - **Instance type**: `t2.micro` or `t3.micro` (Free tier)
   - **Key pair**: Create new or proceed without key pair (use EC2 Instance Connect).
   - **Network settings / Security Group**: Check:
     - Allow SSH from Anywhere (or My IP)
     - Allow HTTP traffic from the internet (Port 80)
     - Add Custom TCP rule for Port 5000 (Anywhere `0.0.0.0/0`)
4. Click **Launch Instance**.

### 2. Connect & Run on EC2
1. In the EC2 console, select your running instance and click **Connect &rarr; EC2 Instance Connect &rarr; Connect** (opens terminal in browser).
2. Run these commands:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv git
   git clone <YOUR_GIT_REPO_URL>
   cd cloud-project
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 app.py
   ```
3. Your application is now accessible worldwide at:
   `http://<YOUR-EC2-PUBLIC-IP>:5000`

---

## 🗄️ Step 3: Connect Amazon RDS MySQL & S3 Bucket

### A. Amazon RDS (MySQL)
1. Go to **AWS RDS Console** &rarr; **Create database**.
2. Engine: **MySQL** (Free tier template).
3. DB instance identifier: `womensafety-db`.
4. Master username: `admin`, Master password: `YourPassword123`.
5. Under Connectivity, attach the same Security Group as your EC2 instance.
6. Once created, copy the **Endpoint** and set it in your `.env` or `config.py`:
   ```bash
   DB_TYPE=mysql
   DB_HOST=<your-rds-endpoint>
   DB_USER=admin
   DB_PASSWORD=YourPassword123
   DB_NAME=womensafety
   ```

### B. Amazon S3 (Incident Photos)
1. Go to **AWS S3 Console** &rarr; **Create bucket**:
   - Bucket name: e.g., `womensafety-reports-2025`
   - Uncheck "Block all public access" (or keep private and use signed URLs).
2. Set in `.env`:
   ```bash
   S3_BUCKET=womensafety-reports-2025
   AWS_REGION=ap-south-1
   ```

---

## 📸 Rubric & Evaluation Evidence Screenshots

For your final review and presentation, capture these exact screens:
1. **EC2 Console**: Instance state showing `Running` with public IP address.
2. **RDS Console**: Database status `Available` showing MySQL engine.
3. **S3 Console**: Bucket object list showing uploaded incident photos.
4. **Live Web App**:
   - Dashboard with Emergency SOS button.
   - Safe Route Finder map showing color-coded alternative paths.
   - Admin console (`/admin`) displaying active cloud connections and SOS distress logs.
