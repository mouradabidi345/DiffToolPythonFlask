import pandas as pd
# import xlrd 
import sqlalchemy
# import math
from sqlalchemy import create_engine
from pandas_profiling import ProfileReport
from snowflake.connector.pandas_tools import write_pandas
# import snowflake.connector
import numpy as np
import win32com.client as client
import datetime
import datacompy
import snowflake.connector
from flask import Flask, request, render_template,request
import pythoncom
from urllib import parse

connecting_stringA = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:bidev.database.windows.net,1433;Database=InfoTrax_Prod;Uid=bidevreader;Pwd=BJbhPxv3nMZhW8u3;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
connecting_stringB = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:dlo6zra872.database.windows.net,1433;Database=Asea_Prod;Uid=aseauser;Pwd=@S34Pr0d;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
connecting_stringC = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:bidev.database.windows.net,1433;Database=ASEA_REPORTS;Uid=BI_primary;Pwd=@234_MgaKaKa!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

paramsA = parse.quote_plus(connecting_stringA)
paramsB = parse.quote_plus(connecting_stringB)
paramsC = parse.quote_plus(connecting_stringC)


# Flask constructor
application = Flask(__name__)  

EngineA = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % paramsA) #Working
EngineB = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % paramsB) #working
EngineC = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % paramsC) #working

#new
join_column_list =[]
def combinedPrimary_key(Primary_key1, Primary_key2):
    
    if ((not Primary_key1 =="") and (not Primary_key2 =="")):
        join_column_list.insert(0,Primary_key1)
        join_column_list.insert(1,Primary_key2)
        return join_column_list
    else:    
        join_columns = Primary_key1
        return join_columns




#Snowflake VS SQL server Ands Sqlserver VS Snowflake:
def  SnowflakeVSSQLSERVER_VICEVERSA(WAREHOUSE1,Columns1 , DATABASE1, SCHEMA1, Table1,filter1,WAREHOUSE2,Columns2, DATABASE2, SCHEMA2,  Table2, filter2,Primary_key1, Primary_key2, Email_Address ): #new
    # resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
    
    if((not WAREHOUSE1 =="") and (WAREHOUSE2 =="")):
        ctx1 = snowflake.connector.connect(
          user='SF_RAW_STAGE_SERVICE',
          password='Zg5XZ!mm%PvA',
          account='ba62849.east-us-2.azure',
          warehouse1= WAREHOUSE1,
          database1=DATABASE1,
          schema1=SCHEMA1
        #   schema='SNAPSHOT'
          )        
# def  SnowflakeQA(Table):      
        cur1 = ctx1.cursor()
    
# # Execute a statement that will generate a result set.
        warehouse1= WAREHOUSE1
        database1= DATABASE1
        schema1=SCHEMA1
        Column1 = Columns1
        Filter1 = filter1

        if warehouse1:
            cur1.execute(f'use warehouse {warehouse1};')
    
        cur1.execute(f'select {Column1} from {database1}.{schema1}.{Table1} {Filter1} ;')
   
    
