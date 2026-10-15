"""Sayı Kâşifleri — canlı, sunucu doğrulamalı sınıf yarışması.
Öğrenci adları ve puanları yalnızca RAM'de saklanır; veritabanı kullanılmaz.
"""
import asyncio
import io
import json
import os
import random
import re
import secrets
import time
from pathlib import Path

import qrcode
from aiohttp import WSMsgType, web

BASE = Path(__file__).resolve().parent
QUESTIONS = json.loads((BASE / 'web' / 'sorular.json').read_text(encoding='utf-8'))
ROOMS = {}
MAX_PLAYERS = 60
MAX_ROOMS = 150
MAX_CUSTOM_QUESTIONS = 60
TEAM_NAMES = ['Mercan Takımı', 'Zümrüt Takımı', 'Safir Takımı', 'Altın Takımı']
CATEGORIES = ('karisik', 'carpan', 'kat', 'asal')


def now_ms():
    return round(time.time() * 1000)


def options_from(data):
    data = data if isinstance(data, dict) else {}
    mode = data.get('mode') if data.get('mode') in ('bireysel', 'takim') else 'bireysel'
    cat = data.get('category') if data.get('category') in CATEGORIES else 'karisik'
    number = data.get('count')
    count = number if type(number) is int and number in (5, 10, 15, 20) else 10
    number = data.get('seconds')
    seconds = number if type(number) is int and number in (15, 20, 30, 45) else 20
    number = data.get('teams')
    teams = number if type(number) is int and number in (2, 3, 4) else 2
    source = 'custom' if data.get('source') == 'custom' else 'hazir'
    return {'mode': mode, 'category': cat, 'count': count, 'seconds': seconds, 'teams': teams,
            'source': source}


def validate_custom_questions(raw):
    """Öğretmenin sorularını yalnızca sunucuda denetle; doğru yanıtları öğrenciye sızdırma."""
    if not isinstance(raw, list) or not (1 <= len(raw) <= MAX_CUSTOM_QUESTIONS):
        raise ValueError(f'1 ile {MAX_CUSTOM_QUESTIONS} arasında kendi sorunuzu ekleyin.')
    cleaned = []
    for i, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f'{i}. soru geçersiz.')
        title, choices, answer, explain = (item.get('text'), item.get('options'),
                                            item.get('correct'), item.get('explain', ''))
        if not isinstance(title, str) or not (3 <= len(title.strip()) <= 280):
            raise ValueError(f'{i}. sorunun metni 3–280 karakter olmalıdır.')
        if not isinstance(choices, list) or len(choices) != 4 or any(
                not isinstance(opt, str) or not (1 <= len(opt.strip()) <= 100) for opt in choices):
            raise ValueError(f'{i}. soru için dört şık (en fazla 100 karakter) girin.')
        opts = [opt.strip() for opt in choices]
        if len(set(opt.casefold() for opt in opts)) != 4:
            raise ValueError(f'{i}. sorunun cevap seçenekleri farklı olmalıdır.')
        if type(answer) is not int or answer not in range(4):
            raise ValueError(f'{i}. sorunun doğru seçeneğini A, B, C veya D olarak belirtin.')
        if not isinstance(explain, str) or len(explain.strip()) > 240:
            raise ValueError(f'{i}. sorunun açıklaması en fazla 240 karakter olmalıdır.')
        cleaned.append({'text': title.strip(), 'options': opts, 'correct': answer,
                        'explain': explain.strip()})
    return cleaned


def build_questions(config, custom_questions=None):
    if config.get('source') == 'custom':
        chosen = random.sample(custom_questions, min(config['count'], len(custom_questions)))
        result = []
        for q in chosen:
            shuffle = list(range(4))
            random.shuffle(shuffle)
            result.append({'text': q['text'], 'options': [q['options'][j] for j in shuffle],
                           'correct': shuffle.index(q['correct']), 'explain': q['explain'],
                           'category': 'ozel'})
        return result
    if config['category'] == 'karisik':
        pool = []
        for key in ('carpan', 'kat', 'asal'):
            pool.extend((key, q) for q in QUESTIONS[key])
        random.shuffle(pool)
        # First questions from all three topics, followed by shuffled remainder.
        first = [(cat, random.choice(QUESTIONS[cat])) for cat in ('carpan', 'kat', 'asal')]
        random.shuffle(first)
        used = {id(q) for _, q in first}
        pool = first + [(cat, q) for cat, q in pool if id(q) not in used]
    else:
        pool = [(config['category'], q) for q in QUESTIONS[config['category']]]
        random.shuffle(pool)
    result = []
    for cat, q in pool[:config['count']]:
        opts = [q['correct'], *q['wrong']]
        random.shuffle(opts)
        result.append({'text': q['text'], 'options': opts, 'correct': opts.index(q['correct']),
                       'explain': q['explain'], 'category': cat})
    return result


