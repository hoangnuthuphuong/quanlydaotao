import os
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
from sqlalchemy import create_engine, text

# hostname = 'localhost'
engine_hbi = create_engine('mysql+mysqlconnector://root:123456@localhost:3306/htsystem_data', echo=False)
conn = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",use_pure=False)
mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",
                               use_pure=False)
myCursor = mydb.cursor()



def export_to_excel(request):
    file_path = './data.xlsx'

    if os.path.exists(file_path):
        with open(file_path, 'rb') as excel_file:
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
            return response
    else:
        return HttpResponse("File not found", status=404)

def display_training_data(request):
    sql = "SELECT * FROM training_data"
    #aaa
    # sql_week = "SELECT * FROM week_training_report1"
    mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",use_pure=False)
    training_data = pd.read_sql(sql, mydb)
    #aaa
    # week_data = pd.read_sql(sql_week, mydb)

    training_data['KEYE'] = (training_data['ID'].astype(str) + training_data['StartDate'].astype(str).str.replace('-', ''))
    training_data['StartDaten'] = pd.to_datetime(training_data['StartDate'])
    training_data['Week_start'] = training_data['StartDaten'].dt.isocalendar().week

    training_data['NgayraSXn'] = pd.to_datetime(training_data['NgayraSX'])
    training_data['TuanraSX'] = training_data['NgayraSXn'].dt.isocalendar().week

    del training_data['StartDaten'], training_data['NgayraSXn']
    training_data = training_data.fillna(0)


    mycursor = mydb.cursor()
    for index, row in training_data.iterrows():
        sql_update = "UPDATE training_data SET KEYE = %s, Week_start = %s, TuanraSX = %s WHERE ID = %s"
        val = (row['KEYE'], row['Week_start'], row['TuanraSX'], row['ID'])
        mycursor.execute(sql_update, val)

    training_data = training_data.sort_values(by=['ID', 'StartDate'])
    mydb.commit()
    mydb.close()
    training_data.to_excel('data.xlsx', sheet_name='Dữ liệu đào tạo', index=False)
    t = loader.get_template('employee_data.html')
    context = {
        'training_data': training_data
    }
    print(training_data)
    return HttpResponse(t.render(context, request))



def dailyreport(request):
        mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data", use_pure=False)
        sql = "SELECT * FROM daily_training_report"
        daily_training_report = pd.read_sql(sql, mydb).fillna(0)

        daily_training_report['KEYE'] = daily_training_report['ID'].astype(str) + daily_training_report['Date'].astype(str).str.replace('-','')
        # Chuyển đổi cột 'Date' sang datetime
        daily_training_report['Datenew'] = pd.to_datetime(daily_training_report['Date'])

        # Tính Weekdays, WEEK, MONTH, YEAR
        daily_training_report['Weekdays'] = daily_training_report['Datenew'].dt.weekday + 2
        daily_training_report['WEEK'] = daily_training_report['Datenew'].dt.isocalendar().week
        daily_training_report['MONTH'] = daily_training_report['Datenew'].dt.month
        daily_training_report['YEAR'] = daily_training_report['Datenew'].dt.year
        del daily_training_report['Datenew']

        # Tính toán realtime_day và date_no_eff
        daily_training_report['realtime_day'] = (daily_training_report['WorkHrs'] - daily_training_report['stop_hours'] - daily_training_report['downtime']).round(1)
        daily_training_report['date_no_eff'] = daily_training_report['realtime_day'].apply(lambda num: 1 if num < 4.87 else 0)

        # Cập nhật các cột trực tiếp trong cơ sở dữ liệu
        mycursor = mydb.cursor()

        for index, row in daily_training_report.iterrows():
            sql_update = "UPDATE daily_training_report SET KEYE = %s, Weekdays = %s, WEEK = %s, YEAR = %s, realtime_day = %s, date_no_eff = %s WHERE ID = %s AND Date = %s"
            val = (row['KEYE'], row['Weekdays'], row['WEEK'], row['YEAR'], row['realtime_day'], row['date_no_eff'], row['ID'], row['Date'])
            mycursor.execute(sql_update, val)

        #Chọn sắp xếp thời gian giảm dần để hiển thị những ngày gần nhất lên trên
        daily_training_report = daily_training_report.sort_values(by=['Date', 'WEEK', 'YEAR'], ascending=[False,False,False])

        mydb.commit()
        mydb.close()
        daily_training_report.to_excel('data.xlsx', sheet_name='Dữ liệu hàng ngày', index=False)
        context = {'daily_training_report': daily_training_report}
        print(daily_training_report)
        return render(request, 'dailyreport.html', context)



