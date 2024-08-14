import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import time
from streamlit_extras.metric_cards import style_metric_cards

from query import *

# st.set_option('deprecation.showPyplotGlobalUse', False)
import plotly.graph_objs as go

theme_plotly = None
st.set_page_config(page_title="Dashboard",page_icon="🌍",layout="wide")
st.sidebar.image("./templates/logohbi-PHUBAI.jpg", caption="HBI", width=250)


if "selected_data" not in st.session_state:
    st.session_state["selected_data"] = None

def first_page():
    st.header(":bar_chart: THỐNG KÊ BÁO CÁO ĐÀO TẠO THEO TUẦN HBI")
    result = week_training_reportabc()
    # df=pd.DataFrame(result,columns=["KEYE","ID","Name","Line","Shift","Plant","Operation","Type_training","Week_start","TuanraSX","Technician","StartDate","NgayraSX"])
    # st.dataframe(df)
    week_data = pd.DataFrame(result,columns=["KEYE", "ID", "Name", "WEEK", "YEAR", "Operation", "chatluong", "ChitieuCL", "DanhgiaCL",
                                             "total_time_week", "total_time", "Ngaydaotao", "TuanLC", "Hieusuat_tuan", "ChitieuHS", "DanhgiaHS", "ttRaSX"])

    # SWITCHER
    WEEK=st.sidebar.multiselect(
        "Chọn tuần",
         options=week_data["WEEK"].unique(),
         default=week_data["WEEK"].unique(),
    )
    Operation=st.sidebar.multiselect(
        "Chọn công đoạn",
         options=week_data["Operation"].unique(),
         default=week_data["Operation"].unique(),
    )
    DanhgiaCL=st.sidebar.multiselect(
        "Chọn chất lượng",
         options=week_data["DanhgiaCL"].unique(),
         default=week_data["DanhgiaCL"].unique(),
    )
    DanhgiaHS=st.sidebar.multiselect(
        "Chọn hiệu suất",
         options=week_data["DanhgiaHS"].unique(),
         default=week_data["DanhgiaHS"].unique(),
    )
    Ngaydaotao=st.sidebar.multiselect(
        "Chọn ngày đào tạo",
         options=week_data["Ngaydaotao"].unique(),
         default=week_data["Ngaydaotao"].unique(),
    )
    TuanLC=st.sidebar.multiselect(
        "Tuỳ chọn TuanLC",
         options=week_data["TuanLC"].unique(),
         default=week_data["TuanLC"].unique(),
    )

    ttRaSX=st.sidebar.multiselect(
        "Chọn thứ tự tuần ra sản xuất",
         options=week_data["ttRaSX"].unique(),
         default=week_data["ttRaSX"].unique(),
    )


    df_selection=week_data.query(
        "WEEK==@WEEK & DanhgiaCL==@DanhgiaCL & Operation ==@Operation  & Ngaydaotao ==@Ngaydaotao & TuanLC==@TuanLC & DanhgiaHS ==@DanhgiaHS  & ttRaSX ==@ttRaSX "
    )

    # st.dataframe(df_selection)



    with st.expander("File dữ liệu báo cáo đào tạo hàng tuần"):
        showData=st.multiselect('Filter: ',df_selection.columns,default=["KEYE", "ID", "Name", "WEEK", "YEAR", "Operation", "chatluong", "ChitieuCL", "DanhgiaCL",
                                         "total_time_week", "total_time", "Ngaydaotao", "TuanLC", "Hieusuat_tuan", "ChitieuHS", "DanhgiaHS", "ttRaSX"])
        st.dataframe(df_selection[showData],use_container_width=True)
    #compute top analytics
    total_employee = float(pd.Series(df_selection['ID']).count())
    datCL = float(pd.Series(df_selection['DanhgiaCL'] == "Đạt").sum())
    khongdatCL = float(pd.Series(df_selection['DanhgiaCL'] == "Không đạt").sum())
    datHS = float(pd.Series(df_selection['DanhgiaHS'] == "Đạt").sum())
    khongdatHS = float(pd.Series(df_selection['DanhgiaHS'] == "Chưa đạt").sum())

    # investment_mean = float(pd.Series(df_selection['Investment']).mean())
    # investment_median= float(pd.Series(df_selection['Investment']).median())
    # rating = float(pd.Series(df_selection['Rating']).sum())


    total1,total2,total3,total4,total5=st.columns(5,gap='small')
    with total1:
        # st.info('Tổng số nhân viên',icon="💰")
        st.metric(label=":white_check_mark: Tổng số nhân viên ",value=f"{total_employee:,.0f}")

    with total2:
        # st.info('Số nhân viên đạt chất lượng',icon="💰")
        st.metric(label=":heavy_check_mark: Tổng số nhân viên đạt chất lượng",value=f"{datCL:,.0f}")


    with total3:
        # st.info('Số nhân viên không đạt chất lượng',icon="💰")
        st.metric(label=":x: Tổng số nhân viên không đạt chất lượng",value=f"{khongdatCL:,.0f}")

    with total4:
        # st.info('Central Earnings',icon="💰")
        st.metric(label=":heavy_check_mark: Tổng số nhân viên đạt hiệu suất",value=f"{datHS:,.0f}")

    with total5:
        # st.info('Central Earnings', icon="💰")
        st.metric(label=":x: Tổng số nhân viên không đạt hiệu suất", value=f"{khongdatHS:,.0f}")

    # with total5:
    #     st.info('Ratings',icon="💰")
    #     st.metric(label="Rating",value=numerize(rating),help=f""" Total Rating: {rating} """)
    # style_metric_cards(background_color="#FFFFFF",border_left_color="#686664",border_color="#000000",box_shadow="#F71938")

    # #variable distribution Histogram
    # with st.expander("DISTRIBUTIONS BY FREQUENCY"):
    #  df.hist(figsize=(16,8),color='#898784', zorder=2, rwidth=0.9,legend = ['Investment']);
    #  st.pyplot()