# Fetch the result set from the cursor and deliver it as the Pandas DataFrame.
        snowflakedf1 = cur1.fetch_pandas_all()
        
        if DATABASE2 == 'InfoTrax_Prod':
            engine2=EngineA 
            df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
            resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
            compare = datacompy.Compare(
            snowflakedf1,
            df2,
            join_columns= resultPrimaryKey) #new
            compare.matches(ignore_extra_columns=False) 
            print(compare.report())
            #sqldatabase = 'InfoTrax_Prod'
            # sqldatabase = 'ASEA_PROD'
            # sqldatabase = 'ASEA_REPORTS'
            # sqldatabase ='DB_ASEA_REPORTS'
            test = datetime.datetime.today()
            Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
            #Today = datetime.datetime.today() #correct
            outlook = client.Dispatch('Outlook.Application')
            message = outlook.Createitem(0)
            message.Display()
            message.To = Email_Address
            message.Subject = 'DIFF APP RESULTS: ' + WAREHOUSE1+'.' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +WAREHOUSE2+ '.' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
            message.Body = compare.report()
            message.Save()
            message.Send()
            cur1.close()
            # cur2.close()


        elif  DATABASE2 == 'ASEA_PROD':
            engine2 = EngineB 
            df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
            resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
            compare = datacompy.Compare(
            snowflakedf1,
            df2,
            join_columns= resultPrimaryKey) #new
            compare.matches(ignore_extra_columns=False) 
            print(compare.report())
            #sqldatabase = 'InfoTrax_Prod'
            # sqldatabase = 'ASEA_PROD'
            # sqldatabase = 'ASEA_REPORTS'
            
            test = datetime.datetime.today()
            Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
            #Today = datetime.datetime.today() #correct
            outlook = client.Dispatch('Outlook.Application')
            message = outlook.Createitem(0)
            message.Display()
            message.To = Email_Address
            message.Subject =  'DIFF APP RESULTS: ' + WAREHOUSE1+'.' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +WAREHOUSE2+ '.' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
            message.Body = compare.report()
            message.Save()
            message.Send()
            cur1.close()
            # cur2.close()



        elif DATABASE2 == 'ASEA_REPORTS':
            engine2 = EngineC
            df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
            resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
            compare = datacompy.Compare(
            snowflakedf1,
            df2,
            join_columns= resultPrimaryKey) #new
            compare.matches(ignore_extra_columns=False) 
            print(compare.report())
            #sqldatabase = 'InfoTrax_Prod'
            # sqldatabase = 'ASEA_PROD'
            # sqldatabase = 'ASEA_REPORTS'
            
            test = datetime.datetime.today()
            Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
            #Today = datetime.datetime.today() #correct
            outlook = client.Dispatch('Outlook.Application')
            message = outlook.Createitem(0)
            message.Display()
            message.To = Email_Address
            message.Subject =  'DIFF APP RESULTS ' + WAREHOUSE1+'.' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +WAREHOUSE2+ '.' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
            message.Body = compare.report()
            message.Save()
            message.Send()
            cur1.close()
            # cur2.close()

    if((WAREHOUSE1 =="") and (not WAREHOUSE2 =="")):

        ctx2 = snowflake.connector.connect(
          user='SF_RAW_STAGE_SERVICE',
          password='Zg5XZ!mm%PvA',
          account='ba62849.east-us-2.azure',
          warehouse2= WAREHOUSE2,
          database2=DATABASE2,
          schema2=SCHEMA2
          )

        cur2 = ctx2.cursor()
        warehouse2= WAREHOUSE2
        database2=DATABASE2
        schema2=SCHEMA2
        Column2 = Columns2
        Filter2 = filter2

        if warehouse2:
            cur2.execute(f'use warehouse {warehouse2};')
    
        cur2.execute(f'select {Column2} from {database2}.{schema2}.{ Table2} {Filter2} ;')
        snowflakedf2 = cur2.fetch_pandas_all()

        if DATABASE1 == 'InfoTrax_Prod':
            engine1=EngineA 
            df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
            resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
            compare = datacompy.Compare(
            df1,
            snowflakedf2,
            join_columns= resultPrimaryKey) #new
            compare.matches(ignore_extra_columns=False) 
            print(compare.report())
            #sqldatabase = 'InfoTrax_Prod'
            # sqldatabase = 'ASEA_PROD'
            # sqldatabase = 'ASEA_REPORTS'
            
            test = datetime.datetime.today()
            Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
            #Today = datetime.datetime.today() #correct
            outlook = client.Dispatch('Outlook.Application')
            message = outlook.Createitem(0)
            message.Display()
            message.To = Email_Address
            message.Subject ='DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +WAREHOUSE2+ '.' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
            message.Body = compare.report()
            message.Save()
            message.Send()
            # cur1.close()
            cur2.close()      


            

        elif DATABASE1 == 'ASEA_PROD':
            engine1=EngineB
            df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
            resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
            compare = datacompy.Compare(
            df1,
            snowflakedf2,
            join_columns= resultPrimaryKey) #new
            compare.matches(ignore_extra_columns=False) 
            print(compare.report())
            #sqldatabase = 'InfoTrax_Prod'
            # sqldatabase = 'ASEA_PROD'
            # sqldatabase = 'ASEA_REPORTS'
            
            test = datetime.datetime.today()
            Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
            #Today = datetime.datetime.today() #correct
            outlook = client.Dispatch('Outlook.Application')
            message = outlook.Createitem(0)
            message.Display()
            message.To = Email_Address
            message.Subject = 'DIFF APP RESULTS: ' + DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +WAREHOUSE2+ '.' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
            message.Body = compare.report()
            message.Save()
            message.Send()
            # cur1.close()
            cur2.close()    

        elif DATABASE1 == 'ASEA_REPORTS':
            engine1=EngineC
            df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
            resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
            compare = datacompy.Compare(
            df1,
            snowflakedf2,
            join_columns= resultPrimaryKey) #new
            compare.matches(ignore_extra_columns=False) 
            print(compare.report())
            #sqldatabase = 'InfoTrax_Prod'
            # sqldatabase = 'ASEA_PROD'
            # sqldatabase = 'ASEA_REPORTS'
            
            test = datetime.datetime.today()
            Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
            #Today = datetime.datetime.today() #correct
            outlook = client.Dispatch('Outlook.Application')
            message = outlook.Createitem(0)
            message.Display()
            message.To = Email_Address
            message.Subject = 'DIFF APP RESULTS: ' + DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +WAREHOUSE2+ '.' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
            message.Body = compare.report()
            message.Save()
            message.Send()
            # cur1.close()
            cur2.close()    



