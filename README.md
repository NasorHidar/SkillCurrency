<div align="center">

<img src="static/images/logo.png" alt="SkillCurrency Logo" width="90" height="90" style="border-radius:12px;">

# SkillCurrency

**Bangladesh's Premier Peer-to-Peer Skill Exchange Marketplace**

[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-0c4b33?logo=django&logoColor=white)](https://djangoproject.com)
[![Channels](https://img.shields.io/badge/Django%20Channels-4.x-0c4b33)](https://channels.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-a855f7)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-22c55e)]()

*Trade coding for design. Teach English for Python. Or simply get paid for what you know.*

[Report Bug](https://github.com/NasorHidar/SkillCurrency/issues) · [Request Feature](https://github.com/NasorHidar/SkillCurrency/issues)

</div>

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [URL Reference](#-url-reference)
- [Core Modules](#-core-modules)
- [Admin Panel](#-admin-panel)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 About the Project

**SkillCurrency** is a full-stack freelance marketplace built specifically for Bangladesh's growing community of digital talent. It goes beyond a typical job board by enabling **skill barter** — users can trade expertise directly without monetary exchange.

> A Python developer can teach coding in exchange for logo design. A marketing expert can offer SEO work in return for video editing lessons. No cash required.

The platform supports both **Paid Services** and **Skill Barter** transactions, backed by a secure workspace, real-time encrypted messaging, milestone tracking, and an AI-powered skill assessment system.

---

## ✨ Key Features

### 🛒 Job Marketplace
- Browse 20+ seeded job listings across multiple categories
- Advanced filtering by **category**, **job type** (Paid / Barter), **budget range**
- Full-text search across titles and descriptions
- **Smart Match** — surfaces jobs aligned with your verified skill badges first

### 🧠 Skill Lab (AI Assessment)
- AI-generated MCQ assessments powered by **Google Gemini**
- Pass → earn a **Skill Badge** with level (1–3)
- Badges displayed on your public profile and power Smart Match

### 🔐 Identity Vault
- Upload NID / TIN documents for identity verification
- Admin reviews and approves via the admin panel
- Verified users get a ✅ badge and unlock full platform trust

### 💼 Workspace
- Accepted proposals create a **Service Agreement** with a shared workspace
- Real-time encrypted chat via **Django Channels** + WebSocket
- **Milestone tracking**: Pending → In Progress → In Review → Completed
- Messages encrypted end-to-end with **Fernet symmetric encryption**

### 💳 Financial Hub
- Personal wallet with full transaction history
- **Top-up** via bKash / SSLCommerz (simulated, production-ready interface)
- **Withdraw** funds with balance validation and atomic DB transactions
- **Downloadable receipts** for every completed transaction

### 👤 User Dashboard
- Weekly activity chart (proposals + job posts per day, real DB data)
- Live stats: wallet balance, active orders, badge count, ID verification status
- Withdraw modal directly from profile page

### 🛠️ Admin Panel
- Auto-sync: ticking `is_identity_verified` → status → `Approved` + user notified
- Full **Job Post management**: list, search, filter, edit, delete
- Inline **Proposal viewer** inside each job record
- Bulk actions: Approve / Reject identities, Mark Open / Completed

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, Django 6.0 |
| **Real-time** | Django Channels 4.x, Daphne (ASGI), WebSocket |
| **Database** | SQLite (dev) — PostgreSQL-ready |
| **AI** | Google Gemini API (`google-generativeai`) |
| **Encryption** | `cryptography` (Fernet) for workspace messages |
| **Frontend** | Vanilla HTML5, CSS3, FontAwesome 6 |
| **Fonts** | Google Fonts — Inter |
| **Auth** | Django `AbstractUser` with custom `CustomUser` model |
| **Payments** | bKash / SSLCommerz (simulated hooks) |

---

## 🏗 System Architecture

```
SkillCurrency/
├── skill_currency/          # Django project config
│   ├── settings.py          # LOGIN_URL, CHANNELS, ENCRYPTION_KEY, etc.
│   ├── urls.py              # Root URL dispatcher
│   ├── asgi.py              # ASGI entry point (Daphne + Channels)
│   └── routing.py           # WebSocket URL routing
│
├── accounts/                # Core application (single-app architecture)
│   ├── models.py            # All 10 data models
│   ├── views.py             # All view logic
│   ├── admin.py             # Custom admin (identity sync, job CRUD)
│   ├── urls.py              # All URL patterns
│   ├── consumers.py         # WebSocket chat consumer
│   ├── context_processors.py
│   ├── management/commands/
│   │   └── seed_jobs.py     # 20 realistic seeded job posts
│   └── templates/accounts/
│       ├── base.html
│       ├── landing.html
│       ├── marketplace_feed.html
│       ├── _job_card_v3.html
│       ├── job_detail.html
│       ├── public_profile.html
│       ├── financial_hub.html
│       ├── workspace.html
│       └── ...
│
└── static/
    ├── css/style.css        # Full design system
    ├── js/                  # WebSocket client
    └── images/
```

### Data Model Relationships

```
CustomUser
  ├── SkillBadge (many)     → SkillCategory
  ├── JobPost (many)        → SkillCategory
  │     └── JobProposal (many) → CustomUser (applicant)
  │           └── ServiceAgreement (1:1)
  │                 ├── Milestone (many)
  │                 └── EncryptedMessage (many)
  ├── Transaction (many)
  └── Notification (many)
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- pip
- Git

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/NasorHidar/SkillCurrency.git
cd SkillCurrency

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Create a .env file or set these directly:
#   GEMINI_API_KEY=your_google_gemini_key
#   ENCRYPTION_KEY=your_fernet_key   (auto-generated if omitted)

# 5. Apply migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Start the dev server
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

### Seeding the Database

```bash
python manage.py seed_jobs
```

Creates:
- **8 Skill Categories** (Web Dev, Design, Python, Agile, UX/UI, etc.)
- **20 Job Posts** — mix of Paid Service and Skill Barter
- Sample users (`buyer1`, `skilled1`, …) with password `testpass123`

The command is **idempotent** — safe to run multiple times.

---

## 📁 URL Reference

| URL | Name | Description |
|---|---|---|
| `/` | `landing_page` | Marketing homepage |
| `/signup/` | `signup` | User registration |
| `/signin/` | `signin` | Login |
| `/signout/` | `signout` | Logout |
| `/marketplace/` | `marketplace_feed` | Browse all jobs |
| `/marketplace/create/` | `create_job` | Post a new job |
| `/marketplace/job/<id>/` | `job_detail` | View job + submit proposal |
| `/profile/<username>/` | `public_profile` | User dashboard |
| `/skill-lab/` | `skill_lab_dashboard` | AI assessment hub |
| `/identity-vault/` | `identity_vault` | ID verification upload |
| `/financial-hub/` | `financial_hub` | Wallet & transactions |
| `/financial-hub/top-up/` | `top_up_wallet` | Add money to wallet |
| `/financial-hub/withdraw/` | `withdraw_funds` | Withdraw funds |
| `/financial-hub/invoice/<ref>/` | `invoice_receipt` | Transaction receipt |
| `/workspace/<id>/` | `workspace` | Active project workspace |
| `/settings/` | `settings_page` | Account settings |
| `/notifications/` | `notifications_page` | Notification center |
| `/admin/` | — | Django admin panel |

---

## 🔑 Core Modules

### `models.py`

| Model | Purpose |
|---|---|
| `CustomUser` | Extended user: role, wallet, NID, verification status, avatar |
| `SkillCategory` | Category for jobs and badges |
| `SkillBadge` | Earned badge: user ↔ category with level (1–3) |
| `AssessmentQuestion` | MCQ question linked to a category |
| `JobPost` | Job listing with type, budget, status |
| `JobProposal` | Bid submitted by a user on a job |
| `ServiceAgreement` | Contract created when a proposal is accepted |
| `Milestone` | Deliverable inside an agreement |
| `EncryptedMessage` | Fernet-encrypted chat message |
| `Transaction` | Wallet top-up, withdrawal, earnings record |
| `Notification` | In-app notification |

### WebSocket Chat (`consumers.py`)
- Room group: `workspace_<agreement_id>`
- Encrypts every message with `Fernet` before saving
- Only workspace participants can connect (enforced server-side)

---

## 🛡 Admin Panel

Access at `/admin/` with superuser credentials.

### Identity Verification Workflow
```
User uploads NID  →  Status: Pending
Admin ticks ✅ "Is Identity Verified"
       ↓  (save_model hook fires)
verification_status → "Approved"
User gets in-app notification ✅
```

**Bulk actions available:**
- ✅ Approve selected identities
- ❌ Reject selected identities

### Job Post Management
- List view with coloured 💰 Paid / 🔄 Barter badges
- Inline proposals visible inside each job record
- Edit any field or delete any post
- Bulk: **Mark Open**, **Mark Completed**

---

## 🗺 Roadmap

- [x] Custom authentication system
- [x] Job marketplace with Smart Match filtering
- [x] AI skill assessments (Google Gemini)
- [x] Identity verification + admin approval workflow
- [x] Real-time encrypted workspace (WebSocket + Fernet)
- [x] Milestone tracking
- [x] Financial Hub (wallet, top-up, withdraw, receipts)
- [x] Full admin panel with auto-verify sync
- [x] Premium UI (animated hero, glassmorphism, marquee)
- [ ] Live payment gateway (SSLCommerz / bKash)
- [ ] Email notifications (verification, proposals)
- [ ] PostgreSQL production database
- [ ] Docker + docker-compose
- [ ] Deployment (Railway / Render)
- [ ] Rating & review system
- [ ] Mobile PWA

---

## 🤝 Contributing

```bash
# Fork → clone → create branch
git checkout -b feature/your-feature

# Make changes, then
git commit -m "feat: describe your change"
git push origin feature/your-feature

# Open a Pull Request on GitHub
```

Ensure `python manage.py check` passes before submitting.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 👨‍💻 Author

**Nasor Hidar** — [@NasorHidar](https://github.com/NasorHidar)

---

<div align="center">

Built with ❤️ in Bangladesh &nbsp;·&nbsp; Empowering the next generation of digital talent

⭐ **Star this repo if it helped you!**

</div>
