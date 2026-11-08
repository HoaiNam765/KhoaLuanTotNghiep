"""User-interface number types and display formats (no model or research changes)."""

INTEGER_VARIABLES=frozenset({'RIDAGEYR','PAD680'})


def number_input_kwargs(variable):
    """Use native integers for age/sitting time and trim trailing zeros on measurements.

    Returning value=None prevents median placeholders being misread as measured values.
    """
    if variable=='RIDAGEYR':
        return {'min_value':18,'max_value':80,'value':None,'step':1,'format':'%d'}
    if variable in INTEGER_VARIABLES:
        return {'min_value':0,'max_value':100000,'value':None,'step':1,'format':'%d'}
    return {'min_value':0.0,'max_value':100000.0,'value':None,'step':0.1,'format':'%g'}
