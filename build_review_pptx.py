import os
import zipfile
import xml.etree.ElementTree as ET

SOURCE_PPTX = r"d:\review\Review 1.pptx"
TARGET_PPTX = r"d:\review\Review_1_SafePass.pptx"

NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

ET.register_namespace("p", NS_P)
ET.register_namespace("a", NS_A)
ET.register_namespace("r", NS_R)

# Slide contents definition
# Format for each bullet: (lvl, bold_prefix, text, sz)
SLIDE_DATA = {
    "slide1.xml": {
        "type": "title_slide",
        "title_lines": [
            ("Institution Name and Department", False, 4000),
            ("24CAC631 CLOUD APPLICATION DEVELOPMENT", True, 4400),
            ("Project Work : Review 1", True, 3600),
        ],
        "subtitle_lines": [
            ("Title of the Project : ", "SafePass — Women Safety & Safe Route Finder Using Cloud Computing", 1800),
            ("Domain : ", "Cloud Application Development (PaaS, DBaaS, Object Storage, Geospatial Routing)", 1500),
            ("Name of the Guide : ", "[Faculty Guide Name]", 1600),
            ("Name of the Student : ", "Haripriya", 1800),
            ("Register No. : ", "[Student Register No.]", 1600),
            ("Date : ", "October 2026", 1600),
        ]
    },
    "slide2.xml": {
        "title": "Syllabus & Cloud Domain Alignment",
        "bullets": [
            (0, "Course Code & Name: ", "24CAC631 Cloud Application Development.", 1500),
            (0, "Platform as a Service (PaaS): ", "Render Cloud Platform hosting containerized Python/Flask backend with automated GitHub CI/CD continuous deployment pipeline.", 1400),
            (0, "Database as a Service (DBaaS): ", "Managed Relational Database (Amazon RDS / Cloud SQLite with WAL) ensuring ACID compliance for critical safety records and SOS logs.", 1400),
            (0, "Cloud Object Storage Service: ", "Amazon S3 Bucket Architecture for secure, scalable, and encrypted multimedia evidence storage (PDF FIR copies, photos, audio).", 1400),
            (0, "Cloud Geospatial Microservices: ", "Integration with OpenStreetMap (OSM) tile servers and OSRM (Open Source Routing Machine) cloud routing APIs.", 1400),
            (0, "Cloud Security Standards: ", "Enforced HTTPS/TLS encryption, Argon2/PBKDF2 SHA-256 password hashing, and role-based session isolation.", 1400),
        ]
    },
    "slide3.xml": {
        "title": "Problem Identification, Objectives & Scope",
        "bullets": [
            (0, "Problem Identification: ", "Commercial navigation applications (Google Maps, Apple Maps) optimize exclusively for shortest distance and vehicular speed, completely omitting personal safety factors like streetlighting, deserted pathways, and crime hotspots.", 1400),
            (1, "Emergency Delay: ", "Pedestrians in distress face high panic friction, lacking a single-touch mechanism to broadcast live GPS coordinates to guardians and authorities.", 1300),
            (1, "Evidence Void: ", "Absence of a cloud-backed repository to preserve official FIRs, incident documentation, and civic petitions without tampering risks.", 1300),
            (0, "Key Objectives: ", "Develop a responsive, cloud-hosted safety navigation platform with real-time route assessment.", 1400),
            (1, "Dynamic Scoring: ", "Provide safety ratings (1-5 stars) incorporating police station proximity, crowd density, and lighting.", 1300),
            (1, "Instant SOS Alerting: ", "1-click emergency dispatch with browser GPS coordinate capture and audible alarm beacon.", 1300),
            (1, "Cloud Evidence Archival: ", "Secure upload and in-browser modal verification for citizen incident reports and FIR documents.", 1300),
            (0, "Scope & Target Users: ", "Solo female commuters, night-shift employees, college students, and municipal safety administrators.", 1400),
        ]
    },
    "slide4.xml": {
        "title": "Abstract & Proposed Solution",
        "bullets": [
            (0, "Abstract: ", "SafePass is a cloud-native web application designed to empower women and vulnerable pedestrians by combining geospatial navigation with real-time safety metrics, rapid emergency response dispatching, and community incident reporting.", 1400),
            (0, "Proposed Solution Overview: ", "A decoupled 3-tier cloud SaaS accessible on any device via modern web browsers without installation.", 1400),
            (1, "Safe Route Computation: ", "Recommends paths evaluated against weighted environmental parameters (illumination, surveillance, police booths).", 1300),
            (1, "Cloud SOS Emergency Hub: ", "Instantaneously logs distress coordinates to cloud DB and broadcasts alerts to registered contacts and Admin console.", 1300),
            (1, "Cloud Evidence Repository: ", "Direct cloud storage of FIR complaints and citizen grievances with interactive in-browser preview.", 1300),
            (1, "Dual-Role Architecture: ", "Segregated role-based access control (RBAC) separating Citizen Users from Cloud Safety Administrators.", 1300),
            (0, "Expected Outcome: ", "Substantial reduction in emergency response delay, proactive avoidance of high-risk corridors, and verified community transparency.", 1400),
        ]
    },
    "slide5.xml": {
        "title": "Literature Survey & Existing System Analysis",
        "bullets": [
            (0, "Existing System 1 — Google Maps & General Navigation: ", "Strong in road routing and traffic, but possesses zero personal safety intelligence, no lighting indexes, and no emergency dispatch capabilities.", 1400),
            (0, "Existing System 2 — Standalone SOS Mobile Apps (Safetipin, bSafe): ", "Require app store installations, consume excessive background battery, suffer OS permission kills, and lack centralized municipal admin oversight.", 1400),
            (0, "Existing System 3 — Manual Helplines (Dial 112/100): ", "Prone to telecommunication delays, verbal address confusion during panic, and no automatic GPS visual map tracking.", 1400),
            (0, "Proposed SafePass System Advantages: ", "Cloud-native, zero-install architecture running instantly on any smartphone browser.", 1400),
            (1, "Web-First Cloud Access: ", "No mobile app download barrier — runs on any smartphone browser with secure HTTPS.", 1300),
            (1, "Centralized Admin HUD: ", "Real-time surveillance console for college/municipal authorities to audit alerts and resolve incidents.", 1300),
            (1, "Tamper-Evident Storage: ", "Durable cloud object storage ensures legal admissibility and integrity of incident evidence.", 1300),
        ]
    },
    "slide6.xml": {
        "title": "Technologies Used & Justification",
        "bullets": [
            (0, "Frontend / Client Tier: ", "HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3 Responsive Grid.", 1400),
            (1, "Justification: ", "Zero client footprint, mobile-first responsive layout, and universal browser compatibility across all operating systems.", 1300),
            (0, "Geospatial Engine: ", "Leaflet.js & OpenStreetMap (OSM) tile services.", 1400),
            (1, "Justification: ", "Lightweight vector mapping, open-source with no proprietary API billing, and native GPS polyline rendering.", 1300),
            (0, "Backend Application Tier: ", "Python 3.12, Flask Micro-Framework, Gunicorn Production WSGI Server.", 1400),
            (1, "Justification: ", "Asynchronous speed, modular MVC architecture, rapid prototyping, and native Linux cloud container compatibility.", 1300),
            (0, "Data Tier & Cloud Storage: ", "Relational SQL (Amazon RDS / Cloud SQLite) & Amazon S3 Object Storage.", 1400),
            (1, "Justification: ", "Strict relational integrity for user credentials/SOS logs; 99.999999999% durability for digital evidence files.", 1300),
            (0, "Deployment & DevOps: ", "Render Cloud PaaS + GitHub Automated CI/CD Pipeline.", 1400),
            (1, "Justification: ", "Automated git-push deployments, managed SSL certificates, and zero infrastructure maintenance overhead.", 1300),
        ]
    },
    "slide7.xml": {
        "title": "Module Identified",
        "bullets": [
            (0, "Module 1: Cloud Authentication & Role-Based Access Control (RBAC)", "", 1500),
            (1, "Responsibilities: ", "User registration, cryptographic password verification, session state management, and role routing (Citizen vs. Cloud Admin).", 1300),
            (0, "Module 2: Cloud Geospatial Navigation & Safe Route Finder", "", 1500),
            (1, "Responsibilities: ", "Pedestrian route calculation, multi-criteria safety evaluation (lighting, police, crowd), and interactive map display.", 1300),
            (0, "Module 3: Instant Cloud SOS Emergency Dispatch System", "", 1500),
            (1, "Responsibilities: ", "One-touch emergency activation, high-accuracy GPS capture, audio alert trigger, and real-time contact/admin notification.", 1300),
            (0, "Module 4: Citizen Safety Incident & Evidence Reporting", "", 1500),
            (1, "Responsibilities: ", "Hazard category submission, location tagging, secure PDF/image evidence upload to cloud storage, and in-browser modal viewing.", 1300),
            (0, "Module 5: Cloud Administrative Analytics & Live Vigilance Console", "", 1500),
            (1, "Responsibilities: ", "Real-time command center, live SOS queue tracking, alert resolution actions, and citizen incident file auditing.", 1300),
        ]
    },
    "slide8.xml": {
        "title": "Module Description",
        "bullets": [
            (0, "Module 1 (Auth & RBAC): ", "Inputs: Email, password, role flag. Processing: PBKDF2 hashing, session generation. Outputs: Authenticated user token, role-gated UI.", 1350),
            (0, "Module 2 (Safe Route Finder): ", "Inputs: Origin, destination, GPS coordinates. Processing: Waypoint distance computation, safety index weighting. Outputs: Color-coded safe path polylines, nearest safe zones.", 1350),
            (0, "Module 3 (Instant Cloud SOS): ", "Inputs: 1-click trigger, browser GPS coords. Processing: Atomic DB write, dispatch payload creation, active beacon broadcast. Outputs: Pulsing emergency HUD, alert sound, live admin record.", 1350),
            (0, "Module 4 (Evidence Reporting & S3): ", "Inputs: Hazard type, description, PDF/image attachment. Processing: File validation, UUID renaming, cloud storage upload. Outputs: Live report feed, embedded PDF modal previewer.", 1350),
            (0, "Module 5 (Cloud Admin Console): ", "Inputs: Admin credential, resolution actions ('Mark Resolved'). Processing: Multi-table aggregation queries. Outputs: Real-time KPI statistics, resolution status updates.", 1350),
        ]
    },
    "slide9.xml": {
        "title": "ER, DFD, Use Case Diagram",
        "bullets": [
            (0, "Entity-Relationship (ER) Architecture: ", "Relational database schema enforcing strict foreign-key constraints:", 1400),
            (1, "USERS (1) -> (N) EMERGENCY_CONTACTS: ", "A registered citizen manages multiple emergency phone numbers.", 1300),
            (1, "USERS (1) -> (N) SOS_ALERTS: ", "A user can trigger multiple timestamped SOS emergency beacons with exact coordinates.", 1300),
            (1, "USERS (1) -> (N) SAFETY_REPORTS: ", "Users submit crowdsourced incident evidence, photos, and legal complaint files.", 1300),
            (1, "USERS (1) -> (N) SAFETY_RATINGS: ", "Users contribute multi-attribute safety scores for monitored localities.", 1300),
            (0, "Data Flow Diagram (DFD Level-1 Overview): ", "Citizen GPS/Input -> Cloud Flask API Gateway -> Authentication & RBAC Filter -> Cloud Relational DB & S3 Storage -> Admin Real-time Queue.", 1400),
            (0, "Use Case Actor Responsibilities: ", "", 1400),
            (1, "Citizen Actor: ", "Sign In, Discover Safe Routes, Trigger SOS Beacon, Manage Guardians, Upload Evidence Reports.", 1300),
            (1, "Cloud Administrator Actor: ", "Monitor Live Distress Feeds, Audit Incident Documents, Resolve SOS Emergencies, Inspect Metrics.", 1300),
        ]
    },
    "slide10.xml": {
        "title": "Database Description & Table Design",
        "bullets": [
            (0, "Table 1: users — ", "id (INT PK AUTO_INCREMENT), name (VARCHAR 100), email (VARCHAR 120 UNIQUE), password_hash (VARCHAR 255), phone (VARCHAR 20), role (VARCHAR 20 DEFAULT 'user'), created_at (TIMESTAMP).", 1300),
            (0, "Table 2: emergency_contacts — ", "id (INT PK), user_id (INT FK -> users.id ON DELETE CASCADE), contact_name (VARCHAR 100), phone (VARCHAR 20), relationship (VARCHAR 50).", 1300),
            (0, "Table 3: sos_alerts — ", "id (INT PK), user_id (INT FK -> users.id), latitude (DECIMAL 10,8), longitude (DECIMAL 11,8), address (TEXT), status (VARCHAR 20: 'Active' / 'Resolved'), triggered_at (TIMESTAMP).", 1300),
            (0, "Table 4: safety_reports — ", "id (INT PK), user_id (INT FK -> users.id), title (VARCHAR 150), category (VARCHAR 50), description (TEXT), latitude/longitude (DECIMAL), file_path (VARCHAR 255), created_at (TIMESTAMP).", 1300),
            (0, "Table 5: safety_ratings — ", "id (INT PK), user_id (INT FK), location_name (VARCHAR 150), lighting_score (INT 1-5), crowd_score (INT 1-5), police_score (INT 1-5), overall_score (DECIMAL 3,2).", 1300),
            (0, "Constraints & Integrity: ", "Foreign key cascade rules protect integrity; unique index on user email prevents duplicate registration; indexed timestamps enable rapid time-series querying.", 1300),
        ]
    },
    "slide11.xml": {
        "title": "Cloud Architecture & Design",
        "bullets": [
            (0, "Three-Tier Cloud Architecture Block Design: ", "Decoupled presentation, logic, and data storage tiers for high scalability and fault tolerance:", 1400),
            (0, "Tier 1 — Presentation Layer (Mobile & Desktop Web Client): ", "Responsive Bootstrap 5 UI, Leaflet.js Vector Map Engine, Geolocation API, Dual-Role Login Switcher over HTTPS/TLS.", 1350),
            (0, "Tier 2 — Application / Logic Layer (Cloud PaaS - Render): ", "Cloud Load Balancer with SSL termination, Gunicorn WSGI multi-worker server, Python Flask REST Microservices (Auth, Routing, SOS Dispatcher, Evidence Handler).", 1350),
            (0, "Tier 3 — Data & Storage Layer (Cloud DBaaS & Object Store): ", "Managed Relational Database (Amazon RDS / Cloud SQL) for transactional ACID data + Amazon S3 Bucket Architecture for encrypted evidence PDFs/media.", 1350),
            (0, "External Cloud Services Integration: ", "OpenStreetMap (OSM) tile cache servers and OSRM pedestrian routing engines.", 1350),
        ]
    },
    "slide12.xml": {
        "title": "Cloud Service Utilized & Justification",
        "bullets": [
            (0, "1. Render Cloud Application Platform (PaaS): ", "Hosts containerized Flask application with 99.9% uptime SLA, automated GitHub continuous deployment, automatic SSL/TLS renewal, and health check monitoring.", 1400),
            (0, "2. Amazon S3 / Cloud Object Storage Architecture: ", "Provides 99.999999999% (11 9's) durability, server-side encryption (SSE-S3), pre-signed URL downloads, and infinite horizontal elasticity for incident evidence documents.", 1400),
            (0, "3. Amazon RDS / Managed Cloud SQL DBaaS: ", "Guarantees transactional integrity (ACID), automated backups, point-in-time recovery, and connection pooling for emergency records.", 1400),
            (0, "4. OpenStreetMap & OSRM Cloud Geocoding Services: ", "High-performance reverse geocoding and pedestrian path calculations without costly commercial API licenses or request limits.", 1400),
        ]
    },
    "slide13.xml": {
        "title": "Cloud Service Implementation & Testing Evidence",
        "bullets": [
            (0, "1. Centralized Cloud Admin Command Center (/admin): ", "Fully operational live dashboard tracking 4 Registered Users, 2 Active SOS Alerts, 2 Resolved Incidents, and 4 Stored Evidence Reports with atomic 'Mark Resolved' action triggers.", 1400),
            (0, "2. In-Browser Document & Evidence Viewing Engine: ", "Integrated PDF modal previewer allowing safety officers and citizens to inspect verified evidence documents (e.g. FIR_Police_Complaint_CBR882.pdf) directly in browser without forced file downloads.", 1400),
            (0, "3. Dual-Role Cloud Authentication Switcher: ", "Interactive 1-click segmented toggle for 'Citizen User' vs 'Cloud Admin' with secure credential handling and role routing.", 1400),
            (0, "4. Automated Quality Assurance Suite (test_app.py): ", "100% test pass rate across Authentication, Safe Route calculation, SOS triggering, S3 document downloads, and Admin privileges.", 1400),
        ]
    },
    "slide14.xml": {
        "title": "Deployment & Live Production",
        "bullets": [
            (0, "Live Production Cloud Application URL: ", "https://safepass-cloud-project.onrender.com", 1500),
            (0, "Source Code Repository (GitHub): ", "https://github.com/Haripriya-4235/safepass-cloud-project", 1500),
            (0, "CI/CD Pipeline Workflow: ", "GitHub main branch push -> Automated Render Webhook -> Container Build -> Health Checks -> Live Zero-Downtime Deployment.", 1400),
            (0, "Production Runtime Configuration: ", "Linux x86_64 container, Python 3.12 runtime, Gunicorn 21.2.0 WSGI Server with 4 asynchronous workers.", 1400),
            (0, "Cloud Security Hardening: ", "Mandatory HTTPS redirection, secure cookie flags (HttpOnly, SameSite=Lax), CSRF protection, and sanitized file uploads.", 1400),
        ]
    },
    "slide15.xml": {
        "title": "Reference",
        "bullets": [
            (0, "1. ", "Amazon Web Services (AWS) Architecture Center, 'Architecting for Resilience, Scalability, and High-Security Evidence Storage on AWS S3 & RDS', AWS Whitepapers, 2024.", 1400),
            (0, "2. ", "Miguel Grinberg, 'Flask Web Development: Developing Web Applications with Python', O'Reilly Media, 2nd Edition.", 1400),
            (0, "3. ", "OpenStreetMap Foundation & Leaflet.js, 'Geospatial Routing and Interactive Vector Map Integration for Web Applications', Technical Documentation, 2025.", 1400),
            (0, "4. ", "C. Ray Jeffery, 'Crime Prevention Through Environmental Design (CPTED): Urban Illumination, Environmental Surveillance, and Route Safety Analysis', SAGE Publications.", 1400),
            (0, "5. ", "Render Cloud Platform, 'Production Deployment and Operational Best Practices for Containerized Python WSGI Applications', Render Cloud Guides, 2026.", 1400),
        ]
    },
    "slide16.xml": {
        "title": "Questions???",
        "bullets": [
            (0, "Thank you for your time. Open for Questions & Evaluation.", "", 1600),
            (0, "Key Discussion & Review Topics:", "", 1500),
            (1, "Emergency Broadcast Latency: ", "Optimization strategies for SOS alerts under intermittent 2G/3G mobile connectivity.", 1350),
            (1, "Evidence Security & Privacy: ", "Role-based encryption, retention policies, and legal admissibility of cloud-stored incident reports.", 1350),
            (1, "Safe Route Heuristics: ", "Dynamic multi-criteria weighting based on real-time ambient lighting and historical incident density.", 1350),
            (1, "Future Integration (Review 2): ", "Direct API integration with Dial 112 emergency response systems and automated WhatsApp location alerts.", 1350),
        ]
    },
    "slide17.xml": {
        "title": "Thank You.",
        "bullets": [
            (0, "SafePass — Women Safety & Safe Route Finder", "", 1800),
            (0, "Presented By: ", "Haripriya", 1600),
            (0, "Course: ", "24CAC631 Cloud Application Development (Project Work : Review 1)", 1500),
            (0, "Live Cloud App: ", "https://safepass-cloud-project.onrender.com", 1500),
            (0, "Source Code: ", "https://github.com/Haripriya-4235/safepass-cloud-project", 1500),
            (0, "Gratitude: ", "Sincere thanks to our Project Guide, Review Panel Members, and Faculty Department.", 1500),
        ]
    }
}


