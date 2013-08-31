from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from core.models import DateStamp


class Message(DateStamp):
    user = models.ForeignKey(User)
    recipient = models.ForeignKey(User, related_name='received_messages')
    #TODO: CHANGE THIS ^ TO THIS v
    #user = models.ForeignKey(User, related_name='recipient'))
    message = models.TextField()

    def __unicode__(self):
        return str(self.created)

    def get_absolute_url(self):
        return reverse('messages:message-detail', kwargs={'pk': self.pk})


