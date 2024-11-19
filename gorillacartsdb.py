# A. Import the sqlite library
import sqlite3

# B. From the objects.py containing our classes for this application,
#    only import the Movie class
from objects import Cart
from datetime import datetime

########################################################################################

#-------------------------------------
# 1. DELETE Record from TB by column name and name
#-------------------------------------
def genDelete_DB(table,column,row):
    database = "Carts.db"
    # create a database connection
    conn = None
    conn = sqlite3.connect(database)
    sql='DELETE FROM {} WHERE {} = ?'.format(table,column)
    cur = conn.cursor()
    cur.execute(sql, (row,))
    conn.commit()

#-------------------------------------
# 2. ADD CUSTOMERS TO DB
#-------------------------------------
def saveCustomerDB(name,zip,telephone,email,category):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect("Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='INSERT INTO Customers (Name, ZIP, Telephone, Email, Category) values (?,?,?,?,?)'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (name,zip,telephone,email,category,))


    # D. Save the changes
    conn.commit()

#-------------------------------------
# 3. ADD SUPPLIER TO DB
#-------------------------------------
def saveSupplierDB(name,zip,telephone,email):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect("Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='INSERT INTO Suppliers (Name, ZIP, Telephone, Email) values (?,?,?,?)'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (name,zip,telephone,email,))

    # D. Save the changes
    conn.commit()
    
#-------------------------------------
# 4. ADD MATERIAL TO DB
#-------------------------------------

def saveMaterialDB(SWPartNo,SupplierPartNo,SupplierID,ProductName,Price,QuantityAvailable):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect("Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='INSERT INTO Materials (SWPartNo, SupplierPartNo, SupplierID, ProductName, Price, QuantityAvailable) values (?,?,?,?,?,?)'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (SWPartNo,SupplierPartNo,SupplierID,ProductName,Price,QuantityAvailable,))

    # D. Save the changes
    conn.commit()

#-------------------------------------
# 5. UPDATE MATERIAL TO DB
#-------------------------------------

def reduceMaterialDB(QuantityAvailable,SWPartNo):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect("Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='UPDATE Materials SET QuantityAvailable = QuantityAvailable - ? WHERE SWPartNo = ?'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (QuantityAvailable,SWPartNo,))

    # D. Save the changes
    conn.commit()
    
#-------------------------------------
# 6. ADD ORDER TO DB
#-------------------------------------
def saveOrderDB(CustomerID,EmpID,Total,Zip):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect("Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='INSERT INTO Orders (CustomerID,EmpID,Total,Date,Zip) values (?,?,?,?,?)'


    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()
    now = datetime.now()
    curdate = now.strftime("%d/%m/%Y %H:%M:%S")
    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (CustomerID,EmpID,Total,curdate,Zip,))

    conn.commit()
    return cur.lastrowid

#-------------------------------------
# 7. ADD ORDERDETAIL (PRODUCTS IN THE ORDER) TO DB
#-------------------------------------

def saveOrderDetailDB(OrderID, ProductID, Qty,AmtPayable):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect("Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='INSERT INTO Order_Detail (OrderID, ProductID, Qty,AmtPayable) values (?,?,?,?)'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (OrderID, ProductID, Qty,AmtPayable,))

    # D. Save the changes
    conn.commit()

#-------------------------------------
# 8. SELECT ONE CUSTOMER FROM DB
#-------------------------------------

def getSingleDictList_DB(title):
    con = sqlite3.connect('Carts.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    customer = []
    cursorObj.execute('SELECT * FROM Customers where CustomerID = ?;',(title,))
    rows = cursorObj.fetchall()
    for individualRow in rows:
        b = {"CustomerID": individualRow[0], "Name" : individualRow[1], "ZIP" : individualRow[2], "Telephone": individualRow[3], "Email": individualRow[4], "Category": individualRow[5] }
        customer.append(b)
    return customer

#-------------------------------------
# 9. SELECT ONE MATERIAL FROM DB
#-------------------------------------

def getSingleMaterialDictList_DB(title):
    con = sqlite3.connect('Carts.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    material = []
    cursorObj.execute('SELECT * FROM Materials where SWPartNo = ?;',(title,))
    rows = cursorObj.fetchall()
    for individualRow in rows:
        b = {"SWPartNo" : individualRow[0], "SupplierPartNo" : individualRow[1], "SupplierID": individualRow[2], "ProductName": individualRow[3], "Price": individualRow[4], "QuantityAvailable": individualRow[5]}
        material.append(b)
    return material

#-------------------------------------
# 10. SELECT ONE SUPPLIER FROM DB
#-------------------------------------

def getSingleSupplierDictList_DB(title):
    con = sqlite3.connect('Carts.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    cursorObj.execute('SELECT * FROM Suppliers where SupplierID = ?;',(title,))
    rows = cursorObj.fetchall()
    Supplier = []
    for individualRow in rows:
        b = {"SupplierID": individualRow[0], "Name" : individualRow[1], "ZIP" : individualRow[2], "Telephone": individualRow[3], "Email": individualRow[4]}
        Supplier.append(b)
    return Supplier

#-------------------------------------
# 11. SELECT ONE ORDER FROM DB
#-------------------------------------

def getSingleODictList_DB(title):
    con = sqlite3.connect('Carts.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    cursorObj.execute('SELECT * FROM Orders where OrderID = ?;',(title,))
    allRows = cursorObj.fetchall()

    OrderList = []

    for individualRow in allRows:
        b = {"OrderID": individualRow[0], "CustomerID" : individualRow[1], "EmpID" : individualRow[2], "Total": individualRow[3], "Date": individualRow[4],"ZIP": individualRow[5]}
        OrderList.append(b)
    return OrderList

#-------------------------------------
# 12. GET ALL THE PRODUCTS INSIDE AN ORDER FROM DB
#-------------------------------------

def getSingleOrderDictList_DB(title):
    con = sqlite3.connect('Carts.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    order = []
    cursorObj.execute('SELECT * FROM Order_Detail where OrderID = ?;',(title,))
    rows = cursorObj.fetchall()
    for individualRow in rows:
        cursorObj.execute('SELECT ProductName, Color FROM Products where ProductID = ?;',(individualRow[1],))
        row=cursorObj.fetchall()
        for i in row:
            b = {"OrderID": individualRow[0], "ProductName":i[0]+" ("+i[1]+")", "ProductID": individualRow[1], "Qty": individualRow[2], "AmtPayable": individualRow[3]}
            order.append(b)
    return order

#-------------------------------------
# 13. GET BOM FOR A PRODUCT FROM DB
#-------------------------------------

def getSingleBOMDictList_DB(title):
    con = sqlite3.connect('Carts.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    material = []
    cursorObj.execute('SELECT * FROM BOMs where ProductID = ?;',(title,))
    rows = cursorObj.fetchall()
    for individualRow in rows:
        cursorObj.execute('SELECT ProductName FROM Materials where SWPartNo = ?;',(individualRow[1],))
        row=cursorObj.fetchone()
        b = {"ProductID" : individualRow[0], "ProductName": row[0], "PartNo" : individualRow[1], "Quantity": individualRow[2]}
        material.append(b)
    return material

#-------------------------------------
# 14. GET THE PRODUCT NAME OF A PRODUCT FROM DB
#-------------------------------------

def getProductName(title):
    con = sqlite3.connect('Carts.db')
    con.row_factory = sqlite3.Row
    cursorObj = con.cursor()
    name = []
    cursorObj.execute('SELECT Name FROM Products where ProductID = ?;',(title,))
    rows = cursorObj.fetchall()
    for individualRow in rows:
        b = {"Name": individualRow[0]}
        name.append(b)
    return name

#-------------------------------------
# 15. UPDATE PERSONAL DETAILS OF A CUSTOMER FROM DB
#-------------------------------------
def updateCustomerDB(customerID,zip,telephone,email,category):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect( "Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='UPDATE Customers set ZIP = ?, Telephone = ?, Email = ?, Category = ? WHERE CustomerID = ?'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (zip, telephone, email, category, customerID))

    # D. Save the changes
    conn.commit()

#-------------------------------------
# 16. UPDATE SUPPLIER DETAILS FROM DB
#-------------------------------------

def updateSupplierDB(zip,telephone,email,supplierid):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect( "Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='UPDATE Suppliers set ZIP = ?, Telephone = ?, Email = ?  WHERE SupplierID = ?'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (zip, telephone, email, supplierid))

    # D. Save the changes
    conn.commit()

#-------------------------------------
# 15. UPDATE MATERIAL DETAILS IN THE DB
#-------------------------------------

def updateMaterialDB(SupplierPartNo,SupplierID,ProductName,Price,QuantityAvailable,SWPartNo):
    #A. Make a connection to the database
    conn = None
    conn = sqlite3.connect( "Carts.db")

    #B. Write a SQL statement to insert a specific row (based on Title name)
    sql='UPDATE Materials set SupplierPartNo = ?, SupplierID = ?, ProductName = ?, Price = ?, QuantityAvailable = ? WHERE SWPartNo = ?'

    # B. Create a workspace (aka Cursor)
    cur = conn.cursor()

    # C. Run the SQL statement from above and pass it 1 parameter for each ?
    cur.execute(sql, (SupplierPartNo,SupplierID,ProductName,Price,QuantityAvailable,SWPartNo,))

    # D. Save the changes
    conn.commit()
    
#-------------------------------------
# 16. DELETE CUSTOMER FROM DB by ID
#-------------------------------------

def delCustomer_DB(title):
    database = "Carts.db"
    # create a database connection
    conn = None
    conn = sqlite3.connect(database)
    sql='DELETE FROM Customers WHERE CustomerID=?'
    cur = conn.cursor()
    cur.execute(sql, (title,))
    conn.commit()


