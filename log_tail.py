import time
from os import stat
from os.path import abspath
from stat import ST_SIZE
import marshal

class LogTail:
    def __init__(self, logfile, posfile):
        self.postracker = {}
        self.posfile = posfile
        self.logfile = abspath(logfile)
        self.f = open(self.logfile,"r")
        prev_pos = self._get_pos_marker()
        print "\t got pos marker at %s" % (prev_pos)

        file_len = stat(self.logfile)[ST_SIZE]
        if (file_len < prev_pos):
            print "RESET"
            # ok, the file size got smaller
            # in this case, treat it as a new file.
            self._reset()
        else:
            print "GOTO PREV ", prev_pos
            # ok, the file size increased, or stayed the same
            #  just move to the last pos, and process the file.
            self._goto(prev_pos)

    def _reset(self):
        self.f.close()
        self.f = open(self.logfile, "r")
        self._goto(0)
        self._place_pos_marker(0)

    def catchup(self):
        file_len = stat(self.logfile)[ST_SIZE]
        self.f.seek(file_len)
        self._place_pos_marker(file_len)

    def _goto(self, new_pos):
        self.f.seek(new_pos)
        self.pos = self.f.tell()
        print "  seek to  :", new_pos
        print "  set pos to :", self.pos

    def _place_pos_marker(self, newpos):
        self.postracker[self.logfile] = newpos
        self.pos = newpos
        ouf = open(self.posfile, 'wb')
        marshal.dump(self.postracker, ouf)
        ouf.close()

    def _get_pos_marker(self):
       if self.posfile == None:
           return 0
       try:
           inf = open(self.posfile, 'rb')
           self.postracker = marshal.load(inf)
           inf.close()
           if self.postracker.has_key(self.logfile):
              return self.postracker[self.logfile]
       except:
           print "Problem loading pos."
       return 0
        
    def tail(self, processor_func, catchup=True):
        print " pos before catch up: ", self.pos
        if catchup:
            self.catchup()

        print " pos after catch up: ", self.pos
        while 1:
            self.pos = self.f.tell()
            line = self.f.readline()
            if not line:
                if stat(self.logfile)[ST_SIZE] < self.pos:
                    self._reset()
                else:
                    time.sleep(1)
                    self.f.seek(self.pos)
            else:
               processor_func(line)
               self._place_pos_marker(self.f.tell())
               

def process(line):
    print "PP: %s" % (line)

if __name__ == "__main__":
    l = LogTail("haproxy_0.log", "./pos")
    l.tail(process, False)
