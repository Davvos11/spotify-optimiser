def get_bool(query: str, true="y", false="n", default=True) -> bool:
    x = "[{true}/{false}]".format(true=(true.upper() if default else true.lower()),
                                  false=(false.lower() if default else false.lower()))
    answer = input(query + " " + x)
    if answer == "":
        return default
    else:
        return answer.lower() == true.lower()
