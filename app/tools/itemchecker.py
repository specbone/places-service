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

    @classmethod
    def has_empty_params(cls, l, any_item=False):
        if any_item:
            return any(True if not li else False for li in l)

        return not any(True if li else False for li in l)
    
    @classmethod
    def has_duplicates(cls, l):
        return len(l) != len(set(l))
    
    @classmethod
    def get_duplicates(cls, l):
        seen = []
        duplicates = [li for li in l if li in seen or seen.append(li)]
        return duplicates

    