from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Viktig for flash-meldinger (enkel UI-feedback)
app.config["SECRET_KEY"] = "dev-secret-change-later"

# SQLite database i prosjektmappen
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agileos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Association table: employees <-> projects (many-to-many)
employee_project = db.Table(
    "employee_project",
    db.Column("employee_id", db.Integer, db.ForeignKey("employee.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    note = db.Column(db.String(120), nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=50)  # 0–100
    mood = db.Column(db.String(10), nullable=False, default="ok")  # good/ok/warn

    projects = db.relationship(
        "Project",
        secondary=employee_project,
        back_populates="employees",
    )


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    progress = db.Column(db.Integer, nullable=False, default=0)  # 0–100

    employees = db.relationship(
        "Employee",
        secondary=employee_project,
        back_populates="projects",
    )


@app.route("/")
def index():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    projects = Project.query.order_by(Project.id.desc()).all()
    return render_template("index.html", employees=employees, projects=projects)


@app.route("/employees/add", methods=["POST"])
def add_employee():
    name = (request.form.get("name") or "").strip()
    note = (request.form.get("note") or "").strip()
    capacity = request.form.get("capacity") or 50
    mood = request.form.get("mood") or "ok"

    if not name:
        flash("Name is required.")
        return redirect(url_for("index"))

    try:
        capacity = int(capacity)
    except ValueError:
        capacity = 50

    capacity = max(0, min(100, capacity))

    employee = Employee(name=name, note=note or None, capacity=capacity, mood=mood)
    db.session.add(employee)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/projects/add", methods=["POST"])
def add_project():
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()
    progress = request.form.get("progress") or 0

    if not name:
        flash("Project name is required.")
        return redirect(url_for("index"))

    try:
        progress = int(progress)
    except ValueError:
        progress = 0

    progress = max(0, min(100, progress))

    project = Project(name=name, description=description or None, progress=progress)
    db.session.add(project)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/projects/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/projects/<int:project_id>/add-employee", methods=["POST"])
def add_employee_to_project(project_id):
    project = Project.query.get_or_404(project_id)
    employee_id = request.form.get("employee_id")

    if not employee_id:
        flash("Please select an employee.")
        return redirect(url_for("index"))

    employee = Employee.query.get_or_404(int(employee_id))

    if employee not in project.employees:
        project.employees.append(employee)
        db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
