# 📦 Registration Bot with Ollama

## Overview
A FastAPI service that lets users register, retrieve, update, and delete user records via a conversational LLM interface. The LLM runs locally with **Ollama** (default model: `llama3.1`).

---

## 📋 Prerequisites
- **Python 3.11+**
- **Ollama** installed and running (`ollama serve`)
- **PostgreSQL** (or any DB supported by SQLAlchemy) – set `DATABASE_URL` in a `.env` file

---

## 🚀 Installation
```bash
# Clone the repo
git clone <repo-url>
cd py_dev

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🦙 Ollama Model Setup
```bash
# Pull the recommended model (llama3.1) – works best with native tool calling
ollama pull llama3.1
```
If you prefer another model that supports tool calling, replace `mistral` with the model name.

---

## ⚙️ Configuration
Create a `.env` file in the project root:
```dotenv
DATABASE_URL=postgresql+psycopg2://user:password@localhost/registration_db
```
Run the migrations (or let SQLAlchemy create tables on first start):
```bash
# The first request will auto‑create tables, or you can use Alembic if set up.
```

---

## ▶️ Running the API
```bash
uvicorn app.main:app --reload
```
The service will be available at `http://127.0.0.1:8000`.

### Endpoints

#### User Management
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/users/` | Create a new user registration |
| `GET` | `/users/` | List all registered users |
| `GET` | `/users/{user_id}` | Get a specific user by UUID |
| `PUT` | `/users/{user_id}` | Update a user's information |
| `DELETE` | `/users/{user_id}` | Delete a user |

#### Chat
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat/{session_id}` | Conversational endpoint – send a JSON `{ "message": "…" }` |

#### Documentation
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

---

## 🧪 Testing

### Automated tests
Automated tests are implemented using `pytest` and `FastAPI TestClient`.
```bash
# Run all tests
python -m pytest test_conversational.py
```

### Manual testing with Postman
A Postman collection is included in the repository: `postman_collection.json`.
1. Open Postman.
2. Click **Import** and select `postman_collection.json`.
3. The collection "Registration Bot API" will appear.
4. You can now execute requests for creating, listing, updating, and deleting users, as well as chatting with the bot.

### Example flow
1. **Start a session**
   ```json
   POST /chat/session1
   { "message": "Hi! I want to register a new user" }
   ```
   → Bot asks for missing fields.
2. **Provide details**
   ```json
   POST /chat/session1
   { "message": "Name: Alice, email: alice@example.com, phone: 5551234567, DOB: 1990-01-01" }
   ```
   → Bot creates the registration and returns a success message.

---

## 🧹 Clean‑up
```bash
# Remove the pulled model if you need space
ollama rm mistral
```

---

## 📄 License
MIT – feel free to adapt and extend.
# auto_chat