def room_code():
    for _ in range(200):
        candidate = f'{random.SystemRandom().randrange(0, 1000000):06d}'
        if candidate not in ROOMS:
            return candidate
    raise RuntimeError('Oda kodu oluşturulamadı')


def make_room(config, ws, submitted_questions=None):
    custom_questions = (validate_custom_questions(submitted_questions)
                        if config['source'] == 'custom' else None)
    if custom_questions:
        config['count'] = min(config['count'], len(custom_questions))
    if len(ROOMS) >= MAX_ROOMS:
        for code, room in list(ROOMS.items()):
            if time.monotonic() - room['last'] > 7200:
                ROOMS.pop(code, None)
        if len(ROOMS) >= MAX_ROOMS:
            raise ValueError('Şu anda yeni oda açılamıyor.')
    code = room_code()
    room = {'code': code, 'host_token': secrets.token_urlsafe(26), 'host_ws': ws,
            'players': {}, 'config': config, 'custom_questions': custom_questions,
            'questions': build_questions(config, custom_questions),
            'index': -1, 'status': 'lobby', 'answers': {}, 'end_monotonic': 0,
            'deadline_ms': 0, 'job': None, 'last': time.monotonic()}
    ROOMS[code] = room
    return room


def board(room):
    players = sorted(room['players'].values(), key=lambda p: (-p['score'], -p['correct'], p['joined']))
    rank = 0
    previous = None
    result = []
    for i, p in enumerate(players):
        scorekey = (p['score'], p['correct'])
        if scorekey != previous:
            rank = i + 1
        previous = scorekey
        result.append({'name': p['name'], 'score': p['score'], 'correct': p['correct'],
                       'team': p['team'], 'online': p['ws'] is not None and not p['ws'].closed,
                       'rank': rank})
    return result


def team_board(room):
    rows = []
    for i in range(room['config']['teams']):
        people = [p for p in room['players'].values() if p['team'] == i]
        rows.append({'team': i, 'name': TEAM_NAMES[i], 'score': sum(p['score'] for p in people),
                     'correct': sum(p['correct'] for p in people), 'players': len(people)})
    return sorted(rows, key=lambda t: (-t['score'], -t['correct'], t['team']))


def snapshot(room, role, token):
    room['last'] = time.monotonic()
    current = None
    if 0 <= room['index'] < len(room['questions']):
        q = room['questions'][room['index']]
        current = {'text': q['text'], 'options': q['options'], 'category': q['category'],
                   'number': room['index'] + 1, 'total': len(room['questions']),
                   'deadline': room['deadline_ms']}
        if room['status'] in ('reveal', 'finished'):
            current.update({'correct': q['correct'], 'explain': q['explain']})
    me = room['players'].get(token) if role == 'player' else None
    answered = token in room['answers'] if role == 'player' else False
    payload = {'serverNow': now_ms(), 'type': 'state', 'role': role, 'code': room['code'], 'status': room['status'],
               'config': room['config'], 'question': current, 'players': board(room),
               'teams': team_board(room) if room['config']['mode'] == 'takim' else [],
               'playerCount': len(room['players']),
               'onlineCount': sum(bool(p['ws'] and not p['ws'].closed) for p in room['players'].values()),
               'answerCount': len(room['answers']),
               'me': {'name': me['name'], 'score': me['score'], 'correct': me['correct'],
                      'team': me['team'], 'answered': answered,
                      'choice': room['answers'].get(token, {}).get('choice'),
                      'earned': room['answers'].get(token, {}).get('earned', 0)} if me else None}
    return payload


async def send_json(ws, data):
    if ws is not None and not ws.closed:
        try:
            await ws.send_json(data)
        except ConnectionError:
            pass


async def publish(room):
    await send_json(room['host_ws'], snapshot(room, 'host', room['host_token']))
    for token, p in list(room['players'].items()):
        await send_json(p['ws'], snapshot(room, 'player', token))


def cancel_job(room):
    task = room.get('job')
    if task and not task.done() and task is not asyncio.current_task():
        task.cancel()
    room['job'] = None


