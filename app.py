#!/usr/bin/env python
from flask import Flask, render_template, request, flash, redirect, url_for, g, session
from flask_bootstrap import Bootstrap 
from models import UserForm, LoginForm, profession_list, countries_list, locations_list, dates_list, test_date_list
from flask_datepicker import datepicker
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import json
from proxy import MyThread, proxy_status, proxies_list
from sqlalchemy_serializer import SerializerMixin
import requests
from bs4 import BeautifulSoup
import os
import pprint
from sqlalchemy import distinct, desc
from List_Scrape.list_scrapy import runner
# import List_Scrape.list_scrapy
import csv
from datetime import date
import datetime


class Config(object):
    SECRET_KEY = '78w0o5tuuGex5Ktk8VvVDF9Pw3jv1MVE'

app = Flask(__name__)
app.config.from_object(Config)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/oet'
app.config['SECRET_KEY'] = "3489wfksf93r2k3lf9sdjkfe9t2j3krl"

Bootstrap(app)
datepicker(app)
db = SQLAlchemy(app)

state_dict = {}

class Profession(db.Model):
   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   profession = db.Column(db.String(30))


class Country_Location_Date(db.Model):
    __tablename__ = 'country_location_date'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    country = db.Column(db.String(30))
    state = db.Column(db.String(30))
    location = db.Column(db.String(70))
    date_ = db.Column(db.String(30))

    def __init__(self, country, state, location, date_):
        self.country = country
        self.state = state
        self.location = location
        self.date_ = date_


class Scrape_Log(db.Model):
    __tablename__ = 'scrape_log'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    dd = db.Column(db.Date)

    def __init__(self, dd):
        self.dd = dd    


class User(db.Model, SerializerMixin):  
    __tablename__ = 'user'

    serialize_only = ('name', 'username', 'password', 'email', 'phone', 'profession', 'country', 'dates', 'locations', 'defer', 'test_date')
    
    name =  db.Column(db.String(50), nullable = False)
    username =  db.Column(db.String(50), nullable = False)
    password =  db.Column(db.String(50), nullable = False) 
    email = db.Column(db.String(30), nullable = False) 
    phone = db.Column(db.String(20), nullable = False) 
    profession =  db.Column(db.String(), nullable = False)    
    country = db.Column(db.String(), nullable = False)
    dates = db.Column(db.String(), nullable = False)
    locations = db.Column(db.String(), nullable = False) 
    status = db.Column(db.Integer, default = 0) 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    defer = db.Column(db.Boolean, default = 0)
    test_date = db.Column(db.String(20), nullable = False)


    def __init__(self, name, username, password, email, phone, profession, country, dates, locations, defer, test_date):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.phone = phone
        self.profession = profession
        self.country = country
        self.dates = dates        
        self.locations = locations
        self.defer = defer
        self.test_date = test_date


class Proxies(db.Model, SerializerMixin):  
    __tablename__ = 'proxy'

    serialize_only = ('state')
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proxy = db.Column(db.String(30), nullable = False)
    bad = db.Column(db.Integer, nullable = False)
 
    def __init__(self, proxy, bad):
        self.proxy = proxy
        self.bad = bad


@app.route('/', methods=['GET', 'POST'])
def admin():
    if not 'username' in session:
        return redirect(url_for("login"))
    users = User.query.order_by(User.name)
    print(request.method)
    return render_template('main.html', users=users)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if os.environ.get('ADMIN_NAME') == request.form['name'] and os.environ.get('ADMIN_PASSWORD') == request.form['password']:
            session['username'] = request.form['name']
            return redirect(url_for('admin'))
   
    return render_template('login.html', form=LoginForm())

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = UserForm(request.form)
    
    if 'type_' in request.form:# == "save":
        # print(len(request.form.getlist('country')))
        # pprint.pprint(request.form.getlist('country'))
        # # print(request.form.getlist('country')[1])
        # print(len(request.form.getlist('locations_')))
        # print("#############################")
        if not form.validate_on_submit():
            flash('Please enter all the fields', 'error')
        else:
            defer = 0
            if "defer" in request.form: defer = 1
            user_ = User(request.form['name'], request.form['username'], request.form['password'], request.form['email'], request.form['phone'], \
                request.form['profession'], "##".join(request.form.getlist('country')), request.form['dates'],  \
                "##".join(request.form.getlist('locations_')), defer, request.form['test_date'])
            
            db.session.add(user_)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('admin'))   
    
    return render_template('user.html', form=form, )


