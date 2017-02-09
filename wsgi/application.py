#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, json, re, bcrypt, datetime, time
from peewee import *
from playhouse.pool import *
from bottle import Bottle, request, response, hook
from urllib.parse import urlparse
from urllib.request import urlopen
from wsgi.ChessTimer import ChessTimer
from time import sleep
import threading

if 'OPENSHIFT_DATA_DIR' in os.environ:
    #db = SqliteDatabase(os.environ['OPENSHIFT_DATA_DIR']+'datumaro.db')
    #url = urlparse(os.environ.get('OPENSHIFT_MYSQL_DB_URL'))
    url = urlparse(os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL'))
    #db = PooledMySQLDatabase(os.environ['OPENSHIFT_APP_NAME'], host=url.hostname, port=url.port, user=url.username, passwd=url.password)
    db = PooledPostgresqlDatabase(os.environ['OPENSHIFT_APP_NAME'], host=url.hostname, port=url.port, user=url.username, password=url.password)
else:
    db = SqliteDatabase('datumaro.db')

@hook('before_request')
def _connect_db():
    db.connect()

@hook('after_request')
def _close_db():
    if not db.is_closed():
        db.close()

class Uzanto(Model):
    nomo = CharField()
    pasvorto = CharField()
    seanco = CharField(max_length=32, null=True)
    poento = IntegerField(default=0)
    pagita = BooleanField(default=False)
    class Meta:
        database = db

class Ordo(Model):
    uzanto = ForeignKeyField(Uzanto)
    jxetono = CharField()
    sku = CharField()
    uzita = BooleanField(default=False)
    class Meta:
        database = db
        
class Tu(Model):
    uzantoO = ForeignKeyField(Uzanto, related_name='tu_o')
    uzantoX = ForeignKeyField(Uzanto, related_name='tu_x')
    tabulo = CharField()
    vico = ForeignKeyField(Uzanto)
    lastaIndekso = IntegerField(default=-1)
    venkulo = ForeignKeyField(Uzanto, related_name='tu_venkajxo')
    donita = BooleanField(default=False)
    egalita = BooleanField(default=False)
    class Meta:
        database = db
    
#db.connect()
#db.create_tables([Tu])

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hased password. Useing bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)

def anstatauxigi(cxeno, indekso, signo):
    listo = list(cxeno)
    listo[indekso] = signo
    return ''.join(listo)

application = Bottle()
app = application

def ensalutita(seanco):
    try:
        Uzanto.get(Uzanto.seanco == seanco)
        return True
    except Uzanto.DoesNotExist:
        return False
    
@app.route('/')
def index():
    return "<b>cxefa</b> pagxo"

@app.route("/testo")
def testo():
    response.content_type = "application/json; charset=utf-8"
    return json.dumps("test!")

@app.route("/subskribi/<nomo>/<pasvorto>")
def subskribi(nomo, pasvorto):
    #PORFARI cxu retposxto/telefono devas konfirmigxi?
    response.content_type = "application/json; charset=utf-8"
    try:
        uzanto = Uzanto.get(Uzanto.nomo == nomo)
        return json.dumps(False)
    except Uzanto.DoesNotExist:
        uzanto = Uzanto(nomo=nomo, pasvorto=get_hashed_password(pasvorto))
        uzanto.save()
        return json.dumps(True)

@app.route("/ensaluti/<nomo>/<pasvorto>")
def ensaluti(nomo, pasvorto):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.nomo == nomo)
    if check_password(pasvorto, uzanto.pasvorto):
        from random import SystemRandom
        import string
        seanco = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
        uzanto.seanco = seanco
        uzanto.save()
        return json.dumps({'seanco': seanco})
    else:
        return json.dumps(False)

@app.route('/saluti/<seanco>')
def saluti(seanco):
    response.content_type = "application/json; charset=utf-8"
    return json.dumps("Saluton " + Uzanto.get(Uzanto.seanco == seanco).nomo)

