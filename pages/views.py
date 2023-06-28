from django.shortcuts import render, redirect
# from .models import *
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Func, F, Value, Q
from .forms import CreateUserForm, FormContactForm
from django.contrib import messages
from .models import ContactForm, AdminForm, kenchiccnew, PodStatus, PendingForm
from django.db import connection
from io import BytesIO


from django.views.decorators.csrf import csrf_exempt


import itertools

from datetime import datetime, date
from django.shortcuts import render
from django.http import HttpResponse

from weasyprint import HTML
import pandas as pd
import datapane as dp
from django.template.loader import get_template
import os
from django.http import FileResponse
from pathlib import Path
from .utils import convert_xls_to_sql

BASE_DIR = Path(__file__).resolve().parent.parent


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return HttpResponse('No file uploaded', status=400)
        try:
            # Call function to convert XLS to SQL
            # column_mappings = get_column_mappings(file)
            convert_xls_to_sql(file)
            return HttpResponse('File uploaded and converted successfully')
        except Exception as e:
            print(f'Error converting XLS to SQL: {e}')
            return HttpResponse('Error converting XLS to SQL', status=500)
    return render(request, 'upload_file.html')


def generate_report_view(request):

    selected_date = request.POST.get('selected_date')
    today = datetime.strptime(selected_date, '%Y-%m-%d').date()
    contacts = ContactForm.objects.filter(
        OrderDate__date=today).order_by('user')

    contacts_df = pd.DataFrame.from_records(contacts.values_list())

    report_df = pd.DataFrame(
        columns=['user', 'delivery_status', 'shop_name', 'invoice_collected', 'ordertime'])

    # contacts = contacts_df.sort_values('User')
    # print(contacts_df)

    for contact in contacts:
        print(contact.OrderTime)
        if contact.invoicepicture:
            # print(contact.invoicepicture.url)
            if contact.user not in report_df['user'].values:
                new_row = {
                    'user': contact.user,
                    'delivery_status': '',
                    'shop_name': '',
                    'invoice_collected': '',
                    'ordertime': '',
                }
                report_df = report_df.append(new_row, ignore_index=True)
            new_row = {
                'user': '',
                'delivery_status': 'Delivered',
                'shop_name': contact.shop_name,
                'invoice_collected': contact.invoicepicture.url,
                'ordertime': contact.OrderTime,
            }
            report_df = report_df.append(new_row, ignore_index=True)
        else:
            if contact.user not in report_df['user'].values:
                new_row = {
                    'user': contact.user,
                    'delivery_status': '',
                    'shop_name': '',
                    'invoice_collected': '',
                    'ordertime': '',
                }
                report_df = report_df.append(new_row, ignore_index=True)
            if 'Invoice Not Collected' in contact.completion_status:

                new_row = {
                    'user': '',
                    'delivery_status': 'Delivered',
                    'shop_name': contact.shop_name,
                    'invoice_collected': 'POD not collected',
                    'ordertime': contact.OrderTime,
                }
                report_df = report_df.append(new_row, ignore_index=True)
            else:
                new_row = {
                    'user': '',
                    'delivery_status': 'Not Delivered',
                    'shop_name': contact.shop_name,
                    'invoice_collected': contact.message,
                    'ordertime': contact.OrderTime,
                }
                report_df = report_df.append(new_row, ignore_index=True)
    print(report_df)
    template = get_template('report.html')
    # report_df = report_df.sort_values('user')
    context = {'report_df': report_df, 'today': today}
    html = template.render(context)

    # Generate the PDF using WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    HTML(string=html).write_pdf(response)

    return response


def register_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        form = CreateUserForm
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get("username")
                messages.success(
                    request, "Account created successfully for " + user)
                return redirect("login")

        context = {"form": form}
        return render(request, "register.html", context)