@app.route('/edit_user', methods=['POST'])
def edit_user():  
    form = UserForm(request.form)
    
    # if request.method == 'POST':
    if request.form['type_'] == "save":
        if not form.validate_on_submit():
            flash('Please enter all the fields', 'error')
        else:         
            defer = 0
            if "defer" in request.form: defer = 1
            print(defer)
            db.session.query(User).filter_by(id = request.form['id']).update({User.name: request.form['name'], User.username: request.form['username'], \
                User.password: request.form['password'], User.email: request.form['email'], User.phone: request.form['phone'], User.profession: request.form['profession'], \
                User.country: "##".join(request.form.getlist('country')), User.dates: request.form['dates'], \
                User.locations: "##".join(request.form.getlist('locations_')), User.defer: defer, User.test_date: request.form['test_date']}, synchronize_session = False)
            db.session.commit()
            flash('Record was successfully updated')
            return redirect(url_for('admin'))   
    else:
        user_ = User.query.filter_by(id=request.form['user_id']).first()
        user_.country = user_.country.split("##")
        user_.locations = user_.locations.split("##")
        # user_.dates = user_.dates.split(",")
        pprint.pprint(user_.country)
    return render_template('user.html', form=form, user=user_)


@app.route('/del_user/<int:user_id>', methods=['GET', 'POST'])
def del_user(user_id):
    db.session.query(User).filter_by(id=user_id).delete()
    db.session.commit()

    return ""


@app.route('/view_log', methods=['GET', 'POST'])
def view_log():
    print("view_log()")
    return render_template('log.html', user_id = request.form['user_id'], tt = datetime.datetime.now())


@app.route('/ajax_get_user_status', methods=['GET', 'POST'])
def ajax_get_user_status():
    users = User.query.order_by(User.name)
    result = ""
    for user_ in users:
        if str(user_.id) in proxy_status:
            result += str(proxy_status[str(user_.id)]) + ","
        else:
            result += "0,"
    result = result[:-1]

    return result


@app.route('/start_proxy/<userId>', methods=['GET', 'POST'])
def start_proxy(userId):
    try:
        if proxy_status[userId] >= 1:
            return ""
    except:
        pass

    proxy_status[userId] = 1
    print("proxy_status[" + userId + "] = " + str(proxy_status[userId]))
    db.session.query(User).filter_by(id = userId).update({User.status: 1}, synchronize_session = False)
    db.session.commit()

    user_ = User.query.filter_by(id=userId).first()
    # user_.locations = json.loads(user_.locations)
    # for key, location_list in user_.locations.items():
    #     for i in range(len(location_list)):
    #         if location_list[i]["s"] != "":
    #             try:
    #                 user_.locations[key][i]["s"] = state_dict[location_list[i]["s"].lower()]
    #             except:
    #                 user_.locations[key][i]["s"] = ""

    t = MyThread(userId, user_.to_dict())
    t.start()

    return ""
        

@app.route('/stop_proxy/<userId>', methods=['GET', 'POST'])
def stop_proxy(userId):
    proxy_status[userId] = 0
    db.session.query(User).filter_by(id = userId).update({User.status: 0}, synchronize_session = False)
    db.session.commit()
    return ""


def status_initialize():
    db.session.query(User).update({User.status: 0}, synchronize_session = False)
    db.session.commit()
    return


# def get_state_list():
#     states = PostalCode.query.all()
#     for state_ in states:
#         state_dict[state_.state.lower()] = state_.state_code
#     return

