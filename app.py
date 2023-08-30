from flask import Flask, flash, render_template, redirect, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import astrology_sign, mbti_type
import random
import json
from collections import namedtuple
import urllib.request, json
import os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///rabbithole.db")


@app.route("/")
def index():
    #checking for current session
    if not session.get("user_id"):
        return redirect("/login")

    return redirect("/profile")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #checking for valid input from user
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            return render_template("register.html", color = '7FB3D5', decor = 'underline')
        #check for input lenght
        usern = request.form.get("username")
        passw = request.form.get("password")
        if len(usern) <= 4 or len(passw) <= 6:
            return render_template("register.html", color = '7FB3D5', decor = 'underline')
        #check for passw confirmation
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", color = '7FB3D5', decor = 'underline', unmatch = 'passwords DO NOT match')

        #check for uniqness of username
        users = db.execute("select user_id from users")
        for user in users:
            if user["user_id"] == usern:
                return render_template("register.html", visibility = 'visible')
        db.execute("INSERT INTO users(user_id,password) VALUES(?,?)", usern, generate_password_hash(passw))
        id = db.execute("select id from users where user_id = ?", usern)[0]['id']
        db.execute("INSERT INTO pictures(id,header_pic,profile_pic) VALUES(?,?,?)", id, None, None)
        db.execute("INSERT INTO profile(id) VALUES(?)",id)
        return render_template("login.html")
    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username and password were submitted
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("login.html", paragraph = 'must provide username and passord')


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE user_id = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("login.html", paragraph = 'invalid username and/or password',visibile = 'visible')

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", visibility = 'hidden')

@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect("/")



#setting up profile using id stored datas
@app.route("/profile/<user_id>")
@app.route("/profile")
def profileview(user_id = None):
    if user_id == None:
        folders = db.execute("SELECT * FROM folder WHERE id = ?", session["user_id"])
        if len(folders) == 0:
            visibility = None
        else:
            visibility = 'block'
        thoughts = db.execute("SELECT * FROM thought WHERE id = ? order by timeth desc", session["user_id"])
        if len(thoughts) == 0:
            visibilthought = 'hidden'
        else:
            visibilthought = 'block'
        pinned_content = db.execute("SELECT * FROM pinned WHERE id = ?", session["user_id"])
        if len(pinned_content) == 0:
            visibility = 'hidden'
        else:
            visibility = 'block'
        #profile pictures
        profile = db.execute("SELECT * FROM profile WHERE id = ?", session["user_id"])[0]
        header_pic = db.execute("SELECT header_pic FROM pictures WHERE id = ?",session["user_id"])
        profile_pic = db.execute("SELECT profile_pic FROM pictures WHERE id = ?",session["user_id"])
        if profile_pic == None:
            profile_pic ='https://geraldblack.com/cdn/shop/products/lace-backless-spaghetti-straps-gown-style-floor-length-beach-wedding-dress-geraldblack-com-28431127085216_600x600.jpg?v=1669965899'
        else:
            profile_pic= profile_pic[0]["profile_pic"]
        if header_pic == None:
            header_pic = 'https://geraldblack.com/cdn/shop/products/lace-backless-spaghetti-straps-gown-style-floor-length-beach-wedding-dress-geraldblack-com-28431127085216_600x600.jpg?v=1669965899'
        else:
            header_pic = header_pic[0]["header_pic"]

        pictures = db.execute("select url from picture where id = ?", session["user_id"])

        diaries = db.execute("select * from diary where id = ?", session["user_id"])


        return render_template("profile.html",visibility = visibility, sign = astrology_sign(profile["astrosign"]), mbti = mbti_type(profile["mbti"]),biography = profile["bio"], name = profile["name"], url = header_pic, urlprofile = profile_pic
        , pinned_content = pinned_content, thoughts = thoughts, folders = folders, visibil = visibilthought, pictures = pictures,diaries = diaries)
    else:
        id = db.execute("select id from users where user_id = ?",user_id)[0]["id"]
        folders = db.execute("SELECT * FROM folder WHERE id = ? and privacy = 'public'", id)
        if len(folders) == 0:
            visibility = None
        else:
            visibility = 'block'
        thoughts = db.execute("SELECT * FROM thought WHERE id = ? and privacy = 'public'", id)
        if len(thoughts) == 0:
            visibilthought = 'hidden'
        else:
            visibilthought = 'block'
        pinned_content = db.execute("SELECT * FROM pinned WHERE id = ?  ", id)
        if len(pinned_content) == 0:
            visibility = 'hidden'
        else:
            visibility = 'block'
        #profile pictures
        profile = db.execute("SELECT * FROM profile WHERE id = ?", id)[0]
        header_pic = db.execute("SELECT header_pic FROM pictures WHERE id = ?",id)
        profile_pic = db.execute("SELECT profile_pic FROM pictures WHERE id = ?",id)
        if profile_pic == None or not profile_pic:
            profile_pic ='https://geraldblack.com/cdn/shop/products/lace-backless-spaghetti-straps-gown-style-floor-length-beach-wedding-dress-geraldblack-com-28431127085216_600x600.jpg?v=1669965899'
        else:
            profile_pic= profile_pic[0]["profile_pic"]
        if header_pic == None or not header_pic:
            header_pic = 'https://geraldblack.com/cdn/shop/products/lace-backless-spaghetti-straps-gown-style-floor-length-beach-wedding-dress-geraldblack-com-28431127085216_600x600.jpg?v=1669965899'
        else:
            header_pic = header_pic[0]["header_pic"]

        pictures = db.execute("select url from picture where id = ? and privacy = 'public'", id)
        diaries = db.execute("select * from diary where id = ? and privacy = ?", id,'public')

        return render_template("profileview.html",visibility = visibility, sign = astrology_sign(profile["astrosign"]), mbti = mbti_type(profile["mbti"]),biography = profile["bio"], name = profile["name"], url = header_pic, urlprofile = profile_pic
        , pinned_content = pinned_content, thoughts = thoughts, folders = folders, visibil = visibilthought, pictures = pictures, id = id, diaries = diaries)

