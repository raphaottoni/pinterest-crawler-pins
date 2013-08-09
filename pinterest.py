import urllib2
import time
import random
import socket
import MySQLdb
from config import *
import os,re

class Pinterest:
  #------inicializacao -------#
  def __init__(self, verbose=0):
    self.db = MySQLdb.connect(host,user,password,database)
    self.cursor = self.db.cursor()
    self. cursor.connection.autocommit(True)

  def findError(self,html):
        erro = re.search("HTML-Error-Code: ([0-9]*)\n",html)
        if (erro):
            #print "achei o erro-"+erro.group(1)
            return erro.group(1)
        else:
            return 0

  def analyzeAnswer(self,html):

    code = self.findError(html)
    if (code != 0):
        if code == "404":
            return 1
        else:
            print "dormindo - code " + code
            time.sleep(random.randint(0,2))
            return 2
    else:
        return 0

  def fetch(self,url):
    done=0
    while(not done):
        html = os.popen("phantomjs ./pinterest.js "+url).read()
        answerCode = self.analyzeAnswer(html)
        if (answerCode == 0):
            done=1;
        elif (answerCode == 1):
            return 1
    return html

  def getImage(self,url):
    done=0
    while(not done):
        try:
            print "tentando pegar"
            req = urllib2.Request(url, None)
            f = urllib2.urlopen(req)
            html = f.read()
            done=1;
        except urllib2.HTTPError, e:
            if ( hasattr(e, 'code') and (e.code == 404 or e.code == 403)):
              return 1
            continue
        except urllib2.URLError, e:
          if ( hasattr(e, 'code') and (e.code == 404 or e.code == 403)):
            return 1
          continue
        except Exception , e :
          print e
          time.sleep(random.randint(0,2))
          continue
    return html


  def fetchPins(self,url,qtd):
    done=0
    while(not done):
        html = os.popen("phantomjs ./pinterestPin.js "+url+ " " +qtd).read()
        answerCode = self.analyzeAnswer(html)
        if (answerCode == 0):
            done=1;
        elif (answerCode == 1):
            return 1
    return html


  def fetchSimple(self,url):
    done=0
    while(not done):
       print "coletando"
       html = os.popen("phantomjs ./pinterestSimple.js "+url).read()
       answerCode = self.analyzeAnswer(html)
       if (answerCode == 0):
            done=1;
       elif (answerCode == 1):
            return 1
    return html


  def snowBall(self):
          self.cursor.execute("select pinterestID from fatos where statusIDs is null or statusIDs = 0 limit 1")
          self.db.commit()
          return self.cursor.fetchone()[0]
  def getIDtoCrawl(self):
          self.cursor.execute("select pinterestID from usersToCollect where statusColeta is null or statusColeta = 0 order by rand() limit 1")
          self.db.commit()
          return self.cursor.fetchone()[0]


  def insereID(self,pinterestID):
        try:
          self.cursor.execute("insert into fatos (pinterestID) values ('"+pinterestID+"')")
          self.db.commit()
        except MySQLdb.IntegrityError, e:
          log = open("/var/tmp/log","a+")
          log.write("Erro de integridade do banco: '"+ str(e)+ "' \n")
          log.close()
  def statusColetaIDs(self,pinterestID,valor):
        try:
          self.cursor.execute("update usersToCollect set statusIDs ='"+valor+"' where pinterestID = '"+pinterestID+"'")
          self.db.commit()
          print "update usersToCollect set statusIDs ='"+valor+"' where pinterestID = '"+pinterestID+"'"
        except Exception, e:
          log = open("/var/tmp/log","a+")
          log.write("Erro de integridade do banco: '"+ str(e)+ "' \n")
          log.close()
  def statusColeta(self,pinterestID,valor, dominio):
        try:
          self.cursor.execute("update usersToCollect set statusColeta ='"+valor+"' , crawler = '"+dominio+"' where pinterestID = '"+pinterestID+"'")
          self.db.commit()
          print "update usersToCollect set statusColeta ='"+valor+"' , crawler = '"+dominio+"' where pinterestID = '"+pinterestID+"'"
        except Exception, e:
          log = open("/var/tmp/log","a+")
          log.write("Erro de integridade do banco: '"+ str(e)+ "' \n")
          log.close()
  def nPinsUser(self,pinterestID,valor):
        try:
          self.cursor.execute("insert into deltaPinUsers (pinterestID,nPins) values  ('"+pinterestID+"' , '"+valor+"')")
          self.db.commit()
          #print ("insert into deltaPinUsers (pinterestID,nPins) values  ('"+pinterestID+"' , '"+valor+"')")
        except Exception, e:
          print str(e)
          log = open("/var/tmp/log","a+")
          log.write("Erro de integridade do banco: '"+ str(e)+ "' \n")
          log.close()

