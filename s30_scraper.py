import json
from pdf2image import convert_from_path


def get_first_page(result):
    ll=['1. CONTRACT ID CODE','2 AMENDMENT/MODFICATIONNO','3 EFFECIVEDAIE','1 CONIRACTDCODE','4 REQUISITION/PURCHASE REQ NO','2. AMENDMENT/MODIFICATION NUMBER','EFFECTIVE DATE',' 2. AMENDMENT/MODIFICATION NO.','3.EFFECTIVE DATE','4. REQUISITION/PURCHASE REQ NO'
        ,'4. REQUISITION/PURCHASE REQUISITION NUMBER','6. ISSUED BY','6 ISSUED BY','6.ISSUED8Y AFLCMC/HBQK','6.ISSUEDBY AFLCMC/HBQK','6. ISSUED BY AFLCMC/HBQK','7 ADMINISTERED BY (Ifotherthan item 6','7. ADMINISTERED BY (If other than Item 6)','7. ADMINISTERED BY (If other than Item 6)',
        '7. ADMINISTERED BY (lf other than Item 6)','5. PROJECT NUMBER (If applicable)','5. PROJECT NO. (If applicable)','5 PROJECT NO,(lf applicsb/e)']

    boxes = []
    my_dict={'CONTRACT CODE':'','AMENDMENT NO':'','EFFECTIVE DATE':'','REQUISITION/PURCHASE NUMBER':'','PROJECT NUMBER':'','ISSUED BY':'','ADMINISTERED BY':'','STANDARD FORM':''}

    for line in result:
        print(line)
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
    issue_code=''
    admin_code=''
    for r in result:
        contract_list=['1. CONTRACT ID CODE','1 CONIRACTDCODE']
        ame_list=['2 AMENDMENT/MODFICATIONNO','2. AMENDMENT/MODIFICATION NUMBER',' 2. AMENDMENT/MODIFICATION NO.']
        date_list=['3 EFFECIVEDAIE','EFFECTIVE DATE','3.EFFECTIVE DATE']
        purchase_list=['4. REQUISITION/PURCHASE REQ NO','4. REQUISITION/PURCHASE REQUISITION NUMBER','4 REQUISITION/PURCHASE REQ NO']
        isuuedd=['6. ISSUED BY','6 ISSUED BY','6.ISSUED8Y AFLCMC/HBQK','6.ISSUEDBY AFLCMC/HBQK','6. ISSUED BY AFLCMC/HBQK']
        project=['5. PROJECT NUMBER (If applicable)','5. PROJECT NO. (If applicable)','5 PROJECT NO,(lf applicsb/e)']
        admin=['7 ADMINISTERED BY (Ifotherthan item 6','7. ADMINISTERED BY (If other than Item 6)',
               '7. ADMINISTERED BY (lf other than Item 6)','7. ADMINISTERED BY (If other than Item 6)']


        for i in boxes:
            if admin_code=='':
                if r[1][0] in admin:
                    present = result.index(r)
                    print(result[present + 1][1][0], 'gggggggggggggggggggggggggggggggggggggggg')
                    admin_string=result[present+2][1][0]
                    digit = 0
                    for ch in admin_string:
                        if ch.isdigit():
                            digit = digit + 1
                    if digit>=3 or len(admin_string.split(' '))==1:
                        admin_code='Code: '+result[present+2][1][0]
            if issue_code=='':
                if r[1][0] in isuuedd:
                    present = result.index(r)
                    print(result[present + 1][1][0], 'gggggggggggggggggggggggggggggggggggggggg')
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
                        if digit>=3 or len(issued_string.split(' '))==1:
                            issue_code='CODE: '+ issued_string

            if (0 <= (r[0][0][1] - i[0][0][1]) < 60) and -20 <= (r[0][0][0] - i[0][0][0]) < 80 and r[1][0] not in ll:
                if i[1] in contract_list:
                    my_dict['CONTRACT CODE']=r[1][0]
                if i[1] in ame_list:
                    my_dict['AMENDMENT NO']=r[1][0]
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
            if -8<=(r[0][0][0]-adminx)<10 and 0<=(r[0][0][1]-adminy)<=60:
                admin_tex.append(r[1][0])
                adminx = r[0][0][0]
                adminy = r[0][0][1]
        if lastx:
            if -8<=(r[0][0][0]-lastx)<10 and 0<=(r[0][0][1]-lasty)<=35:
                isuued_tex.append(r[1][0])
                lastx = r[0][0][0]
                lasty = r[0][0][1]
    if len(isuued_tex)>0:
        my_dict['ISSUED BY']='\n'.join(isuued_tex)
    if len(admin_tex)>0:
        my_dict['ADMINISTERED BY'] = '\n'.join(admin_tex)

    print(my_dict)
    with open(r'C:\Users\vikra\pdf_extraction2\SF26\s30outputs\HDTRA1-19-F-0087-P00010_Fully Executed_Redacted.json', 'w') as fp:
        json.dump(my_dict, fp)
    return my_dict
def mains30(result):
    mydict=get_first_page(result)
    return mydict