@app.route("/setheader", methods=["GET", "POST"])
def setheader():
    if request.method == "POST":
        #check if valid input TO DO!!!
        url = request.form.get("url")
        db.execute("UPDATE pictures SET header_pic = ? WHERE id = ?" , url, session["user_id"])
        return redirect("/profile")

@app.route("/setprofile", methods=[ "POST"])
def setprofile():
        #check if valid input TO DO!!!
        urlprofile = str(request.form.get("url"))
        db.execute("UPDATE pictures SET profile_pic = ? WHERE id = ?" , urlprofile, session["user_id"])
        return redirect("/profile")

#adding picture from pictures template view
@app.route("/addpictureview", methods = ["POST","GET"])
def addpictureview():
    url = request.form.get("url")
    privacy = request.form.get("privacy")
    id_pic = random.randint(0,10000)
    note = request.form.get("note")
    folder = request.form.get("folder")
    db.execute("INSERT INTO picture(id,url,privacy,idpic,note,folder) VALUES(?,?,?,?,?,?)" , session["user_id"], url,privacy,id_pic,note,folder)
    return redirect("/pictures")


@app.route("/pictures/<id>")
@app.route("/pictures")
def pictures(id = None):
    if id == None:
        folders = db.execute("select name from folder where id = ?", session["user_id"])
        pictures = db.execute("select * from picture where id = ?", session["user_id"])
        return render_template("pictures.html", pictures = pictures,folders = folders)
    else:
        id = int(id)
        user_id = db.execute("select user_id from users where id = ?", id)[0]["user_id"]
        folders = db.execute("select name from folder where id = ? and privacy = 'public' ", id)
        pictures = db.execute("select * from picture where id = ? and privacy = 'public' ", id)
        return render_template("picturesview.html", pictures = pictures,folders = folders, user_id = user_id)

#adding pictures from normale view and from folder view
@app.route("/addpicture", methods = ["POST","GET"])
@app.route("/addpicture/<foldername>", methods = ["POST","GET"])
def addpicture(foldername = None):

    if foldername == None:
        url = request.form.get("url")
        privacy = request.form.get("privacy")
        id_pic = random.randint(0,10000)
        note = request.form.get("note")
        folder = request.form.get("folder")
        if folder == "folder":
            db.execute("INSERT INTO picture(id,url,privacy,idpic,note) VALUES(?,?,?,?,?)" , session["user_id"], url,privacy,id_pic,note)
            return redirect("/profile")
        else:
            db.execute("INSERT INTO picture(id,url,privacy,idpic,note,folder) VALUES(?,?,?,?,?,?)" , session["user_id"], url,privacy,id_pic,note,folder)
            return redirect("/profile")
    else:
        url = request.form.get("url")
        privacy = request.form.get("privacy")
        id_pic = random.randint(0,10000)
        note = request.form.get("note")
        db.execute("INSERT INTO picture(id,url,privacy,folder,idpic,note) VALUES(?,?,?,?,?,?)" , session["user_id"], url,privacy,foldername,id_pic,note)
        return folderview(foldername)

