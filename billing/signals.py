from django.db.models.signals import post_save, pre_init
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import user_logged_in
from django.dispatch.dispatcher import receiver
from django.contrib.auth.hashers import make_password
# from .models import Profile, UserSession
from django.shortcuts import redirect
import datetime
from .models import *
from django.contrib.sessions.models import Session
from .import views
from twilio.rest import TwilioRestClient
from twilio.rest import Client
User = get_user_model()



@receiver(user_logged_in)
def remove_other_sessions(sender, user, request, **kwargs):
    # remove other sessions
    Session.objects.filter(usersession__user=user).delete()

    # save current session
    request.session.save()

    # create a link from the user to the current session (for later removal)
    UserSession.objects.get_or_create(
        user=user,
        session=Session.objects.get(pk=request.session.session_key)
    )
    return redirect('log')
