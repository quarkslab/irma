# ______________________________________________________________ TASKS RESPONSE FORMATTER

class IrmaTaskReturn:
    @staticmethod
    def success(msg):
        return (IrmaReturnCode.success, msg)

    @staticmethod
    def warning(msg):
        return (IrmaReturnCode.warning, msg)

    @staticmethod
    def error(msg):
        return (IrmaReturnCode.error, msg)

# ______________________________________________________________ FRONTEND RESPONSE FORMATTER

class IrmaFrontendReturn:
    @staticmethod
    def response(code, msg, **kwargs):
        ret = {'code':code, 'msg':msg}
        ret.update(kwargs)
        return ret

    @staticmethod
    def success(**kwargs):
        return IrmaFrontendReturn.response(IrmaReturnCode.success, "success", **kwargs)

    @staticmethod
    def warning(msg, **kwargs):
        return IrmaFrontendReturn.response(IrmaReturnCode.warning, msg, **kwargs)

    @staticmethod
    def error(msg, **kwargs):
        return IrmaFrontendReturn.response(IrmaReturnCode.error, msg, **kwargs)

# ______________________________________________________________ RETURN CODE

class IrmaReturnCode:
    success = 0
    warning = 1
    error = -1
    label = {success:"success", warning:"warning", error:"error"}