@app.route("/statistiko/<seanco>")
def statistiko(seanco):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    argxentaj = Parto.select().where(Parto.uzanto == uzanto.id, Parto.orita == False).count()
    oraj = Parto.select().where(Parto.uzanto == uzanto.id, Parto.orita == True).count()
    muroj = Parto.select().where(Parto.uzanto == uzanto.id, Parto.murita == True).count()
    if uzanto.nomo == 'hsn6':
        uzantoj = Uzanto.select().count()
        return json.dumps({'argxentaj':argxentaj, 'oraj':oraj, 'muroj':muroj, 'uzantoj':uzantoj})
    else:
        return json.dumps({'argxentaj':argxentaj, 'oraj':oraj, 'muroj':muroj})

@app.route("/rango/<seanco>")
def rango(seanco):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    uzantoj = Uzanto.select().order_by(-Uzanto.poento).limit(7)
    sep_unuaj = {}
    for (uzanto, i) in zip(uzantoj[:7], range(0,7)):
        sep_unuaj[str(i)] = (uzanto.nomo, str(uzanto.poento))
    return json.dumps(sep_unuaj)

@app.route('/ordo/<seanco>/<ordoj>')
def ordo(seanco, ordoj):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    ordoj = ordoj.split(',')
    for ordo in ordoj:
        ordo = ordo.split('-')
        try:
            jxetono = ordo[0]
            sku = ordo[1]
        except IndexError:
            break;
        #PORFARI kontrolu la ordon per Bazar
        '''
        respondo = json.loads(str(urlopen('https://pardakht.cafebazaar.ir/devapi/v2/api/validate/<package_name>/inapp/<product_id>/purchases/<purchase_token>/').read())[2:-1])
        try:
            respondo['purchaseState'] == 0
        except KeyError:
            print(respondo['error']+' --> '+respondo['error_description'])
        '''
        Uzanto.update(pagita=True).where(Uzanto.seanco == seanco).execute()
        
    return json.dumps(True)
    
@app.route("/konverti/<seanco>/<oro>")
def konverti(seanco, oro):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    oro = int(oro)
    if uzanto.oro < oro or oro <= 0:
        return json.dumps(False)
    else:
        Uzanto.update(mono=Uzanto.mono+oro*40, oro=Uzanto.oro-oro).where(Uzanto.seanco == seanco).execute()
        return json.dumps(True)

tempiloj = {}
finitaj = []
fintempo = 600
def kontroli_tempon(tttu):
    global tempiloj
    global finitaj
    global fintempo
    while True:
        #gxisdatigi tempilo_{id}_uzanto{O|X} je tempiloj:
        exec('tempiloj["tempilo_{id}_uzantoO"] = tempilo_{id}.elapsed_time("uzantoO")'.format(id=tttu.id), globals())
        exec('tempiloj["tempilo_{id}_uzantoX"] = tempilo_{id}.elapsed_time("uzantoX")'.format(id=tttu.id), globals())
        if tttu.id in finitaj:
            break
        #kontroli se tempo finis por uzanto:
        if int(tempiloj['tempilo_{id}_uzantoO'.format(id=str(tttu.id))]) >= fintempo:
            rezigni(tttu.uzantoO.seanco, tttu.id, mana=True)
            break
        if int(tempiloj['tempilo_{id}_uzantoX'.format(id=str(tttu.id))]) >= fintempo:
            rezigni(tttu.uzantoX.seanco, tttu.id, mana=True)
            break
        sleep(1)

