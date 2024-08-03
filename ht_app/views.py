import MySQLdb
import mysql.connector
import pandas as pd
from django.contrib import messages
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from .forms import SearchForm

# hostname = 'localhost'
# engine_hbi = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/htsystem_data', echo=False)
# mydb = mysql.connector.connect(host=hostname, user='root', passwd='123456', database="htsystem_data")
# mydb = MySQLdb.connect(host=hostname, user='root', passwd='123456', database="htsystem_data")
# myCursor = mydb.cursor()

conn = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",
                               use_pure=False)
mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",
                               use_pure=False)
myCursor = mydb.cursor()

# sql = """
# INSERT INTO DAILY_EMPLOYEE_REPORT (id, Name, Line, Shift, Date, Eff, date_no_eff, total_work_hours, stop_hours, downtime ) VALUES ("241769, BUI QUANG HAO, Line 095, RIT, ")
# """



def display_training_data(request):
    sql = "SELECT * FROM training_data"
    mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",
                                   use_pure=False)
    training_data = pd.read_sql(sql, mydb)
    t = loader.get_template('employee_data.html')
    context = {
        'training_data': training_data
    }

    print(training_data)
    return HttpResponse(t.render(context, request))


def edit_data(request, ID):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM training_data WHERE ID = %s", [ID])
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        record = dict(zip(columns, row)) if row else None
        connection.commit()

    if not record:
        messages.error(request, 'Record not found.')
        return redirect('index')

    if request.method == 'POST':
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
                connection.commit()
            messages.success(request, 'Chỉnh sửa dữ liệu thành công!')
        except Exception as e:
            messages.error(request, f"Lỗi: {e}")
        return redirect('edit_data', ID=ID)
    context = {'record': record}
    return render(request, 'edit.html', context)


@csrf_exempt
def search_danhsach_nv_ajax(request):
    if request.method == 'POST':
        id = request.POST.get('idnv')
        line = request.POST.get('line')
        startdate = request.POST.get('startdate')
        shift = request.POST.get('shift')
        print(id, line, startdate, shift)

        sql_search = f"""
        select * from htsystem_data.training_data where 1=1
        """
        if id != '' and 'n' not in str(id):
            sql_search += f""" and id='{id}'"""
        if line != '':
            sql_search += f""" and line='{line}'"""
        if shift != '':
            sql_search += f""" and shift='{shift}'"""
        if startdate != '':
            sql_search += f""" and startdate='{startdate}'"""

        data_h = pd.read_sql(sql_search, engine_hbi)
        print(data_h)
        json_data = data_h.to_dict(orient='records')

        return JsonResponse({'data_table': json_data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


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
                filter_data = filter_data.to_dict(orient='records')

    context = {'form': form, 'filter_data': filter_data}
    return render(request, 'index.html', context)
    # return redirect('index')


def add_employee(request):
    if request.method == 'POST':
        new_id = request.POST.get('ID')
        check_query = "SELECT COUNT(*) FROM training_data WHERE ID = %s"
        check_params = (new_id,)

        try:
            with connection.cursor() as cursor:
                cursor.execute(check_query, check_params)
                count = cursor.fetchone()[0]

                if count > 0:
                    messages.error(request, 'Mã nhân viên này đã tồn tại. Thêm nhân viên khác!')
                    return render(request, 'add_employee.html')
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


# Hàm sửa các giá trị nan
def handle_nan_values(data):
    return data.where(pd.notnull(data), None)


import logging

logger = logging.getLogger(__name__)


def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            return HttpResponse('File tải lên không phải là file Excel.')
        try:
            df = pd.read_excel(excel_file, engine='openpyxl')
            # df['StartDate'] = df['StartDate'].fillna('00/00/0000')
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
            return HttpResponse('Dữ liệu đã được tải lên thành công!')
        except Exception as e:
            conn.rollback()
            logger.error(f'Lỗi khi tải lên file Excel: {str(e)}')
            return HttpResponse('Có lỗi xảy ra khi tải lên file. Vui lòng kiểm tra lại.')
    return render(request, 'upload_excel.html')


def upload_LC(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            return HttpResponse('File tải lên không phải là file Excel.')
        try:
            df = pd.read_excel(excel_file, engine='openpyxl')
            df = df.fillna('')
            print(df)
            cursor = conn.cursor()
            for index, row in df.iterrows():
                stt = row['stt']
                cursor.execute("SELECT COUNT(*) FROM duongcong WHERE stt = %s", [stt])
                count = cursor.fetchone()[0]

                if count == 0:
                    insert_query = '''
                        INSERT INTO duongcong (stt, operation, note, machine, thread, day1, day2, day3, day4, day5, day6, day7, day8, day9, day10, day11, day12, day13, day14, day15, day16, day17, day18, day19, day20, day21, day22, day23, day24, day25, day26, day27, day28, day29, day30, day31, day32, day33, day34, day35, day36, day37, day38, day39, day40, day41, day42, day43, day44, day45, day46, day47, day48, day49, day50, day51, day52, day53, day54, day55, day56, day57, day58, day59, day60, day61, day62, day63, day64, day65, day66, day67, day68, day69, day70, day71, day72, day73, day74, day75, day76, day77, day78)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    params = (
                        row['stt'], row['operation'], row['note'], row['machine'], row['thread'],
                        row['day1'], row['day2'], row['day3'], row['day4'], row['day5'], row['day6'], row['day7'],
                        row['day8'], row['day9'], row['day10'], row['day11'], row['day12'], row['day13'], row['day14'],
                        row['day15'], row['day16'], row['day17'], row['day18'], row['day19'], row['day20'],
                        row['day21'], row['day22'], row['day23'], row['day24'], row['day25'], row['day26'],
                        row['day27'], row['day28'], row['day29'], row['day30'], row['day31'], row['day32'],
                        row['day33'], row['day34'], row['day35'], row['day36'], row['day37'], row['day38'],
                        row['day39'], row['day40'], row['day41'], row['day42'], row['day43'], row['day44'],
                        row['day45'], row['day46'], row['day47'], row['day48'], row['day49'], row['day50'],
                        row['day51'], row['day52'], row['day53'], row['day54'], row['day55'], row['day56'],
                        row['day57'], row['day58'], row['day59'], row['day60'], row['day61'], row['day62'],
                        row['day63'], row['day64'], row['day65'], row['day66'], row['day67'], row['day68'],
                        row['day69'], row['day70'], row['day71'], row['day72'], row['day73'], row['day74'],
                        row['day75'], row['day76'], row['day77'], row['day78']
                    )

                    cursor.execute(insert_query, params)
                    conn.commit()

            cursor.close()
            conn.close()
            return HttpResponse('Dữ liệu đã được tải lên thành công!')
        except Exception as e:
            conn.rollback()
            logger.error(f'Lỗi khi tải lên file Excel: {str(e)}')
            return HttpResponse('Có lỗi xảy ra khi tải lên file. Vui lòng kiểm tra lại.')
    return render(request, 'uploadLC.html')


def display_duongcong(request):
    sql = "SELECT * FROM data_training_curse"
    data_training_curse = pd.read_sql(sql, mydb)
    data_training_curse = data_training_curse.to_dict(orient='records')
    context = {'data_training_curse': data_training_curse}
    return render(request, 'duongcong.html', context)
