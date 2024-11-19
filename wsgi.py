from os import name
from tmdbv3api import Movie, Person, TMDb
import random, csv, time
from datetime import date, datetime
import networkx as nx
from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session
from os.path import exists
import time

# 4. From the objects.py containing our classes for this application, only import the Movie class
from objects import Cart
from gorillacartsdb import *
from autotrackrdb import *
from actorguessrdb import *

# 5. Import the sqlite library
# import sqlite3
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

tmdb = TMDb()
tmdb.api_key = '6d59b820b0e6718bc094062277bb2fd7'
movie = Movie()
person = Person()
history_dict = {}

os.environ["TZ"] = "America/New_York"
time.tzset()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

G = nx.read_edgelist("dataset.edgelist", delimiter='|', data=[('movie', str)])
G = nx.relabel_nodes(G, lambda x: x.lower())

@app.route('/', methods=['GET', 'POST'])
@app.route('/celebguessr', methods=['GET', 'POST'])
def celebguessr():
    def randomActorPicker():
        top_100_actors = []
        for i in range(1, 6):
            popular_actors = person.popular(page=i)
            top_100_actors.extend(popular_actors)
            if len(top_100_actors) >= 100:
                break
        for actor in top_100_actors:
            if actor['name'].lower() not in G.nodes:
                top_100_actors.remove(actor)
        history_dict = getActors()
        while True:
            try:
                getToday(datetime.now().date())
            except:
                newDate(datetime.now().date())
            randomActor = top_100_actors[random.randint(0,len(top_100_actors)-1)]
            if str(datetime.now().date()) in list(history_dict.keys()):
                return person.search(history_dict[str(datetime.now().date())])[0]
            elif str(datetime.now().date()) not in list(history_dict.keys()):
                saveActor(datetime.now().date(),randomActor['name'])
                return randomActor


    randomActorPicker()

    def Game(userInput):
        # getting today's date and first date
        actorOfTheDay = randomActorPicker()
        actorInfo = person.details(actorOfTheDay['id'])
        moviesIn = []
        for i in actorOfTheDay['known_for']:
            try:
                moviesIn.append(i['original_title'])
            except:
                try:
                    moviesIn.append(i['original_name'])
                except:
                    moviesIn.append("No known feature films for this celebrity.")

        # tips handling
        tips = {'birthday': actorInfo['birthday'], 'location': actorInfo['place_of_birth'], 'gender': actorInfo['gender'], 'knownfor': moviesIn}
        actorOfTheDay = actorOfTheDay['name']
        if tips['gender'] == 1:
            tips['gender'] = 'Female'
        elif tips['gender'] == 2:
            tips['gender'] = 'Male'
        bdayprintout = ("This celebrity was born on "+tips['birthday']+" in "+tips['location']+'.')
        genderprintout = ("The celebrity identifies as a "+tips['gender']+'.')
        movieprintout = "Some movies today's celebrity has performed in:<br>"
        for m in moviesIn:
            movieprintout = movieprintout + m + '<br>'

        # if already guessed
        if userInput.lower() in session["actorGuesses"] and session['status'] == True:
            return ["You already guessed this celebrity."]

        elif session['status'] == False:
            return ["You already won!"]

        # if requesting tip
        elif userInput in ['tip'] and session['status'] == True:
            if bdayprintout not in session['tipList']:
                session['tipList'].append(bdayprintout)
            elif genderprintout not in session['tipList']:
                session['tipList'].append(genderprintout)
            elif movieprintout not in session['tipList']:
                session['tipList'].append(movieprintout)
            else:
                return ["Sorry, you've used all your tips."]

        # if guess is in actor list
        elif userInput.lower() in G.nodes and session['status'] == True:
            session["guessCount"] = session["guessCount"] + 1
            try:
                # if correct
                if len(nx.shortest_path(G,userInput.lower(),actorOfTheDay.lower()))-1 == 0:
                    today = datetime.now().date()
                    updateToday("won",today, 1)
                    updateToday("guesses",today, int(session['guessCount']))
                    updateToday("tips",today, len(session['tipList']))
                    data = getToday(today)
                    if data['bestguesses'] == 0:
                        bestPerformance(int(session['guessCount']),len(session['tipList']),today)
                    elif session['guessCount'] < data['bestguesses']:
                        bestPerformance(int(session['guessCount']),len(session['tipList']),today)
                    elif session['guessCount'] == data['bestguesses'] and len(session['tipList']) < data['besttips']:
                        bestPerformance(int(session['guessCount']),len(session['tipList']),today)
                    if session["guessCount"] == 1:
                        session['guessList'].append(["You guessed it! Today's Celeb of the Day is "+actorOfTheDay+"! You guessed in "+str(session['guessCount'])+" attempt.",0,"https://image.tmdb.org/t/p/w500"+person.images(person.search(userInput.lower())[0]['id'])['profiles'][0]['file_path']])
                    else:
                        session['guessList'].append(["You guessed it! Today's Celeb of the Day is "+actorOfTheDay+"! You guessed in "+str(session['guessCount'])+" attempts.",0,"https://image.tmdb.org/t/p/w500"+person.images(person.search(userInput.lower())[0]['id'])['profiles'][0]['file_path']])
                    session['guessList'].sort(key=lambda x: x[1])
                    session['status'] = False
                # if one away
                elif len(nx.shortest_path(G,userInput.lower(),actorOfTheDay.lower()))-1 == 1:
                    session['actorGuesses'].append(userInput.lower())
                    session['guessList'].append(["Close! "+userInput.title()+" is 1 actor from the Celeb of the Day. They were together in "+G.get_edge_data(userInput.lower(),actorOfTheDay.lower())['movie'],1,"https://image.tmdb.org/t/p/w500"+person.images(person.search(userInput.lower())[0]['id'])['profiles'][0]['file_path']])
                    session['guessList'].sort(key=lambda x: x[1])
                # if many away
                else:
                    session['actorGuesses'].append(userInput.lower())
                    session['guessList'].append([userInput.title()+" is "+str(len(nx.shortest_path(G,userInput.lower(),actorOfTheDay.lower()))-1)+" celebrities away from the Celeb of the Day.",len(nx.shortest_path(G,userInput.lower(),actorOfTheDay.lower()))-1,"https://image.tmdb.org/t/p/w500"+person.images(person.search(userInput.lower())[0]['id'])['profiles'][0]['file_path']])
                    session['guessList'].sort(key=lambda x: x[1])

            # if no shortest path
            except:
                session['actorGuesses'].append(userInput.lower())
                session['guessList'].append([userInput.title()+" doesn't have any connection with the Celeb of the Day.",10,"https://image.tmdb.org/t/p/w500"+person.images(person.search(userInput.lower())[0]['id'])['profiles'][0]['file_path']])
                session['guessList'].sort(key=lambda x: x[1])
        # if not in DB
        else:
            return ["That's not a celebrity in our database, sorry."]
            # Check if user input is in session

        # global actorGuesses
    # Get user input from form submission
    if request.method == 'POST':
        today = datetime.now().date()
        data = getToday(today)
        given_date = datetime.strptime('2023-04-12', '%Y-%m-%d').date()
        # Calculate the difference between the given date and today's date
        date_difference = today - given_date
        if(request.form['action'] == 'tip'):
            result = Game('tip')
            return render_template('celebguessr.html', date = datetime.now().date(), result = result, guessCount = session["guessCount"], guesses = session["guessList"], tips = session["tipList"], numTips = len(session['tipList']), status = session['status'], daysSince = date_difference.days,todayguesses = data['guesses'], todayplayers = data['players'], todaytips = data['tips'], todaywon = data['won'], minguessestips = [data['bestguesses'],data['besttips']])
        else:
            userInput = request.form['userInput']
            result = Game(userInput.strip())
            return render_template('celebguessr.html', date = datetime.now().date(), result = result, guessCount = session["guessCount"], guesses = session["guessList"], tips = session["tipList"], numTips = len(session['tipList']), status = session['status'], daysSince = date_difference.days,todayguesses = data['guesses'], todayplayers = data['players'], todaytips = data['tips'], todaywon = data['won'], minguessestips = [data['bestguesses'],data['besttips']])

    try:
        session['guessList']
        today = datetime.now().date()
        data = getToday(today)
        if session['date'] != datetime.now().date():
            todayPlayers += 1
            updateToday("players",today,1)
            given_date = datetime.strptime('2023-04-12', '%Y-%m-%d').date()
            # Calculate the difference between the given date and today's date
            date_difference = today - given_date
            session['guessList'] = []
            session['tipList'] = []
            session['guessCount'] = 0
            session["actorGuesses"] = []
            session['status'] = True
            session['date'] = date.today()
            return render_template('celebguessr.html', date = datetime.now().date(), guessCount = session["guessCount"], guesses = session["guessList"], tips = session["tipList"], numTips = len(session['tipList']), status = session['status'], daysSince = date_difference.days,todayguesses = data['guesses'], todayplayers = data['players'], todaytips = data['tips'], todaywon = data['won'], minguessestips = [data['bestguesses'],data['besttips']])
        else:
            given_date = datetime.strptime('2023-04-12', '%Y-%m-%d').date()
            # Calculate the difference between the given date and today's date
            date_difference = today - given_date
            return render_template('celebguessr.html', date = datetime.now().date(), guessCount = session["guessCount"], guesses = session["guessList"], tips = session["tipList"], numTips = len(session['tipList']), status = session['status'], daysSince = date_difference.days,todayguesses = data['guesses'], todayplayers = data['players'], todaytips = data['tips'], todaywon = data['won'], minguessestips = [data['bestguesses'],data['besttips']])
    except:
        today = datetime.now().date()
        updateToday("players",today,1)
        data = getToday(today)
        given_date = datetime.strptime('2023-04-12', '%Y-%m-%d').date()
        # Calculate the difference between the given date and today's date
        date_difference = today - given_date
        session['guessList'] = []
        session['tipList'] = []
        session['guessCount'] = 0
        session["actorGuesses"] = []
        session['status'] = True
        session['date'] = date.today()
        return render_template('celebguessr.html', date = datetime.now().date(), guessCount = session["guessCount"], guesses = session["guessList"], tips = session["tipList"], numTips = len(session['tipList']), status = session['status'], daysSince = date_difference.days,todayguesses = data['guesses'], todayplayers = data['players'], todaytips = data['tips'], todaywon = data['won'], minguessestips = [data['bestguesses'],data['besttips']])

