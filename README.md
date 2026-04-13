# O2mation POS System Offline

O2mation Â· POS is a fast, offline-ready Point of Sale system designed for supermarkets, retail stores, and small businesses. It features a modern React-based frontend and a Python/Flask backend, ensuring reliability and performance in offline environments.

## Features

- **Inventory Management**: Track stock levels, manage products, and handle low-stock alerts.
- **Sales & Checkout**: Fast barcode-ready checkout experience with cart management and transaction summaries.
- **Category Management**: Organize products into customizable categories with icons and colors.
- **Vendor Tracking**: Manage supplier information and procurement sources.
- **User Management**: Multi-user support with role-based access control (RBAC).
- **Offline First**: Designed to run locally with high performance and data persistence.
- **Modern UI**: Clean, responsive interface built with React, Tailwind CSS, and Chakra UI (v3).

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Chakra UI.
- **Backend**: Python, Flask, SQLite3.
- **Desktop Wrapper**: Python-based desktop application (located in the `desktop/` folder).

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.10+)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cruzyxd/O2mation-POS-System-Offline.git
   cd O2mation-POS-System-Offline
   ```

2. **Setup Backend**:
   ```bash
   cd backend
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

3. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

1. **Start Backend**:
   ```bash
   cd backend
   python run.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Run as Desktop App** (Optional):
   ```bash
   cd desktop
   python main.py
   ```

## Development

- Use `init_pos_db.py` to reset and initialize the database.
- Use `seed_mock_data.py` to populate the database with test data.

## Brand Identity

This project follows the **O2mation** brand guidelines. The logo is constructed in code using specific typography and the `oxygen.500` (#00E074) dot separator.

---
Created by [cruzyxd](https://github.com/cruzyxd).
