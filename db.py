import commands

def run_mysql(query, column_header=True, db="operations"):
  user = 'your mysql user'
  passwd = "your mysql pass"
  host = "your mysql host"

  options = " -e "
  if not column_header:
    options = " -sse "

  cmd = "mysql -u %s -h %s -p%s %s %s '%s'" % (user, host, passwd, db, options, query)
  print "Running %s" % cmd
  out = commands.getoutput(cmd)
  print out
  return out.split("\n")