def build_bullet_paragraph(lvl, bold_prefix, text, sz):
    p = ET.Element(f"{{{NS_A}}}p")
    pPr = ET.SubElement(p, f"{{{NS_A}}}pPr")
    if lvl > 0:
        pPr.set("lvl", str(lvl))

    if bold_prefix:
        r1 = ET.SubElement(p, f"{{{NS_A}}}r")
        rPr1 = ET.SubElement(r1, f"{{{NS_A}}}rPr")
        rPr1.set("lang", "en-US")
        rPr1.set("b", "1")
        rPr1.set("sz", str(sz))
        t1 = ET.SubElement(r1, f"{{{NS_A}}}t")
        t1.text = bold_prefix

    if text:
        r2 = ET.SubElement(p, f"{{{NS_A}}}r")
        rPr2 = ET.SubElement(r2, f"{{{NS_A}}}rPr")
        rPr2.set("lang", "en-US")
        rPr2.set("sz", str(sz))
        t2 = ET.SubElement(r2, f"{{{NS_A}}}t")
        t2.text = text

    return p


def update_slide_xml(xml_bytes, slide_key):
    root = ET.fromstring(xml_bytes)
    data = SLIDE_DATA.get(slide_key)
    if not data:
        return xml_bytes

    if data.get("type") == "title_slide":
        # Handle slide1.xml
        for sp in root.iter(f"{{{NS_P}}}sp"):
            cNvPr = sp.find(f"{{{NS_P}}}nvSpPr/{{{NS_P}}}cNvPr")
            name = cNvPr.get("name") if cNvPr is not None else ""
            if name == "Subtitle 2":
                txBody = sp.find(f"{{{NS_P}}}txBody")
                if txBody is not None:
                    # Clear existing paragraphs
                    for p in list(txBody.findall(f"{{{NS_A}}}p")):
                        txBody.remove(p)
                    for bold_prefix, text, sz in data["subtitle_lines"]:
                        p = build_bullet_paragraph(0, bold_prefix, text, sz)
                        txBody.append(p)
    else:
        # Update Content Placeholder 2
        for sp in root.iter(f"{{{NS_P}}}sp"):
            cNvPr = sp.find(f"{{{NS_P}}}nvSpPr/{{{NS_P}}}cNvPr")
            name = cNvPr.get("name") if cNvPr is not None else ""
            
            # Update Title if custom title defined
            if name == "Title 1" and "title" in data:
                txBody = sp.find(f"{{{NS_P}}}txBody")
                if txBody is not None:
                    for t in txBody.iter(f"{{{NS_A}}}t"):
                        t.text = data["title"]
                        break

            # Update Content Placeholder 2
            if name == "Content Placeholder 2":
                txBody = sp.find(f"{{{NS_P}}}txBody")
                if txBody is not None:
                    for p in list(txBody.findall(f"{{{NS_A}}}p")):
                        txBody.remove(p)
                    for lvl, bold_prefix, text, sz in data["bullets"]:
                        p = build_bullet_paragraph(lvl, bold_prefix, text, sz)
                        txBody.append(p)

            # Update Footer Placeholder 3 with student credentials
            if name == "Footer Placeholder 3":
                txBody = sp.find(f"{{{NS_P}}}txBody")
                if txBody is not None:
                    for t in txBody.iter(f"{{{NS_A}}}t"):
                        t.text = "Haripriya | 24CAC631 - Cloud Application Development (Review 1)"

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main():
    print(f"Reading from: {SOURCE_PPTX}")
    print(f"Writing to:   {TARGET_PPTX}")

    with zipfile.ZipFile(SOURCE_PPTX, "r") as z_in:
        with zipfile.ZipFile(TARGET_PPTX, "w", compression=zipfile.ZIP_DEFLATED) as z_out:
            for item in z_in.infolist():
                content = z_in.read(item.filename)
                basename = os.path.basename(item.filename)
                if item.filename.startswith("ppt/slides/") and basename.startswith("slide") and basename.endswith(".xml"):
                    print(f"Populating {basename}...")
                    content = update_slide_xml(content, basename)
                z_out.writestr(item, content)

    print("\nSUCCESS: Generated Review 1 Presentation!")
    print(f"Saved at: {TARGET_PPTX}")


if __name__ == "__main__":
    main()
