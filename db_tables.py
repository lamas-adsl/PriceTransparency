from sqlalchemy import create_engine, Column, Integer, Numeric, String, DECIMAL, Time, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from sqlalchemy.engine import URL
import pyodbc


"""
    Connect to the database and open session
"""
connection_string = (
    r"Driver={SQL Server};"
    r"Server=ROYC-WIN10\SQLEXPRESS;"
    r"Database=ChainStorePriceDev;"
    r"Trusted_Connection=yes"
)
connection_url = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": connection_string}
)
engine = create_engine(connection_url)
Session = sessionmaker(bind=engine)
session = Session()


def insert(user_exec, *args):
    """
    Run the sql procedure with the arguments, get the arguments loop of them ,create standard string
    of the procedure execution, and run the execetion
    :param user_exec: procedure name, args: arguments to sent
    :return:
    """
    with engine.begin() as conn:
        sargs = ' '
        for aa in args:
            if type(aa) != datetime and type(aa) != timedelta:
                if "'" in str(aa):
                    aa = aa.replace("'", '"')
                if str(aa) == 'NULL':
                    sargs = sargs + 'NULL, '
                else:
                    sargs = sargs+"'"+str(aa)+"', "
            else:
                aa = str(aa)
                sargs = sargs+"'"+aa[:len(aa)-3]+"', "
        sargs = sargs[:len(sargs) - 2]
        txt = text("exec "+user_exec+sargs)
        is_insert = conn.execute(txt)
        return is_insert


def select(user_exec, *args):
    with engine.begin() as conn:
        sargs = ' '
        for aa in args:
            if type(aa) != datetime and type(aa) != timedelta:
                if "'" in str(aa):
                    aa = aa.replace("'", '"')
                if str(aa) == 'NULL':
                    sargs = sargs + 'NULL, '
                else:
                    sargs = sargs+"'"+str(aa)+"', "
            else:
                aa = str(aa)
                sargs = sargs+"'"+aa[:len(aa)-3]+"', "
        sargs = sargs[:len(sargs) - 2]
        txt = text("exec "+user_exec+sargs)
        selected = conn.execute(txt)
        return selected