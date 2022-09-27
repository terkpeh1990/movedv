import threading
from django.http import request
from dvla_billing.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from twilio.rest import Client
from django.contrib import messages

class  SendMessageThread(threading.Thread):
    def __init__(self, detail):
        self.detail = detail
        threading.Thread.__init__(self)

    def run(self):
        print("started")
        try:
            for i in self.detail:
                try:
                    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                    message = client.messages.create(
                    to="+233" + i.order_id.customer.phone,
                    from_=TWILIO_PHONE_NUMBER,
                    body="Dear" + " " + i.order_id.customer.name + ",\n" + "you have made payment for"+ " "+ i.product.name +".\n"+"REF. No:"+" "+ i.order_id.id + "\nThank you for chooing DVLA ODA Branch."

                            )
                except IOError:
                    print('fail')
                    pass
        except Exception as e:
            print(e)


    