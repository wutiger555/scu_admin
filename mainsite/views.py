from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


@csrf_exempt 
def responseHome(request):
    name = request.session['name']
    schclass = request.session['class']
    template = get_template('index.html')
    html = template.render(locals())
    return HttpResponse(html)

@csrf_exempt 
def responseLogin(request):
    template = get_template('login.html')
    html = template.render(locals())
    return HttpResponse(html)

def responseSchedule(request):
    template = get_template('schedule.html')
    html = template.render(locals())
    return HttpResponse(html)

# login
@csrf_exempt 
def stream_response(request):
    if request.method == 'POST':
        if request.POST.get('id', False):
            # Session
            id = request.POST.get('id')
            passwd = request.POST.get('passwd')
            if not id in request.session:
               request.session['id'] =  id
               request.session['passwd'] = passwd
            else:
                message = request.session['id'] +' 您已經登入過了!'


            r = requests.post('https://web.sys.scu.edu.tw/login0.asp', data={'id':request.session['id'],'passwd':request.session['passwd']})

            if 'Login=ok' in r.headers['Set-Cookie'] and len(id) == 8:
                ary = get_info(r)

                name = ary[3]
                schclass = ary[5]
                request.session['name'] = ary[3]
                request.session['class'] = ary[5]
                r.cookies.set('parselimit', 'Infinity')


                template = get_template('index.html')
                html = template.render(locals())
                return HttpResponse(html)
            else:
                template = get_template('loginFail.html')
                html = template.render(locals())
                return HttpResponse(html)


        
def get_info(r):
    r.encoding = 'big5'
    soup = BeautifulSoup(r.text, 'html.parser')
    body = soup.body

    ary = []
    for i in body.stripped_strings:
        ary = i.replace('：','').replace('\xa0\xa0','\xa0').replace('\xa0',' ').split(' ')
        break
    return ary


# 獲得所有Sessions
def get_allsessions(request):
    if request.session != None:
        strsessions=""
        for key1,value1 in request.session.items():
            strsessions = strsessions + key1 +":"+ str(value1) + "<br>"
        return HttpResponse(strsessions)
    else:
        return HttpResponse("Session 不存在!")

# 刪除指定Sessions
def delete_session(request,key=None):
    if key in request.session:
        response = HttpResponse('Delete Session: '+ key)
        del request.session[key]
        return response
    else:
        return HttpResponse("No Such Session:" + key)

def getTable(id, passwd):
    r = requests.post('https://web.sys.scu.edu.tw/login0.asp', data={'id':request.session['id'],'passwd':request.session['passwd']})
    r.cookies.set('parselimit', 'Infinity')
    n = requests.get('https://web.sys.scu.edu.tw/SelectCar/selcar81.asp', cookies = r.cookies, data={'procsyear':'108', 'procterm':'2'})
    n.encoding = 'big5'
    soup = BeautifulSoup(n.text,"html.parser") #將網頁資料以html.parser
    trs = soup.find_all('tr')
    df = tableSort(trs)
    drawTable1(df)
    drawTable2(df)

    template = get_template('index.html')
    html = template.render(locals())
    return HttpResponse(html)

def tableSort(trs):
    df = pd.DataFrame(index=['1', '2', '3', '4', 'E', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D'], #處理Rows
                  columns=['禮拜一', '禮拜二', '禮拜三', '禮拜四', '禮拜五', '禮拜六', '禮拜日']) #處理columns
    count = 0

    for tr in trs:

        tds = tr.find_all('td')
        col_count = 0
        if count > 5:
            trName = str(count - 1)
        else:
            trName = str(count)
        if count == 5: #非輸字節數處理
            trName = "E"
        elif count == 11:
            trName = 'A'
        elif count == 12:
            trName = 'B'
        elif count == 13:
            trName = 'C'
        elif count == 14:
            trName = 'D'

        for td in tds:
            tdTxt = str(td.text)
            tdTxt = tdTxt[1:].replace(" 　"," ").replace("\n","(")
            if col_count == 1:
                df.at[trName, '禮拜一'] = tdTxt
            elif col_count == 2:
             df.at[trName, '禮拜二'] = tdTxt
            elif col_count == 3:
                df.at[trName, '禮拜三'] = tdTxt
            elif col_count == 4:
                df.at[trName, '禮拜四'] = tdTxt
            elif col_count == 5:
                df.at[trName, '禮拜五'] = tdTxt
            elif col_count == 6:
                df.at[trName, '禮拜六'] = tdTxt
            elif col_count == 7:
                df.at[trName, '禮拜日'] = tdTxt
            col_count = col_count + 1
        count = count + 1
    return df

def drawTable1(df):
    image = Image.open("static/img/課表.jpg")
    draw = ImageDraw.Draw(image)
    font=ImageFont.truetype("simsun.ttc", 10)

    d = 0
    e = 0
    for index, row in df.iterrows():
        if index == '5':
            e = 1.5
        c = 0
        for weekday in row:
            for i in range(len(str(weekday))):
                if weekday[i].isdigit() and weekday[i+1]!='組':
                    weekday = weekday.replace(weekday[i],'\n'+weekday[i],1)
                    break
            draw.text((270+(98*c), 250+(65*d)+e), weekday, font=font,fill=(0,0,0))
            c = c+1
        d = d+1
    image.save("static/img/test.jpg")

def drawTable2(df):
    image = Image.open("static/img/課表_2.jpg")
    draw = ImageDraw.Draw(image)
    font=ImageFont.truetype("simsun.ttc", 7)

    d = 0
    e = 0
    for index, row in df.iterrows():
        if index == '5':
            e = 10
        
        c = 0
        for weekday in row:
            for i in range(len(weekday)):
                if weekday[i].isdigit() and weekday[i+1]!='組':
                    weekday = weekday.replace(weekday[i],'\n'+weekday[i],1)
                    break
            draw.text((175+(65*c), 120+(40*d)+e), weekday, font=font,fill=(0,0,0))
            c = c+1
        d = d+1

    image.save("static/img/test2.jpg")