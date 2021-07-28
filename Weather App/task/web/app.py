import os
import requests as requests
from flask import Flask
import sys
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from flask import redirect
from flask import flash


def add_city_db(name_):
    city_ = City(name=name_)
    db.session.add(city_)
    db.session.commit()


def get_city_by_name(name_):
    return db.session.query(City).filter(City.name == name_).all()


def get_all_city():
    try:
        cities_ = db.session.query(City).all()
    except:
        return None
    return cities_


app = Flask(__name__)
app.config.update(SECRET_KEY=os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)


class City(db.Model):
    __tablename__ = "city"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),unique=True, nullable=False)


db.create_all()


@app.route('/')
def index():
    weather_dict_ = {}
    city_list_ = get_all_city()
    if city_list_ is None:
        return render_template('index.html')
    for city_ in city_list_:
        req_ = "https://api.openweathermap.org/data/2.5/weather?q={}&appid=c16236231879181bd77b179e5e157984".format(city_.name)
        resp_ = requests.get(req_)
        temp_ = resp_.json()["main"]["temp"]
        state_ = resp_.json()["weather"][0]["main"]
        temp_ = round((round(temp_) - 273.15))
        weather_dict_.update({city_.name: [temp_, state_, city_.id]})
    return render_template('index.html', weather=weather_dict_)


@app.route('/add', methods=['POST', 'GET'])
def add_city():
    req_ = "https://api.openweathermap.org/data/2.5/weather?q={}&appid=c16236231879181bd77b179e5e157984".format(request.form['city_name'])
    resp_ = requests.get(req_)
    if resp_.status_code != 200:
        flash("The city doesn't exist!")
    elif len(get_city_by_name(request.form['city_name'])) > 0:
        flash("The city has already been added to the list!")
    else:
        add_city_db(request.form['city_name'])
    return redirect("/")


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    print(city_id)
    city = db.session.query(City).filter(City.id == city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
