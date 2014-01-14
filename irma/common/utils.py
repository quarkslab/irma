# ______________________________________________________________ RESPONSE FORMATTER

def response(code, info):
    return {"result":code, "info":info}

def success(info):
    return (IrmaRetCode.success, info)

def warning(info):
    return (IrmaRetCode.warning, info)

def error(info):
    return (IrmaRetCode.error, info)

# ______________________________________________________________ RETURN CODE

class IrmaRetCode:
    success = "success"
    warning = "warning"
    error = "error"