import datetime
from typing import List, Optional


class Helper:
    """
    Several common helper functions
    """
    @staticmethod
    def getRazr(db_razr, coeff):
        result = db_razr
        is_tmp = False
        if result > 50:
            result -= 100
            is_tmp = True
        if result == 30:
            result = 1.2 if coeff is None else coeff * 0.3
        else:
            result /= 2
        return round(result, 1), is_tmp

    @staticmethod
    def getRazrStr(db_razr, coeff):
        (rz, isTmp) = Helper.getRazr(db_razr, coeff)
        return str(rz) + ('*' if isTmp else '')

    @staticmethod
    def shortPlayerName(lastname, firstname, fathername):
        result = (lastname if lastname else "") + ' '
        if firstname and firstname != '' and firstname != 'Щ':
            result += firstname[0]
        result += '.'
        if fathername and fathername != '' and fathername != 'Щ':
            result += fathername[0]
        result += '.'
        return result

    @staticmethod
    def getDate(target: datetime.date, available: List[datetime.date]) -> datetime.date:
        """
        :param target: requested date
        :param available: list of dates available
        :return: the appropriate date from he list
        """
        src: List[datetime.date] = sorted(available)
        if target < src[0]:
            return src[0]

        return next(d for d in reversed(src) if d <= target)

    @staticmethod
    def smartSplit(data: Optional[str]) -> list:
        result = [None]
        if data is not None:
            result = list(filter(lambda x: x != '', data.replace(",", ' ').replace(";", ' ').split(" ")))
        return result