#delete pictures
@app.route("/deletepic/<idpic>",methods = ["POST","GET"])
def deletepic(idpic):
    db.execute("delete from picture where idpic = ?", idpic)
    return redirect("/pictures")


@app.route("/search/<query>",methods = ["GET"])
def search(query):
     if request.method == "GET":
          if query is not None:
               results = db.execute("select user_id from users where user_id like ?",'%' + query + '%')
               response = jsonify(results)
               return response


@app.route("/setname", methods=[ "POST"])
def setname():
        #check if valid input TO DO!!!
        sign = request.form.get("sign")
        mbti = request.form.get("mbti")
        profile_name = request.form.get("name")
        db.execute("UPDATE profile SET name = ? WHERE id = ?" , profile_name, session["user_id"])
        db.execute("UPDATE profile SET mbti = ? WHERE id = ?" , mbti, session["user_id"])
        db.execute("UPDATE profile SET astrosign = ? WHERE id = ?" , sign, session["user_id"])
        return redirect("/profile")


@app.route("/setbio", methods=[ "POST"])
def setbio():
        #check if valid input TO DO!!!
        profile_bio = request.form.get("bio")
        db.execute("UPDATE profile SET bio = ? WHERE id = ?" , profile_bio, session["user_id"])
        return redirect("/profile")

@app.route("/addpinned/<foldername>", methods=["GET","POST"])
@app.route("/addpinned", methods=["GET","POST"])
def addpinned(foldername = None):
    if request.method == "POST":
        if foldername == None:
            title = request.form.get("title")
            description = request.form.get("description")
            imageurl = request.form.get("image_url")
            link = request.form.get("link")
            folder = request.form.get("folder")
            idpinned = random.randint(0,10000)
            if folder != 'folder':
                db.execute("INSERT INTO pinned(id,title,url,description,picture,idpinned,folder) VALUES(?,?,?,?,?,?,?)" , session["user_id"], title, link, description, imageurl,idpinned,folder)
            else:
                db.execute("INSERT INTO pinned(id,title,url,description,picture,idpinned) VALUES(?,?,?,?,?,?)" , session["user_id"], title, link, description, imageurl,idpinned)
            return redirect("/profile")
        else:
            title = request.form.get("title")
            description = request.form.get("description")
            imageurl = request.form.get("image_url")
            link = request.form.get("link")
            idpinned = random.randint(0,10000)
            db.execute("INSERT INTO pinned(id,title,url,description,picture,idpinned,folder) VALUES(?,?,?,?,?,?,?)" , session["user_id"], title, link, description, imageurl,idpinned,foldername)
            return folderview(foldername)
    return redirect("/profile")

@app.route("/deletepinned/<idpinned>",methods = ["GET"])
def deletepinned(idpinned):
    db.execute("DELETE FROM pinned WHERE id = ? and idpinned = ?",session["user_id"], idpinned)
    return redirect("/profile")

#delete thoughts
@app.route("/deletethought/<idthought>/<foldername>",methods = ["GET"])
@app.route("/deletethought/<idthought>",methods = ["GET"])
def deletethought(idthought,foldername = None,view = None):
    if foldername == None:
        db.execute("DELETE FROM thought WHERE id = ? and idthought = ?",session["user_id"], idthought)
        return redirect("/profile")
    else:
        db.execute("DELETE FROM thought WHERE id = ? and idthought = ?",session["user_id"], idthought)
        return folderview(foldername)


@app.route("/deletethoughtview/<idthought>",methods = ["GET"])
def deletethoughtview(idthought):
    db.execute("DELETE FROM thought WHERE id = ? and idthought = ?",session["user_id"], idthought)
    return redirect("/thoughts")

