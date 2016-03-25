# coding=utf-8
import requests
from _django_orm import *
url = 'http://120.25.65.201:8082/send/email/'


def send_email():
	for email_queue in EmailQueue.objects.filter(is_sended=False):
		email_data = {"email": email_queue.email, "title": email_queue.title, "content": email_queue.content}
		try:
			result = requests.post(url, data=email_data)
		except Exception,e:
			result = None
		if result:
			email_queue.is_sended = True
			email_queue.save()


if __name__ == "__main__":
    send_email()
