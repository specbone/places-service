class ItemChecker:

    @classmethod
    def json_item(cls, d, k, alt_return=None):
        try:
            return d[k]
        except Exception:
            return alt_return

    @classmethod
    def json_item_from_array(cls, d, k, i, alt_return=None):
        item = cls.json_item(d, k)
        try:
            return item[i]
        except Exception:
            return alt_return