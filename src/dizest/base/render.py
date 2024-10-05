from abc import *
import traceback

class BaseRenderer:
    className = []
    hasAttribute = []

    def check(self, value):
        for item in self.className:
            try:
                if isinstance(value, item):
                    return True
            except:
                pass
            try:
                if value == item:
                    return True
            except:
                pass
        for item in self.hasAttribute:
            if hasattr(value, item):
                return True
        return False

    def render(self, value, **kwargs):
        try:
            res = self.__render__(value, **kwargs)
        except Exception as e:
            try:
                res = self.__error__(value, e, **kwargs)
            except:
                res = value
        return res

    def __error__(self, value, err, **kwargs):
        stderr = traceback.format_exc().replace("\n", "<br>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;").replace(" ", "&nbsp;").strip()
        stderr = f"<div class='text-red'>{stderr}</div>"
        return stderr

    @abstractmethod
    def __render__(self, value, **kwargs):
        pass