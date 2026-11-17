class CabecalhosDeSegurancaMiddleware:
    """Aplica CSP e cabeçalhos modernos sem depender de pacote externo.

    O admin do Django usa scripts e estilos inline, por isso fica fora da CSP
    estrita; as demais rotas usam ``script-src 'self'``.
    """

    CSP = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
    PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=()"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/admin/"):
            return response
        response.setdefault("Content-Security-Policy", self.CSP)
        response.setdefault("Permissions-Policy", self.PERMISSIONS_POLICY)
        response.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        return response
