import json
import pandas as pd
import tabula
import re
import pdfplumber
import camelot





def get_first_page(result):
    ll=['2 CONTRACINO','3 SOLICITATIONNO','2. CONTRA CT NO.',' 5 DAIE ISSUED','2. CONTRACT NUMBER','3. SOLICITATION NUMBER','5. DATE ISSUED','2. CONTRACT NO.','3. SOLICITATION NO.','5.DATE ISSUED','RATING','6. REQUISITION/PURCHASE NUMBER','6 REQUISITION P URCHASE NO','6.RE QUISITION/P URCHASE NO.','A. NAME'
        ,'C. E-MAIL ADDRESS','AREA CODE','AMENDMENT NO.','AMENDMENT NO','INUMBER','EXTENSION','DATE','20. AMOUNT','28. AWARD DATE','4. TYPE OF SOLICITATION','4 TYPE OF SOLICITATION|','20 AMOUNT',
        '28 AWARDDAIE','28 AWARDDATE','18. OFFERDATE','18 OFFERDATE','18. OFFER DATE']

    ammends=[]
    boxes = []
    datess=[]
    my_dict = {'Contract Number': '', 'Solicitation Number': '', 'Solicitation Type': '', 'Date Issued': '',
               'REQUISITION/PURCHASE NUMBER': '', 'Email': '', 'RATING': '', 'Area Code': '', 'EXTENSION': '',
               'Number': '',
               'AMENDMENT NO.': [], 'Date': [], 'Award Date': '', 'Award Amount': '', 'Offer Date': ''}
    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['STANDARD FORM']=str(line[1][0])
        if str(line[1][0]) in ll:
            line[0][2][1] = line[0][2][1] + 5
            line[0][3][1] = line[0][3][1] + 50
            boxes.append([line[0],line[1][0]])



    for r in result:

        for i in boxes:
            amend_list = ['AMENDMENT NO.','AMENDMENT NO']
            datelist = ['DATE']
            if i[1] in amend_list:
                if r[1][0] not in ll and (0<=(r[0][0][1]-i[0][0][1])<80) and 0<=(i[0][0][0]-r[0][0][0])<80:
                    ammends.append(r[1][0])
                    my_dict['AMENDMENT NO.']=ammends
            if i[1] in datelist:
                if r[1][0] not in ll and (0 <= (r[0][0][1] - i[0][0][1]) < 80) and 0 <= (i[0][0][0] - r[0][0][0]) < 80:
                    datess.append(r[1][0])
                    my_dict['Date'] = datess


            if (0<=(r[0][0][1]-i[0][0][1])<80) and 0<=(r[0][0][0]-i[0][0][0])<80 and r[1][0] not in ll :
                contract_listt=['2 CONTRACINO','2. CONTRACT NO.','2. CONTRACT NUMBER','2. CONTRA CT NO.']
                SOLICITATION_listt=['3 SOLICITATIONNO','3. SOLICITATION NUMBER','3. SOLICITATION NO.']
                Date_listt=['5.DATE ISSUED','5. DATE ISSUED',' 5 DAIE ISSUED']
                Purchase_list=['6. REQUISITION/PURCHASE NUMBER','6 REQUISITION P URCHASE NO','6.RE QUISITION/P URCHASE NO.']
                name_list=['A. NAME']
                emaill_list=['C. E-MAIL ADDRESS']
                area_list=['AREA CODE']
                number_list=['INUMBER']
                extension_list=['EXTENSION']
                datelist=['DATE']
                Soliciation_typeee = ['4. TYPE OF SOLICITATION','4 TYPE OF SOLICITATION|']
                awardlist=['20. AMOUNT','20 AMOUNT']
                awarddatee=['28. AWARD DATE','28 AWARDDAIE','28 AWARDDATE']
                offerdatee=['18. OFFERDATE','18. OFFER DATE']


                # fulll_list=[contract_listt,SOLICITATION_listt,Date_listt,Purchase_list]
                # namess=['Contract Number','Solicitation Number']
                # for i in fulll_list:
                answer=r[1][0]
                if str(i[1]) in contract_listt:
                    name='Contract Number'
                elif str(i[1]) in SOLICITATION_listt:
                    name='Solicitation Number'
                elif str(i[1]) in Date_listt:
                    name='Date Issued'
                elif str(i[1]) in Purchase_list:
                    name='REQUISITION/PURCHASE NUMBER'
                elif  str(i[1]) in name_list:
                    name='Name'
                elif str(i[1]) in emaill_list:
                    name='Email'
                elif str(i[1]) in area_list:
                    name='Area Code'
                elif str(i[1]) in extension_list:
                    name='EXTENSION'
                elif str(i[1]) in number_list:
                    name='Number'
                elif str(i[1]) in Soliciation_typeee:
                    name = 'Solicitation Type'
                    # r[1][0]=list(r[1])
                    answer = (str(r[1][0]).split(' ', 1))[1]
                elif str(i[1]) in awardlist:
                    name='Award Amount'
                elif str(i[1]) in datelist:
                    datess.append(r[1][0])
                elif str(i[1]) in awarddatee:
                    # datess.append(r[1][0])
                    name='Award Date'
                elif str(i[1]) in offerdatee:
                    name='Offer Date'
                else:
                    name=str(i[1])
                if name=='AMENDMENT NO.':
                    my_dict[name] = ammends
                elif name=='Date':
                    my_dict[name]=datess
                else:
                    my_dict[name]=answer

                break

    return my_dict