def login_admin(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        users = AdminForm.objects.values_list('username', flat=True)
        if username in users:
            print("user in usernames")
            passwords = AdminForm.objects.values_list('password1', flat=True)
            if password in passwords:
                print("got here")
                return redirect("admin2")
            else:
                return redirect("login_admin")
        else:
            return redirect("login_admin")

    context = {}
    return render(request, "login_admin.html", context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "!!Please, try again")
        context = {}
        return render(request, "login.html", context)


@csrf_exempt
def workerror(request):

    return render(request, "workerror.html")


def logout_user(request):
    logout(request)
    return redirect("home")


def serve_apk(request, filename):
    apk_file = os.path.join(BASE_DIR, "apk_files", filename)
    # apk_file = os.path.join('apk_files', filename)
    response = FileResponse(
        open(apk_file, 'rb'), content_type='application/vnd.android.package-archive')
    return response


@csrf_exempt
@login_required(login_url='login')
def home_page(request):

    def remove_punc(string):
        punc = '''()'",[]'''
        for ele in string:
            if ele in punc:
                string = string.replace(ele, "")
        return string

    # get user. so request from frontend should have user
    user = request.user
    # filter from database the posting_description per truck and get the corresponding id of each truck
    # did this as trucks were distinct objects with no possibility of duplication
    routeplan = kenchiccnew.objects.filter(Q(Posting_Description__icontains='KCX 469Y') | Q(Posting_Description__icontains='KCX 850W') | Q(Posting_Description__icontains='KDD 090R') | Q(Posting_Description__icontains='KDD 205J') | Q(Posting_Description__icontains='KDD 206J') | Q(Posting_Description__icontains='KDE 017W') | Q(Posting_Description__icontains='KDG 805F') | Q(Posting_Description__icontains='KCF 445R') | Q(Posting_Description__icontains='KCH 314V') | Q(Posting_Description__icontains='KCH 316V') | Q(Posting_Description__icontains='KCL 442A') | Q(Posting_Description__icontains='KCU 236D') | Q(Posting_Description__icontains='KCU 237D') | Q(Posting_Description__icontains='KCU 410E') | Q(Posting_Description__icontains='KCX 833H') | Q(Posting_Description__icontains='KCZ 313B') | Q(Posting_Description__icontains='KCZ 314B') | Q(Posting_Description__icontains='KDE 958P') | Q(Posting_Description__icontains='KCX 806H') | Q(
        Posting_Description__icontains='KDE 848J') | Q(Posting_Description__icontains='KDH 424A') | Q(Posting_Description__icontains='KDG 240Y') | Q(Posting_Description__icontains='KDH 339E') | Q(Posting_Description__icontains='KDH 338E') | Q(Posting_Description__icontains='KCZ 792Y') | Q(Posting_Description__icontains='KDD 671A') | Q(Posting_Description__icontains='KDH 516N') | Q(Posting_Description__icontains='KDH 085N') | Q(Posting_Description__icontains='KDH 142V') | Q(Posting_Description__icontains='KDJ 574E') | Q(Posting_Description__icontains='KBJ 956K') | Q(Posting_Description__icontains='KCU 235D') | Q(Posting_Description__icontains='KCX 640F') | Q(Posting_Description__icontains='KDA 061G') | Q(Posting_Description__icontains='KDA 880B') | Q(Posting_Description__icontains='KDB 428S') | Q(Posting_Description__icontains='KDB 729Y') | Q(Posting_Description__icontains='KDD 110J')).values_list('id')
    routeplan = list(itertools.chain(*routeplan))
    routeplan.sort()
    # print(routeplan)
    # did the same with users. filtered them and got the corresponding of the currently logged in user.
    # if user isn't assigned any route, return error

    userid = kenchiccnew.objects.filter(
        Posting_Description__icontains=user).values_list('id')
    userid = list(itertools.chain(*userid))
    # print(userid)
    if not len(userid):
        return redirect("workerror")

    # this was simply to get the number out of the single item list.
    userid = userid[0]
    # print(userid)
    # get the last assigned truck id and assign it to maxinroute variable
    # print(routeplan[-1])

    maxinroute = routeplan[-1]
    cursor = connection.cursor()
    # literally can't remember the logic here
    cursor.execute(
        "select id from pages_kenchiccnew where id=(select max(id) from pages_kenchiccnew);")
    trr = cursor.fetchone()
    # print(trr)
    # if the user id is not the last id, assign userid2 to the next id after the one that matches the user
    # I'm really confused now
    # otherwise userid is the lastid
    # I think this was the logic to get the shops assigned to a particular individual

    # how the fuck did I think of this. next level shit
    # you clearly get the list
    # in between the ids, lies the shops assigned a user
    # shit. How the fuck did they not pick this project
    if userid != maxinroute:
        userid2 = routeplan[routeplan.index(userid)+1]
    else:
        userid2 = trr[0]
        # print(userid2)
    # userid2 = userid2-1
    # print(userid2)
    userid2 = userid2-1
    # retrieve the list of shops here
    data = list(kenchiccnew.objects.filter(id__range=(userid, userid2)
                                           ).values_list('Customer_Name', 'Posting_Description'))

    usercarroute = []
    if any(ele in data for ele in str(user)):

        # print(ele)
        usercarroute.append(ele)
    data.pop(0)

    # get the assigned route of user, and their respective truck
    routeandname = list(kenchiccnew.objects.filter(
        id=userid).values_list('Customer_Name', 'Posting_Description'))

    routeandname = list(itertools.chain(*routeandname))

    # print(routeandname)

    # modifying data. where data is list of shops assigned to user
    data = [str(i) for i in data]
    data = [remove_punc(i) for i in data]

    form = FormContactForm(request.POST, request.FILES)
    # print(form.errors)
    # to filter if user has already delivered to certain shop

    prevcollectedinvoices = ContactForm.objects.filter(user__icontains=request.user).filter(
        completion_status__icontains="Invoice Collected").values_list("shop_name")
    prevcollectedinvoices = list(itertools.chain(*prevcollectedinvoices))
    # cleaning form data and submitting it
    if form.is_valid():
        shop_name = form.cleaned_data.get("shop_name")
        completion_status = form.cleaned_data.get("completion_status")
        message = form.cleaned_data.get("message")
        invoicepicture = form.cleaned_data.get("invoicepicture")
        # print(completion_status)
        if completion_status == "1":
            completion_status = "Invoice Collected"
            # print(completion_status)
            if shop_name in prevcollectedinvoices:
                messages.error(request, "not sent...duplicate data")
                return redirect("home")

            elif invoicepicture is None:
                messages.error(
                    request, "not sent...Take Invoice picture pls!!")
                return redirect("home")
            else:

                user = str(user)

                obj = ContactForm.objects.create(
                    shop_name=shop_name,
                    completion_status=completion_status,
                    message=message,
                    invoicepicture=invoicepicture,
                    user=user
                )

                obj.save()

                print('nimefika aje hapa')

                messages.success(request, "Information sent")
        elif completion_status == "2":
            completion_status = "Invoice Not Collected"
        # if any(ele in shop_name for ele in user):
            #messages.error(request, "not sent... select viable shop")
            # return redirect("home")

            user = str(user)

            obj = ContactForm.objects.create(
                shop_name=shop_name,
                completion_status=completion_status,
                message=message,
                invoicepicture=invoicepicture,
                user=user
            )

            obj.save()

            # print('nimefika hapa hapa')

            messages.success(request, "Information sent")

        elif completion_status == "3":
            completion_status = "Shop Closed"
        # if any(ele in shop_name for ele in user):
            #messages.error(request, "not sent... select viable shop")
            # return redirect("home")

            user = str(user)

            obj = ContactForm.objects.create(
                shop_name=shop_name,
                completion_status=completion_status,
                message=message,
                invoicepicture=invoicepicture,
                user=user
            )

            obj.save()

            # print('nimefika hapa hapa')

            messages.success(request, "Information sent")
        elif completion_status == "4":
            completion_status = "Time"
        # if any(ele in shop_name for ele in user):
            #messages.error(request, "not sent... select viable shop")
            # return redirect("home")

            user = str(user)

            obj = ContactForm.objects.create(
                shop_name=shop_name,
                completion_status=completion_status,
                message=message,
                invoicepicture=invoicepicture,
                user=user
            )

            obj.save()

            # print('nimefika hapa hapa')

            messages.success(request, "Information sent")

        elif completion_status == "5":
            completion_status = "Not Ordered"
        # if any(ele in shop_name for ele in user):
            #messages.error(request, "not sent... select viable shop")
            # return redirect("home")

            user = str(user)

            obj = ContactForm.objects.create(
                shop_name=shop_name,
                completion_status=completion_status,
                message=message,
                invoicepicture=invoicepicture,
                user=user
            )

            obj.save()

            # print('nimefika hapa hapa')

            messages.success(request, "Information sent")
        elif completion_status == "6":
            completion_status = "Wrong Route"
            # if any(ele in shop_name for ele in user):
            #messages.error(request, "not sent... select viable shop")
            # return redirect("home")

            user = str(user)

            obj = ContactForm.objects.create(
                shop_name=shop_name,
                completion_status=completion_status,
                message=message,
                invoicepicture=invoicepicture,
                user=user
            )

            obj.save()

            # print('nimefika hapa hapa')

            messages.success(request, "Information sent")
        else:
            user = str(user)

            obj = ContactForm.objects.create(
                shop_name=shop_name,
                completion_status=completion_status,
                message=message,
                invoicepicture=invoicepicture,
                user=user
            )

            obj.save()

            # print('nimefika hapa hapa')

            messages.success(request, "Information sent")
    else:
        print('whats happen')
        messages.error(
            request, "Please provide shop name and completion status!")
    collectedinvoices = ContactForm.objects.filter(user__icontains=request.user).filter(
        completion_status__icontains="Invoice Collected").values_list("shop_name")
    collectedinvoices = list(itertools.chain(*collectedinvoices))
    # print(collectedinvoices)

    return render(request, 'home.html', {'action': "Display all ContactForm", 'form': form, 'data': data, 'collectedinvoices': collectedinvoices, 'usercarroute': usercarroute})


@csrf_exempt
# @login_required(login_url='login_admin')
def admin2(request):
    today = date.today()
    dbitems = ContactForm.objects.all()
    users = ContactForm.objects.filter(
        OrderDate__date=today).values_list('user').distinct()
    users = list(itertools.chain(*users))
    if not len(users):
        users = ['no drops yet']

    # print(users)
    completed_order = []
    # shop_names = []
    pendin_invoices = []
    pendingdeliveries = []
    for user in users:
        def remove_punc(string):
            punc = '''()'",[]'''
            for ele in string:
                if ele in punc:
                    string = string.replace(ele, "")
            return string

        shop_names = ContactForm.objects.filter(user__icontains=user, OrderDate__date=today).values_list(
            'shop_name', 'completion_status', 'OrderTime')
        shop_names = itertools.chain(*shop_names)
        # shop_names = [remove_punc(i) for i in shop_names]
        shops = []
        shops_names = [str(i) for i in shop_names]
        shops_names = [remove_punc(i) for i in shops_names]

        for i in shops_names:
            shops.append(i)

        shopss = ''.join(str(x) for x in shops)
        # print(shopss)
        # print(shop_names)
        # shop_names.append(shop_names)
        completion_status = ContactForm.objects.filter(
            user__icontains=user).values_list('completion_status')
        order_times = ContactForm.objects.filter(
            user__icontains=user).values_list('OrderDate', flat=True)

        # order_times.append(datetime_date1)
        # print(datetime_date1)
        # shop_names = ContactForm.objects.filter(user__icontains=user).values_list('shop_name', flat=True)

        # shop_names = list(shop_names)
        # shop_names = [remove_punc(i) for i in shop_names]
        shops = [shops[x:x+3] for x in range(0, len(shops), 3)]
        shopss = shops_per_user(user)
        # pendingdeliveries = []
        # check pending drops realtime
        if '' in shopss:
            def drops(user):

                return list(ContactForm.objects.filter(user__icontains=user).values_list('shop_name'))
            drops = drops(user)
            remaining = len(drops)
            pendingdelivery = 'all'
            pendingdeliveria = (user, pendingdelivery)
            pendingdeliveries.append(pendingdeliveria)
            # print(user,remaining)
        else:
            def drops(user):

                return list(ContactForm.objects.filter(user__icontains=user).values_list('shop_name'))
            drops = drops(user)
            # for y in drops:
            #     print(y[0])
            # shops = list(shops)
            # print(shops)
            # for name in shops:
            #     print(name)
            # print(drops)
            remainings = [x for x in shopss if x not in [y[0] for y in drops]]

            remainings.pop(0)
            # print(remaining)

            remaining = len(remainings)
            usera = (user, remaining)
            pendingdelivery = (usera, remainings)
            pendingdeliveries.append(pendingdelivery)
            # print(user,remaining)
        user = (user, remaining)
        complete = (user, shops)

        completed_order.append(complete)
        # print(completed_order)
        shop_loc = kenchiccnew.objects.filter(
            Posting_Description__icontains=user).values_list('Customer_Name')

        shop_loc = list(itertools.chain(*shop_loc))

        def pending_invoices(user):
            return list(PodStatus.objects.filter(user__icontains=user, podstatus='POD Not Collected').values_list('shop_name', 'OrderDate'))

        # def pendingcollected_invoices(user):
        #     return list(PodStatus.objects.filter(user__icontains=user).values_list('shop_name'))

        def collectedinvoices(user):
            return list(PodStatus.objects.filter(user__icontains=user, podstatus='POD Collected', OrderDate__date=today).values_list('shop_name'))
            # return kenchiccnew.objects.filter(id__in=routeplan).values()

        collectedinvoices = collectedinvoices(user)
        # collectedinvoices = list(collectedinvoices)
        # print(collectedinvoices)

        pendinginvoices = pending_invoices(user)

        pendinginvoices = [x for x in pendinginvoices if x[0]
                           not in [y[0] for y in collectedinvoices]]
        pendin_invoices.append(pendinginvoices)
        # print("pending 2" , pendinginvoices)
        # print("this is the new data ", data)

    return render(request, 'admin2.html', {'action': "Display all ContactForm", 'dbitems': dbitems, 'users': users, 'completed_order': completed_order, 'shops': shops, 'pending_invoices': pendin_invoices, 'pendingdeliveries': pendingdeliveries})


def pending(request):
    today = date.today()

    users = ContactForm.objects.values_list('user').distinct()
    users = list(itertools.chain(*users))
    print(users)

    pendin_invoices = []
    for user in users:

        def pending_invoices(user):
            invoices = PodStatus.objects.filter(
                user__icontains=user, podstatus='POD Not Collected').values_list('shop_name', 'OrderDate')
            formatted_invoices = []
            for shop_name, order_date in invoices:
                formatted_date = datetime.strftime(
                    order_date, "%B %d, %Y %I:%M %p")
                formatted_invoices.append((shop_name, formatted_date))
            return formatted_invoices

        # def pendingcollected_invoices(user):
        #     return list(PodStatus.objects.filter(user__icontains=user).values_list('shop_name'))

        def collectedinvoices(user):
            return list(PodStatus.objects.filter(user__icontains=user, podstatus='POD Collected', OrderDate__date=today).values_list('shop_name'))
            # return kenchiccnew.objects.filter(id__in=routeplan).values()

        collectedinvoices = collectedinvoices(user)
        # collectedinvoices = list(collectedinvoices)
        # print(collectedinvoices)
        pendinginvoices = pending_invoices(user)
        pending_forms = []
        for form in list(PendingForm.objects.filter(user__icontains=user).values_list('shop_name')):
            # print("this is a form", form)
            shop_name_parts = form[0].split(',')
            if len(shop_name_parts) >= 2:
                shop_name = shop_name_parts[0].strip()[1:]
                # print("continued to ", shop_name)

                try:
                    order_date_str = shop_name_parts[1].strip()[:-1]
                    order_date_formatted = datetime.strptime(
                        order_date_str, '%Y-%m-%dT%H:%M:%S%z')
                    order_date = order_date_formatted.strftime(
                        "%B %d, %Y %I:%M %p")
                    # print("continued to ", order_date)
                except ValueError:
                    # Skip this PendingForm instance if the order date is invalid
                    continue
                shopname_and_date = f"{shop_name} {order_date}"

                # print('this is shopname and date', shopname_and_date)
                pending_forms.append(shopname_and_date)

        # print('these are the pending forms ',pending_forms)

        new_pending_invoices = []
        for shop_name, order_date in pendinginvoices:
            # print(shop_name, order_date)
            shopname_and_date = f"{shop_name} {order_date}"
            if shopname_and_date not in pending_forms:
                new_pending_invoices.append((shop_name, order_date))
        pendinginvoices = new_pending_invoices

        pendinginvoices = [x for x in pendinginvoices if x[0]
                           not in [y[0] for y in collectedinvoices]]
        complete = (user, pendinginvoices)
        pendin_invoices.append(complete)
    # print(pendin_invoices)

    return render(request, 'pending.html', {'pending_invoices': pendin_invoices})


def shops_per_user(user):
    routeplan = kenchiccnew.objects.filter(Q(Posting_Description__icontains='KCX 469Y') | Q(Posting_Description__icontains='KCX 850W') | Q(Posting_Description__icontains='KDD 090R') | Q(Posting_Description__icontains='KDD 205J') | Q(Posting_Description__icontains='KDD 206J') | Q(Posting_Description__icontains='KDE 017W') | Q(Posting_Description__icontains='KDG 805F') | Q(Posting_Description__icontains='KCF 445R') | Q(Posting_Description__icontains='KCH 314V') | Q(Posting_Description__icontains='KCH 316V') | Q(Posting_Description__icontains='KCL 442A') | Q(Posting_Description__icontains='KCU 236D') | Q(Posting_Description__icontains='KCU 237D') | Q(Posting_Description__icontains='KCU 410E') | Q(Posting_Description__icontains='KCX 833H') | Q(Posting_Description__icontains='KCZ 313B') | Q(Posting_Description__icontains='KCZ 314B') | Q(Posting_Description__icontains='KDE 958P') | Q(Posting_Description__icontains='KCX 806H') | Q(
        Posting_Description__icontains='KDE 848J') | Q(Posting_Description__icontains='KDH 424A') | Q(Posting_Description__icontains='KDG 240Y') | Q(Posting_Description__icontains='KDH 339E') | Q(Posting_Description__icontains='KDH 338E') | Q(Posting_Description__icontains='KCZ 792Y') | Q(Posting_Description__icontains='KDD 671A') | Q(Posting_Description__icontains='KDH 516N') | Q(Posting_Description__icontains='KDH 085N') | Q(Posting_Description__icontains='KDH 142V') | Q(Posting_Description__icontains='KDJ 574E') | Q(Posting_Description__icontains='KBJ 956K') | Q(Posting_Description__icontains='KCU 235D') | Q(Posting_Description__icontains='KCX 640F') | Q(Posting_Description__icontains='KDA 061G') | Q(Posting_Description__icontains='KDA 880B') | Q(Posting_Description__icontains='KDB 428S') | Q(Posting_Description__icontains='KDB 729Y') | Q(Posting_Description__icontains='KDD 110J')).values_list('id')
    routeplan = list(itertools.chain(*routeplan))
    routeplan.sort()

    # did the same with users. filtered them and got the corresponding of the currently logged in user.
    # if user isn't assigned any route, return error

    userid = kenchiccnew.objects.filter(
        Posting_Description__icontains=user).values_list('id')
    userid = list(itertools.chain(*userid))
    # print(userid)
    if not len(userid):
        return ''

    # this was simply to get the number out of the single item list.
    userid = userid[0]
    # print(userid)
    # get the last assigned truck id and assign it to maxinroute variable
    # print(routeplan[-1])

    maxinroute = routeplan[-1]
    cursor = connection.cursor()
    # literally can't remember the logic here
    cursor.execute(
        "select id from pages_kenchiccnew where id=(select max(id) from pages_kenchiccnew);")
    trr = cursor.fetchone()
    # print(trr)

    if userid != maxinroute:
        userid2 = routeplan[routeplan.index(userid)+1]
    else:
        userid2 = trr[0]
        # print(userid2)
    # userid2 = userid2-1
    # print(userid2)
    userid2 = userid2-1
    # retrieve the list of shops here
    data = list(kenchiccnew.objects.filter(id__range=(userid, userid2)
                                           ).values_list('Customer_Name', 'Posting_Description'))
    shops = []
    for Customer_Name, Posting_Description in data:
        if Customer_Name is not None and Customer_Name != '':

            shopname_and_pd = f"{Customer_Name} {Posting_Description}"
            shops.append((shopname_and_pd))

    # print(shops)

    # print(len(shops))
    return shops
