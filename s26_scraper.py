import json
import re
from paddleocr import PaddleOCR

import numpy as np
import pdfplumber
import camelot
from pdf2image import convert_from_path
import os

ocr = PaddleOCR(use_angle_cls=True, lang='en')




def get_first_page(result):
    ll=['2. CONTRACT (PROC. INST. IDENT.) NO.','2. CONTRACT (Proc Inst. Indent ) NO','3. EFFECTIVE DATE','3 EFFECTIVE DATE',' 4. REQUISITION / PURCHASE REQUEST /PROJECT NO.','[4 REQUISIT:ON/PURCHASE REQUEST/PROJECT NO.','RATING',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)','3.EFFECTIVE DATE',
        '5. ISSUED BY AFLCMC/HBQK','5 ISSUED BY','6 ADMINISTERED BY (if other than ftem 5)','6 ADMINISTERED BY (if other than ftem 5)',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)']

    boxes = []

    my_dict={'CONTRACT CODE':'','EFFECTIVE DATE':'','REQUISITION/PURCHASE NUMBER':'','RATING':'','ISSUED BY':'','ADMINISTERED BY':'','STANDARD FORM':''}

    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['STANDARD FORM']=str(line[1][0])
        if str(line[1][0]) in ll:
            boxes.append([line[0],line[1][0]])
    isuued_tex = []
    admin_tex=[]
    lastx = ''
    lasty = ''
    adminx = ''
    adminy = ''
    admin_code=''
    issue_code=''
    for r in result:
        contract_list=['2. CONTRACT (PROC. INST. IDENT.) NO.','2. CONTRACT (Proc Inst. Indent ) NO']
        rating_list=['RATING']
        date_list=['3. EFFECTIVE DATE','3 EFFECTIVE DATE']
        purchase_list=[' 4. REQUISITION / PURCHASE REQUEST /PROJECT NO.','[4 REQUISIT:ON/PURCHASE REQUEST/PROJECT NO.']
        isuuedd=['5. ISSUED BY','5 ISSUED BY','5. ISSUED BY AFLCMC/HBQK']
        project=['5. PROJECT NUMBER (If applicable)','5. PROJECT NO. (If applicable)','5 PROJECT NO,(lf applicsb/e)']
        admin=['6 ADMINISTERED BY (if other than ftem 5)',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)']


        for i in boxes:
            if str(i[1]) in purchase_list:
                xx=301
                yy=35
            else:
                xx=150
                yy=60
            if admin_code=='':
                if r[1][0] in admin:
                    present = result.index(r)
                    admin_string=result[present+2][1][0]
                    digit = 0
                    for ch in admin_string:
                        if ch.isdigit():
                            digit = digit + 1
                    if digit>=3:
                        admin_code='Code: '+result[present+2][1][0]
            if issue_code=='':
                if r[1][0] in isuuedd:
                    present = result.index(r)
                    splited=result[present+1][1][0].split(' ')
                    if len(splited)==2:
                        if splited[0]=='CODE':
                            issue_code="CODE: "+splited[1]
                    if issue_code=='':
                        issued_string=result[present+2][1][0]
                        digit = 0
                        for ch in issued_string:
                            if ch.isdigit():
                                digit = digit + 1
                        if digit>=3:
                            issue_code='Code: '+result[present+2][1][0]
            if (0 <= (r[0][0][1] - i[0][0][1]) <= yy) and -20 <= (r[0][0][0] - i[0][0][0]) <= xx and r[1][0] not in ll:

                if i[1] in contract_list:
                    my_dict['CONTRACT CODE']=r[1][0]
                if i[1] in rating_list:
                    my_dict['RATING']=r[1][0]
                if i[1] in date_list:
                    my_dict['EFFECTIVE DATE'] = r[1][0]
                if i[1] in purchase_list:
                    my_dict['REQUISITION/PURCHASE NUMBER'] = r[1][0]

                if i[1] in project:
                    my_dict['PROJECT NUMBER']=r[1][0]
                if i[1] in isuuedd:
                    lastx = r[0][0][0]
                    lasty = r[0][0][1]
                    isuued_tex.append(issue_code)
                if i[1] in admin:
                    adminx = r[0][0][0]
                    adminy = r[0][0][1]
                    admin_tex.append(admin_code)

        if adminy:
            if -8<=(r[0][0][0]-adminx)<10 and 0<=(r[0][0][1]-adminy)<=62:
                admin_tex.append(r[1][0])
                adminx = r[0][0][0]
                adminy = r[0][0][1]
        if lastx:
            if -8<=(r[0][0][0]-lastx)<10 and 0<=(r[0][0][1]-lasty)<=35:
                if 'NAME AND ADDRESS' not in r[1][0]:
                    isuued_tex.append(r[1][0])
                    lastx = r[0][0][0]
                    lasty = r[0][0][1]
    if len(isuued_tex)>0:
        my_dict['ISSUED BY']='\n'.join(isuued_tex)
    if len(admin_tex)>0:
        my_dict['ADMINISTERED BY'] = '\n'.join(admin_tex)
    return my_dict

