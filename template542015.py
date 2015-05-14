import httplib2
import pprint
import time
import os
import shutil
#import urllib2
#libraries for gdrive file operations
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from apiclient import errors
from apiclient import http
#libraries for web browsing
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#libraries for onedrive file upload
import onedrive
import commands #to read output

#libraries for dropbox file upload

class file:#bas class file
	authorized=False#whether authorization has taken place or not
	listupdated=False#whether file list is updated or not
	downloadfilepath=None
	#distributed
	def __init__(self,location):
		self.address=location#address of file on pc
		
	def upload(self):
		pass
	@staticmethod
	def authorize():
		pass

class gdrivefile(file):
	drive_service=None
	filelist=[]
	currentquota=None
	downloadfilepath='/home/utkarsh/Downloads/Syncitall Goodle drive Downloads'

	def upload(self):
		if gdrivefile.authorized==False :
			gdrivefile.authorize()
			gdrivefile.authorized=True

		FILENAME = self.address
		media_body = MediaFileUpload(FILENAME, mimetype='', resumable=True)
		body = {
		  'title': FILENAME,
		  'description': '',
		  'mimeType': ''
		}
		try:
			file = gdrivefile.drive_service.files().insert(body=body, media_body=media_body).execute()
			#iINSERT CODE TO UPDATE FILE LIST
		except errors.HttpError,error :
			print("error in uploading file")	

		#pprint.pprint(file)

	@staticmethod
	def authorize():
		CLIENT_ID = '268285193546-qpu3mbasinue8ofpiah50fu928lcf24b.apps.googleusercontent.com'
		CLIENT_SECRET = '0iyrUyCs-MhAIyOMeYKeeQO-'

		# Check https://developers.google.com/drive/scopes for all available scopes
		OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

		# Redirect URI for installed apps
		REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

		flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE,
                           redirect_uri=REDIRECT_URI)
		authorize_url = flow.step1_get_authorize_url()
		#print 'Go to the following link in your browser: ' + authorize_url
		driver=webdriver.Firefox()#depends on your browser
		driver.get(authorize_url)
		#login=driver.find_element_by_name("signIn")
		#login.send_keys(Keys.RETURN)
		accept= WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "submit_approve_access")))
		accept.send_keys(Keys.RETURN)
    	#accept.click()
		a=driver.find_element_by_id("code")

		code=a.get_attribute('value')
		driver.quit()
		#code = raw_input('Enter verification code: ').strip()#change here
		credentials = flow.step2_exchange(code)

		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		http = credentials.authorize(http)

		gdrivefile.drive_service = build('drive', 'v2', http=http)
	@staticmethod
	def updatefilelist():#information about files on your drive
		if gdrivefile.authorized==False :
			gdrivefile.authorize()
			gdrivefile.authorized=True
		page_token = None
		while True:
			try:
				param={}
				if page_token:
					param['pageToken']=page_token
				dfiles=gdrivefile.drive_service.files().list(**param).execute()
				gdrivefile.filelist.extend(dfiles['items'])
				page_token=dfiles.get('nextPageToken')
				gdrivefile.listupdated=True
				if not page_token:
					break
			except errors.HttpError:
				print("error in udating list")
				break
	@staticmethod
	def getfile():
		if gdrivefile.listupdated==False:
			gdrivefile.updatefilelist()
		ref=[]	
		sample=raw_input('enter the file name ').strip()
		for gfile in gdrivefile.filelist:#change here
			if sample in gfile['title']:
				if sample==gfile['title']:
					return gfile
				ref.append(gfile['title'])
		print("No match found.Following are the related files")
		for name in ref:
			print(name)	
		return None				



	@staticmethod					
	def download():
		file2download=gdrivefile.getfile()
		if file2download==None:
			return
		else:
			downloadedfile=open(file2download.get('title'),"wb")

			download_url=file2download.get('downloadUrl')
			if download_url:
				resp ,content=gdrivefile.drive_service._http.request(download_url)
				if resp.status==200:
					#print('Status',resp)
					downloadedfile.write(content)
					
					src=os.getcwd()+'/'+file2download.get('title')
					downloadaddress=raw_input('Where do you want to download file?enter address(d for default)').strip()

					if downloadaddress!= "d" :
						downloaddest=downloadaddress +'/'+file2download.get('title')
						
					else :
						downloaddest=gdrivefile.downloadfilepath+'/'+file2download.get('title')
						print(src)
						print(downloaddest)
					os.rename(src,downloaddest)	
						
					#src=r"C:\\Users\\windows\\Downloads\\" +  file2download.get('title')
					#dest=os.getcwd()+r"\\" file2download.get('title')
					#shutil.move(dest,src)	
						
					downloadedfile.close()
					#os.rename(dest,src)
					
				else :
					print("An error occured in downloading")
			else:
				print("No such file exists ")

	@staticmethod
	def getquota():
		if gdrivefile.authorized==False :
			gdrivefile.authorize()
			gdrivefile.authorized=True
		about=gdrivefile.drive_service.about().get().execute()	
		gdrivefile.currentquota=[about['quotaBytesTotal'],about['quotaBytesUsed']]
				
				

  			

