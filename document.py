import requests 
import json

class Document:

    def __init__(self, title=None, id=None):
        self.id = id
        self.title = title
        self.authors = None
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
            self.references = self.get_refs_by_doc_id(id)
            self.title = self.get_doc_title_by_id(id)
            self.citations = self.get_citations_by_id(id)
            # TO DO: add self.authors

        elif title != None:
            self.title = title

            results = self.get_refs_by_doc_name(title)

            if 'docId' in results:
                self.id = results['docId']
                self.citations = self.get_citations_by_id(self.id)
            
            if 'references' in results:
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

        refsList = docRefsDict['references']
        refDocIds = []
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
        headers = {
            'Referer': 'https://ieeexplore.ieee.org/document/'+docId+'/citations',
            }

        response = requests.get('https://ieeexplore.ieee.org/rest/document/'+ docId +'/citations', headers=headers)
        respDict = json.loads(response.text)
        citationDict = respDict['paperCitations']['ieee']
        citationList = []
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