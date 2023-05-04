# myapp/views.py

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Func, F, Value, Q
from pages.forms import CreateUserForm, FormContactForm, FormPendingForm
from django.contrib import messages
from pages.models import ContactForm, AdminForm, kenchiccnew, PodStatus, PendingForm
from django.db import connection


from django.views.decorators.csrf import csrf_exempt

import cv2

import itertools

from datetime import datetime, date

from django.contrib.auth import authenticate, login
from django.http import JsonResponse

from django.contrib.auth import get_user
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import numpy as np
import io

@api_view(['GET'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def daily_report(request, selected_date):
    username = request.COOKIES.get('username')
    user = username

    # print(user)
    if not username:
        return Response({'error': 'User is not authenticated.'})
    else:

        today = datetime.strptime(selected_date, '%Y-%m-%d').date()
        contacts = ContactForm.objects.filter(OrderDate__date=today)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="daily_report.pdf"'

        # create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response)

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        for contact in contacts:
            if contact.completion_status == "Invoice Collected":
                    p.drawString(100, 100, contact.shop_name)
                    p.drawString(100, 80, contact.completion_status)
                    p.drawString(100, 60, contact.user)
                    p.drawString(100, 40, contact.invoicepicture.url)
            else:
                p.drawString(100, 100, contact.shop_name)
                p.drawString(100, 80, contact.completion_status)
                p.drawString(100, 60, contact.user)

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()
        return response


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getRoutes(request):


    routes = [
        {
            'Endpoint': '/homeapi/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Returns an dict of data and collectedinvoices'

        },
        {
            'Endpoint': '/homeapi/login',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Returns a response after receiving username and password, confirming if user is authenticated'
        },
        {
            'Endpoint': '/homeapi/submitform/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'accepts form data from frontend'

        },

    ]
    view = APIView()
    # Set the queryset for the view
    view.queryset = routes

    # Return the response
    return JsonResponse(routes, safe=False, status=200)

@csrf_exempt
def login_page(request):
    if request.user.is_authenticated:
        return JsonResponse({"redirect": "home"}, safe=False, status=200)

    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            print(username)
            # print(password)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                response = JsonResponse({"redirect": "home"}, safe=False, status=200)
                response.set_cookie("username", user.username, max_age=60*60*24*365) # expires in a year
                return response
            else:
                return JsonResponse({"error": "Please, try again"}, safe=False, status=401)
        return JsonResponse({"error": "Please, try again"}, safe=False, status=200)


@api_view(['GET'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def home_page(request):
    username = request.COOKIES.get('username')
    user = username

    print(user)
    if not username:
        return Response({'error': 'User is not authenticated.'})
    else:
        # Retrieve user data from the request
        today = date.today()

        print(user)
        def routeplan():
            print('routeplan called')
            return kenchiccnew.objects.filter(Q(Posting_Description__icontains='KCX 469Y') | Q(Posting_Description__icontains='KCX 850W') | Q(Posting_Description__icontains='KDK 643F')| Q(Posting_Description__icontains='KDH 659T')| Q(Posting_Description__icontains='KDK 014F') | Q(Posting_Description__icontains='KDD 090R') | Q(Posting_Description__icontains='KDD 205J') | Q(Posting_Description__icontains='KDD 206J') | Q(Posting_Description__icontains='KDE 017W') | Q(Posting_Description__icontains='KDG 805F') | Q(Posting_Description__icontains='KCF 445R') | Q(Posting_Description__icontains='KCH 314V') | Q(Posting_Description__icontains='KCH 316V') | Q(Posting_Description__icontains='KCL 442A') | Q(Posting_Description__icontains='KCU 236D') | Q(Posting_Description__icontains='KCU 237D') | Q(Posting_Description__icontains='KCU 410E') | Q(Posting_Description__icontains='KCX 833H') | Q(Posting_Description__icontains='KCZ 313B') | Q(Posting_Description__icontains='KCZ 314B') | Q(Posting_Description__icontains='KDE 958P') | Q(Posting_Description__icontains='KCX 806H') | Q(Posting_Description__icontains='KDE 848J') | Q(Posting_Description__icontains='KDH 424A') | Q(Posting_Description__icontains='KDG 240Y') | Q(Posting_Description__icontains='KDH 339E') | Q(Posting_Description__icontains='KDH 338E') | Q(Posting_Description__icontains='KCZ 792Y') | Q(Posting_Description__icontains='KDD 671A') | Q(Posting_Description__icontains='KDH 516N') | Q(Posting_Description__icontains='KDH 085N') | Q(Posting_Description__icontains='KDH 142V') | Q(Posting_Description__icontains='KDJ 574E') | Q(Posting_Description__icontains='KBJ 956K') | Q(Posting_Description__icontains='KCU 235D') | Q(Posting_Description__icontains='KCX 640F') | Q(Posting_Description__icontains='KDA 061G') | Q(Posting_Description__icontains='KDA 880B') | Q(Posting_Description__icontains='KDB 428S') | Q(Posting_Description__icontains='KDB 729Y') | Q(Posting_Description__icontains='KDD 110J')).values_list('id')


        def routeandname(userid):
            return list(
                kenchiccnew.objects
                    .exclude(Customer_Name__isnull=True)
                    .exclude(Posting_Description__isnull=True)
                    .filter(id=userid)
                    .values_list('Customer_Name', 'Posting_Description')
            )



        def userid(user):
            return kenchiccnew.objects.filter(Posting_Description__icontains=user).values_list('id')


        def data(userid, userid2):

            data = kenchiccnew.objects.filter(id__range=(userid, userid2)).values_list('Customer_Name', 'Posting_Description')
            data = [d for d in data if all(field is not None for field in d)]
            return list(data)

        def pending_invoices(user):
            return list(PodStatus.objects.filter(user__icontains=user, podstatus='POD Not Collected').values_list('shop_name', 'OrderDate'))

        # def pendingcollected_invoices(user):
        #     return list(PodStatus.objects.filter(user__icontains=user).values_list('shop_name'))


        def collectedinvoices(user):
            return list(PodStatus.objects.filter(user__icontains=user, podstatus='POD Collected', OrderDate__date=today).values_list('shop_name'))
            # return kenchiccnew.objects.filter(id__in=routeplan).values()

        routeplan1 = routeplan()
        routeplan = list(itertools.chain(*routeplan1))
        routeplan.sort()

        if not userid(user):
            data = ["No assigned route"]

        else:
            userid = userid(user)
            userid = list(itertools.chain(*userid))

            userid = userid[0]
            routeandname = routeandname(userid)
            routeandname = list(itertools.chain(*routeandname))
            maxinroute = routeplan[-1]
            cursor = connection.cursor()
            cursor.execute(
                "select id from pages_kenchiccnew where id=(select max(id) from pages_kenchiccnew);")
            trr = cursor.fetchone()
            if userid != maxinroute:
                userid2 = routeplan[routeplan.index(userid)+1]
            else:
                userid2 = trr[0]
            userid2 = userid2-1

            # Retrieve and process additional data from the database
            # data = kenchiccnew.objects.filter(id=author.id).values()
            data = data(userid, userid2)

        collectedinvoices = collectedinvoices(user)
        # collectedinvoices = list(collectedinvoices)
        # print(collectedinvoices)
        data = [str(i) for i in data]

        def remove_punc(string):
            punc = '''()'",[]'''
            for ele in string:
                if ele in punc:
                    string = string.replace(ele, "")
            return string
        data = [remove_punc(i) for i in data]
        data = list(data)
        # collectedinvoices = collectedinvoices
        data = [d for d in data if d[0] not in [c[0] for c in collectedinvoices]]
        data = list(data)
        pendinginvoices = pending_invoices(user)
        pending_forms = []
        for form in list(PendingForm.objects.filter(user__icontains=user).values_list('shop_name')):
            print("this is a form", form)
            shop_name_parts = form[0].split(',')
            if len(shop_name_parts) >= 2:
                shop_name = shop_name_parts[0].strip()[1:]
                # print("continued to ", shop_name)

                try:
                    order_date_str = shop_name_parts[1].strip()[:-1]
                    order_date_formatted = datetime.strptime(order_date_str, '%Y-%m-%dT%H:%M:%S%z')
                    order_date = order_date_formatted.strftime("%B %d, %Y %I:%M %p")
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

            # order_date_formatted = datetime.strptime(order_date, '%Y-%m-%dT%H:%M:%S%z')
            order_date = order_date.strftime("%B %d, %Y %I:%M %p")
            shopname_and_date = f"{shop_name} {order_date}"
            # print(shopname_and_date)
            if shopname_and_date not in pending_forms:
                new_pending_invoices.append((shop_name, order_date))
        pendinginvoices = new_pending_invoices
        # print("this is the data ", data)
        # print("these are the collected invoices", collectedinvoices)
        data = [x for x in data if x not in [y[0] for y in collectedinvoices]]
        # print("pending 1" , pendinginvoices)
        pendinginvoices = [x for x in pendinginvoices if x[0] not in [y[0] for y in collectedinvoices]]
        # print("pending 2" , pendinginvoices)
        # print("this is the new data ", data)

        # print(collectedinvoices)
    return JsonResponse({'data': data, 'collectedinvoices': collectedinvoices, 'pendinginvoices':pendinginvoices}, safe=False, status=200)


@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes((permissions.AllowAny,))
def getcsrftoken(request):
    return JsonResponse({'success': 'CSRF cookie set'})

@api_view(['POST'])
@ensure_csrf_cookie
@permission_classes((permissions.AllowAny,))
def tracking(request):
    username = request.COOKIES.get('username')
    print(username)
    gpsposition = request.POST.get("position")
    print(gpsposition)
    fcmToken = request.POST.get("fcmtoken")
    print(fcmToken)
    print('nice')

    return JsonResponse({'success': 'received'}, safe=False, status=200)


@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def submit_form(request):
    username = request.COOKIES.get('username')
    user = username

    print(user)
    if not username:
        return Response({'error': 'User is not authenticated.'})
    else:

        # Parse the form data from the request
        shop_name = request.POST.get("shop_name")
        print(shop_name)
        completion_status = request.POST.get("completion_status")
        print(completion_status)
        message = request.POST.get("message")
        print(message)
        # invoicepicture = scan_invoice(request)
        invoicepicture = request.FILES.get("invoicepicture")
        podstatus(request, user, shop_name)
        pod_status = request.POST.get("podstatus")
        print(pod_status)
        print(invoicepicture)
        form = FormContactForm(request.POST, request.FILES)
        print('checking whether form is valid')
        if form.is_valid():
            print('form is valid')
            print(completion_status)
            # Check the completion status and handle it accordingly
            if completion_status == "true":
                if pod_status == 'POD Collected':
                    completion_status = "Invoice Collected"

                    # Create a ContactForm object with the form data
                    user = str(user)
                    obj = ContactForm.objects.create(
                        shop_name=shop_name,
                        completion_status=completion_status,
                        message=message,
                        invoicepicture=invoicepicture,
                        user=user
                    )
                    obj.save()
                    # print('object saved')

                    # messages.success(request, "Information sent")
                    return JsonResponse({"message": "success"}, safe=False, status=200)

                else:

                    completion_status = "Invoice Not Collected"

                    # Create a ContactForm object with the form data
                    user = str(user)
                    obj = ContactForm.objects.create(
                        shop_name=shop_name,
                        completion_status=completion_status,
                        message=message,
                        invoicepicture=invoicepicture,
                        user=user
                    )
                    obj.save()
                    print('object saved')

                    # messages.success(request, "Information sent")
                    return JsonResponse({"message": "success"}, safe=False, status=200)
            elif completion_status == "false":
                print('completion_status false')
                completion_status = "Not Delivered"

                # Create a ContactForm object with the form data
                user = str(user)
                if message == "OTHER":
                    message = request.POST.get("otherReasonforlackofdelivery")
                else:
                    message = message
                obj = ContactForm.objects.create(
                    shop_name=shop_name,
                    completion_status=completion_status,
                    message=message,
                    invoicepicture=invoicepicture,
                    user=user
                )
                obj.save()
                print('object saved')

                # messages.success(request, "Information sent")
                return JsonResponse({"message": "success"}, safe=False, status=200)
            else:
                print(form.errors)
                return JsonResponse({"message": "error"}, safe=False, status=200)

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def submit2_form(request):
    username = request.COOKIES.get('username')
    user = username

    print(user)
    if not username:
        return Response({'error': 'User is not authenticated.'})
    else:

        # Parse the form data from the request
        shop_name = request.POST.get("shop_name")
        # order_date = request.POST.get("order_date")

        invoicepicture = request.FILES.get("invoicepicture")

        pod_status = "Pending Invoice Collected"

        form = FormPendingForm(request.POST, request.FILES)
        print('checking whether form is valid')
        if form.is_valid():

            obj = PendingForm.objects.create(
                shop_name=shop_name,
                podstatus = pod_status,
                # order_datedate = order_date,
                invoicepicture=invoicepicture,
                user=user
            )
            obj.save()
            print('object saved')

            # messages.success(request, "Information sent")
            return JsonResponse({"message": "success"}, safe=False, status=200)



        else:
            print(form.errors)
            return JsonResponse({"message": "error"}, safe=False, status=200)

def logout_user(request):
    logout(request)
    return redirect("home")



def podstatus(request, user, shop_name):
    podstatus = request.POST.get("podstatus")
    user = str(user)


    obj = PodStatus.objects.create(
        user = user,
        podstatus = podstatus,
        shop_name = shop_name,
    )
    obj.save()
def scan_invoice(request):
    invoice_picture = request.FILES.get("invoicepicture")
    print(invoice_picture)
    print('wat')
    if not invoice_picture:
        print('no invoice picture')
        return

    # Read the image from the file
    image = cv2.imdecode(np.frombuffer(invoice_picture.read(), np.uint8), cv2.IMREAD_UNCHANGED)


    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to remove noise and make the image binary
    th = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,5,3)

    # Perform edge detection to find the edges of the document
    edges = cv2.Canny(th, 100, 200)

    # Find the corners of the document in the image using Harris corner detection
    corners = cv2.goodFeaturesToTrack(edges, 100, 0.01, 10)
    corners = np.int0(corners)
    # Define the source and destination points for the perspective transform
    A4_width = 8.27
    A4_height = 11.69
    src = np.array([[0,0],[0,A4_height],[A4_width,A4_height],[A4_width,0]], dtype='float32')
    dst = np.array([[0,0],[0,image.shape[0]],[image.shape[1],image.shape[0]],[image.shape[1],0]], dtype='float32')

    # Calculate the perspective transform matrix
    transform_matrix = cv2.getPerspectiveTransform(src, dst)

    # Perform the perspective transform to correct the perspective of the image
    width = image.shape[1]
    height = image.shape[0]
    scan = cv2.warpPerspective(image, transform_matrix, (width, height))
    # Save the processed image back to the file

    file_bytes = cv2.imencode('.jpg', scan)[1].tobytes()

    return file_bytes