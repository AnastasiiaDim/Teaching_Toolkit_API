# Teaching Toolkit REST API

A lightweight REST API built with FastAPI to manage language school workflows, handle student records, and track completed lessons.

## Features

- **Student Management (CRUD):** Add, view, and delete student profiles.
- **Lesson Tracking:** Log completed lessons tied to specific students with automatic timestamping and static price capturing.
- **Dynamic Calculation:** Quick balance and invoice simulation based on custom lesson counts.
- **Automatic Documentation:** Built-in interactive API playground via Swagger UI.

## Tech Stack

- Python 3.10+
- FastAPI
- Pydantic (Data validation)
- Uvicorn (ASGI server)

---

## Getting Started

### 1. Installation

Clone the repository and install the required dependencies:

```bash
pip install fastapi uvicorn pydantic
