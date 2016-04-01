import os
import Queue
import threading
import urllib2
class DownloadThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url = self.queue.get()
            print self.name + "begin download" + url + "..."
            self.download_file(url)
            self.queue.task_done()
            print self.name + " download completed!!!"

    def download_file(self, url):
        urlhandler = urllib2.urlopen(url)
        fname = os.path.basename(url) + ".html"
        with open(fname, "wb") as f:
            while True:
                chunk = urlhandler.read(1024)
                if not chunk: break
                f.write(chunk)

if __name__ == "__main__":
     urls = ["https://github.com/EnigmaCurry/blogofile",
             "http://stackoverflow.com/questions/7835272/django-operationalerror-2006-mysql-server-has-gone-away",
             "http://www.iteye.com/problems/91073"]

     queue = Queue.Queue()
     for i in range(5):
         t = DownloadThread(queue)
         t.setDaemon(True)
         t.start()

     for url in urls:
         queue.put(url)
     queue.join()