def Tabuloj(tabulo):
    T = dict([(str(_//9), tabulo[_:_+9]) for _ in range(0, len(tabulo), 9)])
    ##:nun T estas tiel: {'0':'oeexxxeeoe', '1':'eeeoxeoxe', ..., '8':'eoxeoxoxo'}
    for I, t in T.items():
        if t[0:3] == 'xxx' or t[3:6] == 'xxx' or t[6:9] == 'xxx' or t[0::3] == 'xxx' or t[1::3] == 'xxx' or t[2::3] == 'xxx' or t[0]+t[4]+t[8] == 'xxx' or t[2]+t[4]+t[6] == 'xxx':
            T[I] = {'t': T[I], 'S': 'X'}
        elif t[0:3] == 'ooo' or t[3:6] == 'ooo' or t[6:9] == 'ooo' or t[0::3] == 'ooo' or t[1::3] == 'ooo' or t[2::3] == 'ooo' or t[0]+t[4]+t[8] == 'ooo' or t[2]+t[4]+t[6] == 'ooo':
            T[I] = {'t': T[I], 'S': 'O'}
        elif not 'e' in t:
            T[I] = {'t': T[I], 'S': 'P'}
        else:
            T[I] = {'t': T[I], 'S': 'E'}
    ##:nun T estas tiel: {'0':{'t':'oeexxxeeoe', 'S': 'X'}, '1':{'t':'eoeoxeoxe', 'S':'E'}, ...}
    return T
    
@app.route('/rekomenci/<seanco>')
def rekomenci(seanco):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    naturo = Uzanto.get(Uzanto.id == 1)
    global tempiloj
    try:
        #atenda aliulo:
        tttu = Tu.get(Tu.uzantoX == naturo, Tu.uzantoO != uzanto)
        #anstatauxigi naturon per uzanto:
        tttu.uzantoX = uzanto
        tttu.vico = tttu.uzantoO
        tttu.save()
        #agordi tempilojn kaj komenci tempilon:
        exec("tempilo_{id}.switch_to('uzantoX')".format(id=str(tttu.id)), globals())
        exec("tempilo_{id}.switch_to('uzantoO')".format(id=str(tttu.id)), globals())
        threading.Thread(target=kontroli_tempon, args=(tttu,)).start()
    except Tu.DoesNotExist:
        try:
            #atenda uzanto:
            tttu = Tu.get(Tu.uzantoX == naturo, Tu.uzantoO == uzanto)
        except Tu.DoesNotExist:
            #krei ludon:
            tttu = Tu.create(uzantoO=uzanto, uzantoX=naturo, tabulo=81*'e', vico=naturo, venkulo=naturo)
            #krei tempilon:
            exec("tempilo_{id} = ChessTimer()".format(id=str(tttu.id)), globals())
            exec("tempiloj['tempilo_{id}_uzantoO'] = 0;tempiloj['tempilo_{id}_uzantoX'] = 0".format(id=str(tttu.id)), globals())
    return json.dumps({'stato':True, 'id':tttu.id})
        
@app.route('/rezigni/<seanco>/<id>')
def rezigni(seanco, id, mana=False):
    global finitaj
    if not mana:
        response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    naturo = Uzanto.get(Uzanto.id == 1)
    try:
        tttu = Tu.get((Tu.id == id) & (Tu.uzantoX != naturo) & ((Tu.uzantoO == uzanto) | (Tu.uzantoX == uzanto)) & (Tu.venkulo == naturo))
    except Tu.DoesNotExist:
        return json.dumps(False)
    if tttu.uzantoO == uzanto:
        tttu.venkulo = tttu.uzantoX
        oponanto = tttu.uzantoX
    elif tttu.uzantoX == uzanto:
        tttu.venkulo = tttu.uzantoO
        oponanto = tttu.uzantoO
    minuso = abs(uzanto.poento-oponanto.poento)
    oponanto.poento += int(minuso/2)+3
    if uzanto.poento > 0:
        uzanto.poento -= int(minuso/2)
    oponanto.save()
    uzanto.save()
    tttu.donita = True
    tttu.save()
    finitaj.append(tttu.id)
    if not mana:
        return json.dumps(True)

@app.route('/tabuloj/<seanco>')
def tabuloj(seanco):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    try:
        tttuj = Tu.select().where((Tu.uzantoO == uzanto) | (Tu.uzantoX == uzanto))
        if tttuj.count() == 0:
            raise Tu.DoesNotExist
    except Tu.DoesNotExist:
        #uzanto ne havas ludon:
        return json.dumps(False)
    tj = {}
    for tttu in tttuj:
        tj[str(tttu.id)] = {'uzantoO':tttu.uzantoO.nomo, 'uzantoX':tttu.uzantoX.nomo, 'venkulo':tttu.venkulo.nomo, 'vico':tttu.vico.nomo}
    return json.dumps(tj)

@app.route('/tabulo/<seanco>/<id>')
def tabulo(seanco, id):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    naturo = Uzanto.get(Uzanto.id == 1)
    global tempiloj
    global finitaj
    global fintempo
    try:
        tttu = Tu.get(((Tu.uzantoO == uzanto) | (Tu.uzantoX == uzanto)) & (Tu.id == id))
    except Tu.DoesNotExist:
        #preta por komenci unuan ludon:
        return json.dumps(False)
    tb = tttu.tabulo
    T = Tabuloj(tb)
    if uzanto == tttu.uzantoO:
        xo = 'o'
        oponanto = tttu.uzantoX
    elif uzanto == tttu.uzantoX:
        xo = 'x'
        oponanto = tttu.uzantoO
    tempilo_uzantoO = 0
    tempilo_uzantoX = 0
    tempilo_uzantoO = tempiloj['tempilo_{id}_uzantoO'.format(id=str(tttu.id))]
    tempilo_uzantoX = tempiloj['tempilo_{id}_uzantoX'.format(id=str(tttu.id))]
    return json.dumps({'Tabulo':T,'uzantoO':tttu.uzantoO.nomo, 'uzantoX':tttu.uzantoX.nomo, 'vico':tttu.vico.nomo, 'lastaIndekso':tttu.lastaIndekso, 'uzanto':uzanto.nomo, 'xo':xo, 'oponanto':oponanto.nomo, 'venkulo':tttu.venkulo.nomo, 'tempilo_uzantoO':int(tempilo_uzantoO), 'tempilo_uzantoX':int(tempilo_uzantoX), 'egalita':tttu.egalita, 'fintempo':fintempo})

@app.route('/agi/<seanco>/<id>/<I>/<i>')
def agi(seanco, id, I, i):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    naturo = Uzanto.get(Uzanto.id == 1)
    global tempiloj
    global finitaj
    global fintempo
    I = int(I)
    i = int(i)
    if I > 8 or i > 8 or I < 0 or i < 0:
        return json.dumps('حرکت اشتباه!')
    try:
        tttu = Tu.get((Tu.id == id) & (Tu.uzantoX != naturo) & ((Tu.uzantoO == uzanto) | (Tu.uzantoX == uzanto)) & (Tu.venkulo == naturo))
    except Tu.DoesNotExist:
        return json.dumps('بازی در جریان نیست!')
    if tttu.vico == uzanto and tttu.lastaIndekso != I and tttu.lastaIndekso != -1:
        return json.dumps('با توجه به حرکت قبلی حریف، تنها در خانه‌های طلایی مجاز به بازی هستید.')
    if tttu.vico != uzanto or tttu.vico == naturo:
        return json.dumps('نوبت شما نیست!')
    #kalkuli lasta stato de la tabulo:
    tb = tttu.tabulo
    T = Tabuloj(tb)
    if T[str(I)]['t'][i] != 'e':
        return json.dumps('خالی نیست!')
    if T[str(I)]['S'] != 'E':
        return json.dumps('برندهٔ این خانه مشخص شده است و نمی‌توان در آن بازی کرد!')
    #cxefa ago:
    if uzanto == tttu.uzantoO:
        tb = anstatauxigi(tb, I*9+i, 'o')
    elif uzanto == tttu.uzantoX:
        tb = anstatauxigi(tb, I*9+i, 'x')
    tttu.tabulo = tb
    tttu.save()
    #kalkuli nova stato de la tabulo:
    tb = tttu.tabulo
    T = Tabuloj(tb)
    ##kontroli se la ludo havas venkulo:
    S = ''
    for III in range(0,9):
        S += T[str(III)]['S']
    ##kontrolado de uzanto kun uzantoX kaj uzantoO estas por antauxzorgi kontraux malnecesaj kalkuloj:
    if uzanto == tttu.uzantoX and (S[0:3] == 'XXX' or S[3:6] == 'XXX' or S[6:9] == 'XXX' or S[0::3] == 'XXX' or S[1::3] == 'XXX' or S[2::3] == 'XXX' or S[0]+S[4]+S[8] == 'XXX' or S[2]+S[4]+S[6] == 'XXX'):
        finitaj.append(tttu.id)
        rezigni(tttu.uzantoO.seanco, tttu.id, mana=True)
    elif uzanto == tttu.uzantoO and (S[0:3] == 'OOO' or S[3:6] == 'OOO' or S[6:9] == 'OOO' or S[0::3] == 'OOO' or S[1::3] == 'OOO' or S[2::3] == 'OOO' or S[0]+S[4]+S[8] == 'OOO' or S[2]+S[4]+S[6] == 'OOO'):
        finitaj.append(tttu.id)
        rezigni(tttu.uzantoX.seanco, tttu.id, mana=True)
    elif not ('E' in S):
        finitaj.append(tttu.id)
        tttu.egalita = True
    if T[str(i)]['S'] == 'E':
        tttu.lastaIndekso = i
    #else:
    elif T[str(i)]['S'] == 'O' or T[str(i)]['S'] == 'X' or T[str(i)]['S'] == 'P':
        tttu.lastaIndekso = -1
    if tttu.vico == tttu.uzantoO:
        tttu.vico = tttu.uzantoX
        exec('tempilo_{id}.switch_to("uzantoX")'.format(id=str(tttu.id)), globals())
    elif tttu.vico == tttu.uzantoX:
        tttu.vico = tttu.uzantoO
        exec('tempilo_{id}.switch_to("uzantoO")'.format(id=str(tttu.id)), globals())
    if uzanto == tttu.uzantoO:
        xo = 'o'
        oponanto = tttu.uzantoX
    elif uzanto == tttu.uzantoX:
        xo = 'x'
        oponanto = tttu.uzantoO
    tempilo_uzantoO = 0
    tempilo_uzantoX = 0
    tempilo_uzantoO = tempiloj['tempilo_{id}_uzantoO'.format(id=str(tttu.id))]
    tempilo_uzantoX = tempiloj['tempilo_{id}_uzantoX'.format(id=str(tttu.id))]
    tttu.save()
    return json.dumps({'Tabulo':T, 'uzantoO':tttu.uzantoO.nomo, 'uzantoX':tttu.uzantoX.nomo, 'vico':tttu.vico.nomo, 'lastaIndekso':tttu.lastaIndekso, 'uzanto':uzanto.nomo, 'xo':xo, 'oponanto':oponanto.nomo, 'venkulo':tttu.venkulo.nomo, 'tempilo_uzantoO':int(tempilo_uzantoO), 'tempilo_uzantoX':int(tempilo_uzantoX), 'egalita':tttu.egalita, 'fintempo':fintempo})

@app.route('/nuligi/<seanco>/<id>')
def nuligi(seanco, id):
    response.content_type = "application/json; charset=utf-8"
    uzanto = Uzanto.get(Uzanto.seanco == seanco)
    naturo = Uzanto.get(Uzanto.id == 1)
    try:
        tttu = Tu.get((Tu.id == id) & (Tu.uzantoX == naturo) & (Tu.uzantoO == uzanto) & (Tu.venkulo == naturo))
        tttu.delete_instance()
        return json.dumps(True)
    except Tu.DoesNotExist:
        return json.dumps(False)
