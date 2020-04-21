import requests 
import json
import re
from dateutil import parser

docPattern = re.compile(r'global\.document\.metadata=([\s\S]+?);?\s*</script>', re.IGNORECASE)
datePattern = re.compile(r'\d+-(\d+\s+\w+\s+\d+)')

class Document:

    def __init__(self, title=None, id=None, citeBool=True, refBool=True):
        self.id = id 
        self.title = title
        self.abstract = None
        self.publishDateStr = None
        self.publishYear = None
        self.publicationTitle = None
        self.authors = []
        self.keywords = []
        self.references = []
        self.citations = []
        


        # TO DO:
        # - publish date (conference date, or publish date, in that order)
        # - abstract
        # - conference name (if applicable)
        # - journal (if applicable)
        # - keywords


        if id != None:
            self.id = id
            self.populate_info_from_doc_page()

            if refBool:
                self.references = self.get_refs_by_doc_id(id)
            if citeBool:
                self.citations = self.get_citations_by_id(id)

        elif title != None:
            self.title = title

            results = self.get_refs_by_doc_name(title)

            if 'docId' in results:
                self.id = results['docId']
                if citeBool:    
                    self.citations = self.get_citations_by_id(self.id)
            
            if refBool and'references' in results:
                self.references = results['references']
            
            if 'authors' in results:
                self.authors = results['authors']

            
    
    def get_refs_by_doc_id(self, docId):
        '''
        Given a document id returns a list of that document's references
        returns a list of reference document ids
        '''

        RefsLink = 'https://ieeexplore.ieee.org/document/' + docId + '/references'
        GetLink = 'https://ieeexplore.ieee.org/rest/document/' + docId + '/references'
        Headers={'Referer':RefsLink + '#references'}
        refReq = requests.get(GetLink, headers=Headers)

        docRefsDict = json.loads(refReq.text)
        refDocIds = []
        if 'references' in docRefsDict:
            refsList = docRefsDict['references']
            
            for ref in refsList:
                if 'links' in ref:
                    linksDict = ref['links']
                    if 'documentLink' in linksDict:
                        # print(linksDict['documentLink'])
                        refId = list(filter(None, linksDict['documentLink'].split('/')))[1]
                        refDocIds.append(refId)
        return refDocIds

    def get_citations_by_id(self, docId):
        #TO DO: ADD ERROR HANDLING
        citationList = []

        headers = {
            'Referer': 'https://ieeexplore.ieee.org/document/'+docId+'/citations',
            }

        response = requests.get('https://ieeexplore.ieee.org/rest/document/'+ docId +'/citations', headers=headers)
        respDict = json.loads(response.text)
        if 'paperCitations' in respDict:
            if 'ieee' in respDict['paperCitations']:
                citationDict = respDict['paperCitations']['ieee']
                for citation in citationDict:
                    if 'links' in citation:
                        linksDict = citation['links']
                        if 'documentLink' in linksDict:
                            citationId = list(filter(None, linksDict['documentLink'].split('/')))[1]
                            citationList.append(citationId)
        return citationList
        # print(respDict['paperCitations']['ieee'][0]['links']['documentLink'])

    def get_doc_title_by_id(self, docId):
        docTitle = ''
        headers = {
        'Referer': 'https://ieeexplore.ieee.org/document/'+ docId,
        }

        try:
            response = requests.get('https://ieeexplore.ieee.org/rest/document/' + docId + '/toc', headers=headers)
            responseDict = json.loads(response.text)
            if 'standardTitle' in responseDict:
                docTitle = responseDict['standardTitle']
            elif 'title' in responseDict:
                docTitle = responseDict['standardTitle']
        except:
            print('Request for document title by id failed.')

        return docTitle

    def search_by_doc_name(self, docName):
        '''
        Given a document name will return a dictionary of the search results
        '''
        docRef = docName.split()
        
        Referer = 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText='
        for w in docRef:
            Referer += '%'+w

        headers = {
            'Content-Type': 'application/json',
            'Referer':Referer
        }

        data = '{"queryText":"' + docName + '","returnFacets":["ALL"]}'

        response = requests.post('https://ieeexplore.ieee.org/rest/search', headers=headers, data=data)
        
        responseDict = json.loads(response.text)
        return responseDict

    def get_authors_by_doc_search(self, docTitle, docId):
        results = {}
        docAuthorList = []

        searchResults = self.search_by_doc_name(docTitle) #will return a dictionary 
        # print(searchResults)
        if 'records' not in searchResults:
            print(f'No results for {docTitle}')
            return None

        try:
            for i, result in enumerate(searchResults['records']):
                if 'articleNumber' in result:
                    if result['articleNumber'] == docId:
                        authors = searchResults['records'][i]['authors']
                        for author in authors:
                            authDict = {}
                            if 'firstName' in author:
                                authDict['firstName'] = author['firstName']
                            if 'lastName' in author:
                                authDict['lastName'] = author['lastName']
                            if 'id' in author:
                                authDict['id'] = author['id']
                            docAuthorList.append(authDict)
                        break
            return  docAuthorList

        except:
            print(f'No author information for {docTitle}')

    def get_refs_by_doc_name(self, docName):
        results = {}
        searchResults = self.search_by_doc_name(docName) #will return a dictionary 
        # print(searchResults)
        if 'records' not in searchResults:
            print(f'No results for {docName}')
            return None


        try:
            authors = searchResults['records'][0]['authors']
            docAuthorList = []
            for author in authors:
                authDict = {}
                if 'firstName' in author:
                    authDict['firstName'] = author['firstName']
                if 'lastName' in author:
                    authDict['lastName'] = author['lastName']
                if 'id' in author:
                    authDict['id'] = author['id']
                docAuthorList.append(authDict)
            results['authors'] = docAuthorList
        except:
            print(f'No author information for {docName}')

        try:
            docId = list(filter(None, searchResults['records'][0]['documentLink'].split('/')))[1]
            refsList = self.get_refs_by_doc_id(docId)
            # print(refsList)
        
            results['docId'] = docId 
            results['references'] = refsList           
        except:
            print(f'Can\'t get reference information for {docName} \n')

        return results
    
    def populate_info_from_doc_page(self):
        url = f'https://ieeexplore.ieee.org/document/{self.id}'

        rsp = requests.get(url)

        metadataMatch = docPattern.search(rsp.text)
        if metadataMatch is not None:
            j = metadataMatch.group(1)
            metadata = json.loads(j)

            self.title = metadata['title']
            self.abstract = metadata.get('abstract')

            pubYear = metadata.get('publicationYear')

            if pubYear is None:
                pubYear = metadata.get('copyrightYear')
            
            if pubYear is not None:
                try:
                    self.publishYear = int(pubYear)
                except ValueError:
                    pass
            
            self.publishDateStr = metadata.get('chronOrPublicationDate')
            
            if self.publishDateStr is None:
                self.publishDateStr = metadata.get('publicationDate')
            
            self.publicationTitle = metadata.get('publicationTitle')
            
            for author in metadata.get('authors', []):
                a = {
                    'name': author.get('name'),
                    'firstName': author.get('firstName'),
                    'lastName': author.get('lastName')
                }
                self.authors.append(a)
            
            for kwdGroup in metadata.get('keywords', []):
                if kwdGroup.get('type') == 'IEEE Keywords':
                    for kwd in kwdGroup['kwd']:
                        self.keywords.append(kwd.lower())