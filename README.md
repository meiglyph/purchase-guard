# PurchaseGuard

PurchaseGuard is a simple web application for managing purchase information, return deadlines, and warranty expiration dates.

It helps users keep track of purchased items and quickly check whether a return or warranty deadline is approaching or has already expired.

## Features

- Add purchase information
- View all purchases
- View purchase details
- Edit purchase information
- Delete purchases
- Search purchases by item name
- Sort purchases by creation date, purchase date, or return deadline
- Display return deadline status
- Display warranty expiration status
- Return a 404 response for missing purchases
- Run automated tests with pytest
- Run tests automatically with GitHub Actions

## Technologies

- Python
- Flask
- SQLite
- SQLAlchemy
- Flask-SQLAlchemy
- pytest
- GitHub Actions

## Requirements

- Python 3.14
- pip
- Git

## Installation

Clone the repository:

```bash
git clone git@github.com:meiglyph/purchase-guard.git
cd purchase-guard
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

macOS and Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the Application

Start the Flask application:

```bash
python app.py
```

Open the following URL in your browser:

```text
http://127.0.0.1:5000
```

The SQLite database is created automatically when the application starts.

## Running the Tests

Run all automated tests:

```bash
python -m pytest -v
```

The tests use a temporary SQLite database and do not modify the development database.

## Automated Testing

GitHub Actions automatically runs the test suite when:

- Code is pushed to the `main` branch
- A pull request targets the `main` branch

The workflow configuration is located at:

```text
.github/workflows/tests.yml
```

## Project Structure

```text
purchase-guard/
├── .github/
│   └── workflows/
│       └── tests.yml
├── instance/
│   └── purchase_guard.db
├── templates/
│   ├── index.html
│   ├── purchase_detail.html
│   └── purchase_form.html
├── tests/
│   └── test_app.py
├── app.py
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License.
