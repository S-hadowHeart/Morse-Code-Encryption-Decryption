import requests
import sys

BASE = 'http://127.0.0.1:10000'


def check_code():
    try:
        r = requests.post(BASE + '/code', data={'textInput': 'sos'})
        print('/code', r.status_code, r.text)
        j = r.json()
        if j.get('status') != 'success':
            print('FAIL: /code did not return success')
            return 1
        if '...' not in j.get('result', ''):
            print('WARN: result does not look like morse:', j.get('result'))
        return 0
    except Exception as e:
        print('ERROR /code', e)
        return 2


def check_chat_create():
    try:
        r = requests.post(BASE + '/chat/create')
        print('/chat/create', r.status_code, r.text)
        j = r.json()
        if j.get('status') != 'success':
            print('FAIL: /chat/create did not return success')
            return 1
        room = j.get('room_code')
        if not room:
            print('FAIL: no room_code')
            return 1
        return 0
    except Exception as e:
        print('ERROR /chat/create', e)
        return 2


if __name__ == '__main__':
    code_rc = check_code()
    create_rc = check_chat_create()
    rc = max(code_rc, create_rc)
    if rc == 0:
        print('SMOKE OK')
    else:
        print('SMOKE FAILED')
    sys.exit(rc)
