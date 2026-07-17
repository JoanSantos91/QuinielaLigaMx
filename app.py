import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

APP_NAME = "quinielaJoanSantos"
DB_PATH = Path(__file__).with_name("quiniela.db")
TZ = ZoneInfo("America/Mexico_City")

PLAYERS = [
    ("TOL", "Diego", "Toluca"),
    ("TIG", "Lupe", "Tigres UANL"),
    ("AME", "Oscar", "América"),
    ("CHI", "Pity", "Guadalajara"),
    ("ATL", "Sholko", "Atlante"),
    ("MTY", "José Luis", "Monterrey"),
    ("ATS", "Lugo", "Atlas"),
    ("JUA", "Jorge Ceballos", "Juárez"),
    ("PUE", "Giovanni Román", "Puebla"),
    ("CAZ", "Joan Santos", "Cruz Azul"),
    ("SAN", "José Juan", "Santos Laguna"),
    ("PUM", "Ricky Zazueta", "Pumas UNAM"),
    ("NEC", "Sebastián", "Necaxa"),
    ("QRO", "Juan Antonio", "Querétaro"),
    ("LEO", "Roger", "León"),
    ("TIJ", "Laura", "Tijuana"),
    ("SLP", "Chino Terrazas", "Atlético de San Luis"),
    ("PAC", "Rodolfo Félix", "Pachuca"),
]

