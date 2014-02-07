import client


c = client.Client()
print "[-] System status:"
c.status()

fn = "/home/alex/tmp/samples/virus.zip"
#fn = "/home/alex/ida23.png"
print "[-] File %s scan"%fn
print c.scan(fn)