def all_active_players_answered(room):
    """Soruyu, bağlı tüm öğrenciler cevapladığında erken tamamla.

    Bağlantısı kopmuş öğrenciler soruyu gereksiz yere açık tutmaz;
    sınıfta hiç aktif öğrenci kalmadıysa normal zaman aşımı sürer.
    """
    active = [token for token, player in room['players'].items()
              if player['ws'] is not None and not player['ws'].closed]
    return bool(active) and all(token in room['answers'] for token in active)


async def question_timeout(room, index):
    try:
        await asyncio.sleep(room['config']['seconds'])
        if room['status'] == 'question' and room['index'] == index:
            await reveal(room)
    except asyncio.CancelledError:
        pass


async def advance(room):
    if room['status'] not in ('lobby', 'reveal'):
        return
    if not room['players']:
        raise ValueError('Yarışmaya başlamadan önce en az bir öğrenci katılmalı.')
    cancel_job(room)
    room['index'] += 1
    if room['index'] >= len(room['questions']):
        room['status'] = 'finished'
        room['deadline_ms'] = 0
    else:
        room['status'] = 'question'
        room['answers'] = {}
        room['end_monotonic'] = time.monotonic() + room['config']['seconds']
        room['deadline_ms'] = now_ms() + room['config']['seconds'] * 1000
        room['job'] = asyncio.create_task(question_timeout(room, room['index']))
    await publish(room)


async def reveal(room):
    if room['status'] != 'question':
        return
    cancel_job(room)
    room['status'] = 'reveal'
    question = room['questions'][room['index']]
    for token, rec in room['answers'].items():
        if token not in room['players']:
            continue
        if rec['choice'] == question['correct']:
            earned = 1000 + round(500 * rec['remaining'] / room['config']['seconds'])
            room['players'][token]['score'] += earned
            room['players'][token]['correct'] += 1
        else:
            earned = 0
        rec['earned'] = earned
    await publish(room)