# Calendario Apertura 2026. Horarios del centro de México.
SCHEDULE = {
1:[("2026-07-16 19:00","Necaxa","Atlante"),("2026-07-16 21:00","Tijuana","Tigres UANL"),("2026-07-17 19:00","Atlético de San Luis","Cruz Azul"),("2026-07-17 19:00","León","Atlas"),("2026-07-17 21:00","Juárez","Puebla"),("2026-07-18 17:00","Pumas UNAM","Pachuca"),("2026-07-18 19:00","Monterrey","Santos Laguna"),("2026-07-18 19:07","Guadalajara","Toluca"),("2026-07-18 21:00","Querétaro","América")],
2:[("2026-07-21 19:00","Cruz Azul","Puebla"),("2026-07-21 21:00","Toluca","Pumas UNAM"),("2026-07-24 19:00","Tigres UANL","Atlético de San Luis"),("2026-07-24 21:00","Atlante","América"),("2026-07-24 21:00","Tijuana","León"),("2026-07-25 17:00","Guadalajara","Juárez"),("2026-07-25 21:00","Santos Laguna","Atlas"),("2026-07-26 17:00","Necaxa","Monterrey"),("2026-07-26 19:00","Pachuca","Querétaro")],
3:[("2026-07-31 19:00","Puebla","Guadalajara"),("2026-07-31 21:00","Atlético de San Luis","Tijuana"),("2026-07-31 21:00","Juárez","Pumas UNAM"),("2026-08-01 17:00","Querétaro","Tigres UANL"),("2026-08-01 19:00","León","Pachuca"),("2026-08-01 19:00","Atlas","Monterrey"),("2026-08-01 21:00","Cruz Azul","Atlante"),("2026-08-02 17:00","América","Santos Laguna"),("2026-08-02 19:00","Toluca","Necaxa")],
4:[("2026-08-15 17:00","Atlante","Toluca"),("2026-08-15 19:00","Monterrey","Juárez"),("2026-08-15 21:00","Atlas","Tigres UANL"),("2026-08-16 12:00","Pumas UNAM","Querétaro"),("2026-08-16 17:00","América","Atlético de San Luis"),("2026-08-16 19:00","Santos Laguna","Guadalajara"),("2026-08-16 21:00","Tijuana","Cruz Azul"),("2026-08-17 19:00","Necaxa","León"),("2026-08-17 21:00","Pachuca","Puebla")],
5:[("2026-08-21 19:00","Puebla","Santos Laguna"),("2026-08-21 21:00","Juárez","América"),("2026-08-22 17:00","Querétaro","Toluca"),("2026-08-22 17:00","Guadalajara","Tijuana"),("2026-08-22 19:00","León","Monterrey"),("2026-08-22 21:00","Tigres UANL","Atlante"),("2026-08-22 21:00","Cruz Azul","Atlas"),("2026-08-23 17:00","Atlético de San Luis","Pachuca"),("2026-08-23 19:00","Pumas UNAM","Necaxa")],
6:[("2026-08-28 19:00","Necaxa","Cruz Azul"),("2026-08-28 19:00","Atlante","León"),("2026-08-28 21:00","Tijuana","Pumas UNAM"),("2026-08-29 17:00","Atlas","Querétaro"),("2026-08-29 17:00","Pachuca","Guadalajara"),("2026-08-29 19:00","América","Puebla"),("2026-08-29 21:00","Santos Laguna","Tigres UANL"),("2026-08-30 18:00","Toluca","Juárez"),("2026-08-30 20:00","Monterrey","Atlético de San Luis")],
7:[("2026-09-04 19:00","Puebla","Toluca"),("2026-09-04 21:00","Juárez","Pachuca"),("2026-09-05 17:00","Atlético de San Luis","Guadalajara"),("2026-09-05 17:00","Querétaro","Monterrey"),("2026-09-05 19:00","Tigres UANL","Necaxa"),("2026-09-05 19:00","América","Tijuana"),("2026-09-05 21:00","Atlas","Atlante"),("2026-09-06 12:00","Pumas UNAM","León"),("2026-09-06 20:00","Cruz Azul","Santos Laguna")],
8:[("2026-09-11 19:00","Necaxa","Puebla"),("2026-09-11 21:00","Atlante","Pachuca"),("2026-09-11 21:00","Tijuana","Querétaro"),("2026-09-12 17:00","León","Atlético de San Luis"),("2026-09-12 19:00","Toluca","Atlas"),("2026-09-12 21:00","Cruz Azul","América"),("2026-09-13 18:00","Santos Laguna","Juárez"),("2026-09-13 18:00","Guadalajara","Pumas UNAM"),("2026-09-13 20:00","Monterrey","Tigres UANL")],
9:[("2026-09-18 19:00","Puebla","Atlante"),("2026-09-18 21:00","Juárez","Tigres UANL"),("2026-09-19 17:00","Atlas","Pumas UNAM"),("2026-09-19 17:00","Atlético de San Luis","Necaxa"),("2026-09-19 19:00","Monterrey","Cruz Azul"),("2026-09-19 21:00","América","Guadalajara"),("2026-09-20 18:00","Pachuca","Tijuana"),("2026-09-20 18:00","Toluca","Santos Laguna"),("2026-09-20 20:00","Querétaro","León")],
10:[("2026-09-25 19:00","Atlante","Monterrey"),("2026-09-25 21:00","Tijuana","Atlas"),("2026-09-26 17:00","Guadalajara","Querétaro"),("2026-09-26 19:00","Santos Laguna","Pachuca"),("2026-09-26 19:00","Tigres UANL","Puebla"),("2026-09-26 21:00","Cruz Azul","Toluca"),("2026-09-27 12:00","Pumas UNAM","Atlético de San Luis"),("2026-09-27 19:00","León","Juárez"),("2026-09-27 21:00","Necaxa","América")],
11:[("2026-10-09 19:00","Querétaro","Atlante"),("2026-10-09 19:00","Puebla","León"),("2026-10-09 21:00","Tigres UANL","Toluca"),("2026-10-10 17:00","Juárez","Tijuana"),("2026-10-10 19:00","Atlas","Guadalajara"),("2026-10-10 21:00","América","Monterrey"),("2026-10-11 17:00","Pachuca","Necaxa"),("2026-10-11 17:00","Atlético de San Luis","Santos Laguna"),("2026-10-11 19:00","Pumas UNAM","Cruz Azul")],
12:[("2026-10-16 19:00","Necaxa","Atlas"),("2026-10-16 21:00","Atlante","Pumas UNAM"),("2026-10-16 21:00","Tijuana","Puebla"),("2026-10-17 17:00","Guadalajara","Tigres UANL"),("2026-10-17 17:00","Santos Laguna","Querétaro"),("2026-10-17 19:00","León","América"),("2026-10-17 19:00","Toluca","Atlético de San Luis"),("2026-10-17 21:00","Cruz Azul","Juárez"),("2026-10-18 19:00","Monterrey","Pachuca")],
13:[("2026-10-20 19:00","Atlético de San Luis","Querétaro"),("2026-10-20 19:00","Juárez","Atlante"),("2026-10-20 21:00","Tigres UANL","León"),("2026-10-20 21:00","Guadalajara","Necaxa"),("2026-10-21 19:00","Puebla","Monterrey"),("2026-10-21 19:00","Atlas","América"),("2026-10-21 19:00","Toluca","Tijuana"),("2026-10-21 21:00","Pachuca","Cruz Azul"),("2026-10-21 21:00","Santos Laguna","Pumas UNAM")],
14:[("2026-10-23 19:00","Necaxa","Juárez"),("2026-10-23 21:00","Atlante","Atlético de San Luis"),("2026-10-24 17:00","León","Toluca"),("2026-10-24 19:00","Monterrey","Guadalajara"),("2026-10-24 21:00","Pumas UNAM","Tigres UANL"),("2026-10-25 17:00","Atlas","Puebla"),("2026-10-25 17:00","América","Pachuca"),("2026-10-25 19:00","Querétaro","Cruz Azul"),("2026-10-25 21:00","Tijuana","Santos Laguna")],
15:[("2026-10-30 19:00","Atlético de San Luis","Atlas"),("2026-10-30 19:00","Juárez","Querétaro"),("2026-10-30 21:00","Puebla","Pumas UNAM"),("2026-10-31 17:00","Pachuca","Tigres UANL"),("2026-10-31 19:00","Guadalajara","Atlante"),("2026-10-31 19:00","Monterrey","Tijuana"),("2026-10-31 21:00","América","Toluca"),("2026-11-01 17:00","Santos Laguna","Necaxa"),("2026-11-01 19:00","Cruz Azul","León")],
16:[("2026-11-06 19:00","Atlético de San Luis","Juárez"),("2026-11-06 19:00","Necaxa","Tijuana"),("2026-11-06 21:00","Atlante","Santos Laguna"),("2026-11-07 17:00","Atlas","Pachuca"),("2026-11-07 17:00","Tigres UANL","Cruz Azul"),("2026-11-07 19:00","Toluca","Monterrey"),("2026-11-07 21:00","Pumas UNAM","América"),("2026-11-08 18:00","Querétaro","Puebla"),("2026-11-08 20:00","León","Guadalajara")],
17:[("2026-11-20 19:00","Puebla","Atlético de San Luis"),("2026-11-20 21:00","Juárez","Atlas"),("2026-11-20 21:00","Tijuana","Atlante"),("2026-11-21 17:00","Santos Laguna","León"),("2026-11-21 17:00","Pachuca","Toluca"),("2026-11-21 19:00","Pumas UNAM","Monterrey"),("2026-11-21 21:00","Tigres UANL","América"),("2026-11-22 17:00","Guadalajara","Cruz Azul"),("2026-11-22 19:00","Querétaro","Necaxa")],
}

