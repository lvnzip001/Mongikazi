from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("find-help/", views.find_help, name="find_help"),
    path("find-work/", views.find_work, name="find_work"),
    path("business/", views.business, name="business"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("trust-safety/", views.trust_safety, name="trust_safety"),
    path("pricing/", views.pricing, name="pricing"),
    path("portals/", views.portals, name="portals"),
    path("resources/", views.resources, name="resources"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
]
