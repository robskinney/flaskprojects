# A. Import the sqlite library
import sqlite3

class Cart:
#-------------------------------------
# 1. GET DETAILS OF ALL THE CUSTOMER FROM DB
#-------------------------------------
    @classmethod
    def getAllCustomers(cls):
        # A. Connection to the database
        con = sqlite3.connect('Carts.db')
        con.execute("CREATE TABLE IF NOT EXISTS Customers (CustomerID integer PRIMARY KEY AUTOINCREMENT, Name text, ZIP text, Telephone text, Email text, Category text)")

        # B. Create a workspace (aka Cursor)
        cursorObj = con.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT * FROM Customers;')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()

        CustomerList = []

        for individualRow in allRows:
            b = {"CustomerID": individualRow[0], "Name" : individualRow[1], "ZIP" : individualRow[2], "Telephone": individualRow[3], "Email": individualRow[4], "Category": individualRow[5] }
            CustomerList.append(b)
        return CustomerList
        
#-------------------------------------
# ORDER TABLE HAS ALL THE INVOICE DETAILS; SO THERE IS NO TABLE CALLED INVOICE 
# WE HAVE CONSIDERED THAT AN INVOICE IS CREATED FOR EACH ORDER 
#-------------------------------------

    # @classmethod
    # def getAllInvoices(cls):
    #     # A. Connection to the database
    #     con = sqlite3.connect('Carts.db')
    #     con.execute("CREATE TABLE IF NOT EXISTS Invoices (InvoiceID integer PRIMARY KEY AUTOINCREMENT, CustomerID integer, ZIP text, Date text, Amount integer, FOREIGN KEY(CustomerID) REFERENCES Customers(CustomerID))")

    #     # B. Create a workspace (aka Cursor)
    #     cursorObj = con.cursor()

    #     # D. Run the SQL Select statement to retive the data
    #     cursorObj.execute('SELECT * FROM Invoices')

    #     # E. Tell Pyton to 'fetch' all of the records and put them in
    #     #     a list called allRows
    #     allRows = cursorObj.fetchall()

    #     InvoiceList = []

    #     for individualRow in allRows:
    #         b = {"InvoiceID" : individualRow[0], "CustomerID" : individualRow[1], "ZIP": individualRow[2], "Date": individualRow[3], "Amount": individualRow[4]}
    #         InvoiceList.append(b)
    #     return InvoiceList
    
#-------------------------------------
# 2. GET DETAILS OF ALL THE STAFFS FROM DB
#-------------------------------------
    @classmethod
    def getAllStaff(cls):
        # A. Connection to the database
        con = sqlite3.connect('Carts.db')
        con.execute("CREATE TABLE IF NOT EXISTS Staff (EmployeeID integer PRIMARY KEY AUTOINCREMENT, Name text, Position text)")

        # B. Create a workspace (aka Cursor)
        cursorObj = con.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT * FROM Staff')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()

        StaffList = []

        for individualRow in allRows:
            b = {"EmployeeID" : individualRow[0], "Name" : individualRow[1], "Position": individualRow[2] }
            StaffList.append(b)
        return StaffList
        
#-------------------------------------
# 3. GET DETAILS OF ALL THE SUPPLIER FROM DB
#-------------------------------------
    @classmethod
    def getAllSuppliers(cls):
        # A. Connection to the database
        con = sqlite3.connect('Carts.db')
        con.execute("CREATE TABLE IF NOT EXISTS Suppliers (SupplierID integer PRIMARY KEY AUTOINCREMENT, Name text, ZIP text, Telephone text, Email text)")

        # B. Create a workspace (aka Cursor)
        cursorObj = con.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT * FROM Suppliers')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()
        SupplierList = []
        for individualRow in allRows:
            b = {"SupplierID": individualRow[0], "Name" : individualRow[1], "ZIP" : individualRow[2], "Telephone": individualRow[3], "Email": individualRow[4]}
            SupplierList.append(b)
        return SupplierList
