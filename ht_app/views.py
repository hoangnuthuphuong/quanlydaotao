from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import create_engine
import mysql.connector
from .forms import SearchForm, EditForm
from django.contrib import messages
from django.db import connection
import MySQLdb
import pandas as pd

hostname = 'localhost'
engine_hbi = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/htsystem_data', echo=False)
mydb = mysql.connector.connect(host=hostname, user='root', passwd='123456', database="htsystem_data")

myCursor = mydb.cursor()


def display_training_data(request):
    sql = "SELECT * FROM training_data"
    training_data = pd.read_sql(sql, mydb)
    training_data = training_data.to_dict(orient='records')
    context = {'training_data': training_data}
    return render(request, 'employee_data.html', context)


def edit_data(request, ID):
    # Fetch existing data
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM training_data WHERE ID = %s", [ID])
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        record = dict(zip(columns, row)) if row else None

    if not record:
        messages.error(request, 'Record not found.')
        return redirect('index')

    if request.method == 'POST':
        # Read form data
        data = {
            'Name': request.POST.get('Name'),
            'Line': request.POST.get('Line'),
            'Shift': request.POST.get('Shift'),
            'Plant': request.POST.get('Plant'),
            'Operation': request.POST.get('Operation'),
            'Type_training': request.POST.get('Type_training'),
            'Week_start': request.POST.get('Week_start'),
            'Week_end': request.POST.get('Week_end'),
            'Technician': request.POST.get('Technician'),
            'StartDate': request.POST.get('StartDate'),
        }

        # Update the data
        update_query = """
            UPDATE training_data
            SET Name = %s, Line = %s, Shift = %s, Plant = %s, Operation = %s,
                Type_training = %s, Week_start = %s, Week_end = %s, Technician = %s, StartDate = %s
            WHERE ID = %s
        """
        params = (
            data['Name'], data['Line'], data['Shift'], data['Plant'], data['Operation'],
            data['Type_training'], data['Week_start'], data['Week_end'], data['Technician'], data['StartDate'], ID
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
            messages.success(request, 'Data updated successfully!')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('edit_data', ID=ID)  # Redirect back to the index page

    context = {'record': record}
    return render(request, 'edit.html', context)


def search_data(request):
    form = SearchForm()
    filter_data = None

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data.get('id', '')
            startdate = form.cleaned_data.get('startdate', '')
            line = form.cleaned_data.get('line', '')
            shift = form.cleaned_data.get('shift', '')

            sql = "SELECT * FROM training_data WHERE 1=1"
            params = []

            if id:
                sql += " AND ID = %s"
                params.append(id)
            if startdate:
                sql += " AND StartDate = %s"
                params.append(startdate)
            if line:
                sql += " AND Line = %s"
                params.append(line)
            if shift:
                sql += " AND Shift = %s"
                params.append(shift)

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                filter_data = pd.DataFrame(rows, columns=columns)
                filter_data.rename(columns={
                    'ID': 'ID nhân viên',
                    'Name': 'Tên nhân viên',
                    'StartDate': 'Ngày bắt đầu',
                    'Line': 'Chuyền',
                    'Shift': 'Ca'
                }, inplace=True)
                filter_data = filter_data.to_dict(orient='records')

    context = {'form': form, 'filter_data': filter_data}
    return render(request, 'index.html', context)


def add_employee(request):
    if request.method == 'POST':
        new_id = request.POST.get('ID')

        # Check if the ID is already present in the database
        check_query = "SELECT COUNT(*) FROM training_data WHERE ID = %s"
        check_params = (new_id,)

        try:
            with connection.cursor() as cursor:
                cursor.execute(check_query, check_params)
                count = cursor.fetchone()[0]

                if count > 0:
                    messages.error(request, 'Employee with this ID already exists. Please enter a different ID.')
                    return render(request, 'add_employee.html')
                # If the ID is unique, proceed with inserting the new employee
                else:
                    data = {
                        'ID': new_id,
                        'Name': request.POST.get('Name'),
                        'Line': request.POST.get('Line'),
                        'Shift': request.POST.get('Shift'),
                        'Plant': request.POST.get('Plant'),
                        'Operation': request.POST.get('Operation'),
                        'Type_training': request.POST.get('Type_training'),
                        'Week_start': request.POST.get('Week_start'),
                        'Week_end': request.POST.get('Week_end'),
                        'Technician': request.POST.get('Technician'),
                        'StartDate': request.POST.get('StartDate'),
                    }

                    insert_query = '''
                        INSERT INTO training_data (ID, Name, Line, Shift, Plant, Operation,
                            Type_training, Week_start, Week_end, Technician, StartDate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    params = (
                        data['ID'], data['Name'], data['Line'], data['Shift'], data['Plant'], data['Operation'],
                        data['Type_training'], data['Week_start'], data['Week_end'], data['Technician'],
                        data['StartDate']
                    )

                    cursor.execute(insert_query, params)
                    connection.commit()
                    messages.success(request, 'Employee added successfully!')
                    return redirect('index')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    return render(request, 'add_employee.html')


# def upload_excel(request):
#     if request.method == 'POST' and request.FILES['excel_file']:
#         excel_file = request.FILES['excel_file']
#         try:
#             wb = openpyxl.load_workbook(excel_file)
#             sheet = wb.active
#             data_list = []
#
#             for row in sheet.iter_rows(min_row=2, values_only=True):  # Bỏ qua tiêu đề
#                 data = {
#                     'Name': row[0],
#                     'Line': row[1],
#                     'Shift': row[2],
#                     'Plant': row[3],
#                     'Operation': row[4],
#                     'Type_training': row[5],
#                     'Week_start': row[6],
#                     'Week_end': row[7],
#                     'Technician': row[8],
#                     'StartDate': row[9],
#                 }
#                 data_list.append(data)
#
#             insert_query = """
#                 INSERT INTO training_data (Name, Line, Shift, Plant, Operation,
#                     Type_training, Week_start, Week_end, Technician, StartDate)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#
#             with connection.cursor() as cursor:
#                 for data in data_list:
#                     cursor.execute(insert_query, tuple(data.values()))
#
#             messages.success(request, 'Employees added successfully from Excel file!')
#         except Exception as e:
#             messages.error(request, f"An error occurred: {e}")
#
#         return redirect('index')
#
#     return render(request, 'upload_excel.html')


from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import MySQLdb

conn = MySQLdb.connect(host=hostname, user='root', passwd='123456', database="htsystem_data")


def handle_nan_values(data):
    return data.where(pd.notnull(data), None)


import logging

# Khai báo logger
logger = logging.getLogger(__name__)


def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            return HttpResponse('File tải lên không phải là file Excel.')

        try:
            df = pd.read_excel(excel_file, engine='openpyxl')
            df['StartDate'] = df['StartDate'].fillna('00/00/0000')
            # df = handle_nan_values(df)
            df = df.fillna('')

            print(df)

            cursor = conn.cursor()

            for index, row in df.iterrows():
                ID = row['ID']
                cursor.execute("SELECT COUNT(*) FROM training_data WHERE ID = %s", [ID])
                count = cursor.fetchone()[0]

                if count == 0:
                    insert_query = '''
                        INSERT INTO training_data (ID, Name, Line, Shift, Plant, Operation,
                            Type_training, Week_start, Week_end, Technician, StartDate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    params = (
                        row['ID'], row['Name'], row['Line'], row['Shift'], row['Plant'], row['Operation'],
                        row['Type_training'], row['Week_start'], row['Week_end'], row['Technician'],
                        row['StartDate']
                    )

                    cursor.execute(insert_query, params)
                    conn.commit()

            cursor.close()
            conn.close()

            return HttpResponse('Dữ liệu từ file Excel đã được tải lên và chèn vào cơ sở dữ liệu MySQL thành công!')

        except Exception as e:
            conn.rollback()
            logger.error(f'Lỗi khi tải lên file Excel: {str(e)}')
            return HttpResponse('Có lỗi xảy ra khi tải lên file Excel. Vui lòng kiểm tra lại.')

    return render(request, 'upload_excel.html')
