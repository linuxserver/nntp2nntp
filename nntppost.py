import sys, os, re, time
from netrc import netrc
from email.Message import Message
from email.utils import make_msgid
from twisted.news.nntp import NNTPClient
from twisted.internet import ssl, reactor, defer
from twisted.internet.protocol import ClientFactory

if len(sys.argv) < 5:
    sys.stderr.write("Usage: %s <from> <groups> <subject> <file1.ync> [file2.ync ...]\n" % sys.argv[0])
    sys.stderr.write("""
The server comes from NNTPSERVER environment variable and
authentication information should be stored in ~/.netrc.

To post files they need to be encoded with yencode first:
http://sourceforge.net/projects/yencode/

The subject will be automatically extended with file information.
""")
    sys.exit(1)

re_file_multi = re.compile(r'^=ybegin part=(?P<part>[0-9]+) total=(?P<total>[0-9]+) line=[0-9]+ size=(?P<size>[0-9]+) name=(?P<name>.*?)\s*$')
re_file_single = re.compile(r'^=ybegin line=[0-9]+ size=(?P<size>[0-9]+) name=(?P<name>.*?)\s*$')
messages = {}
fromaddr = sys.argv[1].strip()
groups = [newsgroup.strip() for newsgroup in sys.argv[2].split(',')]
comment = sys.argv[3].strip().replace('%', '%%')
subject = """[%(file)d/%(files)d] """ + comment + """ - "%(name)s" yEnc (%(part)d/%(parts)d) %(size)d bytes - file %(file)d of %(files)d"""
file_list = sys.argv[4:]
filecount = 1
nntpserver = os.environ.get('NNTPSERVER', 'news-europe.giganews.com:443')
nntpport = 443
if ':' in nntpserver:
    nntpserver, nntpport = nntpserver.split(':')
    nntpport = int(nntpport)
nntpuser, _, nntppass = netrc().authenticators(nntpserver) or (None, None, None)

print "Process yEnc files"
for yncfile in file_list:
    if not os.access(yncfile, os.R_OK):
        raise RuntimeError("ERROR: file %s is not readable" % repr(yncfile))
    with open(yncfile) as fd:
        ync_line = fd.readline().strip()
    ma_file = re_file_multi.match(ync_line) or re_file_single.match(ync_line)
    if not ma_file:
        raise RuntimeError("ERROR: file %s does not seem to be yEnc file" % repr(yncfile))
    ma_file = ma_file.groupdict()
    part = int(ma_file.get('part', 1))
    total = int(ma_file.get('total', 1))
    size = int(ma_file['size'])
    name = ma_file['name']
    if name in messages:
        curparts, curtotal, curcount = messages[name]
        if curtotal != total or part in curparts:
            raise RuntimeError("ERROR: inconsistency with file %s" % repr(yncfile))
        curparts.append([part, None, yncfile, size])
    else:
        messages[name] = ([[part, None, yncfile, size]], total, filecount)
        filecount = filecount + 1
    print "...processed file", yncfile
filecount -= 1

print "Check parts and generate subjects"
for name, value in messages.items():
    parts, total, curfile = value
    lastpart = 0
    parts.sort()
    for part in parts:
        if part[0] != lastpart + 1:
            raise RuntimeError("ERROR: part %d for file %s not exist" % (lastpart + 1, name))
        lastpart += 1
        part[1] = subject % {
            'part'  : part[0],
            'parts' : total,
            'name'  : name,
            'file'  : curfile,
            'files' : filecount,
            'size'  : part[3],
        }
    print "...processed file", name

def postFilesGenerator():
    print "Post %d files in parts" % len(messages)
    for name, value in messages.items():
        parts, total, curfile = value
        print "...post file", curfile
        for num, subj, fname, size in parts:
            with open(fname) as src:
                lines = len(src.readlines())
            with open(fname) as src:
                bytecount = len(src.read())
            print "....%s" % subj
            msgid = make_msgid()
            msgid = re.sub(r'@.*>$', '@notexists.local>', msgid)
            msgid = msgid.replace('<', '<Part%dof%d.' % (num, total))            
            with open(fname) as src:
                msgdata = src.read()
            msg = Message()
            msg["From"] = fromaddr
            msg["Subject"] = subj
            msg["User-Agent"] = "postfiles.py (http://sourceforge.net/projects/nntp2nntp/)"
            msg["X-No-Archive"] = "yes"
            msg["Message-Id"] = msgid
            msg["Lines"] = str(lines)
            msg["Bytes"] = str(bytecount)
            msg.set_payload(msgdata)
            yield msg.as_string()
        print "...processed file", name


class PosterClient(NNTPClient):
    def __init__(self, postparts):
        NNTPClient.__init__(self)
        self._postparts = postparts

    def quit(self):
        NNTPClient.quit(self)
        reactor.stop()

    def failed(self, message, error):
        print message + ":", error
        self.quit()
    postFailed = lambda s, e: s.failed("Posting failed", e)
    authFailed = lambda s, e: s.failed("Auth failed", e)
    
    def _headerInitial(self, (code, message)):
        NNTPClient._headerInitial(self, (code, message))
        if nntpuser != None:
            self.sendLine('AUTHINFO USER ' + nntpuser)
            self._newState(None, self.authFailed, self.authUserOk)
        else: self.postArticle(self._postparts.next())

    def authUserOk(self, (code, message)):
        if code != 381: self.authFailed(error)
        self._endState()
        self.sendLine('AUTHINFO PASS ' + nntppass)
        self._newState(None, self.authFailed, self.authPassOk)

    def authPassOk(self, (code, message)):
        if code != 281: self.authFailed(error)
        self._endState()
        data = self._postparts.next()
        self.postArticle(data)

    def postedOk(self):
        try: self.postArticle(self._postparts.next())
        except StopIteration: self.quit()

class PosterFactory(ClientFactory):
    def buildProtocol(self, addr):
        return PosterClient(postFilesGenerator())

print "Connect to server", nntpserver
factory = PosterFactory()
reactor.connectSSL(nntpserver, nntpport, PosterFactory(), ssl.CertificateOptions())
reactor.run()
print "All files successfully posted."
