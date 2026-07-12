<div align="center">
  <img src="https://img.icons8.com/color/96/000000/django.png" alt="Django Logo"/>
  <h1>🛍️ PickUp E-Commerce Engine</h1>
  <p>
    <strong>A comprehensive, high-performance, and scalable e-commerce platform built on Django.</strong>
  </p>
  
  <p>
    <a href="#features"><img src="https://img.shields.io/badge/Features-Extensive-success?style=for-the-badge&logo=appveyor" alt="Features"/></a>
    <a href="#tech-stack"><img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/></a>
    <a href="#tech-stack"><img src="https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/></a>
    <a href="#license"><img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="License"/></a>
  </p>
</div>

<br />

> **PickUp** is a production-ready e-commerce solution engineered for reliability and user experience. Featuring advanced inventory management, automated PDF invoicing, and dynamic content rendering directly from the Django Admin interface.

---

## 📑 Table of Contents
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🗄️ Core Architecture](#️-core-architecture)
- [🚀 Getting Started](#-getting-started)
- [📖 Additional Documentation](#-additional-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Key Features

| 🛒 **Storefront & Shopping** | ⚙️ **Backend & Administration** |
| :--- | :--- |
| **Persistent Cart & Wishlist**: Session-based seamless shopping experience. | **Dynamic Catalog**: Category & product management with auto-SKU generation. |
| **Order Tracking**: Confirmed, Shipped, Delivered, and Cancelled statuses. | **Real-Time Inventory**: Automated stock tracking and alerts. |
| **Custom Authentication**: Specialized user models for e-commerce profiles. | **Automated Invoices**: WeasyPrint-powered professional PDF generation. |
| **User Engagement**: Integrated product feedback, reviews, and contact forms. | **Headless CMS Capabilities**: Configurable site banners, galleries, and team members. |

---

## 🛠️ Tech Stack

<div align="center">
  <table>
    <tr>
      <td align="center" width="96">
        <img src="https://techstack-generator.vercel.app/python-icon.svg" alt="icon" width="65" height="65" />
        <br>Python
      </td>
      <td align="center" width="96">
        <img src="https://techstack-generator.vercel.app/django-icon.svg" alt="icon" width="65" height="65" />
        <br>Django
      </td>
      <td align="center" width="96">
        <img src="https://techstack-generator.vercel.app/js-icon.svg" alt="icon" width="65" height="65" />
        <br>JavaScript
      </td>
      <td align="center" width="96">
        <img src="https://techstack-generator.vercel.app/mysql-icon.svg" alt="icon" width="65" height="65" />
        <br>SQL
      </td>
    </tr>
  </table>
</div>

- **Core Backend:** Python 3.8+, Django 4.x
- **Database Architecture:** SQLite (Development) / PostgreSQL (Production)
- **Document Generation:** WeasyPrint (PDF Invoices)
- **Frontend Assets:** HTML5, CSS3, Vanilla JS, Bootstrap

---

## 🗄️ Core Architecture

The platform is built on a highly relational and modular architecture:

- 🔐 **Authentication:** Custom `User` model inheriting from `AbstractBaseUser`.
- 📦 **Catalog & Stock:** `Category`, `Product`, and `Inventory` proxy models for scalable stock logic.
- 🛍️ **Cart & Sessions:** Custom `Cart`, `CartItem`, and `Wishlist` utilities for persistent sessions.
- 💳 **Order Fulfillment:** Secure checkout workflow managed via `Order` and `OrderItem`.
- 📝 **Dynamic Content (CMS):** `ContactConfig`, `Announcement`, `Gallery`, and `TeamMember` apps controllable via the Admin Panel.

---

## 🚀 Getting Started

### Prerequisites
Before you begin, ensure you have the following installed:
- **Python 3.8** or higher
- **WeasyPrint System Dependencies:** `Cairo`, `Pango`, and `GDK-PixBuf`

### Installation Guide

**1. Clone the repository:**
```bash
git clone https://github.com/sharik10ahmed/Project_5_Django.git
cd Project_5_Django/ecommerce
```

**2. Initialize & activate virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```
> *For detailed WeasyPrint installation instructions on Windows or Linux, see the [ecommerce/README.md](ecommerce/README.md).*

**4. Setup the database:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**5. Create a superuser:**
```bash
python manage.py createsuperuser
```

**6. Launch the server:**
```bash
python manage.py runserver
```

> **Storefront:** `http://127.0.0.1:8000`  
> **Admin Panel:** `http://127.0.0.1:8000/admin`

---

## 📖 Additional Documentation

For module-specific configurations, troubleshooting, and CI/CD setup, refer to the secondary guide:
- 🔗 **[WeasyPrint PDF Generator & Environment Setup](ecommerce/README.md)**

---

## 🤝 Contributing

We welcome contributions! Please follow these steps to contribute:
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

<div align="center">
  <p>Crafted with ❤️ and clean code architecture. </p>
</div>