#SnowflakeVS SnowFlake:
def  SnowflakeQA(WAREHOUSE1,Columns1 , DATABASE1, SCHEMA1, Table1,filter1,WAREHOUSE2,Columns2, DATABASE2, SCHEMA2,  Table2, filter2,Primary_key1, Primary_key2, Email_Address): #new
    print(Primary_key1, Primary_key2)
    ctx1 = snowflake.connector.connect(
          user='SF_RAW_STAGE_SERVICE',
          password='Zg5XZ!mm%PvA',
          account='ba62849.east-us-2.azure',
          warehouse1= WAREHOUSE1,
          database1=DATABASE1,
          schema1=SCHEMA1
          )    

    ctx2 = snowflake.connector.connect(
          user='SF_RAW_STAGE_SERVICE',
          password='Zg5XZ!mm%PvA',
          account='ba62849.east-us-2.azure',
          warehouse2= WAREHOUSE2,
          database2=DATABASE2,
          schema2=SCHEMA2
          )
  
    cur1 = ctx1.cursor()
    
# # Execute a statement that will generate a result set.
    warehouse1= WAREHOUSE1
    database1= DATABASE1
    schema1=SCHEMA1
    Column1 = Columns1
    Filter1 = filter1

    if warehouse1:
        cur1.execute(f'use warehouse {warehouse1};')
    
    
    
    
    cur1.execute(f'select {Column1} from {database1}.{schema1}.{Table1} {Filter1} ;')
    print(cur1)
    
# Fetch the result set from the cursor and deliver it as the Pandas DataFrame.
    snowflakedf1 = cur1.fetch_pandas_all()
    
    
    cur2 = ctx2.cursor()
    warehouse2= WAREHOUSE2
    database2=DATABASE2
    schema2=SCHEMA2
    Column2 = Columns2
    Filter2 = filter2

    if warehouse2:
        cur2.execute(f'use warehouse {warehouse2};')
    
    cur2.execute(f'select {Column2} from {database2}.{schema2}.{ Table2} {Filter2} ;')


    snowflakedf2 = cur2.fetch_pandas_all()

    
    resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2)
    print(resultPrimaryKey)


    compare = datacompy.Compare(
    snowflakedf1,
    snowflakedf2,
    

    join_columns= resultPrimaryKey)
    
    

    compare.matches(ignore_extra_columns=False) 
    print(compare.report())
    #sqldatabase = 'InfoTrax_Prod'
    # sqldatabase = 'ASEA_PROD'
    # sqldatabase = 'ASEA_REPORTS'
    
    test = datetime.datetime.today()
    Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
    #Today = datetime.datetime.today() #correct
    pythoncom.CoInitialize()
    outlook = client.Dispatch('Outlook.Application')
    message = outlook.Createitem(0)
   
    message.To = Email_Address
    message.Subject =  'DIFF APP RESULTS: ' + WAREHOUSE1+'.' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +WAREHOUSE2+ '.' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
    message.Display()
    message.Body= compare.report()
    # message.Save()
    # message.Display(True)
    message.Save()
    message.Send()


    cur1.close()
    cur2.close()





# SQLSERVER VS SQLSERVER:

