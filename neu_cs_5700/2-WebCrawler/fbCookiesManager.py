#
# The definition of FBCookie
#
# Store the csrf token and session id information
# Offering cookie for program to perform further HTTP Requests
class FBCookie(object):
    """docstring for FBCookie"""
    csrftoken = ""
    sessionid = ""

    def __init__(self, ct, sid):
        super(FBCookie, self).__init__()
        FBCookie.csrftoken = ct
        FBCookie.sessionid = sid

    def __str__(self):
        return "cookie's csrf token: {}, cookie's session id: {}".format(FBCookie.csrftoken, FBCookie.sessionid)

    def set_csrftoken(self, ct):
        FBCookie.csrftoken = ct

    def get_csrftoken(self):
        return FBCookie.csrftoken

    def set_sessionid(self, sid):
        FBCookie.sessionid = sid

    def get_sessionid(self):
        return FBCookie.sessionid