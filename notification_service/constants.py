class CSP:
    """The “special” source values of 'self', 'unsafe-inline', 'unsafe-eval', 'none'
    and hash-source ('sha256-...') must be quoted! e.g.: CSP_DEFAULT_SRC = ("'self'",).
    Without quotes they will not work as intended.
    Ref. https://django-csp.readthedocs.io/en/stable/configuration.html.
    """

    SELF = "'self'"
    NONE = "'none'"
    UNSAFE_INLINE = "'unsafe-inline'"
    UNSAFE_EVAL = "'unsafe-eval'"
