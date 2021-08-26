from sqlite3 import Error
import sqlite3
import pandas as pd
import ipaddress
import datetime
import xmltodict
import json
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from postgres import connection, cursor

public_ip_tables = ["PDC_DCI_OUTSIDE", "CDC_DCI_OUTSIDE", "PHX_DCI_OUTSIDE", "DFW_DCI_OUTSIDE"]


def get_current_time():
    date_string = str(datetime.datetime.now())
    return date_string.split('.')[0]
def custom_find_key(element, json_data):
    paths = element.split(".")
    for i in range(0, len(paths)):
        json_data = json_data[paths[i]]
    return json_data
def check_existing_table(table_name):
    try:
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        check_table_sql = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='" + table_name + "'"
        cursor.execute(check_table_sql)
        res = cursor.fetchone()
        db.close()
        if res[0] == 0:
            return False
        else:
            return True
    except:
        return False
def select_max_range_item_in_search(search_array, search_item):
    check_flag = False
    pop_indexes = []
    for i in range(len(search_array)):
        item = search_array[i]
        if not item[8] == search_item[8]:
            continue
        arr_ip = item[1]
        item_ip = search_item[1]
        if not len(arr_ip.split('/')) == 2 or not len(item_ip.split('/')) == 2:
            continue
        exist_mask = int(arr_ip.split('/')[1])
        new_mask = int(item_ip.split('/')[1])
        if new_mask > exist_mask:
            pop_indexes.append(i)
        else:
            check_flag = True
    if check_flag:
        return search_array
    if len(pop_indexes) > 0:
        for index in pop_indexes:
            search_array.pop(index)
    search_array.append(search_item)
    return search_array
def excel_database(file, table_name):
    df = pd.read_excel(file)
    df_array = df.to_numpy()
    index = 0
    with sqlite3.connect(database='database.db') as conn:
        cur = conn.cursor()
        check_table_sql = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='" + table_name + "'"
        cur.execute(check_table_sql)
        if cur.fetchone()[0] == 0:
            create_table_sql = 'CREATE TABLE ' + table_name + '(id INT NOT NULL, IP CHAR(256), STATUS CHAR(256))'
            cur.execute(create_table_sql)
        for i in range(len(df_array)):
            try:
                row = df_array[i]
                ip_string = row[0]
                ips = ip_string.split('\n')
                status = row[1]
                print(index, ips, status)
                for ip in ips:
                    index = index + 1
                    insert_sql = "INSERT INTO " + table_name + "(id, IP, STATUS) VALUES ("
                    insert_sql += str(index) + ", '" + ip + "', '" + status + "')"
                    print(insert_sql)
                    cur.execute(insert_sql)
            except Exception as err:
                print(err)
    db_record_time(table_name)
def get_pci():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='DC_PCI';")
    if cursor.fetchone()[0] == 0:
        return []
    else:
        cursor.execute("SELECT * FROM DC_PCI")
        pci_rows = cursor.fetchall()
        return pci_rows
