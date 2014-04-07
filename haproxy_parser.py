import time
import datetime
from os import stat
from os.path import abspath, basename
from stat import ST_SIZE
import marshal
import re

from log_tail import LogTail
from db import run_mysql


pattern = re.compile(r'haproxy\[(?P<pid>\d+)]: ' 
                     r'(?P<client_ip>(\d{1,3}\.){3}\d{1,3}):' 
                     r'(?P<client_port>\d{1,5}) ' 
                     r'\[(?P<accept_date>\d{2}/\w{3}/\d{4}(:\d{2}){3}\.\d{3})] ' 
                     r'(?P<frontend_name>\S+) ' 
                     r'(?P<backend_name>\S+)/' 
                     r'(?P<server_name>\S+) ' 
                     r'(?P<Tq>(-1|\d+))/' 
                     r'(?P<Tw>(-1|\d+))/' 
                     r'(?P<Tc>(-1|\d+))/' 
                     r'(?P<Tr>(-1|\d+))/' 
                     r'(?P<Tt>\+?\d+) ' 
                     r'(?P<status_code>\d{3}) ' 
                     r'(?P<bytes_read>\d+) ' 
                     r'(?P<captured_request_cookie>\S+) ' 
                     r'(?P<captured_response_cookie>\S+) ' 
                     r'(?P<termination_state>[\w-]{4}) ' 
                     r'(?P<actconn>\d+)/' 
                     r'(?P<feconn>\d+)/' 
                     r'(?P<beconn>\d+)/' 
                     r'(?P<srv_conn>\d+)/' 
                     r'(?P<retries>\d+) ' 
                     r'(?P<srv_queue>\d+)/' 
                     r'(?P<backend_queue>\d+) ' 
                     r'(\{(?P<captured_request_headers>.*?)\} )?' 
                     r'(\{(?P<captured_response_headers>.*?)\} )?' 
                     r'"(?P<http_request>.+)"' 
                     ) 

def process(line):
    match = pattern.search(line)
    if not match:
        print "\t couldn't match:\n ", line
        print "-" * 80
        return
    fields = match.groupdict()
    write(fields)

def write(d):
    # note, it would be better to use mysql specific escaping, not just use re.escape
    try:
      request = d["http_request"]
 
      if should_ignore(request):
         return
      request = re.escape(request)[0:250]
      total_time = d["Tt"]
      processing_time = d["Tr"]
      status_code = d["status_code"]
      server = d["server_name"]
      clientip = d["client_ip"]
      dt = datetime.datetime.strptime(  d["accept_date"], "%d/%b/%Y:%H:%M:%S.%f").strftime('%Y-%m-%d %H:%M:%S')
 
      sql = "insert into haproxy(`accept_date`,`clientip`, `tt`, `tr`, `code`, `request`, `server`) values(\"%s\", \"%s\", %s, %s, %s, \"%s\", \"%s\"); " % (dt, clientip, total_time, processing_time, status_code, request, server)
      run_mysql(sql) 
    except:
      print "unable to write: ", d

def should_ignore(request):
    if request.startswith("GET /js"):
       return True
    if request.startswith("GET /images"):
       return True
    if request.startswith("GET /css"):
       return True
    
    return False

if __name__ == "__main__":
    log = "/var/log/haproxy_0.log"
    pos_file =  "%s.pos" % (basename(log).replace(".", "_"))
    l = LogTail(log, pos_file)
    l.tail(process, True)
