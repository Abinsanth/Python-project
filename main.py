from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

# Event Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)

# Create database before first request
with app.app_context():
    db.create_all()


# Home Page - Add & Delete Events
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        time = request.form['time']
        organizer = request.form['organizer']
        new_event = Event(name=name, date=date, location=location, time=time, organizer=organizer)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('index'))

    events = Event.query.all()
    return render_template('index.html', events=events)

# Delete Event
@app.route('/delete/<int:id>')
def delete_event(id):
    event = Event.query.get(id)
    if event:
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('index'))

# Analytics Page
@app.route('/analytics')
def analytics():
    events = Event.query.all()

    # Analysis on Date
    date_counts = {}
    organizer_counts = {}

    for event in events:
        date_counts[event.date] = date_counts.get(event.date, 0) + 1
        organizer_counts[event.organizer] = organizer_counts.get(event.organizer, 0) + 1

    # Generate Date Graph
    plt.figure(figsize=(6, 4))
    plt.bar(date_counts.keys(), date_counts.values(), color='blue')
    plt.xlabel('Date')
    plt.ylabel('Number of Events')
    plt.title('Events by Date')
    plt.xticks(rotation=45)
    plt.tight_layout()
    date_graph = "static/date_graph.png"
    plt.savefig(date_graph)
    plt.close()

    # Generate Organizer Graph
    plt.figure(figsize=(6, 4))
    plt.bar(organizer_counts.keys(), organizer_counts.values(), color='green')
    plt.xlabel('Organizer')
    plt.ylabel('Number of Events')
    plt.title('Events by Organizer')
    plt.xticks(rotation=45)
    plt.tight_layout()
    organizer_graph = "static/organizer_graph.png"
    plt.savefig(organizer_graph)
    plt.close()

    return render_template('analytics.html', date_graph=date_graph, organizer_graph=organizer_graph)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database is created
    app.run(debug=True)