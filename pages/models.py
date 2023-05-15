from django.db import models


# from django.core.exceptions import ValidationError


def upload_location(instance, filename):
    ext = filename.split(".")[-1]
    user = "%s" % (instance.user,)
    # get filename

    shop_name = "%s" % (instance.shop_name,)
    OrderDate = "%s" % (instance.OrderDate,)

    filename = "{}.{}.{}".format(user, shop_name, OrderDate)

    return "%s/%s.%s" % (user, filename, ext)


class ContactrForm(models.Model):
    daily_report = models.FileField(upload_to="daily_reports/", null=True, blank=True)

    def __str__(self):
        return "{}".format(self.daily_report)


class PendingForm(models.Model):
    podstatus = models.CharField(max_length=51, unique=False)
    shop_name = models.CharField(max_length=150)
    invoicepicture = models.ImageField(upload_to=upload_location, null=True, blank=True)
    OrderDate = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return "{} {} {} {} {}".format(
            self.podstatus,
            self.shop_name,
            self.invoicepicture,
            self.user,
            self.OrderDate,
        )


class PodStatus(models.Model):
    podstatus = models.CharField(max_length=50, unique=False)
    shop_name = models.CharField(max_length=150)
    OrderDate = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return "{} {} {} {}".format(
            self.podstatus, self.shop_name, self.OrderDate, self.user
        )


class ContactForm(models.Model):
    shop_name = models.CharField(max_length=150)
    completion_status = models.CharField(max_length=50, unique=False)
    # invoice_title = models.CharField(max_length=200)

    invoicepicture = models.ImageField(upload_to=upload_location, null=True, blank=True)
    OrderTime = models.TimeField(auto_now=True)
    OrderDate = models.DateTimeField(auto_now=True)

    message = models.CharField(max_length=200, unique=False, blank=True)
    user = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return "{} {} {} {} {} {} {}".format(
            self.shop_name,
            self.completion_status,
            self.message,
            self.user,
            self.OrderTime,
            self.OrderDate,
            self.invoicepicture,
        )


class AdminForm(models.Model):
    username = models.CharField(max_length=32, unique=True)
    email = models.CharField(max_length=50, unique=True)
    password1 = models.CharField(max_length=10, unique=True)
    password2 = models.CharField(max_length=10, unique=True)


class kenchiccnew(models.Model):
    Customer_Name = models.TextField()
    Posting_Description = models.TextField()
    Route_Plan = models.TextField()
    Ordered_Weight = models.TextField()

    def __str__(self):
        return "{} {} {} {}".format(
            self.Customer_Name,
            self.Posting_Description,
            self.Route_Plan,
            self.Ordered_Weight,
        )
