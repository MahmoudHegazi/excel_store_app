import pwd_hasher
import sqlite3
import datetime
import subprocess
import json
import xmltodict
import os
import functions
import ssl
import logging
import math
import openpyxl
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, abort, session, jsonify, send_from_directory, Response, Blueprint, flash
from flask import jsonify
from postgres import connection, cursor, setupdb
from werkzeug.utils import secure_filename
from sqlite3 import Error


app = Flask(__name__)

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(levelname)s %(threadName)s : %(message)s')
app.secret_key = 'ffce805ea02504f5a59820c1ea8985e0432f39566059d7f8'
uploads_dir = os.path.join(app.static_folder, 'uploads')
vr_key = "nf:rpc-reply.nf:data.show.ip.interface.__XML__BLK_Cmd_ip_show_interface_command_brief.__XML__OPT_Cmd_ip_show_interface_command_operational.__XML__OPT_Cmd_ip_show_interface_command_vrf.__XML__OPT_Cmd_ip_show_interface_command___readonly__.__readonly__.TABLE_vrf"
int_key = "nf:rpc-reply.nf:data.show.ip.interface.__XML__BLK_Cmd_ip_show_interface_command_brief.__XML__OPT_Cmd_ip_show_interface_command_operational.__XML__OPT_Cmd_ip_show_interface_command_vrf.__XML__OPT_Cmd_ip_show_interface_command___readonly__.__readonly__.TABLE_intf"
ssl._create_default_https_context = ssl._create_unverified_context
ALLOWED_EXTENSIONS = set(['xlsx', 'xls', 'xlsm', 'xlsb', 'csv', 'xltx', 'xlam'])
# inventory code 8/9/2021

# function to create download folder
def createDownloadFolder():
    download_folder = os.path.join(app.static_folder, 'downloads\\')
    downloadDay = str(datetime.datetime.today().strftime("%Y-%m-%d"))
    download_folder = download_folder+downloadDay
    try:
        os.makedirs(download_folder)
    except FileExistsError:
        # directory already exists
        return download_folder
    return download_folder

# function to create new dir in the upload folder for each excel there are folder with time
def CreateNewDir():
    UPLOAD_FOLDER = os.path.join(app.static_folder, 'excel_uploads\\')
    uploadDay = str(datetime.datetime.today().strftime("%Y-%m-%d"))
    UPLOAD_FOLDER = UPLOAD_FOLDER+uploadDay
    try:
        os.makedirs(UPLOAD_FOLDER)
    except FileExistsError:
        # directory already exists
        return UPLOAD_FOLDER
    return UPLOAD_FOLDER