@app.route("/addthought", methods = ["POST","GET"])
@app.route("/addthought/<folder>", methods = ["POST","GET"])
def addthought(folder = None):
    text = request.form.get("thought")
    privacy = request.form.get("privacy")
    foldername = request.form.get("folder")
    if folder == None:
        db.execute("INSERT INTO thought(id,think,privacy,idthought,folder) VALUES(?,?,?,?,?)" , session["user_id"], text, privacy,random.randint(0,10000),foldername)
        return redirect("/profile")
    if foldername == 'folder':
        db.execute("INSERT INTO thought(id,think,privacy,idthought) VALUES(?,?,?,?)" , session["user_id"], text, privacy,random.randint(0,10000))
        return redirect("/profile")
    else:
        db.execute("INSERT INTO thought(id,think,privacy,folder,idthought) VALUES(?,?,?,?,?)" , session["user_id"], text, privacy, folder,random.randint(0,10000))
        return folderview(folder)

@app.route("/addthoughtview",methods = ["POST","GET"])
def addthoughtview():
    text = request.form.get("thought")
    privacy = request.form.get("privacy")
    folder = request.form.get("folder")

    if folder == 'folder':
        db.execute("INSERT INTO thought(id,think,privacy,idthought) VALUES(?,?,?,?)" , session["user_id"], text, privacy,random.randint(0,10000))
        return redirect("/thoughts")
    else:
        db.execute("INSERT INTO thought(id,think,privacy,folder,idthought) VALUES(?,?,?,?,?)" , session["user_id"], text, privacy, folder,random.randint(0,10000))
        return redirect("/thoughts")
@app.route("/thoughts/<id>", methods = ["POST","GET"])
@app.route("/thoughts", methods = ["POST","GET"])
def thoughts(id = None):
    if id == None:
        thoughts = db.execute("select * from thought where id = ? order by timeth desc", session["user_id"])
        folders = db.execute("select * from folder where id = ? ",session["user_id"])
        return render_template("thoughts.html", thoughts = thoughts,folders = folders)
    else:
        id = int(id)
        thoughts = db.execute("select * from thought where id = ? and privacy = 'public' order by timeth desc", id)
        user_id = db.execute("select user_id from users where id = ?",id)[0]["user_id"]
        return render_template("thoughtview.html", thoughts = thoughts, user_id = user_id)


@app.route("/addfolder", methods = ["POST","GET"])
def addfolder():
    text = request.form.get("title")
    privacy = request.form.get("privacy")
    db.execute("INSERT INTO folder(id,name,privacy) VALUES(?,?,?)" , session["user_id"], text, privacy)
    return redirect("/profile")

@app.route("/editfoldername/<foldername>", methods = ["POST","GET"])
def editfoldername(foldername):
    text = request.form.get("name")
    db.execute("UPDATE folder SET name=? where id = ? and name =?" , text,session["user_id"], foldername)
    db.execute("UPDATE thought SET folder=? where id = ? and folder =?" , text,session["user_id"], foldername)
    db.execute("UPDATE pinned SET folder=? where id = ? and folder =?" , text,session["user_id"], foldername)
    db.execute("UPDATE picture SET folder=? where id = ? and folder =?" , text,session["user_id"], foldername)
    return folderview(text)


@app.route("/folderview/<foldername>", methods = ["GET"])
def folderview(foldername):
        username = db.execute("select user_id from users where id = ? ",session["user_id"] )[0]["user_id"]
        thoughts = db.execute("select * from thought where id = ? and folder = ? order by timeth desc", session["user_id"], foldername)
        pictures = db.execute("select url from picture where id = ? and folder = ?", session["user_id"],foldername)
        pinned = db.execute("select * from pinned where id = ? and folder = ?", session["user_id"],foldername)
        diaries = db.execute("select * from diary where id = ? and folder = ?", session["user_id"],foldername)
        return render_template("folder.html", foldername = foldername,user = username,thoughts = thoughts, pictures = pictures,pinned_content=pinned, diaries = diaries )




