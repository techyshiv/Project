from flask import Flask,render_template,url_for,flash,redirect,jsonify,request,session
from flask import Markup
from flaskwebgui import FlaskUI
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.sql.default_comparator
import os
import json
import num2word
import datetime
import time
from datetime import date, timedelta
from collections import defaultdict 
import smtplib as sm
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
result_stock = defaultdict(int)
db_path=os.path.join(os.path.dirname(__file__))
db_uri='sqlite:///'+os.path.join(db_path,'dbfile.sqlite')
app=Flask(__name__)
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
ui=FlaskUI(app)
app.config['SECRET_KEY'] = 'thisismysecretkeydonotstealit'
app.config['SQLALCHEMY_DATABASE_URI']=db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80))
    email=db.Column(db.String(80))
    password=db.Column(db.String(80))
    confirm_password=db.Column(db.String(80))
    mobile_number=db.Column(db.String(10))

db.create_all()
# def getData(data):
#     return data

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method=='POST':
        name=request.form.get('user')
        email=request.form.get('email')
        password=request.form.get('pass')
        confirm_password=request.form.get('conpass')
        mobile_number=request.form.get('mobile')
        
        user = User.query.filter_by(name=name).first()
        if user:
            data="Username already Exist please Login."
            return render_template('signup.html',data=data)
        else:
            entry=User(name=name,email=email,password=password,confirm_password=confirm_password,mobile_number=mobile_number)
            db.session.add(entry)
            db.session.commit()
            # return redirect(url_for('start'))

            data="You've successfully enroll in our awesome app!"
            prop="alert alert-info"
            with open("user.json","r+") as f:
                json_object=json.loads(f.read())
                if(len(json_object)>=1):
                    f.seek(0)
                    f.truncate()
                    json_object[0]["Name"]=name
                    json_object[0]["Password"]=password
                    json_object[0]["ConfirmPassword"]=confirm_password
                    json_object[0]["Mobile"]=mobile_number
                    json.dump(json_object,f,indent=4)
                else:
                    f.seek(0)
                    f.truncate()
                    json_object.append({"Name":name,"Password":password,"ConfirmPassword":confirm_password,"Mobile":mobile_number})
                    json.dump(json_object,f,indent=4)
            return render_template('signup.html',data=data,prop=prop)

    return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        emaildata=""             
        email = request.form.get('email')
        password = request.form.get('pass')
        user_name=User.query.filter_by(email=email).first()
        all_user=[]
        for i in User.query.order_by(User.email).all():
            all_user.append(i.email)
        # print(all_user)
        # print(user_name)
        if (email in all_user) and (password==user_name.password):
            # print(all_user)
            with open("email.json","r+") as f:
                json_object=json.loads(f.read())
                if len(json_object)>=1:
                    f.seek(0)
                    f.truncate()
                    json_object[0]["Email"]=email 
                    json.dump(json_object,f,indent=4)       
                else:
                    f.seek(0)
                    f.truncate()
                    json_object.append({"Email":email})
                    json.dump(json_object,f,indent=4)
            with open("user.json","r+") as f:
                json_object=json.loads(f.read())
                if "Email" in json_object[0]:
                    pass
                else:
                    json_object[0]["Id"]=1
                    json_object[0]["Email"]=email
                    f.seek(0)
                    f.truncate()
                    json.dump(json_object,f,indent=4)
            with open("area.json","r+") as f:
                jsonobj=json.loads(f.read())
                arealen=None
                exelen=None
                cuslen=None
                total=[]
                grandtotal=None
                if "Area" in jsonobj[0]["User1"]:
                    arealen=len(jsonobj[0]["User1"]["Area"])
                else:
                    arealen=""
                if "Executive" in jsonobj[0]["User1"]:
                    exelen=len(jsonobj[0]["User1"]["Executive"])
                else:
                    exelen=""
                if "Customer_Details" in jsonobj[0]["User1"]:
                    cuslen=len(jsonobj[0]["User1"]["Customer_Details"])
                else:
                    cuslen=""
                if "Payment_Details" in jsonobj[0]["User1"]:
                    grandtotal=jsonobj[0]["User1"]["Payment_Details"]
                    for val in range(len(grandtotal)):
                        if grandtotal[val]["PaymentStatus"] == "Success":
                            total.append(float(grandtotal[val]["GrandTotal"]))
                sum_total = sum(total)
                sum_total = round(sum_total,2)
            return render_template("index.html",email=email,area=arealen,exen=exelen,cus=cuslen,total=sum_total)
        else:
            if (email in all_user) and (password!=user_name.password):
                data1="Oops you entered wrong password"
                prop="alert alert-info"
                return render_template('login.html',data=data1,prop=prop)
            else:
                data1="Username or Email Not Exist Please register."
                prop="alert alert-info"
                return render_template('login.html',data=data1,prop=prop)



@app.route('/start')
def start():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
        with open("area.json","r+") as f:
            jsonobj=json.loads(f.read())
            arealen=None
            exelen=None
            cuslen=None
            total=[]
            grandtotal=None
            if "Area" in jsonobj[0]["User1"]:
                arealen=len(jsonobj[0]["User1"]["Area"])
            else:
                arealen=""
            if "Executive" in jsonobj[0]["User1"]:
                exelen=len(jsonobj[0]["User1"]["Executive"])
            else:
                exelen=""
            if "Customer_Details" in jsonobj[0]["User1"]:
                cuslen=len(jsonobj[0]["User1"]["Customer_Details"])
            else:
                cuslen=""
            if "Payment_Details" in jsonobj[0]["User1"]:
                grandtotal=jsonobj[0]["User1"]["Payment_Details"]
            if grandtotal!=None:
                for val in range(len(grandtotal)):
                    if grandtotal[val]["PaymentStatus"] == "Success":
                        total.append(float(grandtotal[val]["GrandTotal"]))
            sum_total = sum(total)
            sum_total = round(sum_total,2)
    return render_template('index.html',email=data,area=arealen,exen=exelen,cus=cuslen,total=sum_total)

@app.route("/getjson")
def getjson():
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        final=[]
        payment=None
        month=[]
        result_stock1 = defaultdict(int)
        if "Payment_Details" in json_object[0]["User1"]:
            payment=json_object[0]["User1"]["Payment_Details"]
        else:
            payment="No Data Found"
        if payment!="No Data Found":
            for val in range(len(payment)):
                if payment[val]["PaymentStatus"] == "Success":
                    # print("Yes")
                    final.append({
                        "Month":payment[val]["Month"],
                        "Payment":round(float(payment[val]["GrandTotal"]),3)
                    })
                    month.append(payment[val]["Month"])
        # print(final)
        for i in final:
            result_stock1[i['Month']]+=i['Payment']
        out=[{'Month' : k, 'Payment' : v} for k,v in result_stock1.items()]
        return jsonify({"Result":out})
@app.route('/area')
def area():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
        return render_template("area.html",email=data)

@app.route('/adddata',methods=['GET','POST'])
def adddata():
    if request.method=="POST":
        area=request.form.get("arealabel")
        data1="Area Added Successfully!"
        prop="alert alert-info"
        with open("email.json","r+") as rf:
            jsonobject=json.loads(rf.read())
            data=jsonobject[0]["Email"]
            with open("area.json","r+") as f:
                new_data=None
                json_object=json.loads(f.read())
                if "Area" in json_object[0]["User1"]:
                    new_data=json_object[0]["User1"]['Area']
                    for val in range(len(new_data)):
                        if area == new_data[val]['Name']:
                            data1="Area Name Already Exist"
                            break
                        else:
                            new_data.append({"Id":len(new_data)+1,"orderId":"Order"+str(len(new_data)+1),"Name":area})
                            f.seek(0)
                            f.truncate()
                            json_object[0]["User1"]['Area']=new_data
                            json.dump(json_object,f,indent=4)
                            break
                        break
                else:
                    new_data=[{"Id":1,"orderId":"Order1","Name":area}]
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]['Area']=new_data
                    json.dump(json_object,f,indent=4)        
            return render_template("area.html",area=area,data1=data1,prop=prop,org_data=new_data,email=data)            
    return render_template("area.html")

@app.route('/executive')
def executive():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            area_name=[]
            if "Area" in json_object[0]["User1"]:
                new_data=json_object[0]["User1"]["Area"]
            if new_data!=None:
                for val in range(len(new_data)):
                    area_name.append(new_data[val]["Name"])
        return render_template("executive.html",email=data,org_data=area_name)