TEAM_SHORT = {"Atlético de San Luis":"San Luis","Guadalajara":"Chivas","Pumas UNAM":"Pumas","Santos Laguna":"Santos","Tigres UANL":"Tigres"}

PLAYER_PINS = {
    "TOL":"4182", "TIG":"5731", "AME":"2604", "CHI":"8395", "ATL":"1476", "MTY":"6928",
    "ATS":"3159", "JUA":"7843", "PUE":"5267", "CAZ":"9041", "SAN":"2386", "PUM":"6714",
    "NEC":"4529", "QRO":"8163", "LEO":"3907", "TIJ":"7452", "SLP":"1849", "PAC":"6275",
}
ALL_TEAMS = sorted({t for games in SCHEDULE.values() for _,h,a in games for t in (h,a)})

def hash_pin(pin): return hashlib.sha256(pin.encode()).hexdigest()
def conn():
    c=sqlite3.connect(DB_PATH,check_same_thread=False); c.row_factory=sqlite3.Row; return c
def now_local(): return datetime.now(TZ).replace(tzinfo=None)

def init_db():
    with conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,code TEXT UNIQUE,name TEXT,team TEXT,pin_hash TEXT,is_admin INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS rounds(id INTEGER PRIMARY KEY,number INTEGER UNIQUE,name TEXT,deadline TEXT,is_open INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS matches(id INTEGER PRIMARY KEY,round_id INTEGER,home_team TEXT,away_team TEXT,kickoff TEXT,home_score INTEGER,away_score INTEGER,UNIQUE(round_id,home_team,away_team));
        CREATE TABLE IF NOT EXISTS predictions(id INTEGER PRIMARY KEY,user_id INTEGER,match_id INTEGER,home_score INTEGER,away_score INTEGER,submitted_at TEXT,UNIQUE(user_id,match_id));
        CREATE TABLE IF NOT EXISTS survivor_picks(id INTEGER PRIMARY KEY,user_id INTEGER,round_id INTEGER,team TEXT,submitted_at TEXT,UNIQUE(user_id,round_id),UNIQUE(user_id,team));
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE IF NOT EXISTS champion_eligible(team TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS champion_picks(id INTEGER PRIMARY KEY,user_id INTEGER UNIQUE,team TEXT UNIQUE,pick_order INTEGER,submitted_at TEXT);
        ''')
        c.execute("INSERT OR IGNORE INTO users(code,name,team,pin_hash,is_admin) VALUES(?,?,?,?,1)",("ADMIN","Administrador","",hash_pin("2026")))
        for code,name,team in PLAYERS:
            c.execute('''INSERT INTO users(code,name,team,pin_hash,is_admin) VALUES(?,?,?,?,0)
            ON CONFLICT(code) DO UPDATE SET name=excluded.name,team=excluded.team,pin_hash=excluded.pin_hash''',(code,name,team,hash_pin(PLAYER_PINS[code])))
        for n,games in SCHEDULE.items():
            deadline=min(datetime.fromisoformat(x[0]) for x in games).isoformat(timespec='minutes')
            c.execute("INSERT OR IGNORE INTO rounds(number,name,deadline,is_open) VALUES(?,?,?,0)",(n,f"Jornada {n}",deadline))
            rid=c.execute("SELECT id FROM rounds WHERE number=?",(n,)).fetchone()[0]
            for ko,h,a in games: c.execute("INSERT OR IGNORE INTO matches(round_id,home_team,away_team,kickoff) VALUES(?,?,?,?)",(rid,h,a,ko))
        c.execute("INSERT OR IGNORE INTO settings VALUES('champion_draft_active','0')")

def result_type(h,a): return None if h is None or a is None else ('L' if h>a else 'V' if h<a else 'E')
def score_prediction(ph,pa,rh,ra):
    if rh is None or ra is None:return 0
    return 2 if (ph,pa)==(rh,ra) else (1 if result_type(ph,pa)==result_type(rh,ra) else 0)

def inject_style():
    st.markdown('''<style>
    .stApp{background:linear-gradient(180deg,#07140e,#0b1d14 45%,#07100c)}[data-testid="stHeader"]{background:transparent}.block-container{max-width:1120px;padding-top:1.2rem}
    .brand{display:flex;align-items:center;gap:14px;margin:4px 0 18px}.ball{width:58px;height:58px;border-radius:50%;display:grid;place-items:center;background:#d7b65d;color:#07140e;font-size:30px;font-weight:900;border:3px solid #f4dfa2}.brand h1{font-size:clamp(1.55rem,4vw,2.5rem);margin:0;color:#f5f4e8}.brand p{margin:0;color:#b9c9bf}.welcome{padding:18px;border:1px solid #31513e;border-radius:18px;background:#0e2519;margin-bottom:14px}.welcome b{color:#f0d37e}div[data-testid="stMetric"]{background:#10291c;border:1px solid #31513e;padding:12px;border-radius:15px}.stButton>button,.stDownloadButton>button{border-radius:12px;font-weight:700}
    </style>''',unsafe_allow_html=True)
def brand(): st.markdown(f'<div class="brand"><div class="ball">⚽</div><div><h1>{APP_NAME}</h1><p>Apertura 2026 · Quiniela, Survivor, duelos y campeón</p></div></div>',unsafe_allow_html=True)

def standings():
    with conn() as c:
        users=c.execute("SELECT id,name,team FROM users WHERE is_admin=0").fetchall()
        rows=c.execute('''SELECT p.user_id,r.number jornada,p.home_score ph,p.away_score pa,m.home_score rh,m.away_score ra FROM predictions p JOIN matches m ON m.id=p.match_id JOIN rounds r ON r.id=m.round_id''').fetchall()
    d={u['id']:{'USER_ID':u['id'],'JUGADOR':u['name'],'EQUIPO':TEAM_SHORT.get(u['team'],u['team']),'TOTAL':0} for u in users}
    for x in rows:
        pts=score_prediction(x['ph'],x['pa'],x['rh'],x['ra']); col=f"J{x['jornada']}"; d[x['user_id']][col]=d[x['user_id']].get(col,0)+pts; d[x['user_id']]['TOTAL']+=pts
    df=pd.DataFrame(d.values()).fillna(0); js=sorted([x for x in df if x.startswith('J')],key=lambda x:int(x[1:])); df=df[['USER_ID','JUGADOR','EQUIPO','TOTAL']+js].sort_values(['TOTAL','JUGADOR'],ascending=[False,True]).reset_index(drop=True); df.insert(0,'POS',range(1,len(df)+1)); return df

def login():
    brand(); st.subheader('Selecciona tu clave')
    opts={f'{c} · {n}':(c,n,t) for c,n,t in PLAYERS}; opts['ADMIN · Administrador']=('ADMIN','Administrador','')
    code,name,team=opts[st.selectbox('Clave de participante',list(opts))]
    if code!='ADMIN': st.markdown(f'<div class="welcome">Hola, <b>{name}</b><br>Equipo para duelos: <b>{TEAM_SHORT.get(team,team)}</b></div>',unsafe_allow_html=True)
    pin=st.text_input('PIN personal',type='password')
    if st.button('Entrar',type='primary',use_container_width=True):
        with conn() as c:u=c.execute("SELECT * FROM users WHERE code=? AND pin_hash=?",(code,hash_pin(pin))).fetchone()
        if u:st.session_state.user=dict(u);st.rerun()
        else:st.error('PIN incorrecto.')

def round_points(uid,j):
    with conn() as c:r=c.execute('''SELECT p.home_score ph,p.away_score pa,m.home_score rh,m.away_score ra FROM predictions p JOIN matches m ON m.id=p.match_id JOIN rounds r ON r.id=m.round_id WHERE p.user_id=? AND r.number=?''',(uid,j)).fetchall()
    return sum(score_prediction(x['ph'],x['pa'],x['rh'],x['ra']) for x in r)
def round_complete(j):
    with conn() as c:r=c.execute('''SELECT COUNT(*) n,SUM(CASE WHEN m.home_score IS NOT NULL AND m.away_score IS NOT NULL THEN 1 ELSE 0 END) d FROM matches m JOIN rounds r ON r.id=m.round_id WHERE r.number=?''',(j,)).fetchone()
    return bool(r['n'] and r['n']==r['d'])
def duels_round(j):
    with conn() as c:
        users={u['team']:u for u in c.execute("SELECT id,name,team FROM users WHERE is_admin=0")}; games=c.execute('''SELECT m.home_team,m.away_team FROM matches m JOIN rounds r ON r.id=m.round_id WHERE r.number=? ORDER BY m.id''',(j,)).fetchall()
    out=[]; complete=round_complete(j)
    for g in games:
        h,a=users.get(g['home_team']),users.get(g['away_team'])
        if not h or not a:continue
        hp,ap=round_points(h['id'],j),round_points(a['id'],j)
        if not complete:hd=ad=0;res='Pendiente'
        elif hp>ap:hd,ad,res=3,0,h['name']
        elif hp<ap:hd,ad,res=0,3,a['name']
        else:hd,ad,res=1,1,'Empate'
        out.append({'J':j,'LOCAL':h['name'],'VISITANTE':a['name'],'PUNTOS QUINIELA':f'{hp}-{ap}','PTS DUELO':f'{hd}-{ad}','RESULTADO':res})
    return out
def duel_standings():
    d={n:{'JUGADOR':n,'EQUIPO':TEAM_SHORT.get(t,t),'PTS':0,'JG':0,'JE':0,'JP':0} for _,n,t in PLAYERS}
    for j in range(1,18):
        if not round_complete(j):continue
        for x in duels_round(j):
            a,b=x['LOCAL'],x['VISITANTE']; pa,pb=map(int,x['PTS DUELO'].split('-'));d[a]['PTS']+=pa;d[b]['PTS']+=pb
            if pa==3:d[a]['JG']+=1;d[b]['JP']+=1
            elif pb==3:d[b]['JG']+=1;d[a]['JP']+=1
            else:d[a]['JE']+=1;d[b]['JE']+=1
    df=pd.DataFrame(d.values()).sort_values(['PTS','JG','JUGADOR'],ascending=[False,False,True]).reset_index(drop=True);df.insert(0,'POS',range(1,len(df)+1));return df

def survivor_status():
    with conn() as c:
        users=c.execute("SELECT id,name FROM users WHERE is_admin=0").fetchall(); picks=c.execute('''SELECT sp.user_id,sp.team,m.home_team,m.away_team,m.home_score,m.away_score FROM survivor_picks sp JOIN rounds r ON r.id=sp.round_id LEFT JOIN matches m ON m.round_id=r.id AND (m.home_team=sp.team OR m.away_team=sp.team)''').fetchall()
    d={u['id']:{'JUGADOR':u['name'],'VIDAS':3.0,'ELECCIONES':0} for u in users}
    for x in picks:
        d[x['user_id']]['ELECCIONES']+=1
        if x['home_score'] is None:continue
        gf=x['home_score'] if x['team']==x['home_team'] else x['away_score'];ga=x['away_score'] if x['team']==x['home_team'] else x['home_score']
        d[x['user_id']]['VIDAS']-=1 if gf<ga else (.5 if gf==ga else 0)
    df=pd.DataFrame(d.values()).sort_values(['VIDAS','JUGADOR'],ascending=[False,True]).reset_index(drop=True);df.insert(0,'POS',range(1,len(df)+1));return df

def survivor_pick(user,rnd,locked):
    with conn() as c:
        used=[x['team'] for x in c.execute("SELECT team FROM survivor_picks WHERE user_id=?",(user['id'],))];old=c.execute("SELECT team FROM survivor_picks WHERE user_id=? AND round_id=?",(user['id'],rnd['id'])).fetchone();ms=c.execute("SELECT home_team,away_team FROM matches WHERE round_id=?",(rnd['id'],)).fetchall()
    teams=sorted({t for m in ms for t in (m['home_team'],m['away_team'])});avail=[t for t in teams if t not in used or (old and t==old['team'])]
    st.caption('Gana: conserva vidas · Empata: −0.5 · Pierde: −1 · No se repiten equipos.')
    if not avail:return st.warning('No hay equipos disponibles.')
    pick=st.selectbox('Equipo Survivor',avail,format_func=lambda x:TEAM_SHORT.get(x,x),disabled=locked)
    if st.button('Guardar Survivor',type='primary',disabled=locked,use_container_width=True):
        try:
            with conn() as c:c.execute('''INSERT INTO survivor_picks(user_id,round_id,team,submitted_at) VALUES(?,?,?,?) ON CONFLICT(user_id,round_id) DO UPDATE SET team=excluded.team,submitted_at=excluded.submitted_at''',(user['id'],rnd['id'],pick,now_local().isoformat()))
            st.success('Elección guardada.')
        except sqlite3.IntegrityError:st.error('Ese equipo ya fue utilizado.')

def champion_order():return standings().head(8)[['POS','USER_ID','JUGADOR','TOTAL']]
def champion_view(user=None,admin=False):
    with conn() as c:
        active=c.execute("SELECT value FROM settings WHERE key='champion_draft_active'").fetchone()['value']=='1';elig=[x['team'] for x in c.execute("SELECT team FROM champion_eligible")];picks=c.execute('''SELECT cp.pick_order,u.id user_id,u.name,cp.team FROM champion_picks cp JOIN users u ON u.id=cp.user_id ORDER BY cp.pick_order''').fetchall()
    if picks:st.dataframe(pd.DataFrame([{'TURNO':x['pick_order'],'JUGADOR':x['name'],'CAMPEÓN':TEAM_SHORT.get(x['team'],x['team'])} for x in picks]),hide_index=True,use_container_width=True)
    if not active:return st.info('La selección de campeón no está activa.')
    if len(picks)>=8:return st.success('Selección finalizada.')
    order=champion_order();picked_ids={x['user_id'] for x in picks};picked_teams={x['team'] for x in picks};nxt=order[~order.USER_ID.isin(picked_ids)].iloc[0];st.write(f"Turno actual: **#{int(nxt.POS)} {nxt.JUGADOR}**")
    if admin:return
    if user['id'] not in set(order.USER_ID):return st.warning('Solo participan los primeros 8 del rol regular.')
    if user['id'] in picked_ids:return st.success('Ya elegiste.')
    if user['id']!=int(nxt.USER_ID):return st.warning('Todavía no es tu turno.')
    avail=[t for t in elig if t not in picked_teams]
    if not avail:return st.error('El administrador debe cargar los equipos elegibles.')
    team=st.selectbox('Equipo campeón',avail,format_func=lambda x:TEAM_SHORT.get(x,x))
    if st.button('Confirmar campeón',type='primary',use_container_width=True):
        with conn() as c:c.execute("INSERT INTO champion_picks(user_id,team,pick_order,submitted_at) VALUES(?,?,?,?)",(user['id'],team,len(picks)+1,now_local().isoformat()))
        st.rerun()

def player_view(user):
    st.markdown(f'<div class="welcome">Bienvenido, <b>{user["name"]}</b> · Equipo: <b>{TEAM_SHORT.get(user["team"],user["team"])}</b></div>',unsafe_allow_html=True)
    df=standings();me=df[df.JUGADOR==user['name']].iloc[0];dv=duel_standings().query('JUGADOR==@user["name"]').iloc[0];sv=survivor_status().query('JUGADOR==@user["name"]').iloc[0]
    a,b,c,d=st.columns(4);a.metric('Posición',f"#{int(me.POS)}");b.metric('Puntos',int(me.TOTAL));c.metric('Duelos',int(dv.PTS));d.metric('Vidas',f"{sv.VIDAS:g}")
    tabs=st.tabs(['Pronósticos','Survivor','Tabla general','Duelos','Campeón'])
    with tabs[0]:
        with conn() as c:rounds=c.execute("SELECT * FROM rounds ORDER BY number").fetchall()
        rd={f"Jornada {r['number']}":r for r in rounds};rnd=rd[st.selectbox('Jornada',list(rd))];locked=not rnd['is_open'] or now_local()>datetime.fromisoformat(rnd['deadline'])
        st.info('Jornada abierta' if not locked else 'Jornada cerrada')
        with conn() as c:ms=c.execute("SELECT * FROM matches WHERE round_id=? ORDER BY kickoff",(rnd['id'],)).fetchall();old={x['match_id']:x for x in c.execute("SELECT * FROM predictions WHERE user_id=?",(user['id'],))}
        vals=[]
        for m in ms:
            st.write(f"**{TEAM_SHORT.get(m['home_team'],m['home_team'])} vs {TEAM_SHORT.get(m['away_team'],m['away_team'])}**");x=old.get(m['id']);q1,q2=st.columns(2);h=q1.number_input(m['home_team'],0,20,int(x['home_score']) if x else 0,key=f"h{m['id']}",disabled=locked);a=q2.number_input(m['away_team'],0,20,int(x['away_score']) if x else 0,key=f"a{m['id']}",disabled=locked);vals.append((m['id'],h,a))
        if st.button('Guardar pronósticos',type='primary',disabled=locked,use_container_width=True):
            with conn() as c:
                for mid,h,a in vals:c.execute('''INSERT INTO predictions(user_id,match_id,home_score,away_score,submitted_at) VALUES(?,?,?,?,?) ON CONFLICT(user_id,match_id) DO UPDATE SET home_score=excluded.home_score,away_score=excluded.away_score,submitted_at=excluded.submitted_at''',(user['id'],mid,h,a,now_local().isoformat()))
            st.success('Guardados.')
    with tabs[1]:
        with conn() as c:rounds=c.execute("SELECT * FROM rounds ORDER BY number").fetchall()
        rd={f"Jornada {r['number']}":r for r in rounds};rnd=rd[st.selectbox('Jornada Survivor',list(rd))];locked=not rnd['is_open'] or now_local()>datetime.fromisoformat(rnd['deadline']);survivor_pick(user,rnd,locked);st.dataframe(survivor_status(),hide_index=True,use_container_width=True)
    with tabs[2]:st.dataframe(df.drop(columns=['USER_ID']),hide_index=True,use_container_width=True)
    with tabs[3]:st.dataframe(duel_standings(),hide_index=True,use_container_width=True);j=st.selectbox('Detalle jornada',range(1,18));st.dataframe(pd.DataFrame(duels_round(j)),hide_index=True,use_container_width=True)
    with tabs[4]:champion_view(user=user)

def admin_view():
    tabs=st.tabs(['Resultados','Activar jornadas','Participantes y PIN','Tabla','Duelos','Survivor','Campeón'])
    with tabs[0]:
        with conn() as c:ms=c.execute('''SELECT m.*,r.number FROM matches m JOIN rounds r ON r.id=m.round_id ORDER BY r.number,m.kickoff''').fetchall()
        opts={f"J{x['number']} · {x['home_team']} vs {x['away_team']}":x for x in ms};m=opts[st.selectbox('Partido',list(opts))];a,b=st.columns(2);hs=a.number_input(m['home_team'],0,20,int(m['home_score'] or 0));vs=b.number_input(m['away_team'],0,20,int(m['away_score'] or 0))
        if st.button('Guardar resultado',type='primary'):
            with conn() as c:c.execute("UPDATE matches SET home_score=?,away_score=? WHERE id=?",(hs,vs,m['id']))
            st.success('Resultado guardado.')
    with tabs[1]:
        with conn() as c:rs=c.execute("SELECT * FROM rounds ORDER BY number").fetchall()
        for r in rs:
            a,b=st.columns([4,1]);a.write(f"Jornada {r['number']} · {'ABIERTA' if r['is_open'] else 'CERRADA'} · {r['deadline']}")
            if b.button('Cerrar' if r['is_open'] else 'Activar',key=f"r{r['id']}"):
                with conn() as c:c.execute("UPDATE rounds SET is_open=1-is_open WHERE id=?",(r['id'],))
                st.rerun()
    with tabs[2]:
        pdf=pd.DataFrame([(c,n,TEAM_SHORT.get(t,t),PLAYER_PINS[c]) for c,n,t in PLAYERS],columns=['CLAVE','PARTICIPANTE','EQUIPO','PIN']);st.warning('Comparte cada PIN de forma privada.');st.dataframe(pdf,hide_index=True,use_container_width=True);st.download_button('Descargar accesos',pdf.to_csv(index=False).encode('utf-8-sig'),'accesos_privados.csv')
    with tabs[3]:st.dataframe(standings().drop(columns=['USER_ID']),hide_index=True,use_container_width=True)
    with tabs[4]:st.dataframe(duel_standings(),hide_index=True,use_container_width=True);j=st.selectbox('Jornada duelos',range(1,18));st.dataframe(pd.DataFrame(duels_round(j)),hide_index=True,use_container_width=True)
    with tabs[5]:st.dataframe(survivor_status(),hide_index=True,use_container_width=True)
    with tabs[6]:
        st.dataframe(champion_order().drop(columns=['USER_ID']),hide_index=True,use_container_width=True)
        with conn() as c:current=[x['team'] for x in c.execute("SELECT team FROM champion_eligible")];active=c.execute("SELECT value FROM settings WHERE key='champion_draft_active'").fetchone()['value']=='1'
        elig=st.multiselect('Equipos elegibles',ALL_TEAMS,default=current)
        if st.button('Guardar equipos elegibles'):
            with conn() as c:c.execute("DELETE FROM champion_eligible");c.executemany("INSERT INTO champion_eligible VALUES(?)",[(x,) for x in elig])
            st.success('Guardados.')
        if st.button('Desactivar selección' if active else 'Activar selección',type='primary'):
            with conn() as c:c.execute("UPDATE settings SET value=? WHERE key='champion_draft_active'",('0' if active else '1',))
            st.rerun()
        champion_view(admin=True)
        if st.button('Reiniciar selección de campeón'):
            with conn() as c:c.execute("DELETE FROM champion_picks")
            st.rerun()

def main():
    st.set_page_config(page_title=APP_NAME,page_icon='⚽',layout='wide',initial_sidebar_state='collapsed');inject_style();init_db()
    if 'user' not in st.session_state:return login()
    brand();u=st.session_state.user;a,b=st.columns([5,1]);a.caption('Quiniela 2/1/0 · Duelos 3/1/0 · Survivor 3 vidas')
    if b.button('Salir',use_container_width=True):del st.session_state.user;st.rerun()
    admin_view() if u['is_admin'] else player_view(u)
if __name__=='__main__':main()