def get_tabless_pages(pdf_path):
    method = ''
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        # Get number of pages
        # Enter code here
        String = "ITEM NO"
        String2="QUANTITY UNIT"
        String3="Item"
        String4="Unit Price"
        String5="Supplies/Service"
        string6="MAX UNIT"
        # Extract text and do the search
        table_pagess=[]
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()
            # print(Text)
            if re.search(String,Text):
                if re.search(string6,Text):
                    method='third'
                    table_pagess.append(i)
            if re.search(String,Text):
                if re.search(String2,Text):
                    method='first'
                    table_pagess.append(i)
            if re.search(String3, Text) and re.search(String4, Text) and re.search(String5,Text):
                method='second'
                table_pagess.append(i)


    return table_pagess,method


def first_method(pdf_path,pagess):
    pagesss=','.join(str(v) for v in pagess)
    itemss = []
    try:
        tables = camelot.read_pdf(pdf_path,
            flavor='stream', edge_tol=500, pages=pagesss)

        tableess = []
        seconddd=False
        for table in tables:
            try:
                index_change=False
                df = table.df
                # print(df)
                try:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
                except:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'AMOUNT']
                    seconddd=True
                tableess.append(table.df)
                indexxx = df.loc[df['ITEM NO'] == 'ITEM NO'].index
                if len(indexxx) == 0:
                    indexxx = df.loc[df['ITEM NO'] == 'ITEM NO \nSUPPLIES/SERVICES'].index
                    index_change = True
                count = 0
                for i in indexxx:
                    dff = df.iloc[i + 1]
                    if seconddd==True:
                        sss = dff['UNIT'].split('\n')
                        if len(sss) > 1:
                            dff['UNIT PRICE'] = sss[1]
                        else:
                            dff['UNIT PRICE'] = ''
                    if index_change == True:
                        data_change = [dff['SUPPLIES/SERVICES'], dff['QUANTITY'], dff['UNIT']]
                        dff['QUANTITY'] = data_change[0]
                        dff['UNIT'] = data_change[1]
                        dff['UNIT PRICE'] = data_change[2]
                    json1 = dff.to_json()
                    # print(json1)
                    aDict = json.loads(json1)
                    if indexxx[-1] == i:
                        full_text = []
                        ccc = df.iloc[(i + 2):]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])
                        str1 = ''.join(full_text)
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        aDict['SUPPLIES/SERVICES'] = str1
                        aDict['Clauses'] = array
                        itemss.append(aDict)
                        count += 1
                    else:
                        full_text = []
                        ccc = df.iloc[i + 2:indexxx[count + 1] - 1]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])

                        str1 = ''.join(full_text)
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        count += 1
                        aDict['SUPPLIES/SERVICES'] = str1
                        aDict['Clauses'] = array
                        itemss.append(aDict)
            except:
                pass
    except:
        pass
    print(itemss)
    return itemss


