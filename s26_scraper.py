import json
import re
from paddleocr import PaddleOCR
import pdfplumber
import camelot
ocr = PaddleOCR(use_angle_cls=True, lang='en')




def get_first_page(result):
    my_dict={'contract_code':'','effective_date':'','requisition/purchase_number':'','rating':'','issued_by':'','administered_by':'','standard_form':'','project_number':''}

    #giving all key pattern to extract relevant data
    all_keys=['2. CONTRACT (PROC. INST. IDENT.) NO.','2. CONTRACT (Proc Inst. Indent ) NO','3. EFFECTIVE DATE','3 EFFECTIVE DATE',' 4. REQUISITION / PURCHASE REQUEST /PROJECT NO.','[4 REQUISIT:ON/PURCHASE REQUEST/PROJECT NO.','RATING',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)','3.EFFECTIVE DATE',
        '5. ISSUED BY AFLCMC/HBQK','5 ISSUED BY','6 ADMINISTERED BY (if other than ftem 5)','6 ADMINISTERED BY (if other than ftem 5)',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)']

    boxes = []
    #iterating over a result from OCR and saving box whxh have value from all_keys
    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['standard_form']=str(line[1][0])
        if str(line[1][0]) in all_keys:
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
        #lists for classifying values for matching
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

            if (0 <= (r[0][0][1] - i[0][0][1]) <= yy) and -20 <= (r[0][0][0] - i[0][0][0]) <= xx and r[1][0] not in all_keys:
                if i[1] in contract_list:
                    my_dict['contract_code']=r[1][0]

                if i[1] in rating_list:
                    my_dict['rating']=r[1][0]

                if i[1] in date_list:
                    if 'Mby' in r[1][0]:
                        r[1][0]=r[1][0].replace('Mby','May')
                    my_dict['effective_date'] = r[1][0]

                if i[1] in purchase_list:
                    my_dict['requisition/purchase_number'] = r[1][0]

                if i[1] in project:
                    my_dict['project_number']=r[1][0]

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
        my_dict['issued_by']='\n'.join(isuued_tex)
    if len(admin_tex)>0:
        my_dict['administered_by'] = '\n'.join(admin_tex)

    return my_dict


#to get pages which contain line items
def get_tabless_pages(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Get number of pages
        NumPages = len(pdf.pages)
        # Extract text and do the search
        table_pagess=[]
        for i in range(1, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search('ITEM', Text) and re.search('SUPPLIES OR SERVICES', Text):
                table_pagess.append(i)
    return table_pagess



def get_tablee(pdf_path,pagess):
    all_pages = ','.join(str(v) for v in pagess)
    itemss = []
    tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=1000, pages=str(all_pages))
    #iterating over tables and manuplating values to append in itemss list
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

        except Exception as e:
            pass

    return itemss



def get_clausess(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        clauses_list = []
        Months_list = ['ggg', 'JAN', 'FEB', 'MAR', "APR", 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            #matching clauses pattern to get relevant line
            NumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = NumRegex.search(Text)
            #after matching pattern applied multiple conditions to extract clauses
            try:
                if array.group():
                    NumRegex2 = re.compile(r'\d{4}', flags=0)
                    NumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    gg = Text.split('\n')
                    for g in gg:
                        ggg = g.split(' ')
                        try:
                            next_linee = gg[gg.index(g) + 1]
                            nn = next_linee.split(' ')
                        except:
                            pass
                        if NumRegex.search(ggg[0]) and NumRegex2.search(nn[-1]):
                            if not NumRegex2.search(ggg[-1]):
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

                        if NumRegex.search(ggg[0]) and (NumRegex2.search(ggg[-1])):
                            if len(g) > 20:
                                g = g.replace('(', '')
                                g = g.replace(')', '')
                                yy = g.split(' ')
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

                        if NumRegex.search(ggg[0]) and (NumRegex3.search(ggg[-1])):
                            if len(g.split(' ')) == 2:
                                cc = ggg[0] + ' ' + gg[gg.index(g) - 1] + ' ' + gg[gg.index(g) + 1] + ' ' + ggg[-1]
                                clauses_list.append(cc)

            except Exception as e:
                pass

    #changing clauses format
    clausess_new_list = []
    for c in clauses_list:
        splited_clause = c.split(' ')
        clausee = splited_clause[0] + ' | ' + ' '.join(splited_clause[1:-1]) + ' | ' + splited_clause[-1]
        clausess_new_list.append(clausee)

    return clausess_new_list




def mains26(pdf_path,result):
    #for getting data from first_page
    my_dict=get_first_page(result)
    #for getting numbers of pages which have line_items
    table_pages=get_tabless_pages(pdf_path)
    #for getting line_items from table_pages
    itemss=get_tablee(pdf_path,table_pages)
    my_dict['items']=itemss
    my_dict['clauses']=get_clausess(pdf_path)
    #for returning response
    return my_dict