@app.route('/celebguessr/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        email = request.form.get('email','')
        rating = request.form.get('rating',1)
        description = request.form.get('description','')
        newFeedback(email,rating,description)
        return redirect(url_for('celebguessr'))
    else:
        return render_template('feedback.html')


def eventcheck(name,date,host,description):
    error = ""
    msg=[]
    if not name:
        msg.append("Name is missing!")
    if len(name) > 25:
        msg.append("Name is too long!")
    if not date:
        msg.append("Date is missing!")
    if len(date) > 12:
        msg.append("Date is the incorrect length!")
    if not host:
        msg.append("Host is missing!")
    if len(host) > 20:
        msg.append("Host name is too long!")
    if not description:
        msg.append("Description is missing!")
    if len(description) > 255:
        msg.append("Description is too long!")
    #prints out message only if there's an error
    if len(msg) > 0:
        error=" \n".join(msg)
    return error

#same one as before, just different variables
def attendeecheck(name,email,comment):
    error = ""
    msg=[]
    if not name:
        msg.append("Name is missing!")
    if len(name) > 25:
        msg.append("Name is too long!")
    if not email:
        msg.append("Email is missing!")
    if len(email) > 100:
        msg.append("Email is too long!")
    if not comment:
        msg.append("Comment is missing!")
    if len(comment) > 255:
        msg.append("Comment is too long!")
    if len(msg) > 0:
        error=" \n".join(msg)
    return error


#Connecting to my database via PyMySQL, using a config.py file
app.config.from_pyfile(app.root_path + '/config_defaults.py')
if exists(app.root_path + '/config.py'):
    app.config.from_pyfile(app.root_path + '/config.py')

#   Let's also add the name "index" since that is a common name for a website home page
@app.route("/gorillacarts")    # Decorator - Now

#   Define what should happen when visiting this page by using a function called index()
def gorillacartsindex():
    # A1) Run a CLASS method called getAllCUstomers().  Instaniation is not needed.
    bList=Cart.getAllCustomers()

    #Return the template index.html but pass it the list of movies
    # stored in the variable bList
    return render_template('gorillacartsindex.html',message=bList )

#------------------------------------------------------------------------------------
# C) Create pages to INSERT records
#------------------------------------------------------------------------------------
#customer insert page
@app.route("/gorillacarts/addcustomer", methods=["GET","POST"]) # Decorator - Now
def addcustomer():
    if request.method == "GET":  # When you first visit the page

        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllCustomers()
        return render_template('addcustomer.html',message=bList)

    elif request.method == "POST": # When you fill out the form and click SUBMIT
        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllCustomers()

        # Get the value from the form object called "movtitle" (it is a textbox)
        name = request.form.get("name", 0)
        zip = request.form.get("ZIP", 0)
        telephone = request.form.get("telephone", 0)
        email = request.form.get("email", 0)
        category = request.form.get("category", 0)

        # Run the function called saveMovieDB passing the method the title of the movie
        #   and the year the movie was release
        saveCustomerDB(name, zip, telephone, email, category)

        # C1) Run a CLASS method called getAllCustomers().  Instaniation is not needed.
        bList=Cart.getAllCustomers()
        return render_template('customers.html',message=bList)

    else:
        # How could it have not been a GET or POST? I have no idea how that could have happened.
        return render_template('addcustomer.html',message='Something went wrong.')

#supplier insert page
@app.route("/gorillacarts/addsupplier", methods=["GET","POST"]) # Decorator - Now
def addsupplier():
    if request.method == "GET":  # When you first visit the page

        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllSuppliers()
        return render_template('addsupplier.html',message=bList)

    elif request.method == "POST": # When you fill out the form and click SUBMIT
        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllSuppliers()

        # Get the value from the form object called "movtitle" (it is a textbox)
        name = request.form.get("name", 0)
        zip = request.form.get("ZIP", 0)
        telephone = request.form.get("telephone", 0)
        email = request.form.get("email", 0)

        # Run the function called saveMovieDB passing the method the title of the movie
        #   and the year the movie was release
        saveSupplierDB(name, zip, telephone, email)

        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllSuppliers()
        return render_template('suppliers.html',message=bList)

    else:
        # How could it have not been a GET or POST? I have no idea how that could have happened.
        return render_template('addsupplier.html',message='Something went wrong.')

#material insert page
@app.route("/gorillacarts/addmaterial", methods=["GET","POST"]) # Decorator - Now
def addmaterial():
    if request.method == "GET":  # When you first visit the page

        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllMaterials()
        sList=Cart.getAllSuppliers()
        return render_template('addmaterial.html',message=bList,suppliermessage=sList)

    elif request.method == "POST": # When you fill out the form and click SUBMIT
        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllMaterials()
        sList=Cart.getAllSuppliers()

        # Get the value from the form object called "movtitle" (it is a textbox)
        SWPartNo = request.form.get("SWPartNo", 0)
        SupplierPartNo = request.form.get("SupplierPartNo", 0)
        SupplierID = request.form.get("SupplierID", 0)
        ProductName = request.form.get("ProductName", 0)
        Price = request.form.get("Price", 0)
        QuantityAvailable = request.form.get("QuantityAvailable", 0)

        # Run the function called saveMovieDB passing the method the title of the movie
        #   and the year the movie was release
        saveMaterialDB(SWPartNo,SupplierPartNo,SupplierID,ProductName,Price,QuantityAvailable)

        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        bList=Cart.getAllMaterials()
        return render_template('materials.html',message=bList)

    else:
        # How could it have not been a GET or POST? I have no idea how that could have happened.
        return render_template('addmaterial.html',message='Something went wrong.')

#place an order page
@app.route("/gorillacarts/placeorder", methods=["GET","POST"]) # Decorator - Now
def placeorder():
    if request.method == "GET":  # When you first visit the page

        # C1) Run a CLASS method to get all necessary details.  Instaniation is not needed.
        sList=Cart.getAllStaff()
        cList=Cart.getAllCustomers()
        pList=Cart.getAllProducts()
        oList=Cart.getAllOrders()
        mList=Cart.getAllMaterials()
        bList=Cart.getAllBOMs()
        return render_template('placeorder.html',message=sList,customermessage=cList,productmessage=pList,ordermessage=oList,bommessage=bList,materialmessage=mList)

    elif request.method == "POST": # When you fill out the form and click SUBMIT
        # C1) Run a CLASS method called getAllMovies().  Instaniation is not needed.
        sList=Cart.getAllStaff()
        cList=Cart.getAllCustomers()
        pList=Cart.getAllProducts()
        oList=Cart.getAllOrders()
        mList=Cart.getAllMaterials()
        bList=Cart.getAllBOMs()

        # Get the value from the form object (it is a drop down menu)
        EmployeeID = request.form.get("EmployeeID", 0)
        CustomerID = request.form.get("CustomerID", 0)
        ProductID1 = request.form.get("ProductID1", 0)
        Quantity1 = request.form.get("quantity1", 0)
        ProductID2 = request.form.get("ProductID2", 0)
        Quantity2 = request.form.get("quantity2", 0)
        ProductID3 = request.form.get("ProductID3", 0)
        Quantity3 = request.form.get("quantity3", 0)
        ProductID4 = request.form.get("ProductID4", 0)
        Quantity4 = request.form.get("quantity4", 0)
        ProductID5 = request.form.get("ProductID5", 0)
        Quantity5 = request.form.get("quantity5", 0)

        #-------------------------------------
        # 1. VERIFY IF THE PLACED ORDER DOESN'T HAVE A PRODUCT WHOSE QUANTITY IS MORE THAN 10
        #-------------------------------------
        order = {}
        if ProductID1 != "" and Quantity1 != "":
            if ProductID1 not in order.keys():
                order[ProductID1] = int(Quantity1)
            else:
                order[ProductID1] = int(order[ProductID1])+int(Quantity1)
        if ProductID2 != "" and Quantity2 != "":
            if ProductID2 not in order.keys():
                order[ProductID2] = int(Quantity2)
            else:
                order[ProductID2] = int(order[ProductID2])+int(Quantity2)
        if ProductID3 != "" and Quantity3 != "":
            if ProductID3 not in order.keys():
                order[ProductID3] = int(Quantity3)
            else:
                order[ProductID3] = int(order[ProductID3])+int(Quantity3)
        if ProductID4 != "" and Quantity4 != "":
            if ProductID4 not in order.keys():
                order[ProductID4] = int(Quantity4)
            else:
                order[ProductID4] = int(order[ProductID4])+int(Quantity4)
        if ProductID5 != "" and Quantity5 != "":
            if ProductID5 not in order.keys():
                order[ProductID5] = int(Quantity5)
            else:
                order[ProductID5] = int(order[ProductID5])+int(Quantity5)
        total = 0
        c=0
        #THROWING AN ERROR MESSAGE IF THE PLACE ORDER PAGE DID NOT HAVE ANY ORDER; THAT IS NO PRODUCT WAS PLACE
        if len(order.keys()) == 0:
            c=1
            return render_template('placeorder.html',errormessage="You have no items added, try again!",message=sList,customermessage=cList,productmessage=pList,ordermessage=oList,bommessage=bList)
        #CHECK IF ANY ONE PRODUCT HAS MORE THAN 10 PEICES ORDERED
        for i in order.keys():
            if int(order[i]) > 10:
                c=1
                return render_template('placeorder.html',errormessage="You have more then 10 units of an item added, try again!",message=sList,customermessage=cList,productmessage=pList,ordermessage=oList)
                break

        #CREATING BOM FOR THE ORDER; THAT IS THE MATERIALS QUANTITY NEEDED TO PREPARE THE ORDER IS CALCULATED
        partslist = {}
        aorder = []
        for j in order.keys():
            for i in bList:
                if int(j) == i['ProductID']:
                    if i['PartNo'] in partslist.keys():
                        partslist[i['PartNo']] = float(partslist[i['PartNo']]) + (float(i['Quantity'])*float(order[j]))
                    else:
                        partslist[i['PartNo']]= (float(i['Quantity'])*float(order[j]))

        #CALCULATING THE POTERNIAL ORDER THAT CAN BE PLACED WITH THE CURRENT INVENTORY
        #THIS IS CALCULATED WITH REFERENCE TO THE ORDER PLACE SO THE POTENTIAL ORDER IS EQUAL OR LESSER THAN THE ACTUAL ORDER DEPEDNING  UPON THE MATERIALS AVIALABLE
        mlistCopy=mList.copy()
        aorder={}
        clr=1
        for i in order.keys():
            pbom=getSingleBOMDictList_DB(int(i))
            aorder[i]=0
            for j in range(order[i]):
                clr=1
                for k in mlistCopy:
                    for m in pbom:
                        if k['SWPartNo'] == m['PartNo']:
                            diff=float(k['QuantityAvailable'])-float(m['Quantity'])
                            if diff >= 0:
                                k['QuantityAvailable'] = float(k['QuantityAvailable']) - float(m['Quantity'])
                            else:
                                clr=0
                                break
                if clr == 1:
                    aorder[i]=aorder[i]+1

        #-------------------------------------
        # 2. VERIFY IF THERE IS MATERIAL IN STOCK TO MAKE THE PRODUCTS
        #-------------------------------------
        needmore = {}
        mList=Cart.getAllMaterials()
        for i in partslist.keys():
            for j in mList:
                if i == j["SWPartNo"] and (float(partslist[i])>float(j["QuantityAvailable"])):
                    needmore[j["SWPartNo"]] = float(partslist[i])-float(j["QuantityAvailable"])
                    c=1

        #THROWING AN ERROR MESSAGE WHEN THERE ARE NOT ENOUGH MATERIALS IN THE INVENTORY
        if c==1:
            return render_template('placeorder.html',errormessage="Not enough materials in inventory, you need more:",errorpart2=needmore,errormessage2="With your material inventory, you can purchase:",errorpart3=aorder,message=sList,customermessage=cList,productmessage=pList,ordermessage=oList)

        #IF THERE IS ENOUGH MATERIAL IN THE INVENTORY THEN CALCULATE THE TOTAL PRICE OF THE ORDER AND PLACE THE ORDER
        if c==0:
            #[{'ProductID': 1, 'ProductName': 'Large Cart', 'Color': 'Red', 'Price': 119.99}, {'ProductID': 2, 'ProductName': 'Small Cart', 'Color': 'Blue', 'Price': 49.99}]
            for i in pList:
                for j in order.keys():
                    if int(j) == i['ProductID']:
                        total += i['Price']*float(order[j])

            Zip=getSingleDictList_DB(CustomerID)[0]["ZIP"]
            OrderID=saveOrderDB(CustomerID,EmployeeID,total,Zip)

            for i in pList:
                 for j in order.keys():
                     if int(j) == i['ProductID']:
                         saveOrderDetailDB(OrderID,int(j),float(order[j]),float(order[j])*i['Price'])
            oList=Cart.getAllOrders()
            for i in partslist.keys():
                reduceMaterialDB(float(partslist[i]),i)
        return render_template('orders.html',message=oList)

    else:
        # How could it have not been a GET or POST? I have no idea how that could have happened.
        return render_template('placeorder.html',message='Something went wrong.')

# E) Create a route to list all customers with Delete, Edit, View options
#------------------------------------------------------------------------------------
@app.route("/gorillacarts/customers", methods=["GET"]) # Decorator
def customerslist():
    if request.method == "GET":
        bList=Cart.getAllCustomers()
        return render_template('customers.html',message=bList)

@app.route("/gorillacarts/products", methods=["GET","POST"]) # Decorator
def productslist():
    if request.method == "GET":
        bList=Cart.getAllProducts()
        return render_template('products.html',message=bList)
    elif request.method == "POST":
        title = getIntegerFormVariable("title")
        bList=Cart.getAllCarts()
        delEstimates_DB(title)

        #Reload Estimate list as a dictionary
        #DETERMINE IF THIS IS USING A CSV FILE OR DATABASE
        bDict=Cart.getAllCarts()
        return render_template('CartList.html',message=bDict )

@app.route("/gorillacarts/suppliers", methods=["GET","POST"]) # Decorator
def supplierslist():
    if request.method == "GET":
        bList=Cart.getAllSuppliers()
        return render_template('suppliers.html',message=bList)
    elif request.method == "POST":
        title = getIntegerFormVariable("title")
        bList=Cart.getAllCarts()
        delEstimates_DB(title)

        #Reload Estimate list as a dictionary
        #DETERMINE IF THIS IS USING A CSV FILE OR DATABASE
        bDict=Cart.getAllCarts()
        return render_template('CartList.html',message=bDict )

@app.route("/gorillacarts/materials", methods=["GET","POST"]) # Decorator
def materialslist():
    if request.method == "GET":
        bList=Cart.getAllMaterials()
        return render_template('materials.html',message=bList)
    elif request.method == "POST":
        title = getFormVariable("title")
        bList=Cart.getAllMaterials()
        delEstimates_DB(title)

        #Reload Estimate list as a dictionary
        #DETERMINE IF THIS IS USING A CSV FILE OR DATABASE
        bDict=Cart.getAllMaterials()
        return render_template('materials.html',message=bDict )

@app.route("/gorillacarts/orders", methods=["GET","POST"]) # Decorator
def orderslist():
    if request.method == "GET":
        bList=Cart.getAllOrders()
        return render_template('orders.html',message=bList)
    elif request.method == "POST":
        title = getIntegerFormVariable("title")
        bList=Cart.getAllOrders()
        delEstimates_DB(title)

        #Reload Estimate list as a dictionary
        #DETERMINE IF THIS IS USING A CSV FILE OR DATABASE
        bDict=Cart.getAllOrders()
        return render_template('orders.html',message=bDict )

#------------------------------------------------------------------------------------
#E) Create a route to EDIT an individual movie
#------------------------------------------------------------------------------------
# NOTE**** THIS EDIT HAS <int:ID> added to it
@app.route("/gorillacarts/editcustomer/<title>", methods=['POST', 'GET'])
def EditFUNCTION(title):
    if request.method == "GET":
        # GET THE MOVIE FOR THE ID
        mSingleDict=getSingleDictList_DB(title)
        # PASS THE SINGLE MOVIE TO THE edit.html PAGE
        return render_template('updatecustomer.html',message=mSingleDict )

@app.route("/gorillacarts/EditMaterial/<title>", methods=['POST', 'GET'])
def EditMaterialFUNCTION(title):
    if request.method == "GET":
        # GET THE MOVIE FOR THE ID
        mSingleDict=getSingleMaterialDictList_DB(title)
        # PASS THE SINGLE MOVIE TO THE edit.html PAGE
        return render_template('updatematerial.html',message=mSingleDict )

@app.route("/gorillacarts/EditSupplier/<title>", methods=['POST', 'GET'])
def EditSupplierFUNCTION(title):
    if request.method == "GET":
        # GET THE MOVIE FOR THE ID
        mSingleDict=getSingleSupplierDictList_DB(title)
        # PASS THE SINGLE MOVIE TO THE edit.html PAGE
        return render_template('updatesupplier.html',message=mSingleDict )

#------------------------------------------------------------------------------------
#E) Create a route to SAVE an individual movie after EDIT
#------------------------------------------------------------------------------------
# NOTE**** THIS EDIT DOES NOT HAVE THE <int:ID> added to it
@app.route("/gorillacarts/Edit", methods=["GET","POST"]) # Decorator - Now
def EditSave():
    # GET THE VALUES FROM THE FORM - USE THE FUNCTIONS AT THE BOTTOM OF THIS
    # CODE PAGE TO HELP YOU GET THE VALUSE
    customerID = getIntegerFormVariable("CustomerID")
    name = getFormVariable("Name")
    zip = getFormVariable("ZIP")
    telephone = getFormVariable("Telephone")
    email = getFormVariable("Email")
    category = getFormVariable("Category")


    # CALL THE FUNCTION updateMovieDB and pass the new values
    xID = updateCustomerDB(
            customerID, zip, telephone, email, category)
    # Retrive the new values from the database and ...
    bList=Cart.getAllCustomers()
    return render_template('customers.html',message=bList)

@app.route("/gorillacarts/EditMaterial", methods=["GET","POST"]) # Decorator - Now
def EditMaterialSave():
    # GET THE VALUES FROM THE FORM - USE THE FUNCTIONS AT THE BOTTOM OF THIS
    # CODE PAGE TO HELP YOU GET THE VALUSE
    SWPartNo = getFormVariable("SWPartNo")
    SupplierPartNo = getFormVariable("SupplierPartNo")
    SupplierID = getIntegerFormVariable("SupplierID")
    ProductName = getFormVariable("ProductName")
    Price = getFormVariable("Price")
    QuantityAvailable = getFloatFormVariable("QuantityAvailable")


    # CALL THE FUNCTION updateMovieDB and pass the new values
    xID = updateMaterialDB(
            SupplierPartNo,SupplierID,ProductName,Price,QuantityAvailable,SWPartNo)
    # Retrive the new values from the database and ...
    bList=Cart.getAllMaterials()
    return render_template('materials.html',message=bList)

@app.route("/gorillacarts/EditSupplier", methods=["GET","POST"]) # Decorator - Now
def EditSupplierSave():
    # GET THE VALUES FROM THE FORM - USE THE FUNCTIONS AT THE BOTTOM OF THIS
    # CODE PAGE TO HELP YOU GET THE VALUSE
    SupplierID = getIntegerFormVariable("SupplierID")
    ZIP = getFormVariable("ZIP")
    Telephone = getFormVariable("Telephone")
    Email = getFormVariable("Email")

    # CALL THE FUNCTION updateMovieDB and pass the new values
    xID = updateSupplierDB(
            ZIP,Telephone,Email,SupplierID)
    # Retrive the new values from the database and ...
    bList=Cart.getAllSuppliers()
    return render_template('suppliers.html',message=bList)

#------------------------------------------------------------------------------------
#E) Create a route to DISPLAY a single movie
#------------------------------------------------------------------------------------
@app.route("/gorillacarts/orderdetails/<title>", methods=['POST', 'GET'])
def DisplayFUNCTION(title):
    # GET THE MOVIE FOR THE ID
    mSingleDict=getSingleOrderDictList_DB(title)
    Date=getSingleODictList_DB(title)[0]["Date"]
    # PASS THE SINGLE MOVIE TO THE edit.html PAGE
    return render_template('orderdetails.html',message=mSingleDict,D=Date)

@app.route("/gorillacarts/bomdetails/<title>", methods=['POST', 'GET'])
def DisplayBOMFUNCTION(title):
    # GET THE MOVIE FOR THE ID
    mSingleDict=getSingleBOMDictList_DB(title)
    # PASS THE SINGLE MOVIE TO THE edit.html PAGE
    return render_template('bomdetails.html',message=mSingleDict)


#------------------------------------------------------------------------------------
#E) Create a route to DELETE a single row
#------------------------------------------------------------------------------------
@app.route("/gorillacarts/deleteFromList/<title>", methods=['POST', 'DELETE', 'GET'])
def deleteFromList(title):
    # CALL THE DELMOVIES_DB function passing it the ID of the movie
    genDelete_DB("Customers","CustomerID",title)
    # Once the movie is deleted, get the new list of movies and ...
    bDict=Cart.getAllCustomers()
    # display it on the movielist page
    return render_template('customers.html',message=bDict )

@app.route("/gorillacarts/deleteSupplierFromList/<title>", methods=['POST', 'DELETE', 'GET'])
def deleteSupplierFromList(title):
    # CALL THE DELMOVIES_DB function passing it the ID of the movie
    genDelete_DB("Suppliers","SupplierID",title)
    # Once the movie is deleted, get the new list of movies and ...
    bDict=Cart.getAllSuppliers()
    # display it on the movielist page
    return render_template('suppliers.html',message=bDict )

@app.route("/gorillacarts/deleteMaterialFromList/<title>", methods=['POST', 'DELETE', 'GET'])
def deleteMaterialFromList(title):
    # CALL THE DELMOVIES_DB function passing it the ID of the movie
    genDelete_DB("Materials","SWPartNo",title)
    # Once the movie is deleted, get the new list of movies and ...
    bDict=Cart.getAllMaterials()
    # display it on the movielist page
    return render_template('materials.html',message=bDict )

# 1. FUNCTION TO HELP GET VARIABLES FROM FORMS
#---------------------------
def getFormVariable(variableName):
    return request.form.get(variableName, 0)

def getIntegerFormVariable(variableName):
    return int(request.form.get(variableName, 0))

def getFloatFormVariable(variableName):
    return float(request.form.get(variableName, 0))


@app.route('/autotrackr')
def autotrackrindex():
    return render_template('autotrackrindex.html')

@app.route('/autotrackr/events/')
@app.route('/autotrackr/events/<event_id>')

#For the events page, we are going to use the get_events() function from database to return a list of dicts with all the events in it.
def events(event_id=None):
    events = get_events()
    #if there is a singular event being put in here, we know to return the event page with both the content from that event as well as
    #the attendees that will be at that event.
    if event_id:
        attendees = get_attendees(event_id)
        event = get_event(event_id)
        #passing these things through so the website knows what information to show.
        return render_template('event.html', event=event, attendees=attendees)
    else:
        return render_template('events.html', events=events)

@app.route('/autotrackr/events/create', methods=['GET', 'POST'])

#This function will be used to add directly to a particular event's table in the database.
def create():
    if request.method == 'POST':
        #using form requests to get all of this information before passing it straight through to the add_event() function.
        name = request.form['name']
        date = request.form['date']
        host = request.form['host']
        description = request.form['description']
        error = eventcheck(name,date,host,description)
        if error:
            return render_template("event_form.html", error=error, name=name, date=date, host=host, description=description)
        add_event(name,date,host,description)
        #once that's complete, we redirect to the events route to see it added to the list.
        return redirect(url_for('events'))
    else:
        #if it doesn't work, we keep it on the event_form.html page so the user can try their changes again
        return render_template('event_form.html')



@app.route('/autotrackr/events/<event_id>/edit', methods=['GET', 'POST'])

def edit(event_id=None):
    #This is very similar to the last function, just takes in an event_id so that the function knows what event it will be editing
    event = get_event(event_id)
    attendees = get_attendees(event_id)
    if request.method == 'POST':
        date = request.form['date']
        name = request.form['name']
        host = request.form['host']
        description = request.form['description']
        error = eventcheck(name,date,host,description)
        if error:
            return render_template("event_form.html", event=event, error=error, name=name, date=date, host=host, description=description)
        #using the edit_event() function from database
        edit_event(event_id,name,date,host,description)
        event = get_event(event_id) #Getting this again in case the user updates, will want to see the changes immediately
        #once done with the edit, it will show the user that newly edited page
        return render_template('event.html', event=event, attendees=attendees)
    else:
        return render_template('event_form.html', event=event)

@app.route('/autotrackr/events/<event_id>/delete', methods=['GET', 'POST'])

#This allows the user to delete events from the database
def delete(event_id=None):
    #using get_event() to display information on the delete_form.html
    event = get_event(event_id)
    if request.method == 'POST':
        #very simple, just uses the delete_event() function with the event_id as a parameter to remove it entirely
        delete_event(event_id)
        #once this is complete, it will return to the events page to show that it has been removed.
        return redirect(url_for('events'))
    else:
        return render_template('delete_form.html', event=event)

@app.route('/autotrackr/events/<event_id>/attendees/add', methods=['GET', 'POST'])

def add_attendee(event_id=None):
    #very similar to the add event function
    event = get_event(event_id)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        comment = request.form['comment']
        error = attendeecheck(name,email,comment)
        if error:
            return render_template("attendee_form.html", error=error, event=event, name=name, email=email, comment=comment)
        #uses the form to create an attendee in database's add_attendee() function based on the event_id that the user is currently on, tying the attendee to a particular event as a foreign key
        add_attendee_db(event_id,name,email,comment)
        #once it's done, it'll redirect to the particular event where the attendee was added
        return redirect(url_for('events', event_id=event_id))
    else:
        #if it fails, it will return to the page where they will be typing attendee info
        return render_template('attendee_form.html', event=event)

@app.route('/autotrackr/events/<event_id>/attendees/<attendee_id>/edit', methods=['GET','POST'])

def edit_attendee(attendee_id,event_id):
    #this acquires the event dictionary as well as the attendee dictionary for the particular page and event we're looking for
    event = get_event(event_id)
    attendee = get_attendee(attendee_id)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        comment = request.form['comment']
        error = attendeecheck(name,email,comment)
        if error:
            return render_template("attendee_form.html", error=error, event=event, attendee=attendee, name=name, email=email, comment=comment)
        #using this info, we use the edit_attendee() function in the database.py to make the changes that the user types in the form we're requesting
        edit_attendee_db(attendee_id,event_id,name,email,comment)
        #once done, we'll want to return to the page that the user was originally on.
        return redirect(url_for('events',event_id=event_id))
    else:
        return render_template('attendee_form.html', attendee=attendee, event=event)

@app.route('/autotrackr/events/<event_id>/attendees/<attendee_id>/delete', methods=['GET', 'POST'])

def del_attendee(attendee_id,event_id):
    #similarly to the last one, takes in the attendee_id and event_id in order to find a specific attendee. Uses the del_attendee() function with that specific information.
    del_attendee_db(attendee_id,event_id)
    #once done, redirects to the specific event page we're looking for
    return redirect(url_for('events',event_id=event_id))

if __name__ == '__main__':
    app.run(debug=True)