# Home()


# graphs
# def graphs():
    # # Convert Hieusuat_tuan to numeric (handle potential errors)
    # df_selection["Hieusuat_tuan"] = pd.to_numeric(df_selection["Hieusuat_tuan"], errors='coerce')


    hieusuat_chart = (df_selection.groupby(by=["Operation"], as_index = False)["Hieusuat_tuan"].mean())

    hieusuat_chart = px.bar(
        hieusuat_chart,
        x="Hieusuat_tuan",
        y="Operation",
        orientation="h",
        title="<b> BIỂU ĐỒ HIỆU SUẤT TRUNG BÌNH THEO CÔNG ĐOẠN </b>",
        color_discrete_sequence=["#0083B8"] * len(hieusuat_chart),
        template="plotly_white",
    )

    hieusuat_chart.update_layout(
        yaxis_title="CÔNG ĐOẠN",
        xaxis_title="Hiệu suất trung bình",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show y-axis grid and set its color
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Set paper background color to transparent
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show x-axis grid and set its color
    )



    hieusuat_tuanchart = df_selection.groupby(by=["WEEK", "YEAR"], as_index = False)["Hieusuat_tuan"].mean()

    hieusuat_tuanchart = px.line(
        hieusuat_tuanchart,
        x="WEEK",
        y="Hieusuat_tuan",
        orientation="v",
        title="<b> BIỂU ĐỒ HIỆU SUẤT TRUNG BÌNH THEO TUẦN </b>",
        color_discrete_sequence=["#0083b8"] * len(hieusuat_tuanchart),
        template="plotly_white",
    )
    hieusuat_tuanchart.update_layout(
        yaxis_title="Hiệu suất trung bình",
        xaxis_title="Tuần",
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False))
    )

    # biểu đồ tròn
    count_cd = df_selection.groupby(by=["Operation"], as_index=False)["ID"].count().rename(columns={"ID": "Count_ID"})
    # pie chart
    fig = px.pie(count_cd, values='Count_ID', names='Operation', title='BIỂU ĐỒ SỐ LƯỢNG NHÂN VIÊN THEO CÔNG ĐOẠN')
    fig.update_layout(legend_title="Công đoạn", legend_y=1)
    fig.update_traces(textinfo='percent+label', textposition='inside')
    # st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

    left, right, center = st.columns(3)
    left.plotly_chart(hieusuat_tuanchart, use_container_width=True)
    center.plotly_chart(fig, use_container_width=True)
    right.plotly_chart(hieusuat_chart, use_container_width=True)

# graphs()

def second_page():
    st.header(":chart: THỐNG KÊ KẾT QUẢ ĐÀO TẠO HBI")
    result = view_all_data()
    # df=pd.DataFrame(result,columns=["KEYE","ID","Name","Line","Shift","Plant","Operation","Type_training","Week_start","TuanraSX","Technician","StartDate","NgayraSX"])
    # st.dataframe(df)
    result_reporta = pd.DataFrame(result,columns=["ID", "Name", "Line", "Shift", "Operation", "Type_training", "NgayraSX",
                                      "Technician", "TuanP2K_max", "Eff_max", "Hieusuatgannhat", "ChitieuHS", "NgayTN",
                                      "TTtuanTN", "Status", "Note", "AMT_week"])

# SWITCHER
    Shift=st.sidebar.multiselect(
        "Chọn ca làm việc",
         options=result_reporta["Shift"].unique(),
         default=result_reporta["Shift"].unique(),
    )
    Operation=st.sidebar.multiselect(
        "Chọn công đoạn",
         options=result_reporta["Operation"].unique(),
         default=result_reporta["Operation"].unique(),
    )
    Type_training=st.sidebar.multiselect(
        "Chọn loại đào tạo",
         options=result_reporta["Type_training"].unique(),
         default=result_reporta["Type_training"].unique(),
    )
    Technician = st.sidebar.multiselect("Pick your Region", result_reporta["Technician"].unique())
    # Technician=st.sidebar.multiselect(
    #     "Chọn hiệu suất",
    #      options=result_reporta["Technician"].unique(),
    #      default=result_reporta["Technician"].unique(),
    # )
    Status=st.sidebar.multiselect(
        "Trạng thái",
         options=result_reporta["Status"].unique(),
         default=result_reporta["Status"].unique(),
    )
    AMT_week=st.sidebar.multiselect(
        "Số tuần trong AMT",
         options=result_reporta["AMT_week"].unique(),
         default=result_reporta["AMT_week"].unique(),
    )

    df_selection=result_reporta.query(
        "Shift==@Shift & Operation==@Operation & Type_training ==@Type_training  & Technician ==@Technician & Status==@Status & AMT_week ==@AMT_week"
    )






selected_page = st.sidebar.selectbox("CHỌN BÁO CÁO", ["Báo cáo đào tạo theo tuần", "Báo cáo kết quả đào tạo"])
if selected_page == "Báo cáo đào tạo theo tuần":
    first_page()
elif selected_page == "Báo cáo kết quả đào tạo":
    second_page()
