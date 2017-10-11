import re

# get_requst_string : String -> String
# GIVEN:a String url which is the page we want to get
# RETURNS: the GET request as a string
def get_requst_string(url):
    # get_req contains all the specifications of the GET request
    get_req = """
GET {} HTTP/1.1
Host: {}
Connection: Keep-Alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
DNT: 1
Accept-Encoding: deflate, sdch
Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2

""".format(url.path, url.netloc)

    return get_req

# sent_get : Sockt, String -> String
# GIVEN: a string contains a html page
# RETURNS: the page seperated to header and body parts
def seperate_http(httpObj):
    anchor = httpObj.find('\r\n\r\n')
    header = httpObj[:anchor]
    body = httpObj[anchor+4:]
    return (header, body)


# search_status : string -> string
# GIVEN: a page as a string
# RETURNS: the status code if it is found, otherwise the first line
# of the string
def search_status(httpString):
    # Initialize a list of status code
    statusCodeList = ['200 OK',
                      '500 INTERNAL SERVER ERROR',
                      '403 FORBIDDEN',
                      '404 NOT FOUND', 
                      '301 MOVED PERMANENTLY',
                      '302 FOUND']
    # The status to be returned is set to none
    status = ''

    # Search for each status code list
    # Return it as soon as we find one
    for statusCode in statusCodeList:
        status = re.search(statusCode,httpString)
        if status:
            return status.group()

    headerLine = httpString.split("\r\n")[0]

    try:
        splitedHeaderLine = headerLine.split()
        if splitedHeaderLine[1][0] == '3':
            return "3XX"
        elif splitedHeaderLine[1][0] == '4':
            return "4XX"
        elif splitedHeaderLine[1][0] == '5':
            return "5XX"
        else:
            return headerLine
    except IndexError as err:
        return headerLine