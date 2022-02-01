class ItemChecker:

    @classmethod
    def dict_item(cls, d, *args, **kwargs):
        alt_value = kwargs['alt_value'] if kwargs else None
        try:
            if not d:
                return alt_value

            for a in args:
                d = d[a]
            return d
        except Exception:
            return alt_value

    @classmethod
    def array_item(cls, a, i, alt_value=None):
        try:
            if not a:
                return alt_value

            return a[i]
        except Exception:
            return alt_value

    