# check if file in allowed extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploadexcel', methods=['POST', 'GET'])
def upload_file():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # check if the post request has the file part

        if 'file' not in request.files:
            flash('Upload Error', 'upload')
            flash('No file part', 'upload')
            return redirect(url_for('inventory'))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Upload Error', 'upload')
            flash('No selected file', 'upload')
            return redirect(url_for('inventory'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            UPLOAD_FOLDER = CreateNewDir()
            # HERE UPloaded excel
            try:
                lastRecoredId = "SELECT * FROM master_db ORDER BY id DESC LIMIT 1;"
                unqiueId = cursor.execute(lastRecoredId)
                selectResult = cursor.fetchone()
            except:
                flash('System', 'upload')
                flash('master_db table is not exist', 'upload')
                return redirect(url_for('inventory'))

            file_extension = ""
            try:
                file_extension = "file" + str(selectResult[0]) + "_"
            except:
                file_extension = ""

            try:
                filename = file_extension + filename
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                empty_sheet_test = pd.read_excel(file_path)
                # check if sheet empty remove it and redirect with message
                if empty_sheet_test.empty:
                    os.remove(file_path)
                    flash('System', 'upload')
                    flash('A blank excel sheet is not loaded, please upload a valid excel sheet', 'upload')
                    return redirect(url_for('inventory'))
                else:
                    file_namedb = filename.split('.')[0]
            except:
                flash('System', 'upload')
                flash('Could Not Upload Excel FIle Make sure file not opened', 'upload')
                return redirect(url_for('inventory'))

            """DROP
            insertSheetQuery = "DROP TABLE master_db;"
            insertSheetQuery1 = "DROP TABLE worksheets;"
            sheetQuery = cursor.execute(insertSheetQuery);
            sheetQuery = cursor.execute(insertSheetQuery1);
            """

            # Insert Sheet Query In Master DB
            filerealname = functions.riskVar(filename)
            insertSheetQuery = "INSERT INTO master_db (filename, file_path, realname) VALUES ('%s' , '%s', '%s') RETURNING id, file_path;"%(file_namedb, file_path, filerealname)
            sheetQuery = cursor.execute(insertSheetQuery);
            sheetQueryResult = cursor.fetchone()
            sheet_id = int(sheetQueryResult[0])
            sheet_path = sheetQueryResult[1]

            # Get All Sheets uploaded
            sheetHandler = pd.ExcelFile(sheet_path)
            worksheetsList = sheetHandler.sheet_names

            uploaded_sheets = []
            # read sheets one by one
            for worksheet in worksheetsList:
                df = pd.read_excel(sheet_path, sheet_name=worksheet)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                dataframe = pd.DataFrame(df)
                if df.empty:
                    continue
                # HERE CREATE TABLES STEP
                sheetLastIdString = "SELECT * FROM master_db ORDER BY id DESC LIMIT 1;"
                sheet_unqiueId = ""
                try:
                    sheetLastIdQuery = cursor.execute(sheetLastIdString)
                    sheetLastIdResult = cursor.fetchone()
                    sheet_unqiueId = str(sheetLastIdResult[0])
                except:
                    sheet_unqiueId = "1"
                # create NEw TABLE QUERY
                tablename = "sheet" + sheet_unqiueId + "_" + functions.filterVar(functions.betterVar(worksheet))
                column_names = [functions.filterVar(functions.betterVar(column)) for column in dataframe.columns]
                # here there was a table with only titles So no insert query
                """
                checkOk = []
                for i, row in df.iterrows():
                    for j, column in row.iteritems():
                        print(column)
                        checkOk.append(str(column) + '<br /><br /><br />')
                    return str(checkOk)
                """

                queryString = "CREATE TABLE IF NOT EXISTS %s (id serial PRIMARY KEY ,"%tablename
                for column in range(len(column_names)):
                    columnName = column_names[column]
                    if column == len(column_names) -1:
                        queryString += " %s TEXT NULL " %columnName
                    else:
                        queryString += " %s TEXT NULL, " %columnName
                queryString += ");"
                cursor.execute(queryString)
                if int(dataframe.size) == len(dataframe.columns):
                    continue

                # insert statment loop over dataframe and insert values
                if len(column_names) == 1:
                    columnsTitles = "(" + column_names[0] + ")"
                else:
                    tupleRow = tuple(column_names)
                    columnsTitles = str(tupleRow).replace("'", "")

                tupleRow = tuple(column_names)
                tuplelist = []
                lastindex = len(column_names) - 1
                insertQuery = "INSERT INTO " + tablename + " " + columnsTitles +  " VALUES "
                for i, row in df.iterrows():
                    loopindex = 0
                    insertQuery += "("
                    for j, column in row.iteritems():
                        if lastindex != loopindex:
                            insertQuery += "'%s', "
                        else:
                            insertQuery += "'%s'"
                        if str(column) == "nan":
                            tuplelist.append(' ')
                        else:
                            tuplelist.append(column)
                        loopindex += 1
                    insertQuery += "), "

                insertQuery = insertQuery[0:len(insertQuery)-2]
                insertQuery += ";"
                tupleTuple = tuple(tuplelist)

                theInsertQuery = insertQuery%tupleTuple
                cursor.execute(theInsertQuery)

                # Here Insert worksheets in worksheets tables MAIN TABLE
                sheetrealname = functions.riskVar(worksheet)
                column_namesString = ','.join(str(e) for e in column_names)
                insertWorkSheetQuery = "INSERT INTO worksheets (file_id, file_name, sheet_name, file_path, real_name, columns) VALUES (%s, '%s', '%s', '%s', '%s', '%s') RETURNING id;"%(sheet_id, file_namedb, tablename, file_path, sheetrealname, column_namesString)
                insertWorkSheetResult = cursor.execute(insertWorkSheetQuery)
                workSheetFetch = cursor.fetchone()
                worksheetid = workSheetFetch[0]
                uploaded_sheets.append(worksheetid)
            flash('Success', 'upload')
            success_message = 'Sheet Path %s'%file_path
            flash(success_message, 'upload')
            return redirect(url_for('inventory'))
        else:
            flash('Upload Error','upload')
            flash('The uploaded file does not have a valid Excel extension', 'upload')
    return redirect(url_for('inventory'))

# route that render the seet
perPage = 10000
@app.route('/table_data/<int:sheet_id>/<int:page>/<string:column_name>/<string:order_type>')
def renderTableData(sheet_id, page, column_name, order_type):
    if 'user' not in session:
        return redirect(url_for('login'))
    if page == 0:
        page = 1
    if request.args.get("perpage"):
        perPage = int(request.args.get("perpage"))

    requestOffset = page * perPage - perPage
    # return str(requestOffset) +  " " + str(requestLimit)
    sheet_data = functions.returnSheetForGivinId(sheet_id, requestOffset, perPage, page, column_name, order_type)
    code = 200
    message = "successful request"
    if not sheet_data['columns']:
        code = 404
        message = "not found or empty sheet"

    resObject = {'titles':sheet_data['columns'], 'rows':sheet_data['sheet_list']}
    return jsonify({
                    'code': code,
                    'message': message,
                    'name': sheet_data['name'],
                    'total': sheet_data['total'],
                    'table': sheet_data['table'],
                    'odrer_type': order_type,
                    'order_by': column_name,
                    'data':resObject
                    })


@app.route('/download_csv/<int:sheet_id>/<string:column_name>/<string:order_type>')
def showtest(sheet_id, column_name, order_type):
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        sheet_data = functions.returnSheetForGivinId(sheet_id, 0, 0, 0, column_name, order_type, True)
        rowList = []
        oneList = []
        for title in sheet_data['columns']:
            oneList.append(title)
        oneList = tuple(oneList)
        rowList.append(oneList)

        for row in sheet_data['sheet_list']:
            tupleRow = tuple(row)
            rowList.append(tupleRow)

        pdf = pd.DataFrame(rowList)
        zipFilePath = createDownloadFolder() + "\\" + sheet_data['table'] + ".zip"
        csvFileName = sheet_data['table'] + ".csv"
        compression_opts = dict(method='zip', archive_name=csvFileName)
        downloadNow = pdf.to_csv(zipFilePath, index=False, compression=compression_opts)
        realDownloadPath  = "static" + zipFilePath.split('static')[1]
        return jsonify({'code': 200, 'message': 'successful download request', 'path': realDownloadPath, 'filename': csvFileName})
    except:
        return jsonify({'code': 400, 'message': 'file could not be downloaded'})
    return str(done)


@app.route('/far')
def inventory():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        # setup postgres you can comment if you need after first run or leave it
        setupdb()
        # LIST Contains All Excel Files
        allfiles = functions.returnFileList()
        # List contains all excelwork sheets (Used in delete)
        allsheets = functions.returnWorksheetsList()
        sidebar = {'title': 'Autonet', 'menu': 'dashboard', 'submenu': ''}
        return render_template('inventory.html', session=session, sidebar=sidebar, allfiles=allfiles, allsheets=allsheets)

# route that will delete the excel file and all tables and recoreds for it + the excel file in the server
@app.route('/delete_excelfile', methods=['GET', 'POST'])
def delete_excelfile():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        delete_counter = 0
        fileToDeleteId = request.form.get('deleted_file')
        if fileToDeleteId == None:
            flash('danger', 'delete')
            flash('Your request could not be processed. Please select a file to delete.', 'delete')
            return redirect(url_for('inventory'))

        if fileToDeleteId == 'none':
            flash('danger', 'delete')
            flash('Your request could not be processed. Please select a file to delete.', 'delete')
            return redirect(url_for('inventory'))

        fileToDeleteId = int(fileToDeleteId)

        """
        insertSheetQuery = "DROP TABLE master_db;"
        insertSheetQuery1 = "DROP TABLE worksheets;"
        sheetQuery = cursor.execute(insertSheetQuery);
        sheetQuery = cursor.execute(insertSheetQuery1);
        """
        # delete the file from Server
        # get the filepath
        try:
            excelFileString = "SELECT file_path FROM master_db WHERE id=%s;"%fileToDeleteId
            excelFileQuery = cursor.execute(excelFileString)
            excelFilePathResult = cursor.fetchone()
            excelFilePath = excelFilePathResult[0]
            os.remove(excelFilePath)
        except:
            flash('danger', 'delete')
            flash('Could not delete Excel File from Server.', 'delete')
            return redirect(url_for('inventory'))

        # GET ALL worksheets for that file
        try:
            WorksheetsString = "SELECT id, sheet_name FROM worksheets WHERE file_id=%s;"%fileToDeleteId
            WorksheetsQuery = cursor.execute(WorksheetsString)
            WorksheetsResult = cursor.fetchall()
        except:
            flash('danger', 'delete')
            flash('Could not delete the Selected File Make sure it exist.')
            return redirect(url_for('inventory'))

        # delete all tables for that file
        try:
            for sheet_table in WorksheetsResult:
                deleteTableString = "DROP TABLE IF EXISTS %s;"%sheet_table[1]
                deleteTableQuery = cursor.execute(deleteTableString)
        except:
            flash('danger', 'delete')
            flash('Could not delete the Selected File Becuase the worksheets Problem1 Contact Developer.')
            return redirect(url_for('inventory'))

        # delete worksheets recoreds
        try:
            for worksheet_table in WorksheetsResult:
                deleteWorksheetString = "DELETE FROM worksheets WHERE id=%s"%worksheet_table[0]
                deleteWorkSheetQuery = cursor.execute(deleteWorksheetString)
                delete_counter += 1
        except:
            flash('danger', 'delete')
            flash('Could not delete the Selected File Becuase the worksheets Problem2 Contact Developer.')
            return redirect(url_for('inventory'))

        # DELETE excel file from master db
        try:
            excelFileStringDelete = "DELETE FROM master_db WHERE id=%s"%fileToDeleteId
            excelFileQuery = cursor.execute(excelFileStringDelete)
        except:
            flash('danger', 'delete')
            flash("Could not delete the File recored From System Database.")
            return redirect(url_for('inventory'))
        # here Every Thing is Fine and delete the file from system with all it's data and tabls
        flash('success', 'delete')
        flash("Congrats You deleted A file From a system that include %s worksheets"%delete_counter, "delete")
        return redirect(url_for('inventory'))

# this route will delete single worksheet Tip: if there only 1 sheet left in the file whole file will be deleted
@app.route('/delete_worksheet', methods=["GET", "POST"])
def delete_worksheet():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        sheet_id = request.form.get("worksheet_delete")
        if sheet_id == None or sheet_id == 'none':
            flash('danger', 'delete')
            flash('Your request could not be processed. Please select a sheet to delete.', 'delete')
            return redirect(url_for('inventory'))

        sheet_id = int(sheet_id)
        # GET worksheet data
        try:
            worksheetString = "SELECT id, file_id, sheet_name, file_path, real_name FROM worksheets WHERE id=%s;"%sheet_id
            worksheetQuery = cursor.execute(worksheetString)
            worksheetResult = cursor.fetchone()
        except:
            flash('danger', 'delete')
            flash('Your request could not be processed. The worksheet could not be found.', 'delete')
            return redirect(url_for('inventory'))

        # GET File ID and path
        try:
            excelFileString = "SELECT id, file_path FROM master_db WHERE id=%s;"%worksheetResult[1]
            excelFileQuery = cursor.execute(excelFileString)
            excelFileResult = cursor.fetchone()
        except:
            flash('danger', 'delete')
            flash('Your request could not be processed. Excel file could not be found.', 'delete')
            return redirect(url_for('inventory'))

        # Get all the other worksheets in the file
        try:
            otherWorksheetsString = "SELECT id FROM worksheets WHERE file_id=%s AND id <> %s;"%(worksheetResult[1], sheet_id)
            otherWorksheetsQuery = cursor.execute(otherWorksheetsString)
            otherWorksheetsResult = cursor.fetchall()
        except:
            flash('danger', 'delete')
            flash('Your request could not be processed. Error (3) was found on the server Contact the developer.', 'delete')
            return redirect(url_for('inventory'))

        if not otherWorksheetsResult:
            try:
                excelFilePath = excelFileResult[1]
                os.remove(excelFilePath)
                excelFileDeleteString = "DELETE FROM master_db WHERE id=%s;"%worksheetResult[1]
                excelFileDeleteQuery = cursor.execute(excelFileDeleteString)
            except:
                flash("danger", "delete")
                flash("The Excel file for this worksheet could not be found.", "delete")
                return redirect(url_for('inventory'))
        else:
            worksheetRealName = functions.rishVarReverse(worksheetResult[4])
            try:
                workbook=openpyxl.load_workbook(worksheetResult[3])
                std=workbook.get_sheet_by_name(worksheetRealName)
                workbook.remove_sheet(std)
                workbook.save(worksheetResult[3])
            except KeyError:
                flash("danger", "delete")
                flash("The selected worksheet could not be deleted from Excel Book.", "delete")
                return redirect(url_for('inventory'))

        # delete the worksheet table
        try:
            worksheetTableString = "DROP TABLE IF EXISTS %s;"%worksheetResult[2]
            worksheetTableQuery = cursor.execute(worksheetTableString)
        except:
            flash("danger", "delete")
            flash("The selected worksheet Table could not be deleted.", "delete")
            return redirect(url_for('inventory'))

        # delete the worksheet recored from workseets
        try:
            worksheetRecoredString = "DELETE FROM worksheets WHERE id=%s;"%worksheetResult[0]
            worksheetRecoredQuery = cursor.execute(worksheetRecoredString)
        except:
            flash("danger", "delete")
            flash("WorkSheet Recored Could not be deleted.", "delete")
            return redirect(url_for('inventory'))

        flash("success", "delete")
        flash("The worksheet has been successfully deleted from the system.", "delete")
        return redirect(url_for('inventory'))

    return redirect(url_for('inventory'))

# route to get the sheets in the file
@app.route('/getsheets/<int:sheetid>', methods=["GET"])
def getSheets(sheetid):
    if 'user' not in session:
        return redirect(url_for('login'))
    sheets_list = functions.returnSheetsForGivinFile(sheetid)
    code = 200
    message = "successful request"
    if not sheets_list:
        code = 404
        message = "No worksheets could be found for this file in the system."
    return jsonify({'code':code, 'message':message, 'data':sheets_list})

@app.route("/update_cell", methods=["POST"])
def updateCell():
    if request.method == "POST":
        code = None
        message = ""
        rtable = None
        rcolumn = None
        rvalue = None
        rid = None
        updateDbRequest = None
        req_data = request.get_json()
        if req_data:
            rtable = req_data['table']
            rcolumn = req_data['column']
            rvalue = req_data['value']
            rid = req_data['id']
            try:
                updateDbRequest = functions.updateThisCell(rtable, rcolumn, rvalue, rid)
            except:
                code = 400
                message = "Bad Request"
                return jsonify({'code':code, 'message':message, 'id':rid, 'value':rvalue})
        else:
            code = 400
            message = "Bad Request"
            return jsonify({'code':code, 'message':message, 'id':rid, 'value':rvalue})


        if updateDbRequest:
            code = 200
            message = "successful request"
            return jsonify({'code':code, 'message':message, 'id':rid, 'value':rvalue})
        else:
            code = 404
            message = "Sorry Could not update the cell."
            return jsonify({'code':code, 'message':message, 'id':rid, 'value':rvalue})
    else:
        return jsonify({code:405, 'message': 'method is not allowed'}, 405)

@app.route('/delete_row', methods=['POST'])
def deletRow():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        row_id = None
        tablename = None
        code = None
        message = ""
        request_data = request.get_json()
        if request_data:
            row_id = request_data['id']
            tablename = request_data['table']
            delete_request = functions.deleteThisRow(tablename, row_id)
            if delete_request:
                # Here the row is deleted
                code = 200
                message = "Successful delete request"
                return jsonify({'code': code, 'message': message, 'id': row_id})
            else:
                code = 404
                message = "row is not found"
                return jsonify({'code': code, 'message': message, 'id': row_id})
        else:
            code = 400
            message = "Bad request"
            return jsonify({'code': code, 'message': message, 'id': row_id})
    else:
        return jsonify({'code': 405, 'message': 'Method is not allowed'}, 405)

@app.route('/insert_row_after', methods=['POST'])
def insertAfter():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        request_data = request.get_json()
        if not request_data:
            return jsonify({'code':400, 'message':'bad request'})
        else:
            tablename = request_data['tablename']
            current_id = request_data['current_id']
            column_names = request_data['column_names']
            values = request_data['values']

            insertAfterNow = functions.insertRowAfter(tablename, current_id, column_names, values)
            if insertAfterNow:
                return jsonify({'code':200, 'message':'successful request', 'success': insertAfterNow})
            else:
                return jsonify({'code':400, 'message':'Crtical Error contact developer'})


@app.route('/insert_row_before', methods=['POST'])
def insertBefore():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        request_data = request.get_json()
        if not request_data:
            return jsonify({'code':400, 'message':'bad request'})
        else:
            tablename = request_data['tablename']
            current_id = request_data['current_id']
            column_names = request_data['column_names']
            values = request_data['values']

            insertBeforeNow = functions.insertRowBefore(tablename, current_id, column_names, values)
            if insertBeforeNow:
                return jsonify({'code':200, 'message':'successful request', 'success': insertBeforeNow})
            else:
                return jsonify({'code':400, 'message':'Crtical Error contact developer'})

# route for normal insert at the end
@app.route('/insert_into', methods=['POST'])
def insertIntoFun():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        request_data = request.get_json()
        if not request_data:
            return jsonify({'code':400, 'message':'bad request'})
        else:
            tablename = request_data['tablename']
            column_names = request_data['column_names']
            values = request_data['values']

            insertNow = functions.insertInto(tablename, column_names, values)
            if insertNow:
                return jsonify({'code':200, 'message':'successful request', 'success': insertNow})
            else:
                return jsonify({'code':400, 'message':'Crtical Error contact developer'})

# Inventory Code End 8/9/2021

@app.route('/')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        sidebar = {'title': 'Autonet', 'menu': 'dashboard', 'submenu': ''}
        return render_template('dashboard.html', session=session, sidebar=sidebar)


@app.route('/pdc')
def pdc():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        sidebar = {'title': 'Autonet', 'menu': 'pdc', 'submenu': ''}
        return render_template('pdc.html', session=session, sidebar=sidebar)

@app.route('/ash')
def ash():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        sidebar = {'title': 'Autonet', 'menu': 'ash', 'submenu': ''}
        return render_template('ash.html', session=session, sidebar=sidebar)

@app.route('/mpls')
def mpls():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        sidebar = {'title': 'Bgp & Color', 'menu': 'mpls', 'submenu': ''}
        return render_template('/mpls.html', session=session, sidebar=sidebar)


@app.route('/nettools')
def nettools():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        sidebar = {'title': 'Autonet', 'menu': 'nettools', 'submenu': ''}
        return render_template('nettools.html', session=session, sidebar=sidebar)


@app.route('/netmikoroute', methods=['POST', 'GET'])
def netmikoroute():
    if request.method == 'GET':
        return render_template('nettools.html')
    else:
        routing = request.form['routing']
        print(routing)
        return render_template('nettools.html')



@app.route('/security')
def security():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        sidebar = {'title': 'Autonet', 'menu': 'security', 'submenu': ''}
        return render_template('security.html', session=session, sidebar=sidebar)


@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        if not session['user'][3] == 1:
            return redirect(url_for('error404'))
        table_names = functions.get_table_names()
        pci_rows = functions.get_pci()
    records = functions.get_record_time()
    sidebar = {'title': 'Autonet', 'menu': 'settings', 'submenu': 'admin'}
    return render_template('admin.html', session=session, sidebar=sidebar, db_rows=pci_rows, table_names=table_names)


@app.route('/admin-xml', methods=['POST', 'OPTIONS'])
def admin_xml():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'You are not logged in'})
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers
        try:
            try:
                file = request.files['xml_file']
                xml_json_flag = 'xml'
            except Exception as xml_error:
                print("xml_error: ", xml_error)
                try:
                    file = request.files['json_file']
                    xml_json_flag = 'json'
                except Exception as json_error:
                    print('json_error: ', json_error)
                    return jsonify({'status': 'error', 'message': 'File is not selected'})
            if not file or not file.filename:
                return jsonify({'status': 'error', 'message': 'File is not selected'})
            print(file.filename)
            table_name = request.form['table_name']
            table_keys = json.loads(request.form['table_keys'])
            table_fields = json.loads(request.form['table_fields'])
            print("table info: ", xml_json_flag, table_name, table_keys, table_fields)
            filename = os.path.join(uploads_dir, file.filename)
            file.save(filename)
            print(filename)
            with open(filename) as file_data:
                if xml_json_flag == 'xml':
                    data_dict = xmltodict.parse(file_data.read())
                elif xml_json_flag == 'json':
                    # json_dump = json.dumps(file_data)
                    data_dict = json.load(file_data)
                else:
                    return jsonify({'status': 'error', 'message': 'Undefined file format'})
                file_data.close()
                # print(data_dict)
                check_vrf = ''
                try:
                    vr_data = functions.custom_find_key(vr_key, data_dict)
                except Exception as error:
                    print("vr_data error: ", error)
                    check_vrf = 'N/A'
                    vr_data = []
                try:
                    int_data = functions.custom_find_key(int_key, data_dict)
                except Exception as error:
                    print("int_data error: ", error)
                    int_data = data_dict['TABLE_intf']['ROW_intf']
                conn = sqlite3.connect('database.db')
                cur = conn.cursor()
                table_name = table_name.replace('-', '_')
                cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='" + table_name + "'")
                check_table = cur.fetchone()
                if check_table[0] == 1 or check_table[0] == '1':
                    print("Table already exist")
                    return jsonify({'status': 'error', 'message': 'Table already exist'})
                else:
                    create_table_sql = 'CREATE TABLE ' + table_name + '(id INT NOT NULL, IP CHAR(256), Location CHAR(256), VRF CHAR(256), '
                    for item in table_fields:
                        create_table_sql += item + " CHAR(256), "
                    create_table_sql = create_table_sql[:-2]
                    create_table_sql += ")"
                    cur.execute(create_table_sql)
                    # conn.commit()
                print("check_vrf: ", check_vrf)
                print("int_data: ", int_data)
                print("len(int_data): ", len(int_data))
                for i in range(len(int_data)):
                    if check_vrf != 'N/A':
                        vr_item = vr_data[i]['ROW_vrf']
                        item_vrf = vr_item['vrf-name-out']
                        int_item = int_data[i]['ROW_intf']
                    else:
                        int_item = int_data[i]
                        item_vrf = int_item['vrf-name-out']
                    item_id = i
                    try:
                        item_ip = int_item['subnet'] + "/" + int_item['masklen']
                    except Exception as error:
                        print("error item_ip: ", error)
                        item_ip = 'N/A'
                    item_location = table_name.replace('_', ' ')
                    insert_sql = "INSERT INTO " + table_name + " (id, IP, Location, VRF"
                    for field_item in table_fields:
                        insert_sql += ", " + field_item
                    insert_sql += ")"
                    insert_sql += " VALUES (" + str(item_id) + ", '" + item_ip + "', '" + item_location + "', '" + item_vrf
                    for field_key in table_keys:
                        try:
                            insert_sql += "', '" + int_item[field_key]
                        except Exception as error:
                            print("error tag: ", error)
                            insert_sql += "', '" + 'N/A'
                    insert_sql += "')"
                    print(insert_sql)
                    cur.execute(insert_sql)
                    conn.commit()
                functions.db_record_time(table_name)
            return jsonify({'status': 'success', 'message': 'success added table', 'vr_data': vr_data, 'int_data': int_data}), 201
        except Exception as err:
            print("error: ", err)
            return jsonify({'status': 'error', 'message': 'Failed to upload file'})


