from datetime import date, timedelta
import pytest
from app import Purchase, create_app, db


@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test_purchase_guard.db"

    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": (
                f"sqlite:///{database_path}"
            ),
            "SECRET_KEY": "test-secret-key",
        }
    )

    with test_app.app_context():
        db.create_all()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def add_purchase(
    client,
    item_name="Test Laptop",
    purchase_date="2026-07-28",
):
    return client.post(
        "/purchases/new",
        data={
            "item_name": item_name,
            "purchase_date": purchase_date,
        },
        follow_redirects=True,
    )


def test_home_page_returns_success(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"PurchaseGuard" in response.data


def test_create_purchase(client, app):
    response = add_purchase(client)

    assert response.status_code == 200
    assert b"Test Laptop" in response.data

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase).where(
                Purchase.item_name == "Test Laptop"
            )
        ).scalar_one()

        assert purchase.purchase_date.isoformat() == (
            "2026-07-28"
        )


def test_display_purchase_detail(client, app):
    add_purchase(client)

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()
        purchase_id = purchase.id

    response = client.get(
        f"/purchases/{purchase_id}"
    )

    assert response.status_code == 200
    assert b"Test Laptop" in response.data


def test_edit_purchase(client, app):
    add_purchase(client)

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()
        purchase_id = purchase.id

    response = client.post(
        f"/purchases/{purchase_id}/edit",
        data={
            "item_name": "Updated Laptop",
            "purchase_date": "2026-07-29",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Updated Laptop" in response.data

    with app.app_context():
        updated_purchase = db.session.get(
            Purchase,
            purchase_id,
        )

        assert updated_purchase.item_name == (
            "Updated Laptop"
        )
        assert updated_purchase.purchase_date.isoformat() == (
            "2026-07-29"
        )


def test_delete_purchase(client, app):
    add_purchase(client)

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()
        purchase_id = purchase.id

    response = client.post(
        f"/purchases/{purchase_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Test Laptop" not in response.data

    with app.app_context():
        deleted_purchase = db.session.get(
            Purchase,
            purchase_id,
        )

        assert deleted_purchase is None


def test_search_filters_by_item_name(client):
    add_purchase(
        client,
        item_name="Mechanical Keyboard",
    )
    add_purchase(
        client,
        item_name="Wireless Mouse",
    )

    response = client.get("/?q=Keyboard")

    assert response.status_code == 200
    assert b"Mechanical Keyboard" in response.data
    assert b"Wireless Mouse" not in response.data


def test_missing_purchase_returns_404(client):
    response = client.get("/purchases/9999")

    assert response.status_code == 404

def test_create_purchase_rejects_negative_price(
    client,
    app,
):
    response = client.post(
        "/purchases/new",
        data={
            "item_name": "Test Laptop",
            "purchase_date": "2026-07-30",
            "price": "-1000",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Price cannot be negative." in response.data

    with app.app_context():
        purchases = db.session.execute(
            db.select(Purchase)
        ).scalars().all()

        assert purchases == []


def test_edit_purchase_rejects_negative_price(
    client,
    app,
):
    add_purchase(client)

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()
        purchase_id = purchase.id

    response = client.post(
        f"/purchases/{purchase_id}/edit",
        data={
            "item_name": "Test Laptop",
            "purchase_date": "2026-07-30",
            "price": "-1000",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Price cannot be negative." in response.data

    with app.app_context():
        purchase = db.session.get(
            Purchase,
            purchase_id,
        )

        assert purchase.price is None

def test_create_purchase_rejects_return_deadline_before_purchase_date(
    client,
    app,
):
    response = client.post(
        "/purchases/new",
        data={
            "item_name": "Test Laptop",
            "purchase_date": "2026-07-30",
            "return_deadline": "2026-07-29",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        b"Return deadline cannot be before purchase date."
        in response.data
    )

    with app.app_context():
        purchases = db.session.execute(
            db.select(Purchase)
        ).scalars().all()

        assert purchases == []


def test_create_purchase_rejects_warranty_end_before_purchase_date(
    client,
    app,
):
    response = client.post(
        "/purchases/new",
        data={
            "item_name": "Test Laptop",
            "purchase_date": "2026-07-30",
            "warranty_end_date": "2026-07-29",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        b"Warranty end date cannot be before purchase date."
        in response.data
    )

    with app.app_context():
        purchases = db.session.execute(
            db.select(Purchase)
        ).scalars().all()

        assert purchases == []


def test_edit_purchase_rejects_return_deadline_before_purchase_date(
    client,
    app,
):
    add_purchase(client)

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()
        purchase_id = purchase.id

    response = client.post(
        f"/purchases/{purchase_id}/edit",
        data={
            "item_name": "Test Laptop",
            "purchase_date": "2026-07-30",
            "return_deadline": "2026-07-29",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        b"Return deadline cannot be before purchase date."
        in response.data
    )

    with app.app_context():
        purchase = db.session.get(
            Purchase,
            purchase_id,
        )

        assert purchase.return_deadline is None


def test_edit_purchase_rejects_warranty_end_before_purchase_date(
    client,
    app,
):
    add_purchase(client)

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()
        purchase_id = purchase.id

    response = client.post(
        f"/purchases/{purchase_id}/edit",
        data={
            "item_name": "Test Laptop",
            "purchase_date": "2026-07-30",
            "warranty_end_date": "2026-07-29",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert (
        b"Warranty end date cannot be before purchase date."
        in response.data
    )

    with app.app_context():
        purchase = db.session.get(
            Purchase,
            purchase_id,
        )

        assert purchase.warranty_end_date is None

def test_create_purchase_preserves_input_after_validation_error(
    client,
):
    response = client.post(
        "/purchases/new",
        data={
            "item_name": "Wireless Headphones",
            "category": "Electronics",
            "store_name": "Example Store",
            "purchase_date": "2026-07-30",
            "price": "-1000",
            "return_deadline": "2026-08-10",
            "warranty_end_date": "2027-07-30",
            "notes": "Keep the receipt.",
        },
    )

    assert response.status_code == 200
    assert b'Wireless Headphones' in response.data
    assert b'Electronics' in response.data
    assert b'Example Store' in response.data
    assert b'2026-07-30' in response.data
    assert b'-1000' in response.data
    assert b'2026-08-10' in response.data
    assert b'2027-07-30' in response.data
    assert b'Keep the receipt.' in response.data


def test_edit_purchase_preserves_input_after_validation_error(
    client,
    app,
):
    add_purchase(client)

    with app.app_context():
        purchase = db.session.execute(
            db.select(Purchase)
        ).scalar_one()
        purchase_id = purchase.id

    response = client.post(
        f"/purchases/{purchase_id}/edit",
        data={
            "item_name": "Edited Laptop",
            "category": "Computers",
            "store_name": "New Store",
            "purchase_date": "2026-07-30",
            "price": "-2000",
            "return_deadline": "2026-08-15",
            "warranty_end_date": "2027-07-30",
            "notes": "Edited notes.",
        },
    )

    assert response.status_code == 200
    assert b'Edited Laptop' in response.data
    assert b'Computers' in response.data
    assert b'New Store' in response.data
    assert b'2026-07-30' in response.data
    assert b'-2000' in response.data
    assert b'2026-08-15' in response.data
    assert b'2027-07-30' in response.data
    assert b'Edited notes.' in response.data

def test_return_status_tone():
    purchase = Purchase(
        item_name="Test Item",
        purchase_date=date.today(),
    )

    purchase.return_deadline = None
    assert purchase.return_status_tone == "neutral"

    purchase.return_deadline = date.today() - timedelta(days=1)
    assert purchase.return_status_tone == "danger"

    purchase.return_deadline = date.today()
    assert purchase.return_status_tone == "warning"

    purchase.return_deadline = date.today() + timedelta(days=1)
    assert purchase.return_status_tone == "warning"

    purchase.return_deadline = date.today() + timedelta(days=2)
    assert purchase.return_status_tone == "success"

def test_warranty_status_tone():
    purchase = Purchase(
        item_name="Test Item",
        purchase_date=date.today(),
    )

    purchase.warranty_end_date = None
    assert purchase.warranty_status_tone == "neutral"

    purchase.warranty_end_date = date.today() - timedelta(days=1)
    assert purchase.warranty_status_tone == "danger"

    purchase.warranty_end_date = date.today()
    assert purchase.warranty_status_tone == "warning"

    purchase.warranty_end_date = date.today() + timedelta(days=1)
    assert purchase.warranty_status_tone == "warning"

    purchase.warranty_end_date = date.today() + timedelta(days=2)
    assert purchase.warranty_status_tone == "success"