def get_tabless_pages(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        # Get number of pages
        # Enter code here
        # Extract text and do the search
        table_pagess=[]
        for i in range(1, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search('ITEM', Text) and re.search('SUPPLIES OR SERVICES', Text):
                table_pagess.append(i)

    return table_pagess

def get_tablee(pdf_path,pagess):
    pagesss = ','.join(str(v) for v in pagess)
    itemss = []
    tables = camelot.read_pdf(pdf_path,
                                  flavor='stream', edge_tol=1000, pages=str(pagesss))
    tableess = []
    for table in tables:
        try:
            df = table.df
            count=0
            try:
                df.columns=['ITEM','SUPPLIES OR SERVICES','Purch Unit','Total Item Amount']
                main_index = df[df['ITEM'] == 'ITEM'].index.tolist()
                df=df.loc[main_index[0]+1:,:]
            except:
                df.columns = ['ITEM', 'ITEM2','SUPPLIES OR SERVICES', 'Purch Unit', 'Total Item Amount']
                df['ITEM']=df['ITEM']+df['ITEM2']
                df.drop('ITEM2', axis=1, inplace=True)
                df.columns = ['ITEM', 'SUPPLIES OR SERVICES', 'Purch Unit', 'Total Item Amount']
                main_index = df[df['ITEM'] == 'ITEM'].index.tolist()
                df = df.loc[main_index[0]+1:, :]


            indexxx1=df[df['ITEM']!=''].index.tolist()
            for i in indexxx1:
                dfff=df.loc[i]

                json1 = dfff.to_json()
                aDict = json.loads(json1)
                aDict['ITEM'] = aDict['ITEM'].replace('\n','')
                res = any(chr.isdigit() for chr in aDict['ITEM'])
                if res:
                    if indexxx1[-1] == i:
                        full_text = []
                        ccc = df.iloc[(i):]
                        for index, row in ccc.iterrows():
                            full_text.append(' '+row['SUPPLIES OR SERVICES']+' '+row['Purch Unit'])
                        str1 = ''.join(full_text)
                        name = re.compile(r'(?:\d{2,6}.\d{1,5}?-\d{1,5})|(?:\d{2,6}.\d{1,5})')
                        array = name.findall(str1)
                        aDict['SUPPLIES OR SERVICES'] = str1
                        aDict['Clauses'] = array
                        itemss.append(aDict)
                        count += 1
                    else:
                        full_text = []
                        ccc = df.iloc[i :indexxx1[count+1] ]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES OR SERVICES']+' '+row['Purch Unit'])

                        str1 = ' '.join(full_text)
                        name = re.compile(r'(?:\d{2,6}.\d{1,5}?-\d{1,5})|(?:\d{2,6}.\d{1,5})')
                        array = name.findall(str1)
                        count += 1
                        aDict['SUPPLIES OR SERVICES'] = str1
                        aDict['Clauses'] = array
                        itemss.append(aDict)
            print(itemss)
            tableess.append(dfff)
        except Exception as e:
            print(e)
            pass

    return itemss


def get_clausess(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        clauses_list=[]
        Months_list=['ggg','JAN','FEB','MAR',"APR",'MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        # Extract text and do the search
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()

            phoneNumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = phoneNumRegex.search(Text)
            try:
                if array.group():
                    # print(Text)
                    phoneNumRegex2 = re.compile(r'\d{4}', flags=0)
                    gg = Text.split('\n')
                    for g in gg:

                        ggg = g.split(' ')
                        if phoneNumRegex.search(ggg[0]) and phoneNumRegex2.search(ggg[-1]):
                            print(g, 'kkkk')
                            if len(g)>20:
                                g=g.replace('(','')
                                g=g.replace(')','')
                                yy=g.split(' ')

                                if yy[-2] in Months_list:
                                    yy[-2]=yy[-1]+'-'+str(Months_list.index(yy[-2]))
                                    yy=yy[:-1]
                                    g=' '.join(yy)
                                    # print(g)
                                if '/' in yy[-1]:
                                    month=yy[-1].split('/')[1]
                                    year=yy[-1].split('/')[2]
                                    yy[-1]=year+'-'+month
                                    g=' '.join(yy)
                                clauses_list.append(g)
                        if phoneNumRegex.search(ggg[0]) and phoneNumRegex2.search(ggg[-1])==None:
                            g=g+gg[gg.index(g)+1]
                            if len(g) > 30:
                                g = g.replace('(', '')
                                g = g.replace(')', '')
                                yy = g.split(' ')

                                if yy[-2] in Months_list:
                                    yy[-2] = yy[-1] + '-' + str(Months_list.index(yy[-2]))
                                    yy = yy[:-1]
                                    g = ' '.join(yy)
                                    # print(g)
                                if '/' in yy[-1]:
                                    month = yy[-1].split('/')[1]
                                    year = yy[-1].split('/')[2]
                                    yy[-1] = year + '-' + month
                                    g = ' '.join(yy)
                                clauses_list.append(g)

            except:
                pass
    clausess_new_list = []
    for c in clauses_list:
        cc = c.split(' ')
        if '.' not in cc[-1]:
            if len(cc[-1].split('-'))==2:
                clausee = cc[0] + ' | ' + ' '.join(cc[1:-1]) + ' | ' + cc[-1]
                clausess_new_list.append(clausee)
    return clausess_new_list

def mains26(pdf_path,result):
    my_dict=get_first_page(result)
    fff=get_tabless_pages(pdf_path)
    itemss=get_tablee(pdf_path,fff)
    my_dict['items']=itemss
    my_dict['clauses']=get_clausess(pdf_path)
    return my_dict


