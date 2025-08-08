# 📝 Blog Platform

A full-featured blog platform built with **Python**, and **Django REST Framework**.  
This platform allows users to create, edit, and share blog posts, interact through comments and likes, and explore trending content.

---

## 🚀 Features


- **User Registration & Authentication** (`register` app)
- **Real-time / API Chat System** (`chat` app)
- **Friend / Follower Connections** (`connection` app)
- **Public & Private Groups** (`group` app)
- **Blog Posts, Comments, Likes** (`post` app)
- **Explore Feed & Search**
- **API-ready for Web & Mobile Integration**

---

## 🛠 Tech Stack

**Backend:** Python, Django, Django REST Framework  
**Database:** Sqlite3
**Authentication:** Token authentication
**Others:** DRF Pagination, Filtering, Django ORM

---

## 📂 Project Structure


│
├── testapi/ # Main project folder
│ ├── settings.py # Project settings
│ ├── urls.py # Root URL configuration
│ ├── asgi.py / wsgi.py # Entry points for deployment
│ └── ...
│
├── register/ # User registration, login, profile
├── chat/ # Chat & messaging system
├── connection/ # Friend/follower connections
├── group/ # Groups management
├── post/ # Blog posts, comments, likes
│
├── requirements.txt # Dependencies
├── manage.py # Django CLI
└── README.md # Documentation