async def api_websocket(request):
    ws = web.WebSocketResponse(heartbeat=25, max_msg_size=128 * 1024)
    await ws.prepare(request)
    affiliation = None
    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                if msg.type == WSMsgType.ERROR:
                    break
                continue
            try:
                data = json.loads(msg.data)
                if not isinstance(data, dict):
                    raise ValueError('Geçersiz istek.')
                action = data.get('action')
                if action == 'create':
                    if affiliation:
                        raise ValueError('Bu pencerede zaten bir odaya bağlısınız.')
                    config = options_from(data.get('config'))
                    room = make_room(config, ws, data.get('questions'))
                    affiliation = ('host', room['code'], room['host_token'])
                    await send_json(ws, {'type': 'created', 'code': room['code'], 'token': room['host_token']})
                    await publish(room)
                elif action in ('join', 'resume', 'host_resume'):
                    code = str(data.get('code', '')).strip()
                    room = ROOMS.get(code)
                    if room is None:
                        raise ValueError('Bu PIN ile açık bir yarışma bulunamadı.')
                    token = str(data.get('token', ''))
                    if action == 'host_resume':
                        if not secrets.compare_digest(token, room['host_token']):
                            raise ValueError('Öğretmen oturumu doğrulanamadı.')
                        if room['host_ws'] is not ws:
                            await send_json(room['host_ws'], {'type': 'notice', 'text': 'Öğretmen oturumu başka sekmede açıldı.'})
                        room['host_ws'] = ws
                        affiliation = ('host', code, token)
                        await send_json(ws, {'type': 'created', 'code': code, 'token': token})
                    elif action == 'resume':
                        person = room['players'].get(token)
                        if not person:
                            raise ValueError('Öğrenci oturumu bulunamadı, yeniden katılın.')
                        if person['ws'] is not ws:
                            await send_json(person['ws'], {'type': 'notice', 'text': 'Bu oyuncu başka cihazdan bağlandı.'})
                        person['ws'] = ws
                        affiliation = ('player', code, token)
                        await send_json(ws, {'type': 'joined', 'code': code, 'token': token})
                    else:
                        if room['status'] != 'lobby':
                            raise ValueError('Yarışma başladı. Yeni oyuncu katılımı kapalı.')
                        if len(room['players']) >= MAX_PLAYERS:
                            raise ValueError('Bu sınıfın katılımcı sınırına ulaşıldı.')
                        name = re.sub(r'\s+', ' ', str(data.get('name', '')).strip())[:24]
                        if len(name) < 2 or any(ord(c) < 32 for c in name):
                            raise ValueError('2–24 karakter arasında bir rumuz girin.')
                        if any(p['name'].casefold() == name.casefold() for p in room['players'].values()):
                            raise ValueError('Bu rumuz kullanılıyor; farklı bir rumuz seçin.')
                        token = secrets.token_urlsafe(24)
                        counts = [sum(p['team'] == i for p in room['players'].values()) for i in range(room['config']['teams'])]
                        team = min(range(len(counts)), key=lambda i: (counts[i], i)) if room['config']['mode'] == 'takim' else None
                        room['players'][token] = {'name': name, 'ws': ws, 'score': 0, 'correct': 0,
                                                   'team': team, 'joined': time.monotonic()}
                        affiliation = ('player', code, token)
                        await send_json(ws, {'type': 'joined', 'code': code, 'token': token})
                    await publish(room)
                else:
                    if not affiliation:
                        raise ValueError('Önce bir odaya katılın.')
                    role, code, token = affiliation
                    room = ROOMS.get(code)
                    if not room:
                        raise ValueError('Oda sona erdi.')
                    if role == 'host' and room['host_ws'] is not ws:
                        raise ValueError('Öğretmen yetkiniz bu sekmede geçerli değil.')
                    if role == 'player' and room['players'][token]['ws'] is not ws:
                        raise ValueError('Oyuncu oturumunuz başka sekmede açık.')
                    if action == 'answer' and role == 'player':
                        choice = data.get('choice')
                        if type(choice) is not int or choice not in range(4):
                            raise ValueError('Geçersiz cevap.')
                        if room['status'] != 'question' or token in room['answers']:
                            continue
                        remaining = max(0.0, room['end_monotonic'] - time.monotonic())
                        if remaining <= 0:
                            await reveal(room)
                            continue
                        room['answers'][token] = {'choice': choice, 'remaining': remaining}
                        if all_active_players_answered(room):
                            await reveal(room)
                        else:
                            await publish(room)
                    elif action == 'next' and role == 'host':
                        await advance(room)
                    elif action == 'reveal' and role == 'host':
                        await reveal(room)
                    elif action == 'reset' and role == 'host':
                        cancel_job(room)
                        room['questions'] = build_questions(room['config'], room.get('custom_questions'))
                        room.update(index=-1, status='lobby', answers={}, deadline_ms=0)
                        for p in room['players'].values():
                            p['score'] = 0
                            p['correct'] = 0
                        await publish(room)
                    elif action == 'end' and role == 'host':
                        cancel_job(room)
                        room['status'] = 'finished'
                        room['deadline_ms'] = 0
                        await publish(room)
                    else:
                        raise ValueError('Bu işlem için yetkiniz yok.')
            except (ValueError, TypeError, KeyError) as exc:
                await send_json(ws, {'type': 'error', 'message': str(exc)})
    finally:
        if affiliation:
            role, code, token = affiliation
            room = ROOMS.get(code)
            if room:
                if role == 'host' and room['host_ws'] is ws:
                    room['host_ws'] = None
                elif role == 'player' and token in room['players'] and room['players'][token]['ws'] is ws:
                    room['players'][token]['ws'] = None
                if room['status'] == 'question' and all_active_players_answered(room):
                    await reveal(room)
                else:
                    await publish(room)
    return ws


async def main_page(_):
    return web.FileResponse(BASE / 'web' / 'index.html')


async def classic_page(_):
    return web.FileResponse(BASE / 'web' / 'klasik.html')


async def qr_page(request):
    url = request.query.get('url', '')
    if len(url) > 300 or not re.fullmatch(r'https?://[^\s]+', url):
        raise web.HTTPBadRequest(text='Geçersiz bağlantı.')
    qr = qrcode.QRCode(box_size=7, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    output = io.BytesIO()
    qr.make_image(fill_color='#0e1335', back_color='white').save(output, format='PNG')
    return web.Response(body=output.getvalue(), content_type='image/png', headers={'Cache-Control': 'no-store'})


async def health(_):
    return web.json_response({'ok': True, 'activeRooms': len(ROOMS)})


app = web.Application(client_max_size=1024 * 16)
app.router.add_get('/', main_page)
app.router.add_get('/klasik', classic_page)
app.router.add_get('/klasik.html', classic_page)
app.router.add_get('/ws', api_websocket)
app.router.add_get('/qr.png', qr_page)
app.router.add_get('/health', health)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '3000'))
    print(f'🎮 SAYI KÂŞİFLERİ CANLI: http://localhost:{port}')
    web.run_app(app, host='0.0.0.0', port=port, access_log=None)