def third_method(pdf_path,pagess):
    pagesss=','.join(str(v) for v in pagess)
    itemss = []
    try:
        tables = camelot.read_pdf(pdf_path,
            flavor='stream', edge_tol=500, pages=pagesss)
        tableess = []

        for table in tables:
            df = table.df
            df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
            tableess.append(table.df)
            indexxx = df.loc[df['ITEM NO'] == 'ITEM NO'].index

            count = 0
            for i in indexxx:
                dff = df.iloc[i + 2]
                json1 = dff.to_json()
                aDict = json.loads(json1)

                if indexxx[-1] == i:
                    full_text = []
                    ccc = df.iloc[(i + 2):]
                    for index, row in ccc.iterrows():
                        full_text.append(row['SUPPLIES/SERVICES'])
                    str1 = ''.join(full_text)
                    aDict['SUPPLIES/SERVICES'] = str1
                    name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                    array = name.findall(str1)
                    aDict['Clauses'] = array
                    itemss.append(aDict)
                    count += 1
                else:
                    full_text = []
                    ccc = df.iloc[i + 2:indexxx[count + 1] - 1]
                    for index, row in ccc.iterrows():
                        full_text.append(row['SUPPLIES/SERVICES'])

                    str1 = ''.join(full_text)
                    count += 1
                    name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                    array = name.findall(str1)
                    aDict['SUPPLIES/SERVICES'] = str1
                    aDict['Clauses'] = array
                    itemss.append(aDict)

    except:
        pass


    return itemss
