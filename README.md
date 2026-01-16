# Task Manager API

A simple task management API built with Python FastAPI.

## Features

- Create, read, update, delete tasks
- User authentication with JWT
- Task priorities and due dates
- RESTful API design

## Quick Start

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## API Endpoints

- `POST /api/auth/login` - User login
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create a task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

## License

MIT