def get_proxies_list():
    if os.environ.get('FREE_PROXY') != "true":
        try:
            proxies_file = open('proxies.txt', 'r') 
            while True: 
                line = proxies_file.readline()                
                if not line: 
                    break
                proxies_list.append(line.strip())
            print("\n:::::::::::  Paid Proxy  ::::::::\n")
            return
        except:
            pass
    print("\n:::::::::::  Free Proxy  ::::::::\n")
    proxies = Proxies.query.filter_by(bad=0)
    for proxy in proxies:
        proxies_list.append(proxy.proxy)
    print(len(proxies_list))
    
    if len(proxies_list) < 50 :
        URL = 'https://github.com/TheSpeedX/PROXY-List/blob/master/http.txt'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        trs = soup.find_all(class_="blob-code blob-code-inner js-file-line")
        for tr in trs:
            if tr.get_text()[0] >= '0' and tr.get_text()[0] <= '9':
                proxies_list.append(tr.get_text())
                proxy = Proxies(tr.get_text(), 0)            
                db.session.add(proxy)
                db.session.commit()
    print(len(proxies_list))
    return


def get_profession_list():
    # print("get_profession_list")
    for pp in Profession.query.order_by(Profession.id): 
        profession_list.append((pp.profession , pp.profession))
    # pprint.pprint(profession_list)


def get_countries_list():
    # print("get_countries_list")
    # pprint.pprint(os.environ.get('REPLACE_COUNTRY_NAMES'))
    replace_country_names = json.loads(str(os.environ.get('REPLACE_COUNTRY_NAMES')))
    # print("####################")s
    # pprint.pprint(len(replace_country_names))
    for pp in db.session.query(distinct(Country_Location_Date.country)).order_by(Country_Location_Date.country):
        if pp[0] in replace_country_names:
            # print("replace: " + pp[0] + " :: " + replace_country_names[pp[0]])
            countries_list.append((replace_country_names[pp[0]] , replace_country_names[pp[0]])) 
        else:   
            countries_list.append((pp[0] , pp[0]))
    countries_list.sort()
    # pprint.pprint(countries_list)


def get_locations_list():
    print("get_locations_list")
    pre_country = ""
    pre_state = ""
    locations = []
    for pp in db.session.query(Country_Location_Date).group_by(Country_Location_Date.location).order_by(Country_Location_Date.state, Country_Location_Date.location):
        country = pp.country
        state = pp.state
        if pre_country == country and pre_state == state: 
            locations.append(pp.location)
            continue
        else:
            if pre_state != "":
                locations_list.append((pre_state, pre_state))
                # locations_list.append(("##".join(locations), pre_state))
            pre_country = country
            pre_state = state
            locations.clear()
            locations.append(pp.location)
    locations_list.append((state , state)) # "##".join(locations)))
    # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    extra_locations = os.environ.get('EXTRA_LOCATIONS').split(":")
    print(len(extra_locations))
    for ll in extra_locations:
        locations_list.append((ll, ll))
    # pprint.pprint(locations_list)


def get_dates_list():
    print("get_dates_list")
    test_date_list.append(("0000-00-00", " - - Select Test Date - - "))
    for pp in db.session.query(distinct(Country_Location_Date.date_)).order_by(Country_Location_Date.date_):
        pp_2 = pp[0].strftime('%d %b %Y').upper()
        print(pp_2)
        dates_list.append((pp_2 , pp_2))
        test_date_list.append((pp_2 , pp_2))  
    # pprint.pprint(dates_list)


def list_to_db():
    print("##############  list_to_db  ###################")
    db.session.query(Country_Location_Date).delete()
    db.session.commit()
    with open('list.csv', 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # 'country', 'state', 'location', 'date']
            # print("country: " + row[0] + "   state: " + row[1] + "   location: " + row[2] + "   date: " + row[3])
            cld = Country_Location_Date(row[0], row[1], row[2], row[3])
            
            db.session.add(cld)
            db.session.commit()
    scrape_log = Scrape_Log(date.today())
    db.session.add(scrape_log)
    db.session.commit()
    


def scrape():
    dd = db.session.query(Scrape_Log).order_by(desc(Scrape_Log.dd)).first()
    to = date.today()#.strftime('%Y-%m-%d')
    print(to)
    print(dd.dd)
    # print(dd.dd + "::::") # + date.today().strftime('%Y-%m-%d'))
    if dd.dd != to:
        runner.start()
        list_to_db()




proxies_file = open('proxies.txt', 'r') 

if __name__ == '__main__':
    scrape()
    status_initialize()
    # get_state_list()
    get_profession_list()
    get_countries_list()
    get_locations_list()
    get_dates_list()
    get_proxies_list()
    app.run(host='0.0.0.0', port=5100, debug=True)
