from unittest import result
import requests
import time
import json
import os
from tqdm import tqdm

VALLY_TYPES = {"15c":"{k.f6}","9c":"{k.f1}","4446":"{k.f3}","3456":"{k.f2}","4536":"{k.f4}","free-oassis":"{k.fo}","captured-oasis":"{k.bt}","village":"{k.dt}"}
RECOURCES_TYPES =  {"wood":"{a:r1}","clay":"{a:r2}","iron":"{a:r3}","crop":"{a:r4}"}


LOGIN_API = "/api/v1/auth/login"
AUTH_API = "/api/v1/auth/"
MAIN_PAGE = "/dorf2.php"
MAP_PAGE = "/karte.php"
MAP_API = "/api/v1/map/position"
SERVER_MAPS = './server-maps/'

def login(domain,base_url,user,passw):
    headers = {}
    headers['Host'] = domain
    headers['Connection'] = 'keep-alive'
    headers['Content-Length'] = '0'
    headers['sec-ch-ua'] = '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"'
    headers['X-Version'] = '1644.12'
    headers['sec-ch-ua-mobile'] = '?0'
    headers['Authorization'] = 'Bearer undefined'
    headers['Content-Type'] = 'application/json; charset=UTF-8'
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    headers['X-Requested-With'] = 'XMLHttpRequest'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    headers['sec-ch-ua-platform'] = '"Windows"'
    headers['Origin'] = base_url
    headers['Sec-Fetch-Site'] = 'same-origin'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Referer'] = base_url + '/logout'
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    headers['Accept-Language'] = 'en-US,en;q=0.9,he;q=0.8'

    login_session = requests.Session()
    res = login_session.get(base_url,headers=headers)


    data = {
    "name":user,
    "password":passw,
    "w":"1920:1080",
    "mobileOptimizations": False
    }
    res = login_session.post(base_url+LOGIN_API,json=data)
    nonce = res.json()["nonce"]
    auth_url = base_url+AUTH_API+nonce
    # print("Auth at : "+auth_url)  
    res = login_session.post(auth_url,headers=headers)
    # print(res.json())
    api_token = res.json()["token"]
    return (login_session,headers,api_token)

def getMainPage(game_session,headers,base_url):
    res = game_session.get(base_url+MAIN_PAGE,headers=headers)
    res = game_session.get(base_url+MAP_PAGE,headers=headers)
    return (game_session,headers)

def getMapFile(game_session,headers,api_token,corX,corY,path,base_url):
    headers['Content-Length'] = '59'
    headers['Authorization'] = 'Bearer '+str(api_token)
    headers['Referer'] =  base_url + MAP_PAGE + '?x=0&y=0'

    # print(api_token)
    data = {"data":{"x":int(corX),
                    "y":int(corY),
                    "zoomLevel":3,
                    "ignorePositions":[]
                    }
    }
    mapAPIUrl = base_url+MAP_API
    res = game_session.post(mapAPIUrl,headers=headers,json=data)
    # print(res.status_code)
    map = open( path + str(corX) + "." + str(corY) + ".json",'w')
    map.write(json.dumps(res.json()))
    map.close()
    # print("got from server and saved file map for :   "+str(corX) + " | " + str(corY))

def getAllMapFiles(game_session,headers,api_token,domain,base_url):
    dirPath = SERVER_MAPS + domain + "/"
    try:
        os.makedirs(dirPath)
    except OSError:
        pass
    corPoints = [-180,-150,-120,-90,-60,-30,0,30,60,90,120,150,180]
    for x in corPoints:
        for y in corPoints:
            getMapFile(game_session,headers,api_token,x,y,dirPath,base_url)
            time.sleep(2)
    # print("All files were added At: " + dirPath)
    return (game_session,headers,api_token,dirPath)