@app.route('/admin-xml-2', methods=['POST', 'OPTIONS'])
def admin_xml_2():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'You are not logged in'})
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000,
            'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
        }
        return '', 200, headers
    try:
        file = request.files['xml_file']
        xml_json_flag = 'xml'
    except Exception as xml_error:
        print("xml_error: ", xml_error)
        try:
            file = request.files['json_file']
            xml_json_flag = 'json'
        except Exception as json_error:
            print('json_error: ', json_error)
            return jsonify({'status': 'error', 'message': 'File is not selected'})
    if not file or not file.filename:
        return jsonify({'status': 'error', 'message': 'File is not selected'})
    table_name = request.form['table_name']
    exclude_vrf = request.form['exclude_vrf']
    exclude_ipnexthop = request.form['exclude_ipnexthop']
    map_ipnexthop = request.form['map_ipnexthop']
    table_keys = json.loads(request.form['table_keys'])
    table_fields = json.loads(request.form['table_fields'])
    filename = os.path.join(uploads_dir, file.filename)
    file.save(filename)
    table_name = table_name.replace('-', '_').strip()
    rt_res = functions.rt_to_db(xml_json_flag, filename, table_name, exclude_vrf, exclude_ipnexthop, map_ipnexthop, table_keys, table_fields)
    if rt_res['status'] == 'error':
        return jsonify(rt_res)
    return jsonify({'status': 'success', 'message': 'success added table'}), 201


