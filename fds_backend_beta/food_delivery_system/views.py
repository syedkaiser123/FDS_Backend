from django.http import HttpResponse


def homepage(request):
    return HttpResponse("<h1>Welcome to Food Delivery System API</h1>")

