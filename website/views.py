from django.shortcuts import render


def home(request):
    """Public landing page."""
    return render(request, "website/home.html")


def find_help(request):
    """Employer-facing marketing page."""
    return render(request, "website/find_help.html")


def find_work(request):
    """Helper-facing marketing page."""
    return render(request, "website/find_work.html")


def business(request):
    """Business and recurring client information page."""
    return render(request, "website/business.html")


def how_it_works(request):
    """Explains the platform process for employers and helpers."""
    return render(request, "website/how_it_works.html")


def trust_safety(request):
    """Trust, verification, safety, and review explanation."""
    return render(request, "website/trust_safety.html")


def pricing(request):
    """High-level pricing and commission explanation."""
    return render(request, "website/pricing.html")


def portals(request):
    """Prepared placeholder links to future role-based portals."""
    return render(request, "website/portals.html")


def resources(request):
    """Prepared brochure, guide, and resource placeholders."""
    return render(request, "website/resources.html")


def about(request):
    """Mission and company story page."""
    return render(request, "website/about.html")


def contact(request):
    """Contact and enquiry page."""
    return render(request, "website/contact.html")


def faq(request):
    """Frequently asked questions."""
    return render(request, "website/faq.html")