@app.route('/exedata',methods=["GET","POST"])
def exedata():
    if request.method=="POST":
        area=request.form.get("Executive")
        executive=request.form.get("exelabel")
        exeid=request.form.get("idlabel")
        address=request.form.get("addlabel")
        mob=request.form.get("moblabel")
        what=request.form.get("whatlabel")
        email=request.form.get("emaillabel")
        data1="Executive Details added Successfully!"
        prop="alert alert-info"

        with open("email.json","r+") as f:
            json_object1=json.loads(f.read())
            data=json_object1[0]["Email"]
            with open("area.json","r+") as f:
                new_data=None
                new_data2=None
                json_object=json.loads(f.read())
                area_name=[]
                for val in range(len(json_object)):
                    new_data2=json_object[val][f"User{val+1}"]["Area"]
                for val in range(len(new_data2)):
                    area_name.append(new_data2[val]["Name"])
                if "Executive" in json_object[0]["User1"]:
                    new_data=json_object[0]["User1"]['Executive']
                    for val in range(len(new_data)):
                        if executive==new_data[val]["HawkerName"]:
                            data1="Executive Name Already Exist"
                            break
                        elif exeid==new_data[val]["HawkerId"]:
                            data1="This Id already used by other."
                            break
                        else:
                            new_data.append({"AreaName":area,"HawkerName":executive,"HawkerId":exeid,"Address":address,"MobileNumber":mob,"WhatsAppNumber":what,"Email":email})
                            f.seek(0)
                            f.truncate()
                            json_object[0]["User1"]['Executive']=new_data
                            json.dump(json_object,f,indent=4)
                            break
                        break
                else:
                    new_data=[{"AreaName":area,"HawkerName":executive,"HawkerId":exeid,"Address":address,"MobileNumber":mob,"WhatsAppNumber":what,"Email":email}]
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]['Executive']=new_data
                    json.dump(json_object,f,indent=4)               
            return render_template("executive.html",area=area,data1=data1,prop=prop,email=data,org_data=area_name)
    return render_template("executive.html")

@app.route("/viewdetails")
def viewdetails():
    with open("email.json","r+") as rf:
        json_object=json.loads(rf.read())
        data=json_object[0]["Email"]
        with open("area.json","r+") as f:
            jsonobj=json.loads(f.read())
            new_data=None
            data1=None
            for val in range(len(jsonobj)):
                if "Executive" in jsonobj[val][f"User{val+1}"]:
                    data1=1
                    new_data=jsonobj[val][f"User{val+1}"]["Executive"]
                    break
                break
    return render_template("executive_details.html",email=data,org_data=new_data,data1=data1)
@app.route("/ViewData")
def ViewData():
    with open("email.json","r+") as rf:
        json_object=json.loads(rf.read())
        data=json_object[0]["Email"]            
    return render_template("executive_show_delte.html",email=data)


@app.route("/View",methods=["GET","POST"])
def View():
    if request.method=="POST":
        area=request.form.get("arealabel")
        prop="alert alert-info"
        data2="Data Not Found"
        with open("email.json","r+") as rf:
            jsonobj=json.loads(rf.read())
            data=jsonobj[0]["Email"]
            with open("area.json","r+") as f:
                new_data=None
                org_data=[]
                data1=None
                json_object=json.loads(f.read())
                for val in range(len(json_object)):
                    new_data=json_object[val][f"User{val+1}"]["Executive"]
                for i in range(len(new_data)):
                    if area==new_data[i]["AreaName"]:
                        data1=1
                        org_data.append(
                        {
                            "AreaName":new_data[i]["AreaName"],
                            "HawkerName":new_data[i]["HawkerName"],
                            "HawkerId":new_data[i]["HawkerId"],
                            "Address":new_data[i]["Address"],
                            "MobileNumber":new_data[i]["MobileNumber"],
                            "WhatsAppNumber":new_data[i]["WhatsAppNumber"],
                            "Email":new_data[i]["Email"]
                        }
                        )
                    # print(org_data)
            return render_template("executive_show_delte.html",org_data=org_data,email=data,data1=data1,prop=prop,data2=data2)
    return render_template("executive_show_delte.html")

@app.route("/delete")
def delete():
    with open("email.json","r+") as rf:
        json_object=json.loads(rf.read())
        data=json_object[0]["Email"]
    return render_template("delete.html",email=data)

@app.route("/DeleteData",methods=["GET","POST"])
def DeleteData():
    if request.method=="POST":
        area=request.form.get("arealabel")
        prop="alert alert-info"
        data2="Data Not Found"
        # print(area)
        with open("email.json","r+") as rf:
            json_object=json.loads(rf.read())
            data=json_object[0]["Email"]
            with open("area.json","r+") as f:
                new_data=None
                data1=None
                org_data=None
                new=None
                jsonobj=json.loads(f.read())
                for val in range(len(jsonobj)):
                    new_data=jsonobj[val][f"User{val+1}"]["Executive"]
                    new=val
                # print(new_data)
                for val in range(len(new_data)):
                    if area==new_data[val]["AreaName"]:
                        data1=1
                        f.seek(0)
                        f.truncate()
                        jsonobj[0]["User1"]["Executive"].remove(new_data[val])
                        json.dump(jsonobj,f,indent=4)
                        break
            return render_template("Delete.html",email=data,data1=data1,prop=prop,data2=data2)
    return render_template("Delete.html",email=data)

@app.route("/Customer")
def Customer():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            customer_name=[]
            if "Executive" in json_object[0]["User1"]:
                new_data=json_object[0]["User1"]["Executive"]
            if new_data!=None:
                for val in range(len(new_data)):
                    customer_name.append(new_data[val]["HawkerName"])
        return render_template("Customer.html",email=data,org_data=customer_name)
@app.route("/AddCustomer",methods=["GET","POST"])
def AddCustomer():
    if request.method=="POST":
        exename=request.form.get("Executive")
        cusname=request.form.get("cname")
        cusid=request.form.get("cusid")
        fname=request.form.get("fname")
        address=request.form.get("address")
        mobile=request.form.get("mobile")
        whatsapp=request.form.get("what")
        email=request.form.get("email")
        startdate=request.form.get("startdate")
        enddate=request.form.get("enddate")
        gender=request.form.get("gender")
        data1="Customer Details added Successfully!"
        prop="alert alert-info"
        with open("email.json","r+") as rf:
            jsonobj=json.loads(rf.read())
            data=jsonobj[0]["Email"]
            with open("area.json","r+") as f:
                new_data=None
                new_data2=None
                json_object=json.loads(f.read())
                customer_name=[]
                for val in range(len(json_object)):
                    new_data=json_object[val][f"User{val+1}"]["Executive"]
                for val in range(len(new_data)):
                    customer_name.append(new_data[val]["HawkerName"])
                if "Customer_Details" in json_object[0]["User1"]:
                    new_data=json_object[0]["User1"]['Customer_Details']
                    for val in range(len(new_data)):
                        if cusname==new_data[val]["CustomerName"]:
                            data1="Customer Name Already Exist."
                            break
                        elif cusid==new_data[val]["CustomerId"]:
                            data1="This Id is already used"
                            break
                        else:
                            new_data.append({"ExecutiveName":exename,"CustomerName":cusname,"CustomerId":cusid,"FatherName":fname,"Address":address,"MobileNumber":mobile,"WhatsAppNumber":whatsapp,"Email":email,"Startdate":startdate,"Enddate":enddate,"Gender":gender})                       
                            f.seek(0)
                            f.truncate()
                            json_object[0]["User1"]['Customer_Details']=new_data
                            json.dump(json_object,f,indent=4)
                            break
                        break
                else:
                    new_data=[{"ExecutiveName":exename,"CustomerName":cusname,"CustomerId":cusid,"FatherName":fname,"Address":address,"MobileNumber":mobile,"WhatsAppNumber":whatsapp,"Email":email,"Startdate":startdate,"Enddate":enddate,"Gender":gender}]
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]['Customer_Details']=new_data
                    json.dump(json_object,f,indent=4)                    
            return render_template("Customer.html",email=data,data1=data1,prop=prop,org_data=customer_name)
    return render_template("Customer.html")

@app.route("/product")
def product():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            org_data=[]
            new_data=None
            for val in range(len(json_object)):
                if "ProductDetails" in json_object[val][f"User{val+1}"]:
                    new_data=json_object[val][f"User{val+1}"]["ProductDetails"]
                    for val in range(len(new_data)):
                        org_data.append(new_data[val])
                    break
        return render_template("product.html",email=data,org_data=org_data)
                

@app.route("/Addproduct",methods=["GET","POST"])
def AddProduct():
    if request.method=="POST":
        product_name=request.form.get("product")
        product_code=request.form.get("code")
        product_price=request.form.get("price")
        data1="Product Added Successfully!"
        prop="alert alert-info"
        with open("email.json","r+") as rf:
            jsonobj=json.loads(rf.read())
            data=jsonobj[0]["Email"]
            with open("area.json","r+") as f:
                new_data=None
                sortproduct=None
                json_object=json.loads(f.read())
                if "ProductDetails" in json_object[0]["User1"]:
                    new_data=json_object[0]["User1"]["ProductDetails"]
                    for val in range(len(new_data)):
                        if product_name in new_data[val]["ProductName"]:
                            data1="Product already Exist."
                            break
                        elif product_code ==new_data[val]["ProductCode"]:
                            data1='this Product Code already taken.'
                            break
                        else:
                            new_data.append({"Id":len(new_data)+1,"ProductName":f"{product_name}:{product_code}","ProductCode":product_code,"Product_Price":product_price})
                            f.seek(0)
                            f.truncate()
                            json_object[0]["User1"]['ProductDetails']=new_data
                            json.dump(json_object,f,indent=4)
                            break
                        break
                else:
                    new_data=[{"Id":1,"ProductName":f"{product_name}:{product_code}","ProductCode":product_code,"Product_Price":product_price}]
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]['ProductDetails']=new_data
                    json.dump(json_object,f,indent=4)
            new_data=sorted(new_data,key=lambda i:(i['Product_Price'], i['ProductName']))
            # print(new_data)
            return render_template("product.html",email=data,data1=data1,org_data=new_data,prop=prop)
    return render_template("product.html")

