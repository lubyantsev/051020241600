from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # Замените 'name' на '__name__'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(50), unique=True, nullable=False)
    buttons = db.relationship('Button', backref='schedule', lazy=True)

class Button(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    when = db.Column(db.String(100), nullable=True)
    where = db.Column(db.String(100), nullable=True)
    who = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(20), nullable=False)

# Создание базы данных, если она еще не существует
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    error = request.args.get('error')
    return render_template('home.html', error=error)


@app.route('/create_schedule', methods=['POST'])
def create_schedule():
    new_password = request.form['new_password']

    # Проверка, существует ли уже расписание с таким паролем
    existing_schedule = Schedule.query.filter_by(password=new_password).first()
    if existing_schedule:
        # Если пароль уже существует, перенаправим на главную страницу с ошибкой или сообщением
        return redirect(url_for('home', error="Этот пароль уже используется."))

    new_schedule = Schedule(password=new_password)
    db.session.add(new_schedule)
    db.session.commit()
    return redirect(url_for('edit_schedule', schedule_id=new_schedule.id))

@app.route('/view_schedule', methods=['POST'])
def view_schedule():
    password = request.form['password']
    schedule = Schedule.query.filter_by(password=password).first()
    if schedule:
        return redirect(url_for('edit_schedule', schedule_id=schedule.id))
    return redirect(url_for('home'))

@app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    schedule = Schedule.query.get(schedule_id)
    if request.method == 'POST':
        when = request.form.get('when')
        where = request.form.get('where')
        who = request.form.get('who')
        color = 'pink' if when and where else 'lightgreen' if when else None

        if color and (when or where):
            new_button = Button(schedule_id=schedule.id, when=when, where=where, who=who, color=color)
            db.session.add(new_button)
            db.session.commit()
            return redirect(url_for('edit_schedule', schedule_id=schedule.id))

        return redirect(url_for('edit_schedule', schedule_id=schedule.id))

    buttons = Button.query.filter_by(schedule_id=schedule.id).all()
    return render_template('schedule.html', schedule=schedule, buttons=buttons)


@app.route('/edit_button/<int:button_id>', methods=['GET', 'POST'])
def edit_button(button_id):
    button = Button.query.get(button_id)

    if request.method == 'POST':
        when = request.form.get('when')
        where = request.form.get('where')
        who = request.form.get('who')

        # Проверка, заполнено ли поле "Когда?"
        if not when:
            return redirect(url_for('edit_schedule', schedule_id=button.schedule_id))

        # Изменение цвета кнопки на светло-изумрудный, если "Кто?" не заполнено
        color = 'lightgreen' if not who else 'pink'

        # Обновление информации о кнопке
        button.when = when
        button.where = where
        button.who = who
        button.color = color

        db.session.commit()
        return redirect(url_for('edit_schedule', schedule_id=button.schedule_id))

    return render_template('edit_button.html', button=button)

@app.route('/save_password/<int:schedule_id>', methods=['POST'])
def save_password(schedule_id):
    password = request.form['password']
    schedule = Schedule.query.get(schedule_id)
    schedule.password = password
    db.session.commit()
    return redirect(url_for('edit_schedule', schedule_id=schedule.id))

if __name__ == '__main__':  # Замените 'name' на '__name__'
    app.run(debug=True)