class ItemChecker:

    @classmethod
    def json_item(cls, d, k):
        try:
            return d[k]
        except Exception:
            return None

    @classmethod
    def json_item_from_array(cls, d, k, i):
        item = cls.json_item(d, k)
        try:
            return item[i]
        except Exception:
            return None