@app.route('/search-ip', methods=['POST', 'OPTIONS'])
def search_nettools():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'You are not logged in'})
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers

        ip_array = request.get_json()['ip_array']
        dbs = ['PDC_DCS_PRD_DSW1_CONNECTED', 'PDC_DCS_PRD_DSW2_CONNECTED', 'PDC_DCS_STG_DSW1_CONNECTED', 'PDC_DCS_STG_DSW2_CONNECTED', 'PDC_DCW_DSW1_CONNECTED', 'PDC_DCW_DSW2_CONNECTED', 'PDC_DCI_SW01_CONNECTED', 'PDC_DCI_SW02_CONNECTED', 'PDC_DCI_SW03_CONNECTED', 'PDC_DCI_SW04_CONNECTED',
               'PDC_DCS_PRD_DSW1', 'PDC_DCS_PRD_DSW2', 'PDC_DCS_STG_DSW1', 'PDC_DCS_STG_DSW2', 'PDC_DCW_DSW1', 'PDC_DCW_DSW2', 'PDC_DCI_SW01', 'PDC_DCI_SW02', 'PDC_DCI_SW03', 'PDC_DCI_SW04',
               'CDC_DCS_PRD_DSW1_CONNECTED', 'CDC_DCS_PRD_DSW2_CONNECTED', 'CDC_DCS_STG_DSW1_CONNECTED', 'CDC_DCS_STG_DSW2_CONNECTED', 'CDC_DCW_DSW1_CONNECTED', 'CDC_DCW_DSW2_CONNECTED', 'CDC_DCI_SW01_CONNECTED', 'CDC_DCI_SW02_CONNECTED', 'CDC_DCI_SW03_CONNECTED', 'CDC_DCI_SW04_CONNECTED',
			   'CDC_DCS_PRD_DSW1', 'CDC_DCS_PRD_DSW2', 'CDC_DCS_STG_DSW1', 'CDC_DCS_STG_DSW2', 'CDC_DCW_DSW1', 'CDC_DCW_DSW2', 'CDC_DCI_SW01', 'CDC_DCI_SW02', 'CDC_DCI_SW03', 'CDC_DCI_SW04',
               'PHX_DCS_DSW1_CONNECTED', 'PHX_DCS_DSW2_CONNECTED', 'PHX_DCW_DSW1_CONNECTED', 'PHX_DCW_DSW2_CONNECTED',
               'PHX_DCS_DSW1', 'PHX_DCS_DSW2', 'PHX_DCW_DSW1', 'PHX_DCW_DSW2',
               'DFW_DCW_DSW1_CONNECTED', 'DFW_DCW_DSW2_CONNECTED', 'DFW_DCW_BSW01_CONNECTED', 'DFW_DCW_BSW02_CONNECTED', 'DFW_DCW_BSW03_CONNECTED', 'DFW_DCW_BSW04_CONNECTED', 'DFW_DCW_LSW01_CONNECTED',
               'DFW_DCW_DSW1', 'DFW_DCW_DSW2', 'DFW_DCW_BSW01', 'DFW_DCW_BSW02', 'DFW_DCW_BSW03', 'DFW_DCW_BSW04', 'DFW_DCW_LSW01',
               'ASH_SW01_CONNECTED', 'ASH_SW02_CONNECTED', 'ASH_NX01_CONNECTED', 'ASH_NX02_CONNECTED', 'ASH_SW05_CONNECTED', 'ASH_SW06_CONNECTED',
               'ASH_SW01', 'ASH_SW02', 'ASH_NX01', 'ASH_NX02', 'ASH_SW05', 'ASH_SW06',
               'SJC_SW01_CONNECTED', 'SJC_SW02_CONNECTED', 'SJC_NX01_CONNECTED', 'SJC_NX02_CONNECTED', 'SJC_SW05_CONNECTED', 'SJC_SW06_CONNECTED',
               'SJC_SW01', 'SJC_SW02', 'SJC_NX01', 'SJC_NX02', 'SJC_SW05', 'SJC_SW06',
                #IF NOT FOUND ON ABOVE DB's SEARCH THIS DB
               'UVN'
              ]
        search_ips = functions.func_search_ip(ip_array, dbs)
        return jsonify({'status': 'success', 'message': search_ips})




