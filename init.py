from flask import Flask, render_template, request, session, url_for, redirect,jsonify
import pymysql.cursors
import html

app=Flask(__name__)

conn=pymysql.connect(
    host="localhost",
    user="root",
    password="",
    db="schems1",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/loginAuth", methods=['GET','POST'])
def loginAuth():
    username=html.escape(request.form["Username"])
    password=html.escape(request.form["Password"])
    cursor=conn.cursor()
    query="SELECT * FROM customer WHERE cID=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    error=None
    if not data:
        error="User Not Exist"
        cursor.close()
        return render_template("login.html",error=error)
    query="SELECT * FROM customer WHERE cID=%s AND password=md5(%s)"
    cursor.execute(query,(username,password))
    data=cursor.fetchone()
    cursor.close()
    if not data:
        error="Wrong Password"
        return render_template("login.html",error=error)
    
    session["Username"]=username
    return redirect(url_for("home"))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registerAuth",methods=["GET","POST"])
def registerAuth():
    username=html.escape(request.form["Username"])
    password=html.escape(request.form["Password"])
    fname=html.escape(request.form["fName"])
    lname=html.escape(request.form["lName"])
    bstreet=html.escape(request.form["bstreet"])
    bapt=html.escape(request.form["bapt"])
    bapt=bapt if bapt else None
    bcity=html.escape(request.form["bcity"])
    bstate=html.escape(request.form["bstate"])
    bcountry=html.escape(request.form["bcountry"])
    bzip=html.escape(request.form["bzip"])
    
    cursor=conn.cursor()
    query="SELECT * FROM customer WHERE cID=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    error=None
    if data:
        error="This User Already Exists"
        cursor.close()
        return render_template("register.html",error=error)
    
    query="Insert INTO customer VALUES (%s,md5(%s),%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,(username,password,fname,lname,bstreet,bapt,bcity,bstate,bcountry,bzip))
    conn.commit()
    cursor.close()
    return redirect(url_for("login"))

@app.route("/home")
def home():
    username=session["Username"]
    cursor=conn.cursor()
    query="SELECT cfname FROM customer WHERE cID=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    name=data["cfname"]
    cursor.close()
    return render_template("home.html",name=name)
    
@app.route("/logout")
def logout():
    session.pop("Username")
    return redirect("/")

@app.route("/viewEditServiceLocation")
def viewEditServiceLocation():
    username=session["Username"]
    cursor=conn.cursor()
    query="SELECT lID, lstreet, lapt, lcity, lstate, lcountry, lzip, took_date, square_footage, bedrooms, occupants\
            FROM customerlocation NATURAL JOIN servicelocation\
            Where cID=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    cursor.close()
    return render_template("viewEditServiceLocation.html",data=data)

@app.route("/AddServiceLocation",methods=["GET","POST"])
def AddServiceLocation():
    username=session["Username"]
    street=html.escape(request.form["street"])
    apt=html.escape(request.form["apartment"])
    city=html.escape(request.form["city"])
    state=html.escape(request.form["state"])
    country=html.escape(request.form["country"])
    zip=html.escape(request.form["zip"])
    took_date=html.escape(request.form["took_date"])
    sq=html.escape(request.form["square_footage"])
    bedrooms=html.escape(request.form["bedrooms"])
    occu=html.escape(request.form["occupants"])
    check=(street,apt,city,state,country,zip)
    cursor=conn.cursor()
    query="SELECT lID\
            FROM servicelocation\
            WHERE lstreet=%s and lapt=%s and lcity=%s and lstate=%s and lcountry=%s and lzip=%s"
    cursor.execute(query,check)
    data=cursor.fetchone()
    if data:
        error="This Service Location Has Already Been Added Before"
        cursor.close()
        return render_template("viewEditServiceLocation.html",error=error)
        
    query="INSERT INTO servicelocation (lstreet,lapt,lcity,lstate,lcountry,lzip,took_date,square_footage,bedrooms,occupants) \
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,(street,apt,city,state,country,zip,took_date,sq,bedrooms,occu))
    conn.commit()
    lID=cursor.lastrowid
    query="INSERT INTO customerlocation(cID,lID) VALUES(%s,%s)"
    cursor.execute(query,(username,lID))
    conn.commit()
    cursor.close()
    return redirect("/viewEditServiceLocation")

@app.route("/DeleteServiceLocation",methods=["POST"])
def DeleteServiceLocation():
    username=session["Username"]
    lID=html.escape(request.form["lID"])
    cursor=conn.cursor()
    query="SELECT * FROM customerlocation WHERE cID=%s and lID=%s"
    cursor.execute(query,(username,lID))
    data=cursor.fetchone()
    if not data:
        error="Invalid Location ID"
        return render_template("viewEditServiceLocation.html",error1=error)
    
    query="DELETE FROM servicelocation WHERE lID=%s"
    cursor.execute(query,(lID))
    conn.commit()
    cursor.close()
    return redirect("/viewEditServiceLocation")
    
   
@app.route("/viewDeviceByLocation")
def viewDeviceByLocation():
    username=session["Username"]
    cursor=conn.cursor()
    query="SELECT lID, lstreet, lapt, lcity, lstate, lcountry, lzip, took_date, square_footage, bedrooms, occupants\
            FROM customerlocation NATURAL JOIN servicelocation\
            Where cID=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    cursor.close()
    return render_template("viewDeviceByLocation.html",data=data)
    
@app.route("/selectLocation",methods=["POST"])
def selectLocation():
    username=session["Username"] 
    lID=html.escape(request.form["lID"])
    cursor=conn.cursor()
    query="SELECT * FROM customerlocation WHERE cID=%s and lID=%s"
    cursor.execute(query,(username,lID))
    data=cursor.fetchone()
    if not data:
        return render_template("viewDeviceError.html")
    session["lID"]=lID
    cursor.close()
    return redirect('/viewDevice')

@app.route("/viewDevice")
def viewDevice():
    username=session["Username"]
    lID=session["lID"]
    cursor=conn.cursor()
    query="SELECT eID, type, model_name\
            FROM enrolldevice NATURAL JOIN customerlocation \
            WHERE cID=%s and lID=%s and status=%s"
    cursor.execute(query,(username,lID,'activate'))
    data=cursor.fetchall()
    cursor.close()
    return render_template("viewDevice.html",data=data,lID=lID)

@app.route("/viewModelByType",methods=["POST"])
def viewModelByType():
    type=html.escape(request.form["type"])
    session["type"]=type
    return redirect("/viewModel")

@app.route("/viewModel")
def viewModel():
    type=session["type"]
    lID=session["lID"]
    cursor=conn.cursor()
    query="SELECT model_name, property FROM model WHERE type=%s"
    cursor.execute(query,(type))
    data=cursor.fetchall()
    cursor.close()
    return render_template("viewModel.html",data=data,lID=lID,type=type)

@app.route("/enrollDevice",methods=["POST"])
def enrollDevice():
    username=session["Username"]
    lID=session["lID"]
    type=session["type"]
    model_name=html.escape(request.form["model_name"])
    cursor=conn.cursor()
    query="SELECT * FROM model WHERE model_name=%s and type=%s"
    cursor.execute(query,(model_name,type))
    data=cursor.fetchone()
    if not data:
        cursor.close()
        return render_template("enrollError.html")
    
    query="SELECT clID FROM customerlocation WHERE cID=%s and lID=%s"
    cursor.execute(query,(username,lID))
    clID=cursor.fetchone()["clID"]
    query="INSERT INTO enrolldevice(clID,type,model_name,status) VALUES(%s,%s,%s,%s)"
    cursor.execute(query,(clID,type,model_name,'activate'))
    conn.commit()
    cursor.close()
    return redirect("/viewDevice")

@app.route("/deleteEnrollment", methods=["POST"])
def deleteEnrollment():
    eID=html.escape(request.form["eID"])
    username=session["Username"]
    lID=session["lID"]
    cursor=conn.cursor()
    query="SELECT * \
            FROM enrolldevice NATURAL JOIN customerlocation \
            WHERE eID=%s and cID=%s and lID=%s and status=%s"
    cursor.execute(query,(eID,username,lID,'activate'))
    data=cursor.fetchone()
    if not data:
        cursor.close()
        return render_template("deleteDeviceError.html")
    query="UPDATE enrolldevice SET status=%s WHERE eID=%s"
    cursor.execute(query,('deactivate',eID))
    conn.commit()
    cursor.close()
    return redirect("/viewDevice")


@app.route("/viewDailyEnergy")
def viewDailyEnergy():
    return render_template("dailyEnergy.html")

@app.route("/viewDailyEnergy_EXCE",methods=["POST"])
def viewDailyEnergy_EXCE():
    username=session["Username"]
    month=html.escape(request.form["month"])
    year=html.escape(request.form["year"])
    cursor=conn.cursor()
    query="SELECT DAY(date_time) as day, FORMAT(SUM(value),3) as dTotal \
            FROM data NATURAL JOIN enrolldevice NATURAL JOIN customerlocation \
            WHERE cID=%s and label=%s and YEAR(date_time)=%s and MONTH(date_time)=%s \
            GROUP BY day"
    cursor.execute(query,(username,'energy use',year,month))
    data=cursor.fetchall()
    day=[row["day"] for row in data]
    dTotal=[row["dTotal"] for row in data]
    query="SELECT DAY(date_time) as day, FORMAT(SUM(value*ep.price),3) as dCost \
            FROM data NATURAL JOIN enrolldevice NATURAL JOIN customerlocation \
            NATURAL JOIN servicelocation JOIN energyprice ep on lzip=ep.zip \
            WHERE cID=%s and label=%s and YEAR(date_time)=%s and MONTH(date_time)=%s \
            and HOUR(date_time) BETWEEN ep.fromhour AND ep.tohour \
            GROUP BY day"
    cursor.execute(query,(username,'energy use',year,month))
    data=cursor.fetchall()
    dCost=[row["dCost"] for row in data]
    cursor.close()
    return render_template("dailyEnergy.html",labels=day,values=dTotal,values1=dCost,month=month,year=year)

@app.route("/AverageMonthlyConsumptionPerType")
def AverageMonthlyConsumptionPerType():
    return render_template("averageMonthlyConsumption.html")

@app.route("/AverageMonthlyConsumptionPerType_EXCE",methods=["POST"])
def AverageMonthlyConsumptionPerType_EXCE():
    username=session["Username"]
    month=html.escape(request.form["month"])
    year=html.escape(request.form["year"])
    cursor=conn.cursor()
    query="CREATE VIEW typeCost(type,cost) AS \
            SELECT type, FORMAT(SUM(value*ep.price),3) as cost \
            FROM data NATURAL JOIN enrolldevice NATURAL JOIN customerlocation \
            NATURAL JOIN servicelocation JOIN energyprice ep on lzip=ep.zip \
            WHERE cID=%s and label=%s and YEAR(date_time)=%s and MONTH(date_time)=%s \
            and HOUR(date_time) BETWEEN ep.fromhour AND ep.tohour \
            GROUP BY type"
    cursor.execute(query,(username,'energy use',year,month))
    conn.commit()
    query="CREATE VIEW typeTotal(type,total) AS \
            SELECT type, COUNT(DISTINCT eID) as total \
            FROM data NATURAL JOIN enrolldevice NATURAL JOIN customerlocation \
            WHERE cID=%s and label=%s and YEAR(date_time)=%s and MONTH(date_time)=%s \
            GROUP BY type"
    cursor.execute(query,(username,'energy use',year,month))
    conn.commit()
    query="SELECT type, FORMAT(cost/total,3) as average FROM typeCost NATURAL JOIN typeTotal"
    cursor.execute(query)
    data=cursor.fetchall()
    type=[row["type"] for row in data]
    average=[row["average"] for row in data]
    query="DROP VIEW typeCost"
    cursor.execute(query)
    query="DROP VIEW typeTotal"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return render_template("averageMonthlyConsumption.html",labels=type,values=average,year=year,month=month)

@app.route("/compareEnergyBetweenLocation")
def compareEnergyBetweenLocation():
    return render_template("compareEnergyBetweenLocation.html")

@app.route("/compareEnergyBetweenLocation_EXCE",methods=["POST"])
def compareEnergyBetweenLocation_EXCE():
    username=session["Username"]
    month=html.escape(request.form["month"])
    year=html.escape(request.form["year"])
    cursor=conn.cursor()
    query="CREATE VIEW LocationTotalConsumption(lID,square_footage,total_consumption) AS \
            SELECT lID, square_footage, SUM(value) as total_consumption\
            FROM data NATURAL JOIN enrolldevice NATURAL JOIN customerlocation NATURAL JOIN servicelocation \
            WHERE label=%s and YEAR(date_time)=%s and MONTH(date_time)=%s \
            GROUP BY lID, square_footage"
    cursor.execute(query,('energy use',year,month))
    conn.commit()
    query="CREATE VIEW OtherAverageConsumption(lID,average) AS \
            SELECT ltc1.lID as lID, AVG(ltc2.total_consumption) as average \
            FROM LocationTotalConsumption ltc1, LocationTotalConsumption ltc2 \
            WHERE ltc1.lID!=ltc2.lID and ltc2.square_footage BETWEEN ltc1.square_footage*0.95 \
            AND ltc1.square_footage*1.05 \
            GROUP BY ltc1.lID"
    cursor.execute(query)
    conn.commit()
    query="SELECT lID, FORMAT(total_consumption/average,3) as rate\
            FROM LocationTotalConsumption NATURAL JOIN OtherAverageConsumption Natural JOIN customerlocation \
            WHERE cID=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    lID=[row["lID"] for row in data]
    rate=[row["rate"] for row in data]
    query="DROP VIEW LocationTotalConsumption"
    cursor.execute(query)
    query="DROP VIEW OtherAverageConsumption"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return render_template("compareEnergyBetweenLocation.html",labels=lID,values=rate,year=year,month=month)

@app.route("/viewSaving")
def viewSaving():
    return render_template("viewSaving.html")

@app.route("/viewSaving_EXCE",methods=["POST"])
def viewSaving_EXCE():
    username=session["Username"]
    month=html.escape(request.form["month"])
    year=html.escape(request.form["year"])
    cursor=conn.cursor()
    query="CREATE VIEW cost(type,oldCost) AS \
            SELECT type, FORMAT(SUM(value*ep.price),3) as oldCost \
            FROM data NATURAL JOIN enrolldevice NATURAL JOIN customerlocation \
            NATURAL JOIN servicelocation JOIN energyprice ep on lzip=ep.zip \
            WHERE cID=%s and label=%s and YEAR(date_time)=%s and MONTH(date_time)=%s \
            and HOUR(date_time) BETWEEN ep.fromhour AND ep.tohour \
            GROUP BY type"
    cursor.execute(query,(username,'energy use',year,month))
    conn.commit()
    query="CREATE VIEW midnightCost(type,newCost) AS \
            SELECT type, FORMAT(SUM(value*ep.price),3) as newCost \
            FROM data NATURAL JOIN enrolldevice NATURAL JOIN customerlocation \
            NATURAL JOIN servicelocation JOIN energyprice ep on lzip=ep.zip \
            WHERE cID=%s and label=%s and YEAR(date_time)=%s and MONTH(date_time)=%s \
            and 0 BETWEEN ep.fromhour AND ep.tohour \
            GROUP BY type"
    cursor.execute(query,(username,'energy use',year,month))
    conn.commit()
    query="SELECT type,oldCost,newCost,oldCost-newCost as saving \
            FROM cost NATURAL JOIN midnightCost"
    cursor.execute(query)
    data=cursor.fetchall()
    type=[row["type"] for row in data]
    oldCost=[row["oldCost"] for row in data]
    newCost=[row["newCost"] for row in data]
    saving=[row["saving"] for row in data]
    query="DROP VIEW cost"
    cursor.execute(query)
    query="DROP VIEW midnightCost"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    return render_template("viewSaving.html",labels=type,values=oldCost,values1=newCost,values2=saving,year=year,month=month)
    
  
  
app.secret_key="Some key you can't guess"
if __name__=="__main__":
    app.run("127.0.0.1",8888,debug=True,threaded=True)