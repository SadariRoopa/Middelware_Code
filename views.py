from django.http import JsonResponse
from django.core.cache import cache
import time

RATE_LIMIT = 3      # requests
TIME_WINDOW = 60    # seconds

def rate_limit_view(request):
    ip = request.META.get('REMOTE_ADDR')
    key = f"rate_limit_{ip}"

    data = cache.get(key)

    current_time = time.time()

    if data:
        requests, start_time = data

        if current_time - start_time < TIME_WINDOW:
            if requests >= RATE_LIMIT:
                return JsonResponse(
                    {"error": "Too many requests"},
                    status=429
                )
            else:
                cache.set(key, (requests + 1, start_time), TIME_WINDOW)
        else:
            cache.set(key, (1, current_time), TIME_WINDOW)
    else:
        cache.set(key, (1, current_time), TIME_WINDOW)

    return JsonResponse({
        "status": "success",
        "message": "Request allowed"
    })
