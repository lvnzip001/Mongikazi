from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .selectors import search_localities


@login_required
@require_GET
def locality_autocomplete(request):
    query = request.GET.get("q", "")
    results = [
        {
            "id": locality.pk,
            "label": locality.display_label,
            "name": locality.name,
            "province": locality.province,
            "type": locality.locality_type,
            "type_label": locality.get_locality_type_display(),
            "subtitle": locality.municipality or locality.province,
        }
        for locality in search_localities(query, limit=12)
    ]
    return JsonResponse({"results": results})