@app.route('/manage-pci', methods=['POST', 'OPTIONS'])
def manage_pci():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'You are not logged in'})
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers
        method_type = request.get_json()['method_type']
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                if method_type == 'add':
                    item_ip = request.get_json()['ip']
                    item_status = request.get_json()['status']
                    insert_id = 1
                    last_sql = "SELECT * FROM DC_PCI ORDER BY id DESC LIMIT 1"
                    cur.execute(last_sql)
                    last_item = cur.fetchall()
                    if len(last_item) > 0:
                        insert_id = last_item[0][0] + 1
                    insert_sql = "INSERT INTO DC_PCI(id, IP, STATUS) VALUES (" + str(insert_id) + ", '" + item_ip + "', '" + item_status + "')"
                    cur.execute(insert_sql)
                    conn.commit()
                    functions.db_record_time('DC_PCI')
                elif method_type == 'edit':
                    item_id = request.get_json()['id']
                    item_ip = request.get_json()['ip']
                    item_status = request.get_json()['status']
                    update_sql = "UPDATE DC_PCI SET IP = '" + item_ip + "', STATUS = '" + item_status + "' WHERE id = '" + item_id + "'"
                    cur.execute(update_sql)
                    conn.commit()
                    functions.db_record_time('DC_PCI')
                elif method_type == 'remove':
                    item_id = request.get_json()['id']
                    delete_sql = "DELETE FROM DC_PCI WHERE id = " + item_id
                    cur.execute(delete_sql)
                    conn.commit()
                    functions.db_record_time('DC_PCI')
                else:
                    return jsonify({'status': 'error', 'message': 'Undefined method'})
        except Exception as error:
            print(error)
            conn.rollback()
        finally:
            conn.close()

        return jsonify({'status': 'success', 'message': 'updated success'})