# engine1 = sqlalchemy.create_engine("mssql+pyodbc://" + "mourada:" + "J+!_b7jHm`+(5" +'"'+"!s" +"@InfoTrax_Prod") #working
EngineA = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % paramsA) #Working
EngineB = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % paramsB) #working
EngineC = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % paramsC) #working

# def  AzureSQlServer(Columns1 , DATABASE1,SCHEMA1 ,Table1, filter1,Columns2, DATABASE2,SCHEMA2 ,Table2,filter2, Primary_key):
def  AzureSQlServer(Columns1 , DATABASE1,SCHEMA1 ,Table1, filter1,Columns2, DATABASE2,SCHEMA2 ,Table2,filter2, Primary_key1, Primary_key2, Email_Address):#new
    # pushdown1 = '(' + 'select * from ' +  Table1 + "" + filter1 +')'
    # pushdown_query1 = "\"%s\""% pushdown1
    # # print(pushdown_query1)
    resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
    print(resultPrimaryKey)#new

    # pushdown1 = 'select * from ' +  Table1 + "" + filter1 + ' Type_alias'
    # print(pushdown1)

    if DATABASE1 == 'InfoTrax_Prod' and DATABASE2 == 'InfoTrax_Prod':
        engine1=EngineA
        engine2=EngineA 
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
        # resultPrimaryKey = combinedPrimary_key(Primary_key1, Primary_key2) #new
        # print(resultPrimaryKey)#new

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey) #new
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
        
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject =  'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  ' +DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()

    

    elif DATABASE1 == 'InfoTrax_Prod' and DATABASE2 == 'ASEA_PROD':
        engine1=EngineA
        engine2=EngineB
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
       
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject = 'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()
    

    elif DATABASE1 == 'InfoTrax_Prod' and DATABASE2 == 'ASEA_REPORTS':
        engine1=EngineA
        engine2=EngineC
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
        
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject =  'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()
    
    elif DATABASE1 == 'ASEA_PROD' and DATABASE2 == 'ASEA_PROD':
        engine1=EngineB
        engine2=EngineB
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
       
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject =  'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()

    elif DATABASE1 == 'ASEA_PROD' and DATABASE2 == 'ASEA_REPORTS':
        engine1=EngineB
        engine2=EngineC
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
       
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject = 'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()
        
    elif DATABASE1 == 'ASEA_REPORTS' and DATABASE2 == 'ASEA_REPORTS':
        engine1=EngineC
        engine2=EngineC
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
      
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject =  'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()

    elif DATABASE1 == 'ASEA_PROD' and DATABASE2 == 'InfoTrax_Prod':
        engine1=EngineB
        engine2=EngineA
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
        
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject =  'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()

    elif DATABASE1 == 'ASEA_REPORTS' and DATABASE2 == 'InfoTrax_Prod':
        engine1=EngineC
        engine2=EngineA
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df1.columns = map(str.upper, df1.columns)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
        
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject =  'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()

    elif DATABASE1 == 'ASEA_REPORTS' and DATABASE2 == 'ASEA_PROD':
        engine1=EngineC
        engine2=EngineB
        
        #df1 = pd.read_sql_query("SELECT" + Columns1 +  "FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        df1 = pd.read_sql_query("SELECT " + Columns1 +  " FROM " + DATABASE1 +"." + SCHEMA1 + ".[" + Table1 + "]" + filter1, engine1)
        # df2 = pd.read_sql_query("SELECT" + Columns2 +  "FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
        df2 = pd.read_sql_query("SELECT " + Columns2 +  " FROM "  + DATABASE2 +'.' + SCHEMA2 + ".["  + Table2 + "]" + filter2, engine2)
    # df2.columns = map(str.upper, df1.columns)
       
    

        compare = datacompy.Compare(
        df1,
        df2,
    

    #join_columns= 'LEGACYNUMBER')
        join_columns= resultPrimaryKey)
    #join_columns= Primary_key)

        compare.matches(ignore_extra_columns=False) 
        print(compare.report())
    
        
        test = datetime.datetime.today()
        Today = test.strftime("%Y-%m-%d %H:%M:%S") #correct
        #Today = datetime.datetime.today() #correct
        outlook = client.Dispatch('Outlook.Application')
        message = outlook.Createitem(0)
        message.Display()
        message.To = Email_Address
        message.Subject =  'DIFF APP RESULTS: ' +DATABASE1+ '.' +SCHEMA1+ '.' +Table1+ '  VS  '+DATABASE2+ '.' +SCHEMA2+ '.' +Table2 + ' ' + ' as of ' + ' ' + str(Today)
        message.Body = compare.report()
        message.Save()
        message.Send()