@app.route("/Edit/Product/")
def EditProduct():
    pro=request.args.get("id")
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        product=json_object[0]["User1"]["ProductDetails"]
        Name=None
        Code=None
        price=None
        for val in range(len(product)):
            if pro==product[val]["ProductCode"]:
                Name=product[val]["ProductName"]
                Code=product[val]["ProductCode"]
                price=product[val]["Product_Price"]
                break
    return render_template("edit_product.html",name=Name,code=Code,price=price,email=data)

@app.route("/updatedata",methods=["GET","POST"])
def updatedata():
    if request.method=="POST":
        product_name=request.form.get("productname")
        product_code=request.form.get("productcode")
        product_price=request.form.get("productprice")
        data1="Product Updated Successfully"
        prop="alert alert-info"
        with open("email.json","r+") as rf:
            jsonobj=json.loads(rf.read())
            data=jsonobj[0]["Email"]
            with open("area.json","r+") as f:
                json_object=json.loads(f.read())
                for val in range(len(json_object[0]["User1"]["ProductDetails"])):
                    if product_code==json_object[0]["User1"]["ProductDetails"][val]["ProductCode"]:
                        f.seek(0)
                        f.truncate()
                        json_object[0][f"User1"]["ProductDetails"][val]["ProductName"]=product_name
                        json_object[0][f"User1"]["ProductDetails"][val]["ProductCode"]=product_code
                        json_object[0][f"User1"]["ProductDetails"][val]["Product_Price"]=product_price
                        json.dump(json_object,f,indent=4)
                        break
            return render_template("edit_product.html",email=data,data1=data1,prop=prop)

@app.route("/Delete/Product/")
def DeleteProducts():
    pro=request.args.get("id")
    data1="Product Deleted Successfully"
    prop="alert alert-info"
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            product=json_object[0]["User1"]["ProductDetails"]
            org_data=[]
            for val in range(len(product)):
                if pro==product[val]["ProductCode"]:
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["ProductDetails"].remove(product[val])
                    json.dump(json_object,f,indent=4)
                    break
            if(len(product)==0):
                f.seek(0)
                f.truncate()
                del json_object[0]["User1"]["ProductDetails"]
                json.dump(json_object,f,indent=4)
            else:
                for val in range(len(product)):
                    org_data.append(product[val])
        return render_template("product.html",data1=data1,prop=prop,org_data=org_data,email=data)


@app.route("/stock")
def stock():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        data1=0
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            for val in range(len(json_object)):
                if "ProductDetails" in json_object[val][f"User{val+1}"]:
                    data1=1
                    new_data=json_object[val][f"User{val+1}"]["ProductDetails"]
                    break
        return render_template("stock_master.html",email=data,values=new_data,data1=data1)

@app.route("/StockMaster",methods=["GET","POST"])
def StockMaster():
    if request.method=="POST":
        final=request.form.get('name')
        data1=request.form.getlist('data[]')
        data2=request.form.getlist('data1[]')
        data3=request.form.getlist('data3[]')
        # print(final)
        # print(data1)
        # print(data2)
        # print(data3)
        with open("email.json","r+") as rf:
            jsonobj=json.loads(rf.read())
            data=jsonobj[0]["Email"]
            with open("area.json","r+") as f:
                json_object=json.loads(f.read())
                new_data=None
                data4=""
                if "StockDetails" in json_object[0]["User1"]:
                    new_data=json_object[0]["User1"]["StockDetails"]
                    for val in range(len(new_data)):
                        if final==new_data[val]["ProductName"]:
                            data4="Yes"
                            break
                        else:
                            data4="Good"
                            new_data.append({"Id":len(new_data)+1,"ProductName":final,"Ingredients":data1,"Quantity":data2,"Unit":data3})
                            f.seek(0)
                            f.truncate()
                            json_object[0]["User1"]['StockDetails']=new_data
                            json.dump(json_object,f,indent=4)
                            break
                        break
                else:
                    new_data=[{"Id":1,"ProductName":final,"Ingredients":data1,"Quantity":data2,"Unit":data3}]
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]['StockDetails']=new_data
                    json.dump(json_object,f,indent=4)
            return jsonify({"Result":data4})
        # return render_template("Stock_master.html",email=data)
@app.route("/ShowStock")
def ShowStock():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            new_data1=None
            data1=0
            if "ProductDetails" in json_object[0]["User1"]:
                data1=1
                new_data1=json_object[0]["User1"]["ProductDetails"]
            if "StockDetails" in json_object[0]["User1"]:
                new_data=json_object[0]["User1"]["StockDetails"]
            else:
                new_data=[]
            return render_template("stock_master.html",org_data=new_data,email=data,values=new_data1,data1=data1)

@app.route('/Record')
def Record():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        data1=0
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            if "Area" in json_object[0]["User1"]:
                data1=1
                new_data=json_object[0]["User1"]["Area"]
        return render_template("record.html",email=data,new_data=new_data,data1=data1)

@app.route("/ViewRecord",methods=["GET","POST"])
def ViewRecord():
    if request.method=="POST":
        AreaName=request.form.get("name")
        ExeName=request.form.get("exename")
        # print(AreaName)
        # print(ExeName)
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            new_data1=None
            mess = ""
            result=[]
            if "Executive" in json_object[0]["User1"]:
                new_data=json_object[0]["User1"]["Executive"]
            if "Customer_Details" in json_object[0]["User1"]:
                new_data1=json_object[0]["User1"]["Customer_Details"]

            if new_data!=None and new_data1!=None:
                for val in range(len(new_data)):
                    if AreaName =="All" and ExeName=="All":
                        for item in range(len(new_data1)):
                            mess = "Customer"
                            result.append(new_data1[item])
                    elif AreaName ==new_data[val]["AreaName"] and ExeName==new_data[val]["HawkerName"]:
                        mess = "Customer"
                        for item in range(len(new_data1)):
                            if ExeName==new_data1[item]["ExecutiveName"]:
                                result.append(new_data1[item])
            else:
                if "Payment_Details" in json_object[0]["User1"]:
                    mess = "Payment"
                    result = json_object[0]["User1"]["Payment_Details"]
        if len(result)==0:    
            return jsonify({"Result":"No Data Found"})
        else:
            # print(result)
            return jsonify({"Result":result,"Message":mess})

@app.route("/RecordView",methods=["GET","POST"])
def RecordView():
    if request.method=="POST":
        month=request.form.get("month")
        cus_id=request.form.get("cusname")
        # print(cus_id)
        new_data=[]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            if "Payment_Details" in json_object[0]["User1"]:
                payment_details=json_object[0]["User1"]["Payment_Details"]
                for val in range(len(payment_details)):
                    if month == payment_details[val]["Month"] and int(cus_id) == payment_details[val]["CustomerId"]:
                        new_data.append(payment_details[val])
            else:
                new_data.append("No Data Found")
        # print(new_data)
        return jsonify({"Result":new_data})

@app.route("/Invoice")
def Invoice():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            product_data=None
            data1=0
            if "ProductDetails" in json_object[0]["User1"]:
                data1=1
                new_data=json_object[0]["User1"]["ProductDetails"]
        return render_template("invoice.html",email=data,org_data=new_data,data1=data1)

@app.route("/Invoice/executive")
def data():
    area=request.args.get('area')
    executive=request.args.get('')
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        exe_list=[]
        if "Executive" in json_object[0]["User1"]:
            new_data=json_object[0]["User1"]["Executive"]
            for val in range(len(new_data)):
                if area =="All":
                    exe_list.append(new_data[val])
                elif area in new_data[val]["AreaName"]:
                    exe_list.append(new_data[val])
        return jsonify({"Result":exe_list})
        
@app.route("/Invoice/customer")
def customer():
    executive=request.args.get('executive')
    # print(executive)
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        cus_list=[]
        if "Customer_Details" in json_object[0]["User1"]:
            new_data=json_object[0]["User1"]["Customer_Details"]
        for val in range(len(new_data)):
            if executive =="All":
                cus_list.append(new_data[val])
            elif executive in new_data[val]["ExecutiveName"]:
                cus_list.append(new_data[val])
        return jsonify({"Result":cus_list})

@app.route("/Invoice/details")
def details():
    cus_name=request.args.get("customer")
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        cus_list=[]
        for val in range(len(json_object)):
            new_data=json_object[val][f"User{val+1}"]["Customer_Details"]
        for val in range(len(new_data)):
            if cus_name==new_data[val]["CustomerName"]:
                cus_list.append(new_data[val])
        return jsonify({"Result":cus_list})