@app.route('/remove-table', methods=['POST', 'OPTIONS'])
def remove_table():
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'You are not logged in'})
    else:
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Max-Age': 1000,
                'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
            }
            return '', 200, headers
        table_name = request.get_json()['table_name']
        conn = sqlite3.connect(database='database.db')
        cursor = conn.cursor()
        drop_sql = "DROP TABLE " + table_name
        cursor.execute(drop_sql)
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': "Removed a table successfully"})


@app.route('/upload-pci', methods=['POST', 'OPTIONS'])
def upload_pci():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Max-Age': 1000,
            'Access-Control-Allow-Headers': 'origin, x-csrftoken, content-type, accept',
        }
        return '', 200, headers
    try:
        file = request.files['pci_file']
    except Exception as pci_error:
        print("pci_error: ", pci_error)
        return jsonify({'status': 'error', 'message': 'Failed to upload file'})
    filename = os.path.join(uploads_dir, file.filename)
    file.save(filename)
    print(filename)
    functions.excel_database(filename, 'DC_PCI')
    return jsonify({'status': 'success', 'message': 'success added table'}), 201


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('dashboard'))
        return render_template('login.html')
    else:
        email = request.form['email']
        pwd = request.form['pwd']
        print(email)
        if email == '' or pwd == '':
            return render_template('login.html', email=email, pwd=pwd)
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM user WHERE email = ?", (email,))
                users = cur.fetchall()
                if len(users) < 1:
                    print("doesn't exist")
                    return redirect(url_for('login'))
                user = users[0]
                stored_pwd = user[4]
                if not pwd_hasher.verify_password(stored_pwd, pwd):
                    print('wrong password')
                    return redirect(url_for('login'))
                print("Login success")
                session['user'] = user
                print('login ok')
        except sqlite3.Error as e:
            print(e)
            conn.rollback()
        finally:
            print("finally")
            conn.close()
        return redirect(url_for('dashboard'))


