from flask import request, render_template, redirect

from app import app, db
from app.model import Todo


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
    except Exception as x:
        print("Unexpected error. Details: {}".format(x))


@app.route("/delete/<int:id>")
def delete_task(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/')
    except Exception as x:
        print("Unexpected error. Details: {}".format(x))


@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except Exception as x:
            print("Unexpected error. Details: {}".format(x))
    else:
        return render_template('update.html', task=task)
