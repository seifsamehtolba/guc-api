
# GUC API

A RESTful backend service powering the [GUC Portal](https://github.com/seifsamehtolba/guc-portal) — a university management system for students, instructors, and administrators at the German University in Cairo (GUC). This API handles authentication, course management, user roles, and administrative operations.

## 🚀 Features

- 🔐 Secure Authentication
- 📚 Course creation, enrollment, and content management
- 📝 Assignment handling and grade viewing
- ⚙️ RESTful structure following clean architecture principles

## 🛠️ Tech Stack

- **Runtime**: Python
- **Framework**: Flask/Selenium

## 📁 Project Structure

```
guc-api/
│
├── controllers/        # Request handlers
├── middleware/         # Auth and error handling
├── models/             # Mongoose schemas
├── routes/             # API endpoints
├── utils/              # Helper functions
├── config/             # DB and server config
├── app.js              # Express app setup
└── server.js           # Entry point
```

## 🔧 Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/seifsamehtolba/guc-api.git
   cd guc-api
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```
4. **Start the server**

   ```bash
   npm run dev
   ```

   Server will run on `http://localhost:5000`

## 📬 API Endpoints (Sample)

| Method | Endpoint              | Description               |
|--------|-----------------------|---------------------------|
| POST   | /api/auth/register    | Register new user         |
| POST   | /api/auth/login       | Authenticate user         |
| GET    | /api/courses          | List all courses          |
| POST   | /api/courses          | Create a new course       |
| PUT    | /api/courses/:id      | Update course info        |
| DELETE | /api/courses/:id      | Delete a course           |

_(Full documentation coming soon)_

## 🤝 Contributing

Pull requests are welcome! If you have ideas for features, improvements, or bug fixes, feel free to open an issue or fork the repo.

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.

---

Let me know if you want me to generate one README that includes both frontend and backend setup together.