def mapFilesToDicts(dirPath):
    # print("Converting files to list of dicts")
    mapFiles = []
    mapJSONS = []
    mapDictsList = []
    for filename in os.listdir(dirPath):
        fileFullPath = os.path.join(dirPath, filename)
        # checking if it is a file
        if os.path.isfile(fileFullPath):
            try:
                mapFile = open(fileFullPath,'r')
            except:
                # print("Could not open file:  "+str(fileFullPath))
                pass
            else:
                try:
                    mapFiles.append(mapFile)
                    mapJson = str(mapFile.read())
                    mapJSONS.append(mapJson)
                    mapDictsList.append(json.loads(mapJson))
                except:
                    # print("Error handling file:  "+str(fileFullPath))
                    pass
                else:
                    # print("File :  "+str(fileFullPath)+"   was added")
                    pass
                mapFile.close()
    # print("Done creating list of dicts")
    return mapDictsList

def generateJsonMap(dirPath="./"):
    if dirPath == "./":
        dirPath = input("Select files location : 1-defualt('./')    2-select domain and auto find path  3-enter costume path    :   ")
        if dirPath == '3': dirPath = input("Enter files location :   ")
        elif dirPath == '2': dirPath = './' + input("Enter server domain (without http://...)") + '/'
        else: dirPath = './'
    finalMapList = removeDuplicateTiles(MergeDicts(mapFilesToDicts(dirPath)))
    # print("Writing to final json file")
    finalJson = json.dumps({"tiles":finalMapList})
    f = open(dirPath + "finalJson.json","w")
    f.write(finalJson)
    f.close()
    return finalJson
    # print("Done writing json")


def MergeDicts(DictsList):
    # print("Merging all files to one")
    fullMapList = []
    for curDict in DictsList:
        fullMapList = fullMapList + curDict["tiles"]
    return fullMapList

def removeDuplicateTiles(fullMapList):
    # print("Removing duplicate tiles ...")
    finalMapList = []
    # [finalMapList.append(x) for x in tqdm(fullMapList) if x not in finalMapList]
    for tile in tqdm(fullMapList):
        if tile not in finalMapList: finalMapList.append(tile)
    return finalMapList

def handleGetMapFilesOnly(base_url,usr,passw):
    # print("lets initilize some starting values, okay?")
    # base_url = input("Paste the server url, with http://... and until .com    :   ")
    domain = base_url.split("//")[-1]
    # usr = input("Enter user name for the server, PLEASE do not use your personal account!    :   ")
    # passw = input("Enter user password for the server, PLEASE do not use your personal account!    :   ")

    (game_session,headers,api_token) = login(domain,base_url,usr,passw)
    getMainPage(game_session,headers,base_url)
    (game_session,headers,api_token,dirPath) = getAllMapFiles(game_session,headers,api_token,domain,base_url)
    return dirPath

def handleGetMapFilesAndProcess(base_url,usr,passw):
    return generateJsonMap(handleGetMapFilesOnly(base_url,usr,passw))


def findOasis(tilesList,corX,corY,rangeSearch,search):
    potentialTiles = []
    matchTiles = []
    # print("Searching for potential oasis: ")
    for tile in tqdm(tilesList):
        if abs(corX - int(tile["position"]["x"])) <= rangeSearch and abs(corY - int(tile["position"]["y"])) <= rangeSearch :
            potentialTiles.append(tile)
    # print ("potential found :" + str(len(potentialTiles)))
    ## print(potentialTiles)
    # print("Searching for matching oasis: ")
    for tile in potentialTiles:
        try:
            if search in tile["title"]:
                matchTiles.append(tile)
        except:
            pass
    # print("matchs found: "+str(len(matchTiles)))
    return matchTiles

def handleOasisSearch(filePath='./finalJson.json'):
    search = VALLY_TYPES[input("Search for : "+ str(VALLY_TYPES.keys())+"\n Select search (type exactly) :  ")]
    rangeSearch = int(input("Search range :  "))
    corX = int(input("your start point X :  "))
    corY = int(input("your start point Y :  "))
    mapFile = input("enter file path, enter 0 for defualt ('./finalJson.json') :  ")
    mapJson = json.loads(open(filePath,'r').read()) if mapFile == "0" else json.loads(open(mapFile,'r').read())
    result = findOasis(mapJson["tiles"],corX,corY,rangeSearch,search)
    # print(result,"\n\n\n")

