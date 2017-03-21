#!/usr/bin/env python

# This file include functions:
# search_page
# search_status
# search_url
# search_flag
# search_cookie
# search_csrftoken
# search_sessionid
# search_location

import re
import socket
import string
import fbCommunicator

# BUFFERSIZE is the memory size assigned to socket.recv()
BUFFERSIZE = 8192

##############################################################################
#
# The definition of read_page
#
# Contract of the function:
# read_page : string -> [string...]
#
# Purpose Statement:
# Given: a url as starting point
# Return: a list of url (under host: cs5700f16.ccs.neu.edu) found in this page
def search_page(pageHtml):

    # find new URLs and return a list of new urls
    urlList = search_url(pageHtml)
    
    # find secrect flags and print it the console
    flagCount = search_flag(pageHtml)

    return (urlList, flagCount)

##############################################################################
#
# The definition of search_status
#
# Contract of the function:
# search_status : string -> string
#
# Purpose Statement:
# GIVEN: a page as a string
# RETURNS: the status code if it is found, otherwise the first line
# of the string
# 
# The function definition:
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

#############################################################################
#
# The defintion of search_url
#
# Contract of the function:
# search_url : string -> [string...]
#
# Purpose Statement
# GIVEN: the page as a string
# RETURNS: a list of urls found in the page
#
# The function definition:
def search_url(httpString):

    # Find all strings in the following form and extract them
    urlList = re.findall('<a href="/fakebook(.+?)">',httpString)

    # If the list is not empty, add a prefix to each of the url
    if urlList:
        i = 0
        for url in urlList:
            urlList[i]= 'http://cs5700f16.ccs.neu.edu/fakebook' + urlList[i]
            i = i+1

    return urlList 

############################################################################
# The definition of search_flag
#
# Contract of the function:
# search_flag : string -> none
#
# Purpose Statement:
# GIVEN: a page as a string
# EFFECT: print all the flags found
#
# The definition
def search_flag(httpString):
    
    # Find all the stings in the following form and extract them
    FlagList = re.findall("""<h2 class='secret_flag' style="color:red">FLAG: (.+?)</h2>""",httpString)

    flagCount = 0
    if FlagList:
        for Flag in FlagList:
            flagCount += 1
            print Flag
    return flagCount

############################################################################
#
# The definition of search_cookie
#
# Contract of the funciton:
# search_cookie : string -> string
#
# Purpose Statement:
# GIVEN: a page as a string
# RETURNS: a cookie as a string
#
# The definition:
def search_cookie(httpString):
    csrftoken = ""
    sessionid = ""

    for line in response_list:
        if line.find("csrftoken=") != -1:
            csrftoken = re.search("Set-Cookie: csrftoken=(.+?);", line).group(0)[22:-1]
        if line.find("sessionid=") != -1:
            sessionid = re.search("Set-Cookie: sessionid=(.+?);", line).group(0)[22:-1]

############################################################################
#
# The definition of search_csrftoken
#
# Contract of the function:
# search_csrftoken : string -> string
#
# Purpose Statement:
# GIVEN: a page as a string
# RETURNS: a csrftoken
#
# The definition:
def search_csrftoken(httpString):
  
    # Split the string into lines
    for line in httpString.split("\r\n"):

        # for each line, if the csrftoken is found, extract and return it 
        if line.find("csrftoken=") != -1:
            csrftoken = re.search("Set-Cookie: csrftoken=(.+?);", line).group(0)[22:-1]
            return csrftoken

############################################################################
#
# The definition of search_sessionid
#
# Contract:
# search_sessionid : string -> string
#
# Purpose Statement:
# GIVEN: a page as a string
# RETURNS: a sessionid
#
# The definition:
def search_sessionid(httpString):
   
    #Split the string into lines
    for line in httpString.split("\r\n"):

        # for each line, if the sessionid is found, extract and return it
        if line.find("sessionid=") != -1:
            sessionid = re.search("Set-Cookie: sessionid=(.+?);", line).group(0)[22:-1]
            return sessionid

############################################################################
#
# The definiton of search_location
#
# Contract:
# search_location : string -> string
#
# Purpose Statement:
# GIVEN: a page as a string
# RETURNS: the location in the header as a string
#
# The definition:
def search_location(httpString):

    # Split the string into lines
    for line in httpString.split("\r\n"):

        # for each line, if the location is found, extract and return it
        if line.find("Location: ") != -1:
            location = line[10:]
            return location
