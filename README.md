# 🛒 Django E-Commerce & Inventory Platform

<div align="center">
  <p>A comprehensive, robust, and highly customizable e-commerce solution built with Django.</p>
</div>

---

## 📌 Overview

This project is a fully-featured e-commerce platform designed to provide a seamless shopping experience while offering powerful backend management tools. From dynamic product catalogs and inventory tracking to automated PDF invoice generation, the platform is engineered with clean architecture, scalability, and maintainability in mind.

It serves as a professional showcase of advanced Django development, custom database modeling, and third-party integrations.

## ✨ Key Features

- **Advanced Product Management:** Dynamic categories, automatic SKU generation, and real-time inventory tracking.
- **Secure Authentication:** Custom user model tailored for e-commerce, including profile and address management.
- **Seamless Shopping Experience:** Persistent shopping cart, wishlist functionality, and streamlined checkout.
- **Order Fulfillment:** Comprehensive order tracking system (Confirmed, Shipped, Delivered, Cancelled).
- **Automated Invoicing:** Professional PDF invoice generation powered by WeasyPrint.
- **Customer Interaction:** Integrated product feedback, review system, and contact messaging.
- **Dynamic Content Management:** Configurable site elements including announcements, team members, galleries, and store contact details directly via the Django admin interface.

## 🛠️ Technology Stack

- **Backend:** Python, Django
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **PDF Generation:** WeasyPrint
- **Frontend Assets:** HTML5, CSS3, JavaScript (Vanilla/Bootstrap)

## 🗄️ Core Architecture

The data architecture is modular and highly relational, designed to handle complex e-commerce workflows:

- **Authentication:** Custom `User` model extending `AbstractBaseUser`.
- **Catalog:** `Category`, `Product`, and an `Inventory` proxy model for focused stock management.
- **Shopping:** `Cart`, `CartItem`, and `Wishlist` session utilities.
- **Transactions:** `Order` and `OrderItem` for checkout and fulfillment.
- **Customer Engagement:** `Feedback` and `ContactMessage`.
- **CMS Capabilities:** `ContactConfig`, `Announcement`, `Gallery`, and `TeamMember` for dynamic frontend content.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- System dependencies for WeasyPrint (Cairo, Pango, GDK-PixBuf)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sharik10ahmed/Project_5_Django.git
   cd Project_5_Django/ecommerce
   ```

2. **Initialize a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: For detailed instructions on installing WeasyPrint system dependencies on Windows/Linux, please refer to the `ecommerce/README.md` guide.*

4. **Prepare the database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create an administrator account:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Launch the application:**
   ```bash
   python manage.py runserver
   ```
   - Storefront: `http://127.0.0.1:8000`
   - Admin Panel: `http://127.0.0.1:8000/admin`

## 📖 Additional Documentation

Specific guides for module configurations, such as the WeasyPrint PDF generator setup, can be found in the [ecommerce/README.md](ecommerce/README.md) file.

## 🤝 Contributing

Contributions, issues, and feature requests are always welcome. Please feel free to check the issues page or submit a pull request if you'd like to improve the project.

---
*Developed with a focus on clean code and robust architecture.*