@app.route("/Invoice/Product")
def productdata():
    pro=request.args.get("pro")
    # print(pro)
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        pro_list=[]
        for val in range(len(json_object)):
            new_data=json_object[val][f"User{val+1}"]["ProductDetails"]
        for val in range(len(new_data)):
            if pro==new_data[val]["ProductName"]:
                pro_list.append(new_data[val])
        return jsonify({"Result":pro_list})

@app.route("/Payment",methods=["GET","POST"])
def Payment():
    if request.method=="POST":
        name=request.form.get("name")
        address=request.form.get("address")
        mobile=request.form.get("mobile")
        email=request.form.get("email")
        date=request.form.get("date")
        month=request.form.get("month")
        year=request.form.get("year")
        payment_mode=request.form.get("mode")
        data1=request.form.getlist('data1[]')
        data2=request.form.getlist('data2[]')
        data3=request.form.getlist('data3[]')
        data4=request.form.getlist('data4[]')
        subtotal=request.form.get("subtotal")
        tax=request.form.get("tax")
        taxammount=request.form.get("taxammount")
        grandtotal=request.form.get("GrandTotal")
        gst=request.form.get("GST")
        m,d,y=request.form.get("fulldate").split("/")
        fulldate=y + "-" + m + "-" + d
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            exename=None
            cusid=None
            count=0
            cus_detail=None
            if "Customer_Details" in json_object[0]["User1"]:
                cus_detail=json_object[0]["User1"]["Customer_Details"]
                names=[cus_detail[i]["CustomerName"] for i in range(len(cus_detail))]
                if name not in names:
                    cus_detail.append({  
                        "ExecutiveName":"Self",
                        "CustomerName":name,
                        "CustomerId":len(cus_detail)+1,
                        "FatherName":"",
                        "Address":address,
                        "MobileNumber":mobile,
                        "WhatsAppNumber":mobile,
                        "Email":email,
                        "Gender":"Person"
                    })
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]['Customer_Details']=cus_detail
                    json.dump(json_object,f,indent=4)
            else:
                cus_detail=[{
                    "ExecutiveName":"Self",
                    "CustomerName":name,
                    "CustomerId":1,
                    "FatherName":"",
                    "Address":address,
                    "MobileNumber":mobile,
                    "WhatsAppNumber":mobile,
                    "Email":email,
                    "Gender":"Person"
                }]
                f.seek(0)
                f.truncate()
                json_object[0]["User1"]['Customer_Details']=cus_detail
                json.dump(json_object,f,indent=4)
            for val in range(len(cus_detail)):
                if cus_detail[val]["CustomerName"] in name:
                    exename =cus_detail[val]["ExecutiveName"]
                    cusid=cus_detail[val]["CustomerId"]
            for val in range(len(json_object)):
                if "Payment_Details" in json_object[val][f"User{val+1}"]:
                    new_data=json_object[val][f"User{val+1}"]["Payment_Details"]
                    count+=len(new_data)
                    new_data.append({
                        "Id":str(len(new_data)+1),
                        "Name":name,
                        "Executive":exename,
                        "CustomerId":cusid,
                        "Address":address,
                        "Mobile":mobile,
                        "Email":email,
                        "Date":date,
                        "Month":month,
                        "Year":year,
                        "FullDate":fulldate,
                        "PaymentMode":payment_mode,
                        "PaymentStatus":"pending",
                        "Product":data1,
                        "Quantity":data2,
                        "Price":data3,
                        "Ammount":data4,
                        "GST":gst,
                        "Tax":tax,
                        "TaxAmmount":taxammount,
                        "SubTotal":subtotal,
                        "GrandTotal":grandtotal
                    })
                    f.seek(0)
                    f.truncate()
                    json_object[val][f"User{val+1}"]['Payment_Details']=new_data
                    json.dump(json_object,f,indent=4)
                else:
                    count=0
                    new_data=[
                        {
                        "Id":"1",
                        "Name":name,
                        "Executive":exename,
                        "CustomerId":cusid,
                        "Address":address,
                        "Mobile":mobile,
                        "Email":email,
                        "Date":date,
                        "Month":month,
                        "Year":year,
                        "FullDate":fulldate,
                        "PaymentMode":payment_mode,
                        "PaymentStatus":"pending",
                        "Product":data1,
                        "Quantity":data2,
                        "Price":data3,
                        "Ammount":data4,
                        "GST":gst,
                        "Tax":tax,
                        "TaxAmmount":taxammount,
                        "SubTotal":subtotal,
                        "GrandTotal":grandtotal
                    }
                    ]
                    f.seek(0)
                    f.truncate()
                    json_object[val][f"User{val+1}"]['Payment_Details']=new_data
                    json.dump(json_object,f,indent=4)
            
        return jsonify({"Result":new_data[count]["Id"]})

@app.route("/invoice/showInvoice/")
def make_payment():
    user=request.args.get("id")
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        id=None
        cusname=None
        address=None
        mobile=None
        date=None
        month=None
        year=None
        product=None
        quantity=None
        price=None
        amm=None
        tax=None
        subtotal=None
        grand=None
        taxammount=None
        full=None
        for val in range(len(json_object)):
            new_data=json_object[val][f"User{val+1}"]["Payment_Details"]
        for val in range(len(new_data)):
            if user==new_data[val]["Id"]:
                id=new_data[val]["Id"]
                cusname=new_data[val]["Name"]
                address=new_data[val]["Address"]
                email=new_data[val]["Email"]
                mobile=new_data[val]["Mobile"]
                date=new_data[val]["Date"]
                month=new_data[val]["Month"]
                year=new_data[val]["Year"]
                product=new_data[val]["Product"]
                quantity=new_data[val]["Quantity"]
                price=new_data[val]["Price"]
                amm=new_data[val]["Ammount"]
                tax=new_data[val]["Tax"]
                taxammount=new_data[val]["TaxAmmount"]
                subtotal=new_data[val]["SubTotal"]
                grand=new_data[val]["GrandTotal"]
                length=[i+1 for i in range(len(product))]
    return render_template("invoice_print.html",id=id,name=cusname,add=address,mob=mobile,date=date,month=month,year=year,product=product,tax=tax,taxam=taxammount,sub=subtotal,total=grand,emails=email,quan=quantity,price=price,amm=amm,email=data,length=length)

@app.route("/Invoice/Payment/Success")
def Success():
    id=request.args.get("pro")
    # print(id)
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        for val in range(len(json_object)):
            new_data=json_object[val][f"User{val+1}"]["Payment_Details"]
            # print(new_data)
            for val in range(len(new_data)):
                if id==new_data[val]["Id"]:
                    # print("Yes")
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["Payment_Details"][val]["PaymentStatus"]="Success"
                    # print(json_object)
                    json.dump(json_object,f,indent=4)
    return render_template("invoice_print.html")

@app.route("/ViewInvoice")
def ViewInvoice():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            area_name=None
            data1=0
            if "Area" in json_object[0]["User1"]:
                data1=1
                area_name=json_object[0]["User1"]["Area"]
        return render_template("view_invoice.html",email=data,area=area_name,data1=data1)

@app.route("/get/customer_data")
def get_customer_data():
    cus_detail = []
    with open("area.json","r+") as f:
        data = json.loads(f.read())
        if "Payment_Details" in data[0]["User1"]:
            cus_detail.append(data[0]["User1"]["Payment_Details"][-1])
        return jsonify({
            "Status":"Success",
            "Data":cus_detail
        })
    
@app.route("/Invoice/getdata/")
def view_invoice():
    date1=request.args.get("pro")
    out=list(date1.split(","))
    strat=out[0]
    end=out[1]
    name=out[2]
    duration=out[3]
    exename=out[4]
    m,d,y=out[5].split("/")
    full=y + "-" + m + "-" + d
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        data=None
        new_data=[]
        invoice_details=None
        payment=None
        if "Payment_Details" in json_object[0]["User1"]:
            payment=json_object[0]["User1"]["Payment_Details"]
        if duration=="Today":
            if payment!=None:
                for val in range(len(payment)):
                    if full==payment[val]["FullDate"] and exename=="All":
                        new_data.append(payment[val])
                    elif full==payment[val]["FullDate"] and exename==payment[val]["Executive"]:
                        new_data.append(payment[val])
        else:
            if payment!=None:
                for val in range(len(payment)):
                    if exename=="All":
                        getdate=payment[val]["FullDate"]
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2-d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        # print(d3)
                        if d3 in all_dates:
                            new_data.append(payment[val])
                        else:
                            pass
                    
                    elif exename==payment[val]["Executive"]:
                        getdate=payment[val]["FullDate"]
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2 - d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        if d3 in all_dates:
                            new_data.append(payment[val])
                        else:
                            pass
        copy_invoice = []
        for val in range(len(new_data)):
            if new_data[val]["PaymentStatus"] == "Success":
                copy_invoice.append(new_data[val])
    return jsonify({"Result":copy_invoice})

@app.route("/payment_report")
def payment_report():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            area_name=None
            data1=0
            if "Area" in json_object[0]["User1"]:
                data1=1
                area_name=json_object[0]["User1"]["Area"]
    return render_template("Payment_Report.html",email=data,area=area_name,data1=data1)

