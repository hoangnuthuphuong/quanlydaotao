from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import create_engine
import mysql.connector
from .forms import SearchForm
from django.contrib import messages
from django.db import connection
import pandas as pd

hostname = 'localhost'
engine_hbi = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/danhsachdaotao', echo=False)
mydb = mysql.connector.connect(host=hostname, user='root', passwd='123456', database="htsystem_data")
myCursor = mydb.cursor()


def display_training_data(request):
    sql = "SELECT * FROM training_data"
    training_data = pd.read_sql(sql, mydb)
    training_data = training_data.to_dict(orient='records')
    context = {'training_data': training_data}
    return render(request, 'employee_data.html', context)


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
    return render(request, 'search.html', context)



def edit_data(request, id):
    # Fetch existing data
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM training_data WHERE ID = %s", [id])
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        if row is None:
            messages.error(request, 'Record not found.')
            return redirect('search')

        record = dict(zip(columns, row))

    if request.method == 'POST':
        # Read form data
        data = {
            'ID': request.POST.get('ID'),
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
            data['Type_training'], data['Week_start'], data['Week_end'], data['Technician'],
            data['StartDate'], id
        )

        with connection.cursor() as cursor:
            cursor.execute(update_query, params)

        messages.success(request, 'Data updated successfully!')
        return redirect('search')

    context = {'record': record}
    return render(request, 'edit.html', context)


# The rest of your views...


@csrf_exempt
def add_employee(request):
    if request.method == 'POST':
        id = request.POST['id']
        name = request.POST['name']
        line = request.POST['line']
        shift = request.POST['shift']
        plant = request.POST['plant']
        operation = request.POST['operation']
        type_training = request.POST['type_training']
        week_start = request.POST['week_start']
        week_end = request.POST['week_end']
        technician = request.POST['technician']
        start_date = request.POST['start_date']

        sql = "INSERT INTO training_data (ID, Name, Line, Shift, Plant, Operation, Type_training, Week_start, Week_end, Technician, StartDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (id, name, line, shift, plant, operation, type_training, week_start, week_end, technician, start_date)
        myCursor.execute(sql, val)
        mydb.commit()
        return redirect('index')
    return render(request, 'add_employee.html')
#
# @csrf_exempt
# def edit_employee(request, employee_id):
#     if request.method == 'POST':
#         name = request.POST['name']
#         line = request.POST['line']
#         shift = request.POST['shift']
#         plant = request.POST['plant']
#         operation = request.POST['operation']
#         type_training = request.POST['type_training']
#         week_start = request.POST['week_start']
#         week_end = request.POST['week_end']
#         technician = request.POST['technician']
#         start_date = request.POST['start_date']
#
#         sql = f"UPDATE training_data SET Name=%s, Line=%s, Shift=%s, Plant=%s, Operation=%s, Type_training=%s, Week_start=%s, Week_end=%s, Technician=%s, StartDate=%s WHERE ID=%s"
#         val = (name, line, shift, plant, operation, type_training, week_start, week_end, technician, start_date, employee_id)
#         myCursor.execute(sql, val)
#         mydb.commit()
#         return redirect('index')
#
#     myCursor.execute("SELECT * FROM training_data WHERE ID = %s", (employee_id,))
#     employee = myCursor.fetchone()
#     return render(request, 'edit_employee.html', {'employee': employee})
