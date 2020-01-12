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
        return result, is_tmp

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
