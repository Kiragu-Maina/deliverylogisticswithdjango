from django.contrib import admin
from .models import ContactForm, PendingForm, PodStatus

admin.site.register(ContactForm)
admin.site.register(PodStatus)
admin.site.register(PendingForm)