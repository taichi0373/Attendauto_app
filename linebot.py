import requests

def send_message(corse_name):
    #LINE通知   
    line_notify_token = 'トークンをかく'
    line_notify_api = 'https://notify-api.line.me/api/notify'

    message = f"{corse_name}の出席が始まりました"

    #LINE通知
    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + line_notify_token}
    line_notify = requests.post(line_notify_api, data=payload, headers=headers)