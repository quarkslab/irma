# ______________________________________________________________ TASKS RESPONSE FORMATTER

class IrmaTaskReturn:
    @staticmethod
    def success(info):
        return (IrmaReturnCode.success, info)

    @staticmethod
    def warning(info):
        return (IrmaReturnCode.warning, info)

    @staticmethod
    def error(info):
        return (IrmaReturnCode.error, info)

# ______________________________________________________________ FRONTEND RESPONSE FORMATTER

class IrmaFrontendReturn:
    @staticmethod
    def response(code, info):
        return {"result":code, "info":info}

    @staticmethod
    def success(info):
        return IrmaFrontendReturn.response(IrmaReturnCode.success, info)

    @staticmethod
    def warning(info):
        return IrmaFrontendReturn.response(IrmaReturnCode.warning, info)

    @staticmethod
    def error(info):
        return IrmaFrontendReturn.response(IrmaReturnCode.error, info)

# ______________________________________________________________ RETURN CODE

class IrmaReturnCode:
    success = "success"
    warning = "warning"
    error = "error"
