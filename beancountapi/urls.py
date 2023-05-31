"""
URL configuration for beancountapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from books import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"books", views.BookViewSet)
router.register(r"accounts", views.AccountViewSet)
router.register(r"currencies", views.CurrencyViewSet)
router.register(r"postings", views.PostingViewSet)
router.register(r"transactions", views.TransactionViewSet)
router.register(r"opens", views.OpenViewSet)
router.register(r"plaintext", views.PlaintextBookViewSet, basename="plaintext")
# router.register(r"balances", views.BalanceSheet, basename="balances")

urlpatterns = [
    path("balances/", views.BalanceSheet.as_view(), name="balancesheet"),
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls")),
]