@app.route("/Payment/Daybook/")
def show_payment_report():
    data1=request.args.get("pro")
    out=list(data1.split(","))
    # print(f"Out is:{out}")
    cus_name=out[2]
    duration=out[3]
    strat=out[0]
    end=out[1]
    y,d,m=out[4].split("-")
    full=y + "-" + d + "-" + m
    # print(f"Full is:{full}")
    exename=out[5]
    invoice_type=out[6]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        data=None
        new_data=None
        new_data1=None
        invoice_details=[]
        cus_details=[]
        if "Payment_Details" in json_object[0]["User1"]:
            new_data=json_object[0]["User1"]["Payment_Details"]
        if "Customer_Details" in json_object[0]["User1"]:
            new_data1=json_object[0]["User1"]["Customer_Details"]   
        if duration=="Today":
            # print("Today")
            if(new_data!=None):
                for val in range(len(new_data)):
                    if full==new_data[val]["FullDate"] and cus_name=="All" and invoice_type=="All":
                        # print("First Condition")
                        invoice_details.append(new_data[val])
                    elif full==new_data[val]["FullDate"] and cus_name =="All" and invoice_type==new_data[val]["GST"]:
                        # print("Second Condition")
                        invoice_details.append(new_data[val])
                    elif full==new_data[val]["FullDate"] and cus_name in new_data[val]["Name"] and invoice_type=="All":
                        # print("First Condition")
                        invoice_details.append(new_data[val])
                    elif full==new_data[val]["FullDate"] and cus_name in new_data[val]["Name"] and invoice_type==new_data[val]["GST"]:
                        # print("Second Condition")
                        invoice_details.append(new_data[val])
        else:
            if(new_data!=None):
                for val in range(len(new_data)):
                    if cus_name =="All" and invoice_type=="All":
                        getdate=new_data[val]["FullDate"]
                        # print(getdate)
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2 - d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        if d3 in all_dates:
                            invoice_details.append(new_data[val])
                        else:
                            pass
                    elif cus_name =="All" and invoice_type==new_data[val]["GST"]:
                        getdate=new_data[val]["FullDate"]
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2 - d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        if d3 in all_dates:
                            invoice_details.append(new_data[val])
                        else:
                            pass

                    elif cus_name in new_data[val]["Name"] and invoice_type=="All":
                        getdate=new_data[val]["FullDate"]
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2 - d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        if d3 in all_dates:
                            invoice_details.append(new_data[val])
                        else:
                            pass
                    elif cus_name in new_data[val]["Name"] and invoice_type==new_data[val]["GST"]:
                        getdate=new_data[val]["FullDate"]
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2 - d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        if d3 in all_dates:
                            new_data.append(new_data[val])
                        else:
                            pass
        copy_invoice = []
        for val in range(len(invoice_details)):
            if invoice_details[val]["PaymentStatus"] == "Success":
                copy_invoice.append(invoice_details[val])
                
    return jsonify({"Invoice":invoice_details})

@app.route("/MostCustomer")
def MostCustomer():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        return render_template("Most_Customer.html",email=data)

@app.route("/Frequent/Customer",methods=["GET","POST"])
def ShowCustomer():
    if request.method=="POST":
        month=request.form.get("month")
        year=request.form.get("year")
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            if "Payment_Details" in json_object[0]["User1"]:
                new_data=json_object[0]["User1"]["Payment_Details"]
            name=[]
            payment_details=[]
            if new_data!=None:
                for val in range(len(new_data)):
                    if year==new_data[val]["Year"] and month==new_data[val]["Month"]:
                        name.append(new_data[val]["Name"])
                        payment_details.append({
                            "CustomerId":new_data[val]["CustomerId"],
                            "CustomerName":new_data[val]["Name"],
                            "Total":new_data[val]["GrandTotal"],
                            "Visited":name.count(new_data[val]["Name"]),
                            "Executive":new_data[val]["Executive"],
                            "Length":val+1
                        })
                        # name.pop()
        payment_details=sorted(payment_details,key=lambda i: i['Visited'],reverse=True)
        return jsonify({"payment":payment_details})
            
@app.route("/MostProduct")
def MostProduct():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        return render_template("Most_Product.html",email=data)

@app.route("/Frequent/Product",methods=["GET","POST"])
def ShowCustomers():
    if request.method=="POST":
        month=request.form.get("month")
        year=request.form.get('year')
        new_data=None
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            payment=None
            product_price=None
            if "Payment_Details" in json_object[0]["User1"] and "ProductDetails" in json_object[0]["User1"] :
                payment=json_object[0]["User1"]["Payment_Details"]
                product_price=json_object[0]["User1"]["ProductDetails"]
            tax=[]
            payment_details=[]
            pro_price=[{}]
            if product_price!=None:
                for i in range(len(product_price)):
                    pro_price[0][product_price[i]["ProductName"]]=product_price[i]["Product_Price"]
            if payment!=None:
                for val in range(len(payment)):
                    if month==payment[val]["Month"] and year==payment[val]["Year"] and product_price!=None:
                        for val1 in range(len(payment[val]["Product"])):
                            payment_details.append({
                                "Product":payment[val]["Product"][val1],
                                "Price":payment[val]["Ammount"][val1],
                                "Sold":payment[val]["Quantity"][val1]
                            })
                        tax.append(payment[val]["Tax"])
            if payment!=None and product_price!=None:
                result1 = defaultdict(int)
                result2 = defaultdict(int)
                for d in payment_details:
                    result1[d['Product']]+=float(d['Price'])
                for d in payment_details:
                    result2[d['Product']]+=int(d['Sold'])
                out=[{'Product': name, 'Ammount': value} for name, value in result1.items()]
                out1=[{'Product': name, 'Sold': value} for name, value in result2.items()]
                # print(tax)
                for i in range(len(out)):
                    out[i]["Price"]=pro_price[0].get(out[i]["Product"])
                    out[i]["Sold"]=out1[i]['Sold']
                    out[i]["Length"]=i+1
                for i in range(len(out)):
                    for j in range(len(tax)):
                        out[i]["Total"]=out[i]['Ammount']+out[i]['Ammount']*(int(tax[j])/100)
                out=sorted(out,key=lambda i:i['Sold'],reverse=True)     
            else:
                out="No Data Found"      
        return jsonify({"Result":out})

@app.route("/StockRecord")
def StockRecord():
    with open("email.json","r+") as rf:
        jsonobj=json.loads(rf.read())
        data=jsonobj[0]["Email"]
        data1=0
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=None
            if "Area" in json_object[0]["User1"]:
                data1=1
                new_data=json_object[0]["User1"]["Area"]
        return render_template("stock_record.html",email=data,org_data=new_data,data1=data1)

@app.route("/StockDetails/")
def StockDetails():
    data1=request.args.get("pro")
    out=list(data1.split(","))
    day=out[2]
    strat=out[0]
    end=out[1]
    exe_name=out[3]
    full=out[4]
    # print(strat)
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        payment=None
        products=None
        if "Payment_Details" in json_object[0]["User1"]:
            payment=json_object[0]["User1"]["Payment_Details"]
        if "StockDetails" in json_object[0]["User1"]:
            products=json_object[0]["User1"]["StockDetails"]
        product_details=[]
        new_data=[]
        if day=="Today":
            if payment!=None:
                for val in range(len(payment)):
                    if full==payment[val]["FullDate"] and exe_name=="All":
                        new_data.append(payment[val])
                    elif full==payment[val]["FullDate"] and exe_name==payment[val]["Executive"]:
                        new_data.append(payment[val])
        else:
            if payment!=None:
                for val in range(len(payment)):
                    if exe_name=="All":
                        getdate=payment[val]["FullDate"]
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2 - d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        # print(d3)
                        if d3 in all_dates:
                            new_data.append(payment[val])
                        else:
                            pass
                    elif exe_name==payment[val]["Executive"]:
                        getdate=payment[val]["FullDate"]
                        y2,m2,d2=getdate.split("-")
                        y2,m2,d2=int(y2),int(m2),int(d2)
                        y,m,d=strat.split("-")
                        y1,m1,d1=end.split("-")
                        m,d,y=int(m),int(d),int(y)
                        m1,d1,y1=int(m1),int(d1),int(y1)
                        if len(str(m2))<2:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + "0" + str(m2) + "-" + str(d2)
                        else:
                            if len(str(d2))<2:
                                d3=str(y2) + "-" + str(m2) + "-" + "0" + str(d2)
                            else:
                                d3=str(y2) + "-" + str(m2) + "-" + str(d2)
                        d2=date(y1,m1,d1)
                        d1=date(y,m,d)
                        delta = d2 - d1
                        all_dates = []
                        for i in range(delta.days + 1):
                            day = d1 + timedelta(days=i)
                            all_dates.append(str(day))
                        # print(d3)
                        if d3 in all_dates:
                            new_data.append(payment[val])
                        else:
                            pass
        if len(new_data)>0:
            for val in range(len(new_data)):
                for i in range(len(new_data[val]["Product"])):
                    if products!=None:
                        for j in range(len(products)):
                            if new_data[val]["Product"][i]==products[j]["ProductName"]:
                                product_details.append({
                                "Product":new_data[val]["Product"][i],
                                "Quantity":new_data[val]["Quantity"][i],
                                "Ingredients":len(products[j]["Ingredients"]),
                                "IngreQuan":sum([int(q) for q in products[j]["Quantity"]]),
                                "Unit":sum([int(value[0]) for value in products[j]["Unit"]]),
                                "FullDate":new_data[val]["FullDate"]
                                })
                           
                    else:
                        product_details.append({
                        "Product":new_data[val]["Product"][i],
                        "Quantity":new_data[val]["Quantity"][i],
                        "Ingredients":0,
                        "IngreQuan":0,
                        "Unit":0,
                        "FullDate":new_data[val]["FullDate"]
                        })
        else:
            product_details="No Data Found"
        # print(product_details)

    return jsonify({"Result":product_details})

