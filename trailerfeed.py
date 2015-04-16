#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import re
import sys
import shutil
import string
import logging
import datetime

dirname = os.path.dirname(os.path.realpath( __file__ ))
sys.path.append( os.path.join(dirname,"dependencies") )

sys.path.append( os.path.join(dirname,"dependencies","pytrailer") )
import pytrailer

sys.path.append( os.path.join(dirname,"dependencies","requests") )
import requests


def usage():
    return '''
usage: [-v] disc
    -h --help  Prints this usage information.
    -s Preferred height of video either 480/720/1080 valid values. Default 1080
    -v --verbose       print extra information
example: ./trailerfeed.py -s 720 ~/Movies/Trailers
'''

def isInternetConnectionAvailable():
    try:
        '''Google IP'''
        import urllib2
        response=urllib2.urlopen('http://74.125.228.100',timeout=5)
        return True
    except urllib2.URLError as err:
        return False

def removeInvalidCharsFromFilename(fileName):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    newFileName = ''.join(c for c in fileName if c in valid_chars)
    return newFileName

def fileNameForMovie(aptMovie):
    title = aptMovie.title
    year = datetime.date.today().year

    try:
        year = re.search(r'(\d{4})',aptMovie.releasedate).groups()[0]
    except:
        pass
    
    fileName = str(title) + ' (' + year + ')'

    return removeInvalidCharsFromFilename(fileName)

def downloadLinkForMovie(aptMovie,preferredResolution=1080):
    #Only 3 resolutions supported 480,720,1080.
    if preferredResolution > 1080:
        preferredResolution = 1080
    elif preferredResolution > 720:
        preferredResolution = 1080
    elif preferredResolution > 480:
        preferredResolution = 720
    else:
        preferredResolution = 480
    
    allTrailers = []
    
    try:
        allTrailers = aptMovie.get_trailerLinks()['Trailer']
    except:
        pass
    
    downloadLink = None
    downloadRes = 0
    
    for trailerUrl in allTrailers:
        res = 480

        if '720p' in trailerUrl:
            res = 720
        elif '1080p' in trailerUrl:
            res = 1080
            
        if res > downloadRes:
            downloadLink = trailerUrl
            
        if downloadRes >= preferredResolution:
            break
    
    if downloadRes < preferredResolution:
        downloadLink = downloadLink.replace('480p.',str(preferredResolution)+'p.')

    return downloadLink

def downloadUrlToPath(url,savePath):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
    }

    r = requests.get(url, headers=headers, allow_redirects=True, stream=True)

    if r.status_code != 200:
        logging.error('Failed to get correct response: ' + str(r.status_code))
        return;
    
    if not r.headers.get('content-length'): # no content length header
        with open(savePath, 'wb') as f:
            f.write(r.content)
    else:
        responseCurrent = 0
        responseSize = int(r.headers.get('content-length'))
        
        with open(savePath, 'wb') as f:
            for data in r.iter_content(chunk_size=1024):
                responseCurrent += len(data)
                done = int(50 * responseCurrent / responseSize)

                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                sys.stdout.flush()        
 
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
    
    logging.info('\n saved file ' + str(savePath))

    return

if __name__ == "__main__":
    
    if len(sys.argv) <= 1:
        logging.error('No folder argument')
        print usage()
        sys.exit(1)
        
    if isInternetConnectionAvailable() == False:
        print '''No internet connection found. Ripsnort requires internet access to run'''
        sys.exit(1)

    savePath=''
    height=1080

    argsList = sys.argv[1:]
    
    loggingLevel = "info"
    
    while ( len(argsList) > 0 ):
        arg = argsList[0]

        if arg == '-h' or arg == '--h' or arg == '--help':
            print usage()
            sys.exit(0)

        elif arg == '-v' or arg == '--v' or arg == '--verbose':
            loggingLevel = "debug"
            
        elif arg == '-s':
            argsList = argsList[1:]
            try:
                height = int(argsList[0])
            except ValueError as e:
                print usage()
                print 'Invalid argument for -s. Must be a number'
                sys.exit(2)

        else:
            savePath = arg

            if not os.path.isdir(savePath):
                print 'Folder path does not exist: ' + savePath
                sys.exit(1)

        #Remove last argument
        argsList = argsList[1:]
        
    if loggingLevel == "debug":
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
        logging.debug('Verbose logging enabled')
    elif loggingLevel == "info":
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
        
    logging.info('Fetching all trailers...')
    aptMovies = pytrailer.getMoviesFromJSON('http://trailers.apple.com/trailers/home/feeds/just_added.json')
    
    for movie in aptMovies:
        urlFetch = downloadLinkForMovie(movie,height)

        aptSaveName = fileNameForMovie(movie)
        
        if '.' in urlFetch:
            aptSaveName += '.' + urlFetch.split('.')[-1].lower()
        else:
            #Assume mov
            aptSaveName += '.mov'
        
        aptSavePath = os.path.join(savePath,aptSaveName)
        
        if (not os.path.exists(aptSavePath)) and urlFetch:
            #Download movie
            logging.info('Downloading ' + aptSaveName + ', ' + str(urlFetch))
            downloadUrlToPath(urlFetch,aptSavePath)

    print ' -- Done -- '
    sys.exit(0)


