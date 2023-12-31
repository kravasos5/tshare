from django.core.mail import EmailMessage
from django.core.signing import Signer
from django.template.loader import render_to_string

from tshare.settings import ALLOWED_HOSTS

# создаю подпись для дополнительной защиты данных
signer = Signer()

#обработчик сигнала регистрации нового пользователя
def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://127.0.0.1:8000'
    context = {'user': user, 'host': host,
               'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.html',
                               context)
    body_text = render_to_string('email/activation_letter_body.html',
                                 context)
    em = EmailMessage(subject=subject, body=body_text,
                      to=[f'{user.email}',])
    em.send()

# обработчик сигнала удаления пользователя
def user_delete(user, protocol, domain):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://127.0.0.1:8000'
    context = {'user': user, 'host': host,
               'sign': signer.sign(user.username)}
    subject = render_to_string('email/delete_user_subject.txt',
                               context)
    body_text = render_to_string('email/delete_user_body.html',
                                 context)
    em = EmailMessage(subject=subject, body=body_text,
                      to=[f'{user.email}', ])
    em.send()