class odrivefile(file):
	filelist=None
	currentquota=None
	downloadfilepath='/home/utkarsh/Downloads/Syncitall Onedrive Downloads'
	def upload(self):#problem-provided method does'nt allows upload of files with path name having spaces
		#code for upload
		if odrivefile.authorized ==False:
			odrivefile.authorize()
			odrivefile.authorized=True
		try :
			 	
			if ' ' not in self.address:#soln 1-no space in address upload the thing directly
				os.system("onedrive-cli put "+self.address)
				return
			#else	
			l=self.address.rfind('/')

			name=self.address[l+1:].strip()
			folder=self.address[:l+1]
			name2=name.replace(" ","")
			os.rename(folder+name,folder+name2)
			self.address=folder+name2
			print(name2)
			src=self.address
			print(src)
			dest=os.getcwd()+'/'+name2
			print(dest)
		
			os.rename(src,dest)
			os.system("onedrive-cli put "+name2)
			os.rename(dest,src)
			return
		except:
			print("error in uploading one drive file")	

	@staticmethod
	def authorize():
		#code for authorization
		'''
		client_id='000000004015642C'
		driver=webdriver.Firefox()
		client_secret='w2A-Ass34UsVdS16PqibDAOmgTdddlTZ'
		
		oredirecturi= 'https://login.live.com/oauth20_desktop.srf'
		startauturl='https://login.live.com/oauth20_authorize.srf?client_id='+client_id+'&scope='+ oscope+ '%20wl.basic&response_type=code&redirect_uri='+oredirecturi
		driver.get(startauturl)
		'''
		oscope='onedrive.readwrite'#scope=how do u want to get access(PROBLEM HERE)=REQUESTED SCOPE DOES'NT MATCHES GIVEN SCOPE
		driver=webdriver.Firefox()
		authurl= 'https://login.live.com/oauth20_authorize.srf?scope='+oscope+'&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&response_type=code&client_id=000000004015642C'
		driver.get(authurl)
		accept= WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.ID, "idBtn_Accept")))
		accept.send_keys(Keys.RETURN)
		endurl=str(driver.current_url)
		driver.quit()
		os.system("onedrive-cli auth "+ endurl)
	@staticmethod	
	def updatefilelist():
		if odrivefile.authorized ==False:
			odrivefile.authorize()
			odrivefile.authorized=True

		templist=commands.getstatusoutput('onedrive-cli ls')[1].strip()
		odrivefile.filelist=templist.split('\n')
		for x in range(len(odrivefile.filelist)):
			odrivefile.filelist[x]=odrivefile.filelist[x][2:]

		
		odrivefile.listupdated=True
		#print(odrivefile.filelist)


	@staticmethod
	def onedrivequota():
		if odrivefile.authorized ==False:
			odrivefile.authorize()
			odrivefile.authorized=True
		odrivefile.currentquota=commands.getstatusoutput('onedrive-cli quota')[1].strip()	

		'''
		FOR ONEDRIVE FILES GET FILE FUNCTION AND DOWNLOAD FUNCTIONS HAVE BEEN MERGED 
		BECAUSE I COUDNT PASS THE VARIABLE BY REFERENCE.
		FIND SOME METHOD TO DO SO AND 




			@staticmethod
			def getfile():
				if odrivefile.listupdated==False:
					odrivefile.updatefilelist()
				oname=raw_input('Enter file name or some reference :').strip()
				if oname in odrivefile.filelist:
					filename=oname#make changes here
				else:
					ref=[]
					for entry in odrivefile.filelist:
						if oname in entry:
							ref.append(entry)
					if ref==[]:
						print("No match for your search")
					else:
						print('May be you were looking for:')
						for	x in ref:
							print(x)
					odrivefile.getfile(filename)			

		'''
	@staticmethod
	def download():
		if odrivefile.listupdated==False:
			odrivefile.updatefilelist()
			odrivefile.listupdated=True
		oname=raw_input('Enter file name or some reference :').strip()
		if oname in odrivefile.filelist:
			filename=oname#make changes here
			print("this is the file name "+ filename)
			downloadedfile=open(filename,"wb")#open the final file
			ofile2download=raw_input("Enter address of file on one drive with format folder1/folder2..../filename").strip()
			#make something so it can get to his file easily(presently avoid folders)
			tempcontent=commands.getstatusoutput('onedrive-cli get '+ofile2download)
			downloadedfile.write(tempcontent[1])
			src=os.getcwd()+'/'+filename

			d=raw_input('Where do you want to store the file.write address (d for default):')
			if d=='d':
				d=odrivefile.downloadfilepath
			d=d+'/'+filename	
			os.rename(src,d)
			downloadedfile.close()			
			
		else:
			ref=[]
			for entry in odrivefile.filelist:
				if oname in entry:
					ref.append(entry)
			if ref==[]:
				print("No match for your search")
			else:
				print('May be you were looking for:')
				for	x in ref:
					print(x)
			odrivefile.download()

	@staticmethod
	def printfilelist():
		if odrivefile.listupdated==False:
			odrivefile.updatefilelist()
			odrivefile.listupdated=True	
		for ofile in odrivefile.filelist:
			print(ofile+ str(type(ofile)))
	@staticmethod
	def getinfo(name):
		
		'''
		namestrt=tempcontent.find('name:')
		namend=tempcontent[namestrt:].find('\n')
		name=tempcontent[namestrt:namend].strip()
		'''
		typestrt=tempcontent.find('type:')
		typend=tempcontent[typestrt:].find('\n')
		filetype=tempcontent[typestrt+5:typend].strip()
		return filetype

	@staticmethod
	def makefinallist(finallist,filelist,folderlist):#since strings are immutable they cannot be changed,list being mutable can be modified.
		#eachelement of list is folder's name in hiearchial folder
		#odrivefile.updatefilelist()
		
		for name in filelist:
			name.replace(' ','\n')
			tempcontent=commands.getstatusoutput('onedrive-cli info '+name)[1]
			#print(tempcontent)
			
			typestrt=tempcontent.find('type:')
			typend=tempcontent[typestrt:].find('\n')
			filetype=tempcontent[typestrt+6:typend].strip()
			print(filetype)
			print('PROBLEM HERE')
			if filetype=='file'	:
				for x in folderlist:
					folder=folder+x
				tmpodrivefile=odrivefile(folder+name)
				#y={name:tmpodrivefile}
				finallist.update({name:tmpodrivefile})
				return
			elif filetype=='folder':
				folderlist.append(name+'/')
				templistcontent=commands.getstatusoutput('onedrive-cli ls ' + name)[1].strip()
				templist=templistcontent.split('\n')
				for x in range(len(templist)):
					templist[x]=templist[x][2:]				
				makefinallist(finallist,templist,folderlist)
		if folderlist!=[]:	
			folderlist.pop()		
		
							
			

		