@app.route("/home")
def home():
    lista = []
    for n in range(20):
        rand = random.randint(0,3)
        if rand == 0:
            count = int(db.execute("select count(*) from thought where id != ?", session["user_id"])[0]["count(*)"])
            num = random.randint(0,count-1)
            el = db.execute("select * from thought where id != ?", session["user_id"])[num]
            el["type"] = 'thought'
            id = el["id"]
            id = db.execute("select user_id from users where id = ?",id)[0]["user_id"]
            el["userid"] = id
            lista.append(el)
        if rand == 1:
            count = int(db.execute("select count(*) from picture where id != ?",session["user_id"])[0]["count(*)"])
            num = random.randint(0,count-1)
            el = db.execute("select * from picture where id != ? ",session["user_id"])[num]
            id = el["id"]
            id = db.execute("select user_id from users where id = ?",id)[0]["user_id"]
            el["type"] = 'picture'
            el["userid"] = id
            lista.append(el)
        if rand == 2:
            count = int(db.execute("select count(*) from diary where id != ?",session["user_id"])[0]["count(*)"])
            num = random.randint(0,count-1)
            el = db.execute("select * from diary where id != ? ",session["user_id"])[num]
            id = el["id"]
            id = db.execute("select user_id from users where id = ?",id)[0]["user_id"]
            el["type"] = 'dairy'
            el["userid"] = id
            lista.append(el)
        if rand == 3:
            count = int(db.execute("select count(*) from folder where id != ?",session["user_id"])[0]["count(*)"])
            num = random.randint(0,count-1)
            el = db.execute("select * from folder where id != ? ",session["user_id"])[num]
            id = el["id"]
            id = db.execute("select user_id from users where id = ?",id)[0]["user_id"]
            el["type"] = 'folder'
            el["userid"] = id
            lista.append(el)
    return render_template("home.html", lista = lista)

@app.route("/adddiary",methods = ["GET","POST"])
@app.route("/adddiary/<foldername>",methods = ["GET","POST"])
def adddiary(foldername = None):
    if request.method == "POST":
        if foldername == None:
            folder = request.form.get("folder")
            privacy = request.form.get("privacy")
            title = request.form.get("title")
            diary = request.form.get("diary")
            url = request.form.get("url")
            iddiary = random.randint(0,10000)
            if folder == 'folder':
                db.execute("INSERT INTO diary(id,title,privacy,diary,url,iddiary) VALUES(?,?,?,?,?,?)" , session["user_id"], title, privacy,diary,url,iddiary)
            else:
                db.execute("INSERT INTO diary(id,title,privacy,folder,diary,url,iddiary) VALUES(?,?,?,?,?,?,?)" , session["user_id"], title, privacy,folder,diary,url,iddiary)
        else:
            privacy = request.form.get("privacy")
            title = request.form.get("title")
            diary = request.form.get("diary")
            url = request.form.get("url")
            iddiary = random.randint(0,10000)
            db.execute("INSERT INTO diary(id,title,privacy,diary,url,iddiary,folder) VALUES(?,?,?,?,?,?,?)" , session["user_id"], title, privacy,diary,url,iddiary,foldername)
            return folderview(foldername)



    return redirect("/diary")

@app.route("/diary",methods = ["GET","POST"])
@app.route("/diary/<id>",methods = ["GET","POST"])
def diary(id = None):
    if id == None:
        diaries = db.execute("select * from diary where id = ?", session["user_id"])
        return render_template("diary.html",diaries = diaries)
    else:
        id = int(id)
        diaries = db.execute("select * from diary where id = ? and privacy = 'public'", id)
        user_id = db.execute("select user_id from users where id = ?", id)[0]["user_id"]
        return render_template("diaryview.html", diaries = diaries,user_id = user_id)

@app.route("/deldiary/<iddiary>",methods = ["GET","POST"])
def deldiary(iddiary):
    diaries = db.execute("delete from diary where id = ? and iddiary=?", session["user_id"],iddiary)
    return redirect("/diary")

@app.route("/editdiary/<iddiary>",methods = ["GET","POST"])
def editdiary(iddiary):
    if request.method == "GET":
        editdiary = db.execute("select * from diary where iddiary = ?", iddiary)
        return render_template("editdiary.html",id = iddiary, toedit = editdiary)
    if request.method == "POST":
        folder = request.form.get("folder")
        privacy = request.form.get("privacy")
        title = request.form.get("title")
        diary = request.form.get("diary")
        url = request.form.get("url")
        if title == None:
            db.execute("update diary set folder = ?, privacy = ?, url = ?,diary = ? where iddiary = ?",folder,privacy,url,diary,iddiary)
        if url == None:
            db.execute("update diary set folder = ?, privacy = ?, title = ?,diary = ? where iddiary = ?",folder,privacy,title,diary,iddiary)
        else:
            db.execute("update diary set folder = ?, privacy = ?, title = ?, url = ?,diary = ? where iddiary = ?",folder,privacy,title,url,diary,iddiary)
        return redirect("/diary")