def week_report(request):
    # Kết nối đến cơ sở dữ liệu MySQL
    mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data", use_pure=False)

    # Truy vấn dữ liệu từ cơ sở dữ liệu MySQL
    sql = "SELECT * FROM daily_training_report"
    daily_training_report = pd.read_sql(sql, mydb)

    sqlt = "SELECT ID, Operation, TuanraSX FROM training_data"
    training_data = pd.read_sql(sqlt, mydb)

    data = pd.merge(daily_training_report, training_data, how='left', left_on=['ID'], right_on=['ID'])

    duongcong_sql = "SELECT * FROM data_training_curse"
    duongcong = pd.read_sql(duongcong_sql, mydb)

    # Xử lý dữ liệu
    week = data.groupby(['ID', 'Name', 'WEEK', 'YEAR', 'Operation'])['chatluong'].sum().reset_index()
    week['ChitieuCL'] = 3
    week['DanhgiaCL'] = 'Đạt'
    week.loc[week['chatluong'] > week['ChitieuCL'], 'DanhgiaCL'] = 'Không đạt'

    tonggio_tuan = data.groupby(['ID', 'WEEK', 'YEAR'])['WorkHrs'].sum().reset_index().rename(
        columns={'WorkHrs': 'total_time_week'}).round(1)
    tonggio_tuan['total_time'] = tonggio_tuan.groupby(['ID', 'YEAR'])['total_time_week'].cumsum().reset_index()[
        'total_time_week'].round(1)
    tonggio_tuan['Ngaydaotao'] = (tonggio_tuan['total_time'] // 7.37)
    tonggio_tuan.loc[((tonggio_tuan['total_time'] / 7.37) - (tonggio_tuan['total_time'] // 7.37)) > (5 / 7.37), 'Ngaydaotao'] = (tonggio_tuan['total_time'] // 7.37) + 1
    week = pd.merge(week, tonggio_tuan, how='left', left_on=['ID', 'WEEK', 'YEAR'], right_on=['ID', 'WEEK', 'YEAR'])
    week['TuanLC'] = (week['Ngaydaotao'] / 6).round(2)
    week = pd.merge(week, data[data['date_no_eff'] == 0].groupby(['ID', 'WEEK', 'YEAR'])['Eff'].mean().round(1).reset_index(), how='left', left_on=['ID', 'WEEK', 'YEAR'], right_on=['ID', 'WEEK', 'YEAR']).rename(columns={'Eff': 'Hieusuat_tuan'})
    week = pd.merge(week, duongcong[['OPERATION', 'COUNT_DAYS', 'EFF_CURVE_BY_DATE']], how='left', left_on=['Operation', 'Ngaydaotao'], right_on=['OPERATION', 'COUNT_DAYS'])

    week['ChitieuHS'] = week['EFF_CURVE_BY_DATE'] - 0.5
    week.loc[week['ChitieuHS'] > 80, 'ChitieuHS'] = 80

    week.loc[week['Hieusuat_tuan'] < week['ChitieuHS'], 'DanhgiaHS'] = 'Không đạt'
    week.loc[week['Hieusuat_tuan'] >= week['ChitieuHS'], 'DanhgiaHS'] = 'Đạt'

    del week['OPERATION'], week['COUNT_DAYS'], week['EFF_CURVE_BY_DATE']
    week['ttRaSX'] = ((week['WEEK'].astype(float) - data['TuanraSX'].astype(float) + 1)).round(0)

    # Kết nối đến cơ sở dữ liệu MySQL và thực hiện chèn dữ liệu
    mycursor = mydb.cursor()

    for index, row in week.iterrows():
        sql_update = """
        INSERT INTO week_training_report1 (ID, Name, WEEK, YEAR, Operation, chatluong, ChitieuCL, DanhgiaCL, total_time_week, total_time, Ngaydaotao, TuanLC, Hieusuat_tuan, ChitieuHS, DanhgiaHS, ttRaSX)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            Name = VALUES(Name),
            WEEK = VALUES(WEEK),
            YEAR = VALUES(YEAR),
            Operation = VALUES(Operation),
            chatluong = VALUES(chatluong),
            ChitieuCL = VALUES(ChitieuCL),
            DanhgiaCL = VALUES(DanhgiaCL),
            total_time_week = VALUES(total_time_week),
            total_time = VALUES(total_time),
            Ngaydaotao = VALUES(Ngaydaotao),
            TuanLC = VALUES(TuanLC),
            Hieusuat_tuan = VALUES(Hieusuat_tuan),
            ChitieuHS = VALUES(ChitieuHS),
            DanhgiaHS = VALUES(DanhgiaHS),
            ttRaSX = VALUES(ttRaSX);
        """
        val = (row['ID'], row['Name'], row['WEEK'], row['YEAR'], row['Operation'], row['chatluong'],
               row['ChitieuCL'], row['DanhgiaCL'], row['total_time_week'], row['total_time'], row['Ngaydaotao'],
               row['TuanLC'], row['Hieusuat_tuan'], row['ChitieuHS'], row['DanhgiaHS'], row['ttRaSX'])
        mycursor.execute(sql_update, val)

    # Cam kết và đóng kết nối
    mydb.commit()
    mydb.close()

    # Xuất dữ liệu ra file Excel
    week.to_excel('data.xlsx', sheet_name='Báo cáo đào tạo tuần', index=False)
    context = {'week_training_report1': week}
    print(week)
    return render(request, 'week_report.html', context)




def result_report(request):
    sql = "SELECT * FROM training_data"
    training_data = pd.read_sql(sql, mydb)
    sqld = "SELECT * FROM daily_training_report"
    daily_training_report = pd.read_sql(sqld, mydb)
    sqlw = "SELECT * FROM week_training_report1"
    week_training_report = pd.read_sql(sqlw, mydb)

    data = training_data[['ID', 'Name', 'Line', 'Shift', 'Operation', 'Type_training', 'NgayraSX', 'Technician']]

    # lấy hiệu suất max
    Eff_max = daily_training_report[daily_training_report['date_no_eff'] == 0].groupby(['ID', 'Name'])['Eff'].max().reset_index().rename(columns={'Eff': 'Eff_max'})
    # Sắp xếp theo ID và Date, nhóm theo ID để lấy ra ngày làm việc cuối cùng của nhân viên
    dulieucuoi_day = daily_training_report.sort_values(by=['ID', 'Date']).groupby('ID').last().reset_index()
    TuanP2K_max = dulieucuoi_day[['ID', 'Name', 'WEEK']].rename(columns={'WEEK': 'TuanP2K_max'})
    dulieucuoi = pd.merge(TuanP2K_max, Eff_max, how='left', left_on=['ID', 'Name'], right_on=['ID', 'Name'])

    # Lấy hiệu suất cuối cùng trong bảng week
    dulieucuoi_week = week_training_report.sort_values(by=['ID', 'WEEK', 'YEAR']).groupby('ID').last().reset_index()
    dulieucuoi_week = dulieucuoi_week[['ID', 'Name', 'Hieusuat_tuan', 'ChitieuHS']].rename(columns={'Hieusuat_tuan': 'Hieusuatgannhat'})
    dulieucuoi = pd.merge(dulieucuoi, dulieucuoi_week, how='left', left_on=['ID', 'Name'], right_on=['ID', 'Name'])

    data = pd.merge(data, dulieucuoi, how='left', left_on=['ID', 'Name'], right_on=['ID', 'Name']).fillna(0)

    # Cho ngày tốt nghiệp tạm thời vì CHƯA SET ĐIỀU KIỆN
    # đúng là status_day vì nếu nghỉ thì là ngày nghỉ việc
    data['NgayTN'] = '2024-08-09'
    # data['NgayTN'] = pd.to_datetime(data['NgayTN'], format='%Y-%m-%d')


    # Tính thứ tự tuần tốt nghiệp = TuanP2K_max - Tuần tốt nghiệp
    data['TTtuanTN'] = data['TuanP2K_max'] - pd.to_datetime(data['NgayTN'], format='%Y-%m-%d').dt.isocalendar().week + 1
    # SET TẠM THỜI
    data['Status'] = 'Tốt nghiệp (tạm)'
    data['Note'] = 'Ghi chú'

    # Tính số tuần trong AMT
    # TuanraSX khác 0: đã ra khỏi AMT
    # data['AMT_week'] = 'Tuân ra SX'
    data.loc[training_data['TuanraSX'].astype('int') != 0, 'AMT_week'] = training_data['TuanraSX'].astype('int') - training_data['Week_start'].astype('int')
    # TuanraSX=0: chưa ra SX,
    #aaa
    for id in list(set(data[training_data['TuanraSX'].astype('int') == 0]['ID'].unique()) & set(week_training_report['ID'].unique())):
        # Tính tuần làm việc gần nhất hiện tại của nhân viên
        week_max = week_training_report[week_training_report['ID'] == id]['WEEK'].unique().max()
        data.loc[training_data['ID'] == id, 'AMT_week'] = week_max - training_data['Week_start'].astype('int')

    data.to_sql('result_report', con=engine_hbi, if_exists='replace', index=False)
    data.to_excel('data.xlsx', sheet_name='Kết quả đào tạo', index=False)
    context = {'result_report': data}
    print(data)
    return render(request, 'result_report.html', context)


def edit_employee_data(request, ID):
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
        if 'delete' in request.POST:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM training_data WHERE ID = %s", [ID])
                    connection.commit()
                messages.success(request, 'Record deleted successfully.')
                return redirect('index')
            except Exception as e:
                messages.error(request, f"Error deleting record: {e}")
                return redirect('edit_employee_data', ID=ID)
        data = {
            'Name': request.POST.get('Name'),
            'Line': request.POST.get('Line'),
            'Shift': request.POST.get('Shift'),
            'Plant': request.POST.get('Plant'),
            'Operation': request.POST.get('Operation'),
            'Type_training': request.POST.get('Type_training'),
            'Week_start': request.POST.get('Week_start'),
            'TuanraSX': request.POST.get('TuanraSX'),
            'Technician': request.POST.get('Technician'),
            'StartDate': request.POST.get('StartDate'),
            'NgayraSX': request.POST.get('NgayraSX'),
        }

        # Update the data
        update_query = """
            UPDATE training_data
            SET Name = %s, Line = %s, Shift = %s, Plant = %s, Operation = %s, Type_training = %s, Week_start = %s, TuanraSX = %s, Technician = %s, StartDate = %s, NgayraSX = %s
            WHERE ID = %s
        """
        params = (
            data['Name'], data['Line'], data['Shift'], data['Plant'], data['Operation'], data['Type_training'],
            data['Week_start'], data['TuanraSX'], data['Technician'], data['StartDate'], data['NgayraSX'], ID
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
                connection.commit()
            messages.success(request, 'Chỉnh sửa dữ liệu thành công!')
        except Exception as e:
            messages.error(request, f"Lỗi: {e}")
        return redirect('edit_employee_data', ID=ID)

    congdoan = ['PAD PRINT', 'MAKE BAND', 'BARTACK', 'ATTACH BUTTON', 'HEM BOTTOM', 'BIND PANEL', 'SEW BAND', 'ATTACH BUTTON', 'BIND LEG']

    context = {'record': record, 'congdoan': congdoan}
    return render(request, 'edit_employee.html', context)


def edit_dailyreport_data(request, ID, Date):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM daily_training_report WHERE ID = %s AND Date = %s", [ID, Date])
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
            'Eff': request.POST.get('Eff'),
            'date_no_eff': request.POST.get('date_no_eff'),
            'WorkHrs': request.POST.get('WorkHrs'),
            'stop_hours': request.POST.get('stop_hours'),
            'downtime': request.POST.get('downtime'),
            'chatluong': request.POST.get('chatluong'),
            'Date': request.POST.get('Date'),
            'Weekdays': request.POST.get('Weekdays'),
            'WEEK': request.POST.get('WEEK'),
            'MONTH': request.POST.get('MONTH'),
            'YEAR': request.POST.get('YEAR'),
        }

        update_query = """
            UPDATE daily_training_report
            SET Name = %s, Line = %s, Shift = %s, Eff = %s, date_no_eff = %s, WorkHrs = %s,
                stop_hours = %s, downtime = %s, chatluong = %s, Weekdays = %s, WEEK = %s, MONTH = %s, YEAR = %s
            WHERE ID = %s AND Date = %s
        """
        params = (
            data['Name'], data['Line'], data['Shift'], data['Eff'], data['date_no_eff'], data['WorkHrs'], data['stop_hours'],
            data['downtime'], data['chatluong'], data['Weekdays'], data['WEEK'], data['MONTH'], data['YEAR'], ID, Date
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
                connection.commit()
            messages.success(request, 'Chỉnh sửa dữ liệu thành công!')
        except Exception as e:
            messages.error(request, f"Lỗi: {e}")
            return redirect('edit_dailyreport_data', ID=ID, Date=Date)

    context = {'record': record}
    return render(request, 'edit_dailyreport_data.html', context)


@csrf_exempt
def search_danhsach_nv_ajax(request):
    if request.method == 'POST':
        id = request.POST.get('idnv')
        line = request.POST.get('line')
        ngaytruoc = request.POST.get('ngaytruoc')
        ngaysau = request.POST.get('ngaysau')
        shift = request.POST.get('shift')
        print(id, line, ngaytruoc, ngaysau, shift)

        sql_search = f"""
        select * from htsystem_data.training_data where 1=1
        """
        if id != '' and 'n' not in str(id):
            sql_search += f""" and id='{id}'"""
        if line != '':
            sql_search += f""" and line='{line}'"""
        if shift != '':
            sql_search += f""" and shift='{shift}'"""

        if ngaytruoc and ngaysau:
            sql_search += f" AND startdate BETWEEN '{ngaytruoc}' AND '{ngaysau}'"
        elif ngaytruoc:
            sql_search += f" AND startdate = '{ngaytruoc}'"
        elif ngaytruoc:
            sql_search += f" AND startdate = '{ngaysau}'"

        data_h = pd.read_sql(sql_search, mydb)
        data_h.to_excel('data.xlsx', sheet_name='Dữ liệu nhân viên', index=False)
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
                        'TuanraSX': request.POST.get('TuanraSX'),
                        'Technician': request.POST.get('Technician'),
                        'StartDate': request.POST.get('StartDate'),
                        'NgayraSX': request.POST.get('NgayraSX'),
                    }

                    insert_query = '''
                        INSERT INTO training_data (ID, Name, Line, Shift, Plant, Operation,
                            Type_training, Week_start, TuanraSX, Technician, StartDate, NgayraSX)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    params = (
                        data['ID'], data['Name'], data['Line'], data['Shift'], data['Plant'], data['Operation'],
                        data['Type_training'], data['Week_start'], data['TuanraSX'], data['Technician'],
                        data['StartDate'], data['NgayraSX']
                    )

                    cursor.execute(insert_query, params)
                    connection.commit()
                    messages.success(request, 'Thêm dữ lệu thành công!')
                    return redirect('index')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
    return render(request, 'add_employee.html')


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
            df = df.fillna('')
            print(df)
            conn = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",use_pure=False)
            cursor = conn.cursor()
            for index, row in df.iterrows():
                ID = row['ID']
                cursor.execute("SELECT COUNT(*) FROM training_data WHERE ID = %s", [ID])
                count = cursor.fetchone()[0]

                if count == 0:
                    insert_query = '''
                        INSERT INTO training_data (ID, Name, Line, Shift, Plant, Operation,
                            Type_training, Week_start, TuanraSX, Technician, StartDate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    '''
                    params = (
                        row['ID'], row['Name'], row['Line'], row['Shift'], row['Plant'], row['Operation'],
                        row['Type_training'], row['Week_start'], row['TuanraSX'], row['Technician'],
                        row['StartDate'].strftime('%Y-%m-%d')
                    )
                    cursor.execute(insert_query, params)
                    conn.commit()

            cursor.close()
            conn.close()
            messages.success(request, 'Dữ liệu đã được tải lên thành công!')
            # return HttpResponse('Dữ liệu đã được tải lên thành công!')
        except Exception as e:
            conn.rollback()
            logger.error(f'Lỗi khi tải lên file Excel: {str(e)}')
            return HttpResponse('Có lỗi xảy ra khi tải lên file. Vui lòng kiểm tra lại.')
    return render(request, 'upload_excel.html')




def dashboard(request):
    sql = "SELECT * FROM training_data"
    mydb = mysql.connector.connect(user="root", password="123456", host="localhost", database="htsystem_data",
                                   use_pure=False)
    data = pd.read_sql(sql, mydb)

    total_training = len(data)
    rit = data['Shift'].value_counts().get('RIT', 0)
    bali = data['Shift'].value_counts().get('BALI', 0)
    print("Tổng số nhân viên đào tạo: ", total_training)
    print("RIT: ", rit)
    print("BALI: ", bali)
    context = {
        'total_training': total_training,
        'rit': rit,
        'bali': bali,
    }
    return render(request, 'index.html', context)