@app.route('/user-manage', methods=['POST', 'GET'])
def user_management():
    if request.method == 'GET':
        if 'user' not in session:
            return redirect(url_for('login'))
        if not session['user'][3] == 1:
            return redirect(url_for('error404'))
        if session['user'][3] != 1:
            return redirect(url_for('error404'))
        sidebar = {'title': 'User Management', 'menu': 'settings', 'submenu': 'user-manage'}
        users = functions.db_manage_user('all', 'none', 'none')
        return render_template('user_management.html', session=session, sidebar=sidebar, users=users)
    else:
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': 'You are not logged in'})
        if session['user'][3] != 1:
            return jsonify({'status': 'error', 'message': 'Permission is not defined'})
        method_type = request.get_json()['method_type']
        if method_type == 'edit':
            user_id = request.get_json()['user_id']
            user_role = request.get_json()['user_role']
            functions.db_manage_user('edit', user_id, user_role)
            return jsonify({'status': 'success', 'message': 'User is updated successfully'})
        elif method_type == 'remove':
            user_id = request.get_json()['user_id']
            functions.db_manage_user('remove', user_id, 'none')
            return jsonify({'status': 'success', 'message': 'User is removed successfully'})


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('dashboard'))
        return render_template('register.html')
    else:
        email = request.form['email']
        name = request.form['name']
        pwd = pwd_hasher.hash_password(request.form['pwd'])
        # user role
        role = 2
        try:
            with sqlite3.connect(database='database.db') as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO user (name, email, role, pwd) VALUES (?, ?, ?, ?)",
                            (name, email, role, pwd))
                conn.commit()
            functions.db_record_time('user')
        except:
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('login'))


@app.route('/404', methods=['GET'])
def error404():
    return "Not found page"


if __name__ == '__main__':
    # app.secret_key = 'ffce805ea02504f5a59820c1ea8985e0432f39566059d7f8'
    # app.secret_key = "random string"
    app.run('0.0.0.0', port=5001) #port can be anything higher than 5000.
