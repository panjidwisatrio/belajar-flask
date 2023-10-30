from datetime import datetime

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Task %r>' % self.id


@app.get("/")
def index_get():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return render_template('index.html', tasks=tasks)


@app.post("/")
def index_post():
    # get task content from user input in html
    task_content = request.form['content']
    # create to-do model
    new_task = Todo(content=task_content)

    try:
        # add new task content to database
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
    except Exception as x:  # handle
        print("Unexpected error. Details: {}".format(x))


if __name__ == "__main__":
    app.run(debug=True)
