import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "development-secret-key",
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///purchase_guard.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))
    store_name = db.Column(db.String(120))
    purchase_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Integer)
    return_deadline = db.Column(db.Date)
    warranty_end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


def parse_optional_date(value):
    if not value:
        return None

    return datetime.strptime(value, "%Y-%m-%d").date()


@app.route("/")
def index():
    purchases = db.session.execute(
        db.select(Purchase).order_by(Purchase.created_at.desc())
    ).scalars().all()

    return render_template(
        "index.html",
        purchases=purchases,
    )


@app.route("/purchases/<int:purchase_id>")
def purchase_detail(purchase_id):
    purchase = db.get_or_404(Purchase, purchase_id)

    return render_template(
        "purchase_detail.html",
        purchase=purchase,
    )


@app.route("/purchases/new", methods=["GET", "POST"])
def create_purchase():
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        purchase_date_value = request.form.get("purchase_date", "")

        if not item_name:
            flash("Item name is required.", "error")
            return render_template(
                "purchase_form.html",
                purchase=None,
                page_title="Add Purchase",
                button_text="Save Purchase",
            )

        if not purchase_date_value:
            flash("Purchase date is required.", "error")
            return render_template(
                "purchase_form.html",
                purchase=None,
                page_title="Add Purchase",
                button_text="Save Purchase",
            )

        purchase = Purchase(
            item_name=item_name,
            category=request.form.get("category", "").strip() or None,
            store_name=request.form.get("store_name", "").strip() or None,
            purchase_date=parse_optional_date(purchase_date_value),
            price=(
                int(request.form["price"])
                if request.form.get("price")
                else None
            ),
            return_deadline=parse_optional_date(
                request.form.get("return_deadline", "")
            ),
            warranty_end_date=parse_optional_date(
                request.form.get("warranty_end_date", "")
            ),
            notes=request.form.get("notes", "").strip() or None,
        )

        db.session.add(purchase)
        db.session.commit()

        flash("Purchase saved successfully.", "success")
        return redirect(url_for("index"))

    return render_template(
        "purchase_form.html",
        purchase=None,
        page_title="Add Purchase",
        button_text="Save Purchase",
    )


@app.route("/purchases/<int:purchase_id>/edit", methods=["GET", "POST"])
def edit_purchase(purchase_id):
    purchase = db.get_or_404(Purchase, purchase_id)

    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        purchase_date_value = request.form.get("purchase_date", "")

        if not item_name:
            flash("Item name is required.", "error")
            return render_template(
                "purchase_form.html",
                purchase=purchase,
                page_title="Edit Purchase",
                button_text="Update Purchase",
            )

        if not purchase_date_value:
            flash("Purchase date is required.", "error")
            return render_template(
                "purchase_form.html",
                purchase=purchase,
                page_title="Edit Purchase",
                button_text="Update Purchase",
            )

        purchase.item_name = item_name
        purchase.category = (
            request.form.get("category", "").strip() or None
        )
        purchase.store_name = (
            request.form.get("store_name", "").strip() or None
        )
        purchase.purchase_date = parse_optional_date(
            purchase_date_value
        )
        purchase.price = (
            int(request.form["price"])
            if request.form.get("price")
            else None
        )
        purchase.return_deadline = parse_optional_date(
            request.form.get("return_deadline", "")
        )
        purchase.warranty_end_date = parse_optional_date(
            request.form.get("warranty_end_date", "")
        )
        purchase.notes = (
            request.form.get("notes", "").strip() or None
        )

        db.session.commit()

        flash("Purchase updated successfully.", "success")
        return redirect(
            url_for(
                "purchase_detail",
                purchase_id=purchase.id,
            )
        )

    return render_template(
        "purchase_form.html",
        purchase=purchase,
        page_title="Edit Purchase",
        button_text="Update Purchase",
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)