class drobboxfile(file):
	def upload(self):
		#code for upload
		pass

	@staticmethod
	def authorize():
		pass
		#code for authorization	
#testing the new update

#google drive testing takes place here
'''
while True:
	command=raw_input('which propoerty do you want to test for google drive :').strip()
	if command=="download":
		gdrivefile.download()
	elif command=="upload":
		add=raw_input("enter address of a file").strip()
		gdrivefile.upload(add)
	elif command =="updatefilelist":
		gdrivefile.updatefilelist()
		for name in gdrivefile.filelist:
			print name['title']
	elif command=="getquota":
		gdrivefile.getquota()		
		a=gdrivefile.currentquota
		for data in a:
			print(data)+ ' bytes'
	elif command=="exit" :
		break
	else :
		pass	
'''

#odrivefile.authorize()
#os.system("onedrive-cli put Game of Thrones S05E05 1080p HDTV [G2G.fm].srt")

		
#one drive testing 
#odrivefile.authorize()

#odrivefile.getfilelist()
#odrivefile.download()
#odrivefile.updatefilelist()
#odrivefile.download()
#odrivefile.oprintquota()
'''
odrivefile.updatefilelist()
odrivefile.printfilelist()
odrivefile.onedrivequota()
print(odrivefile.currentquota)
'''
#f1=odrivefile(raw_input('Enter address of file'))
#f1.upload()
'''
odrivefile.printfilelist()
odrivefile.upload()

'''
odrivefile.updatefilelist()

#os.system("onedrive-cli tree")
finallist={}
folder=[]
odrivefile.makefinallist(finallist,odrivefile.filelist,folder)
print(finallist)


#print(templink)
'''
for line in templink:
	print(line+'we did it')
'''
#code for getting link of a file in onedrive
'''-----------------------------------------------MAIN PROGRAM AFTERWARDS--------------------------------------------------------------------------------'''

'''--------------------------------------------------------------------------------------------------------------------------------------------------------'''



