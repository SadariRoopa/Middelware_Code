from django.http import JsonResponse
from django.core.cache import cache
import time

class RateLimitMiddleware:
    """
    Allows only N requests per time window from one IP.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 5          # ✅ requests allowed
        self.window = 60        # ✅ time window in seconds (60 sec)

    def __call__(self, request):
        ip = self.get_client_ip(request)
        cache_key = f"rl:{ip}"

        data = cache.get(cache_key, {"count": 0, "start": time.time()})
        current_time = time.time()

        # Reset window if time passed
        if current_time - data["start"] > self.window:
            data = {"count": 0, "start": current_time}

        data["count"] += 1
        cache.set(cache_key, data, timeout=self.window)

        if data["count"] > self.limit:
            return JsonResponse(
                {"error": "Rate limit exceeded. Try again later."},
                status=429
            )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