def Mainfunction(WAREHOUSE1,Columns1, DATABASE1,SCHEMA1,Table1, filter1,WAREHOUSE2,Columns2, DATABASE2,SCHEMA2,Table2,filter2, Primary_key1, Primary_key2, Email_Address):
    
    if WAREHOUSE1 == '' and WAREHOUSE2 =="":
        result = AzureSQlServer(Columns1 , DATABASE1,SCHEMA1 ,Table1, filter1,Columns2, DATABASE2,SCHEMA2 ,Table2,filter2, Primary_key1, Primary_key2, Email_Address) #new
    

    elif ((not WAREHOUSE1 =="") and (WAREHOUSE2 =="")):
        result = SnowflakeVSSQLSERVER_VICEVERSA(WAREHOUSE1,Columns1 , DATABASE1, SCHEMA1, Table1,filter1,WAREHOUSE2,Columns2, DATABASE2, SCHEMA2,  Table2, filter2,Primary_key1, Primary_key2 ,Email_Address )


    elif   ((WAREHOUSE1 =="") and (not WAREHOUSE2 =="")):
        result =  SnowflakeVSSQLSERVER_VICEVERSA(WAREHOUSE1,Columns1 , DATABASE1, SCHEMA1, Table1,filter1,WAREHOUSE2,Columns2, DATABASE2, SCHEMA2,  Table2, filter2,Primary_key1, Primary_key2, Email_Address )

    

    elif ((not WAREHOUSE1 =="") and (not WAREHOUSE2 =="")):
        
        # result = SnowflakeQA(WAREHOUSE1,Columns1 , DATABASE1, SCHEMA1, Table1,filter1,WAREHOUSE2,Columns2, DATABASE2, SCHEMA2,  Table2, filter2,Primary_key1, Primary_key2, Email_Address) #new
        result = SnowflakeQA(WAREHOUSE1,Columns1 , DATABASE1, SCHEMA1, Table1,filter1,WAREHOUSE2,Columns2, DATABASE2, SCHEMA2,  Table2, filter2,Primary_key1, Primary_key2, Email_Address) #new


##SqlServer VS Sql server  Working with one Primary key
# job =  Mainfunction("","""ID,ACCOUNTYPE
# ,LEGACYNUMBER""", 'InfoTrax_Prod','dbo','Tbl_DISTRIBUTOR', """WHERE CreatedDate BETWEEN '2015-01-10' AND DATEADD(month,-1, GETDATE()) AND UpdatedDate <= DATEADD(month, -1, GETDATE())""" ,"","""ID,ACCOUNTYPE
# ,LEGACYNUMBER""",'ASEA_PROD', 'dbo', 'Tbl_DISTRIBUTOR', """WHERE CreatedDate BETWEEN '2015-01-10' AND DATEADD(month,-1, GETDATE()) AND UpdatedDate <= DATEADD(month, -1, GETDATE())""", 'ID', '')        #qlServer VS Sql server  Working with one Primary key 



# #SqlServer VS Sql server  Working with2 primary keys
# job =  Mainfunction("","""ACCOUNTTYPE
# ,LEGACYNUMBER""", 'InfoTrax_Prod','dbo','Tbl_DISTRIBUTOR', """WHERE CreatedDate BETWEEN '2015-01-10' AND DATEADD(month,-1, GETDATE()) AND UpdatedDate <= DATEADD(month, -1, GETDATE())""" ,"","""ACCOUNTTYPE
# ,LEGACYNUMBER""",'ASEA_PROD', 'dbo', 'Tbl_DISTRIBUTOR', """WHERE CreatedDate BETWEEN '2015-01-10' AND DATEADD(month,-1, GETDATE()) AND UpdatedDate <= DATEADD(month, -1, GETDATE())""", 'FIRSTNAME', '') #qlServer VS Sql server  Working with2 primary keys