@app.route("/profile")
def profile():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    return render_template("profile.html",email=data)

@app.route("/Profile")
def Profile_Data():
    with open("user.json","r+") as f:
        json_object=json.loads(f.read())
        Name=json_object[0]["Name"]
        Email=json_object[0]["Email"]
        Mobile=json_object[0]["Mobile"]
        Details={
            'Name':Name,
            'Email':Email,
            'Mobile':Mobile
        }
        return jsonify({"Result":Details}) 

@app.route("/payment_update")
def payment_update():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    return render_template("payment_update.html",email=data)

@app.route("/update_payment",methods=["GET","POST"])
def update_payment():
    if request.method=="POST":
        invoice_id=request.form.get("invoicelabel")
        # print(invoice_id)
        with open("email.json","r+") as f:
            json_object=json.loads(f.read())
            data=json_object[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            data1=None
            data2="Payment Status already Success"
            prop="alert alert-info"
            payment=json_object[0]["User1"]["Payment_Details"]
            for val in range(len(payment)):
                if invoice_id==payment[val]["Id"]:
                    # print("Yes")
                    if payment[val]["PaymentStatus"]=="Success":
                        # print("yes")
                        data2="Payment Status already Success"
                        data1=2
                        # print(data2)
                        break
                    else:
                        data1=1
                        f.seek(0)
                        f.truncate()
                        json_object[0]["User1"]["Payment_Details"][val]["PaymentStatus"]="Success"
                        json.dump(json_object,f,indent=4)
                else:
                    data2="Invoice Id is Not Present."
        return render_template("payment_update.html",data1=data1,prop=prop,data2=data2,email=data)

@app.route("/invoice/invoice_autocomplete",methods=["POST"])
def Autocomplete():
    data=request.get_json(force=True)
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        cus_detail=None
        result=[]
        if "Customer_Details" in json_object[0]["User1"]:
            cus_detail=json_object[0]["User1"]["Customer_Details"]
        if cus_detail!=None:
            for val in range(len(cus_detail)):
                if data['words'] in cus_detail[val]["CustomerName"] or data['words'] in cus_detail[val]["WhatsAppNumber"]:
                    result.append(cus_detail[val])
    return jsonify({"Result":result})

@app.route("/Edit/Executive/")
def EditExecutive():
    exename=request.args.get("id")
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        exedetails=json_object[0]["User1"]["Executive"]
        id=None
        name=None
        for val in range(len(exedetails)):
            if exename==exedetails[val]["HawkerName"]:
                area=exedetails[val]["AreaName"]
                id=exedetails[val]["HawkerId"]
                break
    return render_template("edit_executive.html",area=area,email=data,id=id,exename=exename)

@app.route("/editexecutive",methods=["GET","POST"])
def editexecutive():
    if request.method=="POST":
        exeid=request.form.get("exeid")
        id=request.form.get("id")
        areaname=request.form.get("area")
        exename=request.form.get("exename")
        address=request.form.get("address")
        mobile=request.form.get("mobile")
        whatsapp=request.form.get("what")
        email=request.form.get("email")
        with open("email.json","r+") as f:
            json_object=json.loads(f.read())
            data=json_object[0]["Email"]
            payment_details=None
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            exedetails=json_object[0]["User1"]["Executive"]
            if "Payment_Details" in json_object[0]["User1"]:
                payment_details=json_object[0]["User1"]["Payment_Details"]
            data1="Executive Details Updated Successfully"
            prop="alert alert-info"
            for val in range(len(exedetails)):
                if id==exedetails[val]["HawkerId"]:
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["Executive"][val]["AreaName"]=areaname
                    json_object[0]["User1"]["Executive"][val]["HawkerName"]=exename
                    json_object[0]["User1"]["Executive"][val]["HawkerId"]=id
                    json_object[0]["User1"]["Executive"][val]["Address"]=address
                    json_object[0]["User1"]["Executive"][val]["MobileNumber"]=mobile
                    json_object[0]["User1"]["Executive"][val]["WhatsAppNumber"]=whatsapp
                    json_object[0]["User1"]["Executive"][val]["Email"]=email
                    json.dump(json_object,f,indent=4)
                    break
            if payment_details!=None:
                for val in range(len(payment_details)):
                    if exeid==payment_details[val]["Executive"]:
                        f.seek(0)
                        f.truncate()
                        json_object[0]["User1"]["Payment_Details"][val]["Executive"]=exename
                        json.dump(json_object,f,indent=4)
        return render_template("edit_executive.html",email=data,data1=data1,prop=prop)


@app.route("/View/Executive/")
def VIEWExecutive():
    exename=request.args.get("id")
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        exedetails=json_object[0]["User1"]["Executive"]
        name=None
        for val in range(len(exedetails)):
            if exename==exedetails[val]["HawkerName"]:
                area=exedetails[val]["AreaName"]
                exename=exedetails[val]["HawkerName"]
                address=exedetails[val]["Address"]
                mobile=exedetails[val]["MobileNumber"]
                what=exedetails[val]["WhatsAppNumber"]
                email=exedetails[val]["Email"]
                break
    return render_template("view_executive.html",area=area,email=data,exename=exename,address=address,mobile=mobile,what=what,emails=email)

@app.route("/delete/Executive/")
def delteExecutive():
    exename=request.args.get("id")
    # print(exename)
    with open("email.json","r+") as f:
        jsonobject=json.loads(f.read())
        data=jsonobject[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        payment_details=None
        exedetails=json_object[0]["User1"]["Executive"]
        if "Payment_Details" in json_object[0]["User1"]: 
            payment_details=json_object[0]["User1"]["Payment_Details"]
        data2="Executive Details Deleted Successfully"
        prop="alert alert-info"
        # print(exedetails)
        for val in range(len(exedetails)):
            if exename==exedetails[val]["HawkerName"]:
                # print('Yes')
                f.seek(0)
                f.truncate()
                json_object[0]["User1"]["Executive"].remove(exedetails[val])
                json.dump(json_object,f,indent=4)
                break
        length=0
        if payment_details!=None:
            for val1 in range(len(payment_details)):
                if exename==payment_details[length+val1]["Executive"]:
                    # print(payment_details)
                    length-=1
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["Payment_Details"].remove(payment_details[val1])
                    json.dump(json_object,f,indent=4)
        if(len(exedetails)==0):
                f.seek(0)
                f.truncate()
                del json_object[0]["User1"]["Executive"]
                json.dump(json_object,f,indent=4)
        if payment_details!=None:
            if(len(payment_details)==0):
                f.seek(0)
                f.truncate()
                del json_object[0]["User1"]["Payment_Details"]
                json.dump(json_object,f,indent=4)
    return render_template("executive_details.html",email=data,data2=data2,prop=prop,org_data=exedetails,data1=1)
    
@app.route("/AddTemplate")
def AddTemplate():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    return render_template("add_template.html",email=data)

@app.route("/addnotice",methods=["GET","POST"])
def addnotice():
    if request.method=="POST":
        notice=request.form.get("Notice")
        sub=request.form.get("Sub")
        mess=request.form.get("mess")
        data1="Template Added Successfully!"
        prop="alert alert-info"
        with open("email.json","r+") as rf:
            jsonobject=json.loads(rf.read())
            data=jsonobject[0]["Email"]
            with open("area.json","r+") as f:
                new_data=None
                json_object=json.loads(f.read())
                if "Notice" in json_object[0]["User1"]:
                    new_data=json_object[0]["User1"]['Notice']
                    for val in range(len(new_data)):
                        if notice == new_data[val]['NoticeName']:
                            data1="Notice Name Already Exist"
                            prop="alert alert-danger"
                        else:
                            new_data.append({"Id":len(new_data)+1,"NoticeName":notice,"Subject":sub,"Body":mess})
                            f.seek(0)
                            f.truncate()
                            json_object[0]["User1"]['Notice']=new_data
                            json.dump(json_object,f,indent=4)
                            break
                        break
                else:
                    new_data=[{"Id":1,"NoticeName":notice,"Subject":sub,"Body":mess}]
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]['Notice']=new_data
                    json.dump(json_object,f,indent=4)        
            return render_template("add_template.html",data1=data1,prop=prop,email=data)            

@app.route("/allnotice")
def allnotice():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        if "Notice" in json_object[0]["User1"]:
            new_data=json_object[0]["User1"]["Notice"]
        else:
            new_data=[]
        return render_template("all_notice.html",org_data=new_data,email=data)

@app.route("/Edit/Notice/")
def editnotice():
    name=request.args.get("id")
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=json_object[0]["User1"]["Notice"]
        for val in range(len(new_data)):
            notice=None
            sub=None
            mess=None
            if name==new_data[val]["NoticeName"]:
                notice=new_data[val]["NoticeName"]
                sub=new_data[val]["Subject"]
                mess=new_data[val]["Body"]
                break
    return render_template("edit_notice.html",notice=notice,sub=sub,mess=mess,email=data)

@app.route("/edit/notice",methods=["GET","POST"])
def EditNotice():
    if request.method=="POST":
        notice=request.form.get("name")
        sub=request.form.get("subject")
        mess=request.form.get("body")
        with open("email.json","r+") as f:
            json_object=json.loads(f.read())
            data=json_object[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            new_data=json_object[0]["User1"]["Notice"]
            data1=""
            prop=""
            for val in range(len(new_data)):
                if notice==new_data[val]["NoticeName"]:
                    data1="Notice Updated Successfully"
                    prop="alert alert-info"
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["Notice"][val]["NoticeName"]=notice
                    json_object[0]["User1"]["Notice"][val]["Subject"]=sub
                    json_object[0]["User1"]["Notice"][val]["Body"]=mess
                    json.dump(json_object,f,indent=4)
        return render_template("edit_notice.html",email=data,data1=data1,prop=prop)

@app.route("/View/Notice/")
def viewnotice():
    name=request.args.get("id")
    # print(name)
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=json_object[0]["User1"]["Notice"]
        for val in range(len(new_data)):
            notice=None
            sub=None
            mess=None
            if name==new_data[val]["NoticeName"]:
                # print("yes")
                notice=new_data[val]["NoticeName"]
                sub=new_data[val]["Subject"]
                mess=new_data[val]["Body"]
                break
    return render_template("view_notice.html",notice=notice,sub=sub,mess=mess,email=data)

@app.route("/delete/Notice/",methods=["GET","POST"])
def DeleteNotice():
    notice=request.args.get("id")
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=json_object[0]["User1"]["Notice"]
        data1=""
        prop=""
        for val in range(len(new_data)):
            if notice==new_data[val]["NoticeName"]:
                data1="Notice Deleted Successfully"
                prop="alert alert-info"
                f.seek(0)
                f.truncate()
                json_object[0]["User1"]["Notice"].remove(new_data[val])
                json.dump(json_object,f,indent=4)
        if(len(new_data)==0):
                f.seek(0)
                f.truncate()
                del json_object[0]["User1"]["Notice"]
                json.dump(json_object,f,indent=4)
    return render_template("all_notice.html",email=data,data1=data1,prop=prop,org_data=new_data) 

@app.route("/Compose")
def Compose():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        area_details=None
        notice=None
        data1=0
        data2=0
        if "Area" in json_object[0]["User1"]:
            data1=1
            area_details=json_object[0]["User1"]["Area"]
        if "Notice" in json_object[0]["User1"]:
            data2=1
            notice=json_object[0]["User1"]["Notice"]
    return render_template("compose_notice.html",email=data,org_data=area_details,data1=data1,data2=data2,notice=notice)   
            
@app.route("/fetch/notice")
def fetch():
    name=request.args.get("id")
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open('area.json',"r+") as f:
        json_object=json.loads(f.read())
        details=json_object[0]["User1"]["Notice"]
        Notice={}
        for val in range(len(details)):
            if name==details[val]["NoticeName"]:
                # print("Yes")
                Notice['subject']=details[val]["Subject"]
                Notice['mess']=details[val]["Body"]
        return jsonify({"Result":Notice})

@app.route("/notice/composenotice",methods=["GET","POST"])
def compose_notice():
    if request.method=="POST":
        cus_name=request.form.get("customerid")
        mail_subject=request.form.get("subject")
        mail_body=request.form.get("body")
        dates=request.form.get("date")
        month=request.form.get("month")
        full=request.form.get("full")
        name=request.form.get("noticeTemplateId")
        email=request.form.get("email")
        password=request.form.get("password")
        # print(email)
        # print(password)
        with open("email.json","r+") as f:
            json_object=json.loads(f.read())
            data=json_object[0]["Email"]
        with open('area.json',"r+") as f:
            json_object=json.loads(f.read())
            cus_detail=[]
            new_data=None
            data1=None
            prop=None
            data2=0
            cus=None
            sendemail=[]
            if "Customer_Details" in json_object[0]["User1"]:
                cus=json_object[0]["User1"]["Customer_Details"]
            if cus!=None:
                for val in range(len(cus)):
                    if cus_name==cus[val]["CustomerName"]:
                        cus_detail.append(cus[val])
                    elif cus_name=="All":
                        cus_detail.append(cus[val])
            if "Notice" in json_object[0]["User1"]:
                data2=1
                notice=json_object[0]["User1"]["Notice"]
            # print(cus_detail)
            if len(cus_detail)>0:
                for val in range(len(cus_detail)):
                    sendemail.append({
                        "CustomerEmail":cus_detail[val]["Email"],
                        "MailBody":mail_body,
                        "MailSubject":mail_subject,
                    })

            if "Compose" in json_object[0]["User1"]:
                data1=f"Notice send to {len(cus_detail)} Customer"
                prop="alert alert-info"
                new_data=json_object[0]["User1"]["Compose"]
                for val in range(len(cus_detail)):
                    new_data.append({
                        "Id":len(new_data)+1,
                        "NoticeName":name,
                        "CustomerName":cus_detail[val]["CustomerName"],
                        "CustomerId":cus_detail[val]["CustomerId"],
                        "CustomerEmail":cus_detail[val]["Email"],
                        "MailBody":mail_body,
                        "MailSubject":mail_subject,
                        "Date":dates,
                        "Time":month,
                        "FullDate":full
                    })
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["Compose"]=new_data
                    json.dump(json_object,f,indent=4)
            else:
                data1=f"Notice send to {len(cus_detail)} Customer"
                prop="alert alert-info"
                new_data=[]
                for val in range(len(cus_detail)):
                    new_data.append({
                        "Id":val+1,
                        "NoticeName":name,
                        "CustomerName":cus_detail[val]["CustomerName"],
                        "CustomerId":cus_detail[val]["CustomerId"],
                        "CustomerEmail":cus_detail[val]["Email"],
                        "MailBody":mail_body,
                        "MailSubject":mail_subject,
                        "Date":dates,
                        "Time":month,
                        "FullDate":full
                    })
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["Compose"]=new_data
                    json.dump(json_object,f,indent=4)
        # print(new_data)
        l=[]
        subject=[]
        body=[]
        if len(sendemail)>0:
            for val in range(len(sendemail)):
                l.append(sendemail[val]["CustomerEmail"])
                subject.append(sendemail[val]["MailSubject"])
                body.append(sendemail[val]["MailBody"])
            try:
                username=email
                server=sm.SMTP("smtp.gmail.com",587)
                server.starttls()
                server.login(username,password)
                for i in range(len(l)):
                    message=MIMEMultipart()
                    message["From"]=username
                    message["To"]=l[i]
                    message['Subject']=subject[i]
                    message["body"]=body[i]
                    html=f'''
                    <html>
                    <head>
                    </head>
                    <body>
                    <h3>{body[i]}</h3>
                    </body>
                    </html>

                    '''
                    part2=MIMEText(html,"html")
                    message.attach(part2)
                    server.sendmail(username,l[i],message.as_string())
                    print(f"Message has been send to {l[i]}")

            except Exception as e:
                print(e)
        return render_template("compose_notice.html",data3=data1,prop=prop,email=data,data2=data2,notice=notice)

@app.route("/ViewCompose")
def ViewCompose():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        new_data=None
        data1=0
        if "Notice" in json_object[0]["User1"]:
            data1=1
            new_data=json_object[0]["User1"]["Notice"]
    return render_template("view_compose.html",email=data,notice=new_data,data1=data1)

@app.route("/getcompose",methods=["GET","POST"])
def getcompose():
    if request.method=="POST":
        duration=request.form.get("duration")
        strat=request.form.get("from")
        end=request.form.get("end")
        notice=request.form.get("template")
        full=request.form.get("full")
        # print(notice)
        with open("email.json","r+") as f:
            json_object=json.loads(f.read())
            data=json_object[0]["Email"]
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            compose=None
            compose_details=[]
            details=[]
            if "Compose" in json_object[0]["User1"]:
                compose=json_object[0]["User1"]["Compose"]
                for val in range(len(compose)):
                    if notice==compose[val]["NoticeName"]:
                        compose_details.append(compose[val])
            # print(compose_details)
            if duration=="Today":
                for val in range(len(compose_details)):
                    if full==compose_details[val]["FullDate"]:
                        details.append(compose_details[val])
            else:
                for val in range(len(compose_details)):
                    getdate=compose_details[val]["FullDate"]
                    y2,m2,d2=getdate.split("-")
                    y2,m2,d2=int(y2),int(m2),int(d2)
                    y,m,d=strat.split("-")
                    y1,m1,d1=end.split("-")
                    m,d,y=int(m),int(d),int(y)
                    m1,d1,y1=int(m1),int(d1),int(y1)
                    d3=(y2,d2,m2)
                    d2=(y1,d1,m1)
                    d1=(y,d,m)
                    if(d1>=d3 and d2>=d3):
                        details.append(compose_details[val])
                    else:
                        pass
        # print(details)
        return jsonify({"Result":details})

@app.route("/delete/compose/",methods=["GET","POST"])
def deletecompose():
    if request.method=="POST":
        id=request.form.get("id")
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            compose=json_object[0]["User1"]["Compose"]
            data1=""
            prop=""
            # print("Id")
            for val in range(len(compose)):
                if int(id)==compose[val]["Id"]:
                    # print("Yes")
                    data1="Compose details deleted Successfully."
                    prop="alert alert-info"
                    f.seek(0)
                    f.truncate()
                    json_object[0]["User1"]["Compose"].remove(compose[val])
                    json.dump(json_object,f,indent=4)
            detail={"data1":data1,"prop":prop}
        return jsonify({"Result":detail})

@app.route("/View/compose/")
def viewcompose():
    id=request.args.get("id")
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        compose=json_object[0]["User1"]["Compose"]
        cusname=""
        sub=""
        body=""
        for val in range(len(compose)):
            if int(id)==compose[val]["Id"]:
                cusid=compose[val]["CustomerId"]
                cusname=compose[val]["CustomerName"]
                notice_publish=compose[val]["FullDate"]
                notice_time=compose[val]["Time"]
                sub=compose[val]["MailSubject"]
                body=compose[val]["MailBody"]
        return render_template("viewcompose.html",email=data,cusname=cusname,sub=sub,body=body,notice_pub=notice_publish,notice_time=notice_time,cus_id=cusid)

@app.route("/Crediential")
def Crediential():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        product_details=None
        reg=None
        data1=0
        full=[]
        name=[]
        if "Executive" in json_object[0]["User1"]:
            data1=1
            product_details=json_object[0]["User1"]["Executive"]
        if "Register" in json_object[0]["User1"]:
            reg=json_object[0]["User1"]["Register"]
        if reg!=None:
            for val in range(len(reg)):
                name.append(reg[val]["Name"])
        # print(name)
        if product_details!=None:
            for val in range(len(product_details)):
                if product_details[val]['HawkerName'] not in name:
                    # print("Yes")
                    full.append({
                        "Id":product_details[val]["HawkerId"],
                        "Name":product_details[val]["HawkerName"],
                        "Area":product_details[val]["AreaName"],
                        "What":product_details[val]["WhatsAppNumber"],
                        "data2":0
                    })
                else:
                    full.append({
                        "Id":product_details[val]["HawkerId"],
                        "Name":product_details[val]["HawkerName"],
                        "Area":product_details[val]["AreaName"],
                        "What":product_details[val]["WhatsAppNumber"],
                        "data2":1
                    })
    return render_template("crediential.html",email=data,data1=data1,org_data=full)

@app.route("/Credientials")
def Credientials():
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        product_details=None
        data1=0
        reg=None
        name=[]
        full=[]
        value=None
        if "Executive" in json_object[0]["User1"]:
            data1=1
            product_details=json_object[0]["User1"]["Executive"]
        if "Register" in json_object[0]["User1"]:
            reg=json_object[0]["User1"]["Register"]
        if reg!=None:
            for val in range(len(reg)):
                name.append(reg[val]["Name"])
        for val in range(len(product_details)):
            if product_details[val]['HawkerName'] not in name:
                value=Markup("<a>Register</a>")
                full.append({
                    "Id":product_details[val]["HawkerId"],
                    "Name":product_details[val]["HawkerName"],
                    "Area":product_details[val]["AreaName"],
                    "What":product_details[val]["WhatsAppNumber"],
                    "data2":0
                })
            else:
                full.append({
                    "Id":product_details[val]["HawkerId"],
                    "Name":product_details[val]["HawkerName"],
                    "Area":product_details[val]["AreaName"],
                    "What":product_details[val]["WhatsAppNumber"],
                    "data2":1
                })
    return render_template("crediential.html",email=data,data1=data1,org_data=full)

@app.route('/assign/<int:id>')
def assign(id): 
    exe_id=id
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        execetails=json_object[0]["User1"]["Executive"]
        Name=None
        emails=None
        for val in range(len(execetails)):
            if exe_id==int(execetails[val]["HawkerId"]):
                Name=execetails[val]["HawkerName"]
                emails=execetails[val]["Email"]
    return render_template("assign.html",email=data,emails=emails,name=Name)

@app.route("/credentials/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        password=request.form.get("password")
        reg=None
        entry=User(name=name,email=email,password=password)
        db.session.add(entry)
        db.session.commit()
        with open("area.json","r+") as f:
            json_object=json.loads(f.read())
            if "Register" in json_object[0]["User1"]:
                reg=json_object[0]["User1"]["Register"]
                reg.append({
                    "Id":len(reg)+1,
                    "Name":name
                })
                f.seek(0)
                f.truncate()
                json_object[0]["User1"]['Register']=reg
                json.dump(json_object,f,indent=4)
                json_object[0]["User1"]["Register"]=reg
            else:
                reg=[{"Id":1,"Name":name}]
                f.seek(0)
                f.truncate()
                json_object[0]["User1"]['Register']=reg
                json.dump(json_object,f,indent=4)
                json_object[0]["User1"]["Register"]=reg
        return redirect(url_for('Credientials'))

@app.route("/print_bill/<int:id>")
def print_bill(id):
    cus_id=id
    customer_ids=[]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        details=[]
        tax=0
        total=0
        sgst=0
        quan_sum=[]
        name=None
        mobile=None
        msg=""
        prev_amm=0
        payment=json_object[0]["User1"]["Payment_Details"]
        for val in range(len(payment)):
            if payment[val]["PaymentStatus"] == "pending" and payment[val]["Id"]!=str(cus_id):
                customer_ids.append({
                    "cus_id":payment[val]["CustomerId"],
                    "total":payment[val]["GrandTotal"]
                })
        for val in range(len(payment)):
            if cus_id==int(payment[val]["Id"]):
                cus_ids=payment[val]["CustomerId"]
                name=payment[val]["Name"]
                mobile=payment[val]["Mobile"]
                for val1 in range(len(payment[val]["Product"])):
                    quan_sum.append(int(payment[val]["Quantity"][val1]))
                    details.append({
                        "Id":val1+1,
                        "Product":payment[val]["Product"][val1].split(":")[0],
                        "Quantity":payment[val]["Quantity"][val1],
                        "Price":payment[val]["Price"][val1],
                        "Ammount":payment[val]["Ammount"][val1]
                    })
                if payment[val]["PaymentStatus"] == "Success":
                    msg="Success"
                else:
                    msg="Pending"  
                sub=payment[val]["SubTotal"]
                tax=payment[val]["Tax"]
                taxammount = payment[val]["TaxAmmount"]
                sgst=int(payment[val]["Tax"])/2
                total=payment[val]["GrandTotal"]
                for val in range(len(customer_ids)):
                    if customer_ids[val]["cus_id"] == cus_ids:
                        prev_amm+=float(customer_ids[val]["total"])
                        break
                #     total=payment[val]["GrandTotal"]
                subtotal=float(total)+prev_amm
        # print(tax)
        # print(sgst)
        # print(total)
        # print(details)
        # print(customer_ids)
    return render_template("bill_payment.html",org_data=details,tax=tax,sgst=sgst,total=total,sub=sub,quan=sum(quan_sum),item=len(details),name=name,taxm=taxammount,mobile=mobile,cus=cus_id,msg=num2word.word(int(subtotal)),msgs=msg,prev=round(prev_amm,3))
@app.route("/logout")
def logout():
    src_file_name="area.json"
    bkp_file_loc=r"C:/Users/ac/Desktop/Backup/"
    # print(bkp_file_loc)
    try:
        # print("Condition start")
        import backup
        backup.take_bkp(src_file_name,"","",bkp_file_loc)
    except(FileNotFoundError):
        print("The file you serach is not found in the current directory")
    return render_template("login.html")

@app.route("/customerManagement/viewCustomer/<int:id>")
def viewcustomer(id):
    cus_id = id
    with open("email.json","r+") as f:
        json_object=json.loads(f.read())
        data=json_object[0]["Email"]
    with open("area.json","r+") as f:
        json_object=json.loads(f.read())
        customer_details = json_object[0]["User1"]["Customer_Details"]
        Name=""
        for val in range(len(customer_details)):
            if cus_id == customer_details[val]["CustomerId"]:
                Name = customer_details[val]["CustomerName"]
    return render_template("view_Customer.html",name=Name,email=data)

if __name__=="__main__":
    app.run(debug=True)   
# ui.run()