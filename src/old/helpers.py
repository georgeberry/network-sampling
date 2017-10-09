def stringify_parameters(parameters):
    stringified = ""
    connect = "-"
    for i,p in enumerate(parameters):
        if i == 0 and connect == "-":
            connect = ""
        if type(p) is tuple or type(p) is list:
            if len(p) != 0:
                stringified += (connect + stringify_parameters(p))
                connect = "-"
        elif callable(p):
            stringified += (connect + p.__name__)
            connect = "-"
        else:
            stringified += (connect + str(p))
            connect = "-"
    return stringified


def get_n_samples(fn, n=200):
    """
    E.g. the value after 200 draws
    """
    for idx in range(n):
        val = next(fn)
    return val