## Snowflake VS Snowflae working with one Primary key    
# job =  Mainfunction('COMPUTE_MACHINE',"""DISTRIBUTORID
# ,STARTDATE
# ,ENDDATE
# ,ACCOUNTTYPE""", 'DB_RAW_DATA','INFOTRAX_PROD','LU_ACCOUNTTYPE_LOG', """""" ,'COMPUTE_MACHINE',"""DISTRIBUTORID
# ,STARTDATE
# ,ENDDATE
# ,ACCOUNTTYPE""",'DB_ASEA_REPORTS', 'DBO', 'LU_ACCOUNTTYPE_LOG', """""", 'DISTRIBUTORID' ,"")  # Snowflake VS Snowflae working one Primary key       



## Snowflake VS Snowflae working with 2 porimary keys #working   
# job=  Mainfunction('COMPUTE_MACHINE',"""DISTRIBUTORID
# ,STARTDATE
# ,ENDDATE
# ,ACCOUNTTYPE""", 'DB_RAW_DATA','INFOTRAX_PROD','LU_ACCOUNTTYPE_LOG', """""" ,'COMPUTE_MACHINE',"""DISTRIBUTORID
# ,STARTDATE
# ,ENDDATE
# ,ACCOUNTTYPE""",'DB_ASEA_REPORTS', 'DBO', 'LU_ACCOUNTTYPE_LOG', """""", 'DISTRIBUTORID', 'ACCOUNTTYPE')  # Snowflake VS Snowflae working with 2 porimary keys #working   






#sqlserver VS snowflake working on both directions
# job =  Mainfunction('COMPUTE_MACHINE',"""DISTRIBUTORID
# ,RANK_CHANGE
# , CAST(STARTDATE AS DATE) AS STARTDATE
# , CAST(ENDDATE AS DATE) AS ENDDATE
# , ACCOUNTTYPE
# , POST_LOG_UPDATE""", 'DB_ASEA_REPORTS','PUBLIC','LU_ACCOUNTTYPE_LOG_QA', """where STARTDATE > '2015-01-01'""" ,'',"""DISTRIBUTORID
#     ,RANK_CHANGE
#     , CAST(STARTDATE AS DATE) AS STARTDATE
#     , CAST(ENDDATE AS DATE) AS ENDDATE
#     , ACCOUNTTYPE
#     , POST_LOG_UPDATE""",'InfoTrax_Prod', 'dbo', 'LU_ACCOUNTTYPE_LOG_QA', """where STARTDATE > '2015-01-01'""",'DISTRIBUTORID', 'RANK_CHANGE')  #sqlserver VS snowflake working directions







# ##databricks SqlServer VS Sql server  Working with one Primary key
# job =  Mainfunction("","""*""", 'InfoTrax_Prod','dbo','TBL_MARKETS', """""" ,"","""*""",'ASEA_REPORTS', 'asea_sales_stage', 'TBL_MARKETS', """""", 'ID', '')        #qlServer VS Sql server  Working with one Primary key 

@application.route('/')
def form():
   return render_template('form.html')

@application.route('/',methods = ['POST', 'GET'])
def result():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       WAREHOUSE_1 = request.form.get("WAREHOUSE1")
       # getting input with name = lname in HTML form 
       Columns_1 = request.form.get("Columns1") 
       print(WAREHOUSE_1)
       print(Columns_1)
       DATABASE_1  = request.form.get("DATABASE1") 
       print(DATABASE_1)
       SCHEMA_1 = request.form.get("SCHEMA1")
       WAREHOUSE_2 = request.form.get("WAREHOUSE2") 
       SCHEMA_2  = request.form.get("SCHEMA2") 
       Table_2  = request.form.get("Table2") 
       filter_2  = request.form.get("filter2") 
       Primary_key_1 = request.form.get("Primary_key1") 
       Primary_key_2 = request.form.get("Primary_key2") 
       Table_1 = request.form.get("Table1") 
       filter_1 = request.form.get("filter1") 
       DATABASE_2 = request.form.get("DATABASE2") 
       Columns_2 = request.form.get("Columns2") 
       Email_Address = request.form.get("Email_Address")

       result = Mainfunction(WAREHOUSE_1,Columns_1, DATABASE_1,SCHEMA_1,Table_1, filter_1,WAREHOUSE_2,Columns_2, DATABASE_2,SCHEMA_2,Table_2,filter_2, Primary_key_1, Primary_key_2, Email_Address)
    
    return render_template('result.html',result = result)

if __name__=='__main__':
   application.run(debug=True)     