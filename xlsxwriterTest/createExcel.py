#!/usr/bin/env python
# encoding: utf-8
'''
@author: bwcheng
@time: 2018/8/15 14:28
@desc:
'''
import xlsxwriter

# 创建excel
workbook = xlsxwriter.Workbook('firstEx.xlsx')
# 创建一个sheet
worksheet = workbook.add_worksheet('first')
# 设置一个加粗样式
bold = workbook.add_format({'bold': True})
# 设置表头内容
headers = ['time', 'letter', 'number']
# 设置填充数据
data = [['7-1', 1, 3], ['7-2', 2, 2], ['7-3', 3, 1]]
# 填充首行
worksheet.write_row('A1', headers, bold)
# 填充其他行
a = 2
for dataList in data:
    index = 'A' + str(a)
    a = a + 1
    worksheet.write_row(index, dataList)
# 添加图表 column为柱形图，line为折线图，pie为饼图
line_chart = workbook.add_chart({'type': 'pie'})
# 添加数据
line_chart.add_series({
    'name': 'first!$B$1',
    'categorides': '=first!$A$2:$A$4',
    'values': '==first!$B$2:$B$4',
    'line': {'color': 'red'}
})

line_chart.add_series({
    'name': 'first!$C$1',
    'categories': '=first!$A$2:$A$4',
    'values': 'first!$C$2:$C$4',
    'line': {'color': 'yellow'}
})
# 设置图表名称  若为饼图只设置title，x、y不用设置
line_chart.set_title({'name': 'compare'})
# 横坐标名称
line_chart.set_x_axis({'name': 'myLetter'})
# 纵坐标名称
line_chart.set_y_axis({'name': 'myNumber'})
# 设置图表风格
line_chart.set_style(2)
# 设置表的偏移量
worksheet.insert_chart('A10', line_chart, {'x_offset': 25, 'y_offset': 10})

workbook.close()
