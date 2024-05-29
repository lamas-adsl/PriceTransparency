from defusedxml.ElementTree import parse
import pandas as pd
import db_tables as db


def parse_xml_to_pandas(xml, name, writer):
    """
    === not in used...
    Get xml and insert to csv the attributes names by columns, and insert the value of the products to the table
    :param xml: to parse, name: of the chain, writer: the csv that we write to him
    :return:
    """
    tree = parse(xml)
    chain = tree.find('ChainId')
    if chain is None:
        chain = tree.find('ChainID')
        if chain is None:
            tree = tree.find('Envelope')
            chain = tree.find('ChainId')
    branch = tree.find('StoreId')
    if branch is None:
        branch = tree.find('StoreID')
    products = tree.find('Items')
    if products is None:
        products = tree.find('Products')
        if products is None:
            products = tree.find('Header')
            if products is None:
                print("Not find products in : " + name)
            else:
                products = products.find('Details')
                products = products.findall('Line')
        else:
            products = products.findall('Product')
    else:
        products = products.findall('Item')
    columns_name = {e.tag for e in products[0]}
    table = pd.DataFrame(columns=columns_name)
    for prod in products:
        data = {}
        for c in columns_name:
            data[c] = prod.find(c).text
        table = table.append(data, ignore_index=True)
    table.to_excel(writer, sheet_name=chain.text+'_'+name[:10], encoding="ISO-8859-8")


def add_to_table(name, *args):
    """
    Get the name of the procedure we want to run, with the arguments and call to the db function
    :param name: of the procedure
    :param args: argument to sent to the procedure
    :return:
    """
    db.insert(name, *args)


def select_from_table(name, *args):
    """
    Get the name of the procedure we want to run, with the arguments and call to the db function
    :param name: of the procedure
    :param args: argument to sent to the procedure
    :return: selected element
    """
    return db.select(name, *args)