def get_clausess(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        clauses_list=[]
        Months_list=['ggg','JAN','FEB','MAR',"APR",'MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            phoneNumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = phoneNumRegex.search(Text)
            lenarray = phoneNumRegex.findall(Text)

            try:
                if array.group():
                    phoneNumRegex2 = re.compile(r'\d{4}', flags=0)
                    phoneNumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    gg = Text.split('\n')
                    for g in gg:
                        third = False
                        ggg = g.split(' ')
                        try:
                            next_linee = gg[gg.index(g) + 1]
                            nn=next_linee.split(' ')
                        except:
                            pass
                        ccc=''
                        if phoneNumRegex.search(ggg[0]) and phoneNumRegex2.search(nn[-1]):
                            if not phoneNumRegex2.search(ggg[-1]):
                                ccc = g + ' ' + next_linee
                                if len(ccc) > 20:
                                    ccc = ccc.replace('(', '')
                                    ccc = ccc.replace(')', '')
                                    yy = ccc.split(' ')
                                    if yy[-2] in Months_list:
                                        yy[-2] = yy[-1] + '-' + str(Months_list.index(yy[-2]))
                                        yy = yy[:-1]
                                        g = ' '.join(yy)
                                    if '/' in yy[-1]:
                                        month = yy[-1].split('/')[1]
                                        year = yy[-1].split('/')[2]
                                        yy[-1] = year + '-' + month
                                        g = ' '.join(yy)
                                    clauses_list.append(g)


                        if phoneNumRegex.search(ggg[0]) and (phoneNumRegex2.search(ggg[-1])) :
                            lennn = False
                            try:
                                next_index=gg[gg.index(g)+1]

                                nexxx=next_index.split(' ')

                                if len(g)>=65 and len(lenarray)>3:
                                    if not phoneNumRegex.search(nexxx[0]):
                                        lennn=True
                                        if g!=gg[-1] or g!=gg[-2] :
                                            thirddd=gg[gg.index(g) + 2]
                                            third_index = gg[gg.index(g) + 2].split(' ')
                                            if not phoneNumRegex.search(third_index[0]) and len(third_index[0])<70 and len(lenarray)>8:
                                                third=True
                            except:
                                pass
                            if len(g)>20:
                                g=g.replace('(','')
                                g=g.replace(')','')
                                yy=g.split(' ')

                                if yy[-2] in Months_list:
                                    yy[-2]=yy[-1]+'-'+str(Months_list.index(yy[-2]))
                                    yy=yy[:-1]
                                    g=' '.join(yy)
                                if '/' in yy[-1]:
                                    month=yy[-1].split('/')[1]
                                    year=yy[-1].split('/')[2]
                                    yy[-1]=year+'-'+month
                                    g=' '.join(yy)
                                if lennn==True and third==False:
                                    g=g.split(' ')
                                    g=' '.join(g[0:-1])+' '+next_index+' '+g[-1]
                                elif lennn==True and third==True:
                                    g = g.split(' ')
                                    g = ' '.join(g[0:-1]) + ' ' + next_index +' '+thirddd+ ' ' + g[-1]
                                clauses_list.append(g)
                        if phoneNumRegex.search(ggg[0]) and (phoneNumRegex3.search(ggg[-1])):
                            if len(g.split(' '))==2:
                                cc=ggg[0]+' '+gg[gg.index(g)-1]+' '+gg[gg.index(g)+1]+' '+ggg[-1]
                                clauses_list.append(cc)


            except Exception as e:
                pass
    clausess_new_list = []
    for c in clauses_list:
        cc = c.split(' ')
        clausee = cc[0] + ' | ' + ' '.join(cc[1:-1]) + ' | ' + cc[-1]
        clausess_new_list.append(clausee)
    return clausess_new_list

def method2(pdf_path,pages):
    itemss_lsit=[]
    for p in pages:
        pp=p+10
        df = tabula.read_pdf(pdf_path, pages=str(p)+'-'+str(pp),
                             stream=True)

        tables_list = []
        tables = df
        count = 0
        data = []

        for t in tables:
            try:

                if count == 0:
                    value = t.columns
                    t.columns = value
                    ff = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in ff))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    count += 1
                    tables_list.append(t)
                else:
                    t.columns = value
                    ff = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in ff))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    tables_list.append(t)
            except:
                pass

    d = '.'.join(data)
    new_list = []
    d = d.replace('Firm Fixed Price', 'Firm Fixed Price fffff')
    d = d.replace('Cost No Fee', 'Cost No Fee fffff')
    d = d.split('fffff')
    line_clauses=[]
    for f in d:
        new_list.append(f)
        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
        array = name.findall(f)
        line_clauses.append(array)

    dff = pd.concat(tables_list, axis=0, ignore_index=True)
    vv = dff.loc[pd.isna(dff["Item"]), :].index

    for v in vv:
        if pd.notnull(dff['Unit Price'][v]):
            if pd.notnull(dff['Unit Price'][v - 1]):
                dff.iloc[v - 1, 3] = str(dff.iloc[v - 1, 3]) + ' ' + str(dff.iloc[v, 3])
            if pd.isnull(dff['Unit Price'][v - 1]):
                dff.iloc[v - 1, 3] = str(dff.iloc[v, 3])
        if pd.notnull(dff['Amount'][v]):
            if pd.notnull(dff['Amount'][v + 1]):
                dff.iloc[v + 1, 4] = str(dff.iloc[v, 4]) + '\n' + str(dff.iloc[v + 1, 4])
            elif pd.isnull(dff['Amount'][v + 1]):
                dff.iloc[v + 1, 4] = str(dff.iloc[v, 4])

    dff.dropna(thresh=2, axis=0, inplace=True)
    dff['Supplies/Services'] = new_list
    dff['Clauses'] = line_clauses
    itemsss=dff.to_json(orient="index")
    itemsss=json.loads(itemsss)
    for it in itemsss:
        itemss_lsit.append(itemsss[str(it)])
    return itemss_lsit


def main(pdf_path,result):
    mydict=get_first_page(result)

    pagess,methodd=get_tabless_pages(pdf_path)
    if methodd=='first':
        iteemms=first_method(pdf_path,pagess)
        mydict['items']=iteemms
    elif methodd=='second':
        iteemms=method2(pdf_path,pagess)
        mydict['items'] = iteemms
    elif methodd=='third':
        iteemms=third_method(pdf_path,pagess)
        mydict['items']=iteemms
    clausess=get_clausess(pdf_path)
    mydict['clauses']=clausess

    return mydict