#-------------------------------------
# 4. GET DETAILS OF ALL THE MATERIALS FROM DB
#-------------------------------------
    @classmethod
    def getAllMaterials(cls):
        # A. Connection to the database
        con = sqlite3.connect('Carts.db')
        con.execute("CREATE TABLE IF NOT EXISTS Materials (SWPartNo text PRIMARY KEY, SupplierPartNo text, SupplierID integer, ProductName text, Price double, QuantityAvailable integer, FOREIGN KEY(SupplierID) REFERENCES Suppliers(SupplierID))")

        # B. Create a workspace (aka Cursor)
        cursorObj = con.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT * FROM Materials')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()

        MaterialList = []

        for individualRow in allRows:
            b = {"SWPartNo" : individualRow[0], "SupplierPartNo" : individualRow[1], "SupplierID": individualRow[2], "ProductName": individualRow[3], "Price": individualRow[4], "QuantityAvailable": float(individualRow[5])}
            MaterialList.append(b)
        return MaterialList
#-------------------------------------
# 5. GET DETAILS OF ALL THE BOM FROM DB
#-------------------------------------
    @classmethod
    def getAllBOMs(cls):
        # A. Connection to the database
        con = sqlite3.connect('Carts.db')
        con.execute("CREATE TABLE IF NOT EXISTS BOMs (ProductID integer,PartNo text, Quantity double, PRIMARY KEY (PartNo,ProductID), FOREIGN KEY(ProductID) REFERENCES Products(ProductID))")

        # B. Create a workspace (aka Cursor)
        cursorObj = con.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT * FROM BOMs')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()

        BOMList = []

        for individualRow in allRows:
            b = {"ProductID" : individualRow[0], "PartNo" : individualRow[1], "Quantity": individualRow[2]}
            BOMList.append(b)
        return BOMList
        
#-------------------------------------
# 6. GET DETAILS OF ALL THE PRODUCT FROM DB
#-------------------------------------
    @classmethod
    def getAllProducts(cls):
        # A. Connection to the database
        con = sqlite3.connect('Carts.db')
        con.execute("CREATE TABLE IF NOT EXISTS Products (ProductID integer PRIMARY KEY AUTOINCREMENT, ProductName text, Color text, Price double)")

        # B. Create a workspace (aka Cursor)
        cursorObj = con.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT * FROM Products')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()
        ProductList = []

        for individualRow in allRows:
            b = {"ProductID": individualRow[0], "ProductName" : individualRow[1], "Color" : individualRow[2], "Price": individualRow[3] }
            ProductList.append(b)
        return ProductList
        
#-------------------------------------
# 7. GET DETAILS OF ALL THE ORDERS INCLUSING THE PRODUCTS IN THE ORDER FROM DB
#-------------------------------------
    @classmethod
    def getAllOrders(cls):
        # A. Connection to the database
        con = sqlite3.connect('Carts.db')
        con.execute("CREATE TABLE IF NOT EXISTS Orders (OrderID integer PRIMARY KEY AUTOINCREMENT, CustomerID integer, EmpID integer, Total double,Date text,ZIP text, FOREIGN KEY(CustomerID) REFERENCES Customers(CustomerID), FOREIGN KEY(ZIP) REFERENCES Customers(ZIP),FOREIGN KEY(EmpID) REFERENCES Staff(EmployeeID))")
        con.execute("CREATE TABLE IF NOT EXISTS Order_Detail (OrderID integer, ProductID integer, Qty int, AmtPayable double, PRIMARY KEY (OrderID,ProductID), FOREIGN KEY(OrderID) REFERENCES Orders(OrderID), FOREIGN KEY(ProductID) REFERENCES Products(ProductID))")
        # B. Create a workspace (aka Cursor)
        cursorObj = con.cursor()

        # D. Run the SQL Select statement to retive the data
        cursorObj.execute('SELECT * FROM Orders')

        # E. Tell Pyton to 'fetch' all of the records and put them in
        #     a list called allRows
        allRows = cursorObj.fetchall()

        OrderList = []

        for individualRow in allRows:
            b = {"OrderID": individualRow[0], "CustomerID" : individualRow[1], "EmpID" : individualRow[2], "Total": individualRow[3], "Date": individualRow[4],"ZIP": individualRow[5]}
            OrderList.append(b)
        return OrderList