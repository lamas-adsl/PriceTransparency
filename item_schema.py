import xml.etree.ElementTree as ET


class Item:
    def __init__(self, base='Items', item='Item', code='ItemCode', type='ItemType', name='ItemName', unit_quantity='UnitQty',
                 quantity_in_package='QtyInPackage', quantity='Quantity', manufacture_country='ManufactureCountry',
                 price='ItemPrice', update_date='PriceUpdateDate', store_code='StoreId', branch_code='SubChainId',
                 chain_code='ChainId', root='Root'):
        self.root = root
        self.base = base
        self.item = item
        self.code = code
        self.type = type
        self.name = name
        self.unit_quantity = unit_quantity
        self.quantity_in_package = quantity_in_package
        self.quantity = quantity
        self.manufacture_country = manufacture_country
        self.price = price
        self.update_date = update_date
        self.store_code = store_code
        self.branch_code = branch_code
        self.chain_code = chain_code

    def get_column(self, column):
        return exec("self.{}".format(column))

    def get_name_package(self):
        name = self.root+'_'+self.item+'_'+self.name
        name = name.replace('..', '')
        name = name.replace('.//', '_')
        name = name.replace('//', '_')
        name = name.replace('/', '_')
        return name


def create_schema(xml):
    item = Item()
    tree = ET.parse(xml)
    root = tree.getroot().tag
    item.root = root
    chain = tree.find('ChainId')
    if chain is None:
        chain = tree.find('ChainID')
        item.chain_code = 'ChainID'
        if chain is None:
            tree = tree.find('Envelope')
            chain = tree.find('ChainId')
            item.chain_code = 'Envelope/ChainId'
    branch = tree.find('StoreId')
    if 'Envelope' in item.chain_code:
        item.store_code = 'Envelope/StoreId'
    else:
        item.store_code = 'StoreId'
    if branch is None:
        branch = tree.find('StoreID')
        if 'Envelope' in item.chain_code:
            item.store_code = 'Envelope/StoreID'
        else:
            item.store_code = 'StoreID'
    branch_code = tree.find('SubChainID')
    if branch_code is None:
        branch_code = tree.find('SubChainId')
        if 'Envelope' in item.branch_code and branch_code is not None:
            item.branch_code = 'Envelope/SubChainId'
    else:
        if 'Envelope' in item.branch_code:
            item.branch_code = 'Envelope/SubChainID'
    products = tree.find('Items')
    if products is None:
        products = tree.find('Products')
        if products is None:
            products = tree.find('Header')
            if products is None:
                print("Not find products in : " + tree.find('.//'+item.base+'/'+item.item+'/'+item.name))
            else:
                products = products.find('Details')
                products = products.findall('Line')
                item.item = 'Line'
                item.base = './/Header/Details'
        else:
            products = products.findall('Product')
            item.item = 'Product'
            item.base = 'Products'
    else:
        products = products.findall('Item')
    nameItm = products[0].find('ItemName')
    if nameItm is None:
        nameItm = products[0].find('ItemNm')
        item.name = 'ItemNm'
    return item