from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import create_engine
import mysql.connector
import MySQLdb
from .forms import LoginForm
from django.contrib import messages

hostname = 'localhost'
engine_hbi = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/danhsachdaotao', echo=False)
mydb = mysql.connector.connect(host=hostname, user='root', passwd='123456', database="htsystem_data")
myCursor = mydb.cursor()

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username == 'phhoan11' and password == 'Phubai123':
                return redirect('homepage')  # Replace 'homepage' with the name of your homepage URL pattern
            else:
                messages.error(request, 'Invalid user, check your ID and password.')
    else:
        form = LoginForm()
    return render(request, 'login_page.html', {'form': form})


def display_training_data(request):
    myCursor.execute("SELECT * FROM training_data")
    result = myCursor.fetchall()
    context = {'data': result}
    return render(request, 'homepage', context)
#
# def search(request):
#     query = request.GET.get('q', '')
#     if query:
#         myCursor.execute(f"SELECT * FROM training_data WHERE Name LIKE '%{query}%'")
#         rows = myCursor.fetchall()
#     else:
#         rows = []
#     return render(request, 'search.html', {'rows': rows, 'query': query})
#
# @csrf_exempt
# def add_employee(request):
#     if request.method == 'POST':
#         id = request.POST['id']
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
#         sql = "INSERT INTO training_data (ID, Name, Line, Shift, Plant, Operation, Type_training, Week_start, Week_end, Technician, StartDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#         val = (id, name, line, shift, plant, operation, type_training, week_start, week_end, technician, start_date)
#         myCursor.execute(sql, val)
#         mydb.commit()
#         return redirect('index')
#     return render(request, 'add_employee.html')
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