def func_search_ip(ips, dbs):
    search_res = []
    try:
        with sqlite3.connect(database='database.db') as conn:
            cur = conn.cursor()
            for ip in ips:
                pci_status = 'NO'
                pci_sql = "SELECT * FROM DC_PCI WHERE IP = '" + ip + "'"
                cur.execute(pci_sql)
                pci_res = cur.fetchall()
                if len(pci_res) > 0 and pci_status == 'NO':
                    print("len(pci_res): ", pci_res)
                    pci_status = pci_res[0][2]
                exist_flag = False
                for db in dbs:
                    if not check_existing_table(db):
                        continue
                    cur.execute("SELECT * FROM " + db)
                    nets = cur.fetchall()
                    for net in nets:
                        if net[1] == 'N/A':
                            continue
                        if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(net[1]):
                            if net[1] == "0.0.0.0/0" and db not in public_ip_tables:
                                continue
                            net = net + (pci_status,)
                            net = net + (ip,)
                            # search_res.append(net)
                            search_res = select_max_range_item_in_search(search_res, net)
                            exist_flag = True
                if not exist_flag:
                    search_res.append(('None', ip, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', pci_status, ip))
            print(search_res)
    except Error as e:
        print(e)
        conn.rollback()
    finally:
        conn.close()
    return search_res
def get_table_names():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = []
    records = get_record_time()
    for table_name in tables:
        table_name = table_name[0]
        # table = pd.read_sql_query("SELECT * from %s" % table_name, db)
        # table.to_csv(table_name + '.csv', index_label='index')
        if table_name == "sqlite_sequence" or table_name == "db_record_time":
            continue
        record_time = ''
        for record in records:
            if record[0] == table_name:
                record_time = record[2]
        if record_time == '':
            record_time = str(datetime.datetime.now()).split('.')[0]
        table_names.append([table_name, record_time])
    cursor.close()
    db.close()
    return table_names
def db_manage_user(method_type, user_id, role):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    if method_type == 'all':
        sql = "SELECT * FROM user"
        cursor.execute(sql)
        users = cursor.fetchall()
        return users
    elif method_type == 'edit':
        sql = "UPDATE user SET role = '" + role + "' WHERE id = '" + user_id + "'"
        cursor.execute(sql)
        db.commit()
        db_record_time('user')
        return True
    elif method_type == 'remove':
        sql = "DELETE FROM user WHERE id = " + user_id
        cursor.execute(sql)
        db.commit()
        db_record_time('user')
        return True
    else:
        return False
def db_record_time(table_name):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    check_table_sql = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='db_record_time'"
    cursor.execute(check_table_sql)
    if cursor.fetchone()[0] == 0:
        create_table_sql = 'CREATE TABLE db_record_time (name CHAR(256) NOT NULL, created_at CHAR(256), updated_at CHAR(256))'
        cursor.execute(create_table_sql)
        db.commit()
    search_sql = "SELECT * FROM db_record_time WHERE name = '" + table_name + "'"
    cursor.execute(search_sql)
    check_table = cursor.fetchone()
    current_time = get_current_time()
    if not check_table:
        cursor.execute("INSERT INTO db_record_time (name, created_at, updated_at) VALUES (?, ?, ?)", (table_name, current_time, current_time))
        db.commit()
    else:
        update_sql = "UPDATE db_record_time SET updated_at = '" + current_time + "' WHERE name = '" + table_name + "'"
        cursor.execute(update_sql)
        db.commit()
def get_record_time():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM db_record_time")
    records = cursor.fetchall()
    return records
def rt_to_db(file_type, filename, table_name, str_vrf, str_ipnexthop, str_map, table_keys, table_fields):
    list_vrf = str_vrf.split('\n')
    ex_vrf = []
    ex_ipnexthop = []
    map_ips = []
    map_locations = []
    for vrf in list_vrf:
        vrf = vrf.strip()
        if vrf:
            ex_vrf.append(vrf)
    # print(ex_vrf)
    list_ipnexthop = str_ipnexthop.split('\n')
    for ipnexthop in list_ipnexthop:
        ipnexthop = ipnexthop.strip()
        if ipnexthop:
            ex_ipnexthop.append(ipnexthop)
    # print(ex_ipnexthop)
    list_maps = str_map.split('\n')
    for item_map in list_maps:
        item_map = item_map.strip()
        if not item_map:
            continue
        item_map_arr = item_map.split('=')
        if not len(item_map_arr) == 2:
            continue
        item_ips = item_map_arr[0].split(',')
        item_location = item_map_arr[1].strip()
        for item_ip in item_ips:
            map_ips.append(item_ip.strip())
            map_locations.append(item_location)
    # print(map_ips)
    # print(map_locations)
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='" + table_name + "'")
    check_table = cur.fetchone()
    if check_table[0] == 1 or check_table[0] == '1':
        print("Table already exist")
        return {'status': 'error', 'message': 'Table already exist'}
    else:
        create_table_sql = 'CREATE TABLE ' + table_name + '(id INT NOT NULL, IP CHAR(256), Location CHAR(256), VRF CHAR(256), L3 CHAR(256), MTU CHAR(256), TAG CHAR(256))'
        cur.execute(create_table_sql)
        conn.commit()
    with open(filename) as file_data:
        if file_type == 'xml':
            ET.register_namespace('', 'http://www.cisco.com/nxos:1.0:urib')
            tree = ET.parse(filename)
            xml_data = tree.getroot()
            xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')
            data_dict = xmltodict.parse(xmlstr, attr_prefix='')
            data_dict = json.loads(json.dumps(data_dict))
        elif file_type == 'json':
            data_dict = json.load(file_data)
        else:
            return {'status': 'error', 'message': 'Undefined file format'}
        file_data.close()
        dict_value = list(get_value_by_key_from_dict('ROW_vrf', data_dict))
        dt_id = 0
        # for row_vrf in dict_value:
        # print("len(dict_value)", len(dict_value))
        for row_vrf_index in range(len(dict_value)):
            row_vrf = dict_value[row_vrf_index]
            # for item in row_vrf:
            # print("len(row_vrf)", len(row_vrf))
            for item_index in range(len(row_vrf)):
                item = row_vrf[item_index]
                if not 'vrf-name-out' in item:
                    continue
                dt_vrf = item['vrf-name-out']
                if dt_vrf in ex_vrf:
                    continue
                if not 'TABLE_addrf' in item:
                    continue
                if not 'ROW_addrf' in item['TABLE_addrf']:
                    continue
                if not 'TABLE_prefix' in item['TABLE_addrf']['ROW_addrf']:
                    continue
                if not 'ROW_prefix' in item['TABLE_addrf']['ROW_addrf']['TABLE_prefix']:
                    continue
                row_prefix = item['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix']
                if not row_prefix:
                    continue
                if not isinstance(row_prefix, list):
                    row_prefix = [row_prefix]
                for prefix_item_index in range(len(row_prefix)):
                    prefix_item = row_prefix[prefix_item_index]
                    if not 'ipprefix' in prefix_item:
                        continue
                    dt_ip = prefix_item['ipprefix']
                    if not 'TABLE_path' in prefix_item:
                        continue
                    if not 'ROW_path' in prefix_item['TABLE_path']:
                        continue
                    row_path = prefix_item['TABLE_path']['ROW_path']
                    dt_location = ''
                    dt_l3 = ''
                    dt_mtu = ''
                    dt_tag = ''
                    if not isinstance(row_path, list):
                        row_path = [row_path]
                    for path_item_index in range(len(row_path)):
                        path_item = row_path[path_item_index]
                        # print("path_item: ", path_item)
                        if dt_l3 == '':
                            if 'ifname' in path_item and 'clientname' in path_item:
                                dt_l3 = path_item['ifname'] + ' ' + path_item['clientname']
                            elif not 'ifname' in path_item and 'clientname' in path_item:
                                dt_l3 = path_item['clientname']
                            elif 'ifname' in path_item and not 'clientname' in path_item:
                                dt_l3 = path_item['ifname']
                            else:
                                dt_l3 = 'N/A'
                        if dt_mtu == '':
                            if 'mtu' in path_item:
                                dt_mtu = path_item['mtu']
                            else:
                                dt_mtu = 'N/A'
                        if dt_tag == '':
                            if 'tag' in path_item:
                                dt_tag = path_item['tag']
                            else:
                                dt_tag = 'N/A'
                        if 'ipnexthop' in path_item:
                            ip_location = path_item['ipnexthop']
                        else:
                            ip_location = table_name
                        if ip_location in ex_ipnexthop:
                            continue
                        if ip_location in map_ips:
                            dt_location = map_locations[map_ips.index(ip_location)]
                        else:
                            if dt_location == '':
                                dt_location = ip_location
                            elif not dt_location in map_ips and not ip_location == table_name:
                                    dt_location = dt_location + ", " + ip_location
                            elif not dt_location in map_ips and ip_location == table_name:
                                dt_location = dt_location
                            else:
                                dt_location = table_name
                    if dt_location == '':
                        continue
                    dt_id = dt_id + 1
                    dt_insert_sql = "INSERT INTO " + table_name + " (id, IP, Location, VRF, L3, MTU, TAG) VALUES ("
                    dt_insert_sql = dt_insert_sql + str(dt_id) + ", '" + dt_ip + "', '" + dt_location + "', '"
                    dt_insert_sql = dt_insert_sql + dt_vrf + "', '" + dt_l3 + "', '" + dt_mtu + "', '" + dt_tag + "')"
                    print(dt_insert_sql)
                    cur.execute(dt_insert_sql)
                    conn.commit()
                    # if dt_id > 2:
                    #     break
        db_record_time(table_name)
        return {'status': 'success'}
def get_value_by_key_from_dict(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in get_value_by_key_from_dict(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in get_value_by_key_from_dict(key, d):
                    yield result

# Inventory Code 8/9/2021
bad_char = [
            '!', '#', '$', '%', '&', '"', '(', ')','*','+',
            '-', '/', ';', '<', '=', '>', '?', '[', ']', '^',
            '`' '˜', '™', 'š', '›', 'œ','ž', 'Ÿ','¡','¢','£','¤',
            '¥','¦','§','¨','©','ª','«','¬','­','®','¯','°','±','²',
            '³','´','µ','¶','·','¹','º','»','¼','½','¾','¿','','‚',
            'ƒ','„','…','†','‡','ˆ','‰','Š','‹','Œ','','Ž','','',
            '‘','’','“','”', '÷', '@', '؟', ','
            ]

def removeStartNumbers(string):
    checkFirst = ''
    result = ''
    for i in string:
        try:
            checkFirst = int(i)
            result += 'x'
        except ValueError:
            result += i
    return result


def filterVar(string):
    string = string.replace(' ','_')
    string = string.replace('-','_')
    return string
def betterVar(string):
    # as not found any filter for create table I did it myself
    string = "%s" %string
    string = removeStartNumbers(string)
    string = string.replace("--", "") if "--" in string else string
    string = string.replace("'", "") if "'" in string else string
    string = string.replace('"', '') if '"' in string else string
    string = string.replace(';', '') if ';' in string else string
    string = string.replace('.', '_') if '.' in string else string
    string = string.replace(chr(92), '') if (chr(92) in string) else string
    string = string.replace('tableoid', '_' + 'tableoid') if 'tableoid' in string else string
    string = string.replace('xmin', '_' + 'xmin') if 'xmin' in string else string
    string = string.replace('cmin', '_' + 'cmin') if 'cmin' in string else string
    string = string.replace('xmax', '_' + 'xmax') if 'xmax' in string else string
    string = string.replace('cmax', '_' + 'cmax') if 'cmax' in string else string
    string = string.replace('ctid', '_' + 'ctid') if 'ctid' in string else string
    for c in bad_char:
        string = string.replace(c, "_") if c in string else string
    return string

def riskVar(string):
    string = string.replace("'",'__fehsinglecomma__')
    string = string.replace('"','__fehduplecomma__')
    return string

def rishVarReverse(string):
    string.replace('__fehsinglecomma__', "'")
    string = string.replace('__fehduplecomma__', '"')
    return string

# this function return all files uploaded to system
def returnFileList():
    files_list = []
    try:
        selectQuery = "SELECT id, filename, file_path FROM master_db ORDER BY id DESC;"
        result2 = cursor.execute(selectQuery);
        selectResult = cursor.fetchall()
        files_list = [{'id': file[0], 'name': file[1], 'path': file[2]} for file in selectResult]
    except:
        files_list = []

    return files_list

# this function return all worksheets in the system no matter the file (will be used in delete)
def returnWorksheetsList():
    sheets_list = []
    try:
        selectSheetsString = "SELECT id, file_id, file_name, sheet_name, file_path FROM worksheets ORDER BY id DESC;"
        selectSheetsQuery = cursor.execute(selectSheetsString);
        selectSheetsResult = cursor.fetchall()
        sheets_list = [{'id': sheet[0], 'file_id': sheet[1], 'filename': sheet[2], 'name': sheet[3], 'path': sheet[4]} for sheet in selectSheetsResult]
    except:
        sheets_list = []

    return sheets_list



# This function returns all worksheets of a given file
def returnSheetsForGivinFile(fileid):
    sheets_list = []
    try:
        selectSheetsString = "SELECT id, file_id, file_name, sheet_name, file_path FROM worksheets WHERE file_id=%s ORDER BY id DESC;"%fileid
        selectSheetsQuery = cursor.execute(selectSheetsString);
        selectSheetsResult = cursor.fetchall()
        sheets_list = [{'id': sheet[0], 'file_id': sheet[1], 'filename': sheet[2], 'name': sheet[3], 'path': sheet[4]} for sheet in selectSheetsResult]
    except:
        sheets_list = []
    return sheets_list


# This function returns worksheets of a given id
def returnSheetForGivinId(sheetid, requestOffset, perPage, page, order_column, order_type, download=False):
    sheet_data = {'sheet_list': [], 'columns': [], 'total':0, 'name':'', 'table': ''}
    page = page
    #, order_column, order_type

    try:
        selectSheetsString = "SELECT sheet_name, columns, real_name FROM worksheets WHERE id=%s;"%sheetid
        selectSheetsQuery = cursor.execute(selectSheetsString);
        selectSheetsResult = cursor.fetchone()
    except:
        return sheet_data

    if selectSheetsResult == None:
        return sheet_data

    tableName = selectSheetsResult[0]


    try:
        if download == False:
            selectTableString = "SELECT * FROM %s ORDER BY %s %s OFFSET %s LIMIT %s;"%(tableName, order_column, order_type, requestOffset, perPage)
        else:
            selectTableString = "SELECT * FROM %s ORDER BY %s %s;"%(tableName, order_column, order_type)

        selectTableQuery = cursor.execute(selectTableString)
        selectTableResult = cursor.fetchall()
        sheet_data['sheet_list'] = selectTableResult
        selectCountString = "SELECT COUNT(id) FROM %s;"%tableName
        selectCountQuery = cursor.execute(selectCountString)
        selectCountResult = cursor.fetchone()
    except:
        return sheet_data

    if selectTableResult != None:
        try:
            columnsList = selectSheetsResult[1].split(',')
            sheet_data['sheet_list'] = selectTableResult
            sheet_data['columns'].append('id')
            for col in columnsList:
                sheet_data['columns'].append(col)
            sheet_data['total'] = selectCountResult[0]
            sheet_data['name'] = selectSheetsResult[2]
            sheet_data['table'] = selectSheetsResult[0]

            return sheet_data
        except:
            sheet_data = {'sheet_list': [], 'columns': [], 'total':0, 'name':''}
            return sheet_data
    else:
        return sheet_data

    return sheet_data


# this function will update selected cell from the created table
def updateThisCell(tablename, columnname, newvalue, rowid):
    cellid = None
    try:
        updateCellString = "UPDATE %s SET %s = '%s' WHERE id=%s RETURNING %s;"%(tablename, columnname, newvalue, rowid, columnname)
        updateCellQuery = cursor.execute(updateCellString);
        updateCellResult = cursor.fetchone()
        cellid = updateCellResult[0]
        return cellid
    except:
        cellid = None

    return cellid


# this function will Delete selected Row from the created table
def deleteThisRow(tablename, rowid):
    success = None
    try:
        deleteRowString = "DELETE FROM %s WHERE id = %s;"%(tablename, rowid)
        deleteRowQuery = cursor.execute(deleteRowString);
        success = True
    except:
        success = None

    return success


# this function will handle Insert after
def insertRowAfter(tablename, current_id, column_names, values):
    # 1- create squence 2- set val with always last id 3- repeat the steps for each row go back to setval and get updated value

    lastIdString = "select max(id) from %s;"%tablename
    lastIdQuery = cursor.execute(lastIdString)
    lastIdResult = cursor.fetchone()
    lastId = lastIdResult[0]
    futureOrder = int(current_id) + 1
    newUpdateMax = 2 + int(current_id)
    # first step move all rows that bigger than target new id eg : new value should be in 6 any thing > 6 moved starting from max id
    # this will make the id after the current row empty

    tempDropString = "DROP SEQUENCE IF EXISTS seq_upd";
    tempDropString1 = "DROP SEQUENCE IF EXISTS seq_two";
    cursor.execute(tempDropString)
    cursor.execute(tempDropString1)

    if int(current_id) != lastId:
        temporarySquence1 = "create temporary sequence IF NOT EXISTS seq_upd;"
        temporarySquence01 = "select setval('seq_upd', (select max(id) from %s) + %s);"%(tablename, newUpdateMax)
        temporarySquence001 = "update %s set id=nextval('seq_upd') where id>%s;"%(tablename, int(current_id))
        cursor.execute(temporarySquence1)
        cursor.execute(temporarySquence01)
        cursor.execute(temporarySquence001)

        # insert new value after current row eg 7 set the id as futrue id which is current + 1
        insertNewRowString = "INSERT INTO %s ("%tablename
        for i_cname in range(len(column_names)):
            if i_cname == len(column_names)-1:
                insertNewRowString += str(column_names[i_cname]) + ") VALUES("
            else:
                insertNewRowString += str(column_names[i_cname]) + ", "
        for i_cvalue in range(len(values)):
            if i_cvalue == 0:
                insertNewRowString += str(values[i_cvalue]) + ", "
            elif i_cvalue == len(values)-1:
                insertNewRowString += "'" + values[i_cvalue] + "');"
            else:
                insertNewRowString += "'" + values[i_cvalue] + "', "
        cursor.execute(insertNewRowString)


        # last step back the group to the new sequence any item > futre id
        temporarySquence2 = "create temporary sequence IF NOT EXISTS seq_two;"
        temporarySquence02 = "select setval('seq_two', %s, false);"%newUpdateMax
        temporarySquence002 = "update %s set id=nextval('seq_two') where id>%s;"%(tablename, futureOrder)
        cursor.execute(temporarySquence2)
        cursor.execute(temporarySquence02)
        cursor.execute(temporarySquence002)
        return True
    else:
        # insert new value after current row eg 7 set the id as futrue id which is current + 1
        insertNewRowString = "INSERT INTO %s ("%tablename
        for i_cname in range(len(column_names)):
            if i_cname == len(column_names)-1:
                insertNewRowString += str(column_names[i_cname]) + ") VALUES("
            elif i_cname == 0:
                continue
            else:
                insertNewRowString += str(column_names[i_cname]) + ", "
        for i_cvalue in range(len(values)):
            if i_cvalue == 0:
                continue
            elif i_cvalue == len(values)-1:
                insertNewRowString += "'" + values[i_cvalue] + "');"
            else:
                insertNewRowString += "'" + values[i_cvalue] + "', "
        cursor.execute(insertNewRowString)
        return True
    return False



# this function will handle Insert after
def insertRowBefore(tablename, current_id, column_names, values):
    # 1- create squence 2- set val with always last id 3- repeat the steps for each row go back to setval and get updated value
    try:
        lastIdString = "select max(id) from %s;"%tablename
        lastIdQuery = cursor.execute(lastIdString)
        lastIdResult = cursor.fetchone()
        lastId = lastIdResult[0]
        futureOrder = int(current_id)
        newUpdateMax = 1 + int(current_id)
        # first step move all rows that bigger than target new id eg : new value should be in 6 any thing > 6 moved starting from max id
        # this will make the id after the current row empty
        tempDropString = "DROP SEQUENCE IF EXISTS seq_downone";
        tempDropString1 = "DROP SEQUENCE IF EXISTS seq_downtwo";
        cursor.execute(tempDropString)
        cursor.execute(tempDropString1)
        temporarySquence3 = "create temporary sequence IF NOT EXISTS seq_downone;"
        temporarySquence03 = "select setval('seq_downone', (select max(id) from %s) + %s);"%(tablename, newUpdateMax)
        temporarySquence003 = "update %s set id=nextval('seq_downone') where id>=%s;"%(tablename, int(current_id))
        cursor.execute(temporarySquence3)
        cursor.execute(temporarySquence03)
        cursor.execute(temporarySquence003)

        # insert new value after current row eg 7 set the id as futrue id which is current + 1
        insertNewRowString = "INSERT INTO %s ("%tablename
        for i_cname in range(len(column_names)):
            if i_cname == len(column_names)-1:
                insertNewRowString += str(column_names[i_cname]) + ") VALUES("
            else:
                insertNewRowString += str(column_names[i_cname]) + ", "
        for i_cvalue in range(len(values)):
            if i_cvalue == 0:
                insertNewRowString += str(values[i_cvalue]) + ", "
            elif i_cvalue == len(values)-1:
                insertNewRowString += "'" + values[i_cvalue] + "');"
            else:
                insertNewRowString += "'" + values[i_cvalue] + "', "
        cursor.execute(insertNewRowString)


        # last step back the group to the new sequence any item > futre id
        temporarySquence2 = "create temporary sequence IF NOT EXISTS seq_downtwo;"
        temporarySquence02 = "select setval('seq_downtwo', %s, false);"%newUpdateMax
        temporarySquence002 = "update %s set id=nextval('seq_downtwo') where id>%s;"%(tablename, newUpdateMax)
        cursor.execute(temporarySquence2)
        cursor.execute(temporarySquence02)
        cursor.execute(temporarySquence002)
        return True
    except:
        return False



# this function will handle Insert at end
def insertInto(tablename, column_names, values):
    # insert new value after current row eg 7 set the id as futrue id which is current + 1
    lastIdString = "select max(id) from %s;"%tablename
    lastIdQuery = cursor.execute(lastIdString)
    lastIdResult = cursor.fetchone()
    lastId = lastIdResult[0]
    futureOrder = lastId + 1
    insertNewRowString = "INSERT INTO %s ("%tablename
    for i_cname in range(len(column_names)):
        if i_cname == len(column_names)-1:
            insertNewRowString += str(column_names[i_cname]) + ") VALUES("
        elif i_cname == 0:
            insertNewRowString += "id, "
        else:
            insertNewRowString += str(column_names[i_cname]) + ", "
    for i_cvalue in range(len(values)):
        if i_cvalue == len(values)-1:
            insertNewRowString += "'" + values[i_cvalue] + "');"
        elif i_cvalue == 0:
            insertNewRowString += str(futureOrder) + ", "
        else:
            insertNewRowString += "'" + values[i_cvalue] + "', "
    cursor.execute(insertNewRowString)
    return True
    return False
