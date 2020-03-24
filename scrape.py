import requests 
import json

def get_refs_by_direct_link(docLink):
    '''
    !!!!better to use get_refs_by_doc_id()

    Given the direct ieee link to a document as a string,
        makes an http GET request to IEEE
        recieves a json of the document's references

        write now rights json to a file, but will likely change
        
        Link must have the document id as the last parameter in the link 
        #ex: doc_link = 'https://ieeexplore.ieee.org/document/8862080'
            8862080 is the document id
    '''
    linkParts = docLink.split('/')
    
    RefsLink = docLink + '/references'
    GetLink = 'https://ieeexplore.ieee.org/rest/document/' + linkParts[-1] + '/references'
    Headers={'Referer':RefsLink + '#references'}
    refReq = requests.get(GetLink, headers=Headers)
    return json.loads(refReq.text)
 
def get_refs_by_doc_id(docId):
    '''
    Given a document id returns a dictionary of that document's references
    '''

    RefsLink = 'https://ieeexplore.ieee.org/document/' + docId + '/references'
    GetLink = 'https://ieeexplore.ieee.org/rest/document/' + docId + '/references'
    Headers={'Referer':RefsLink + '#references'}
    refReq = requests.get(GetLink, headers=Headers)
    return json.loads(refReq.text)

def search_by_doc_name(docName):
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

def get_refs_by_doc_name(docName):
    searchResults = search_by_doc_name(docName) #will return a dictionary 
    # print(searchResults)

    authors = searchResults['records'][0]['authors']
    docAuthorList = []
    for author in authors:
        authorList.append({'firstName':author['firstName'], 
            'lastName':author['lastName'], 
            'searchablePreferredName': author['searchablePreferredName'],
            'id':author['id']})

    docId = list(filter(None, searchResults['records'][0]['documentLink'].split('/')))[1]
    docRefsDict = get_refs_by_doc_id(docId)
    refsList = docRefsDict['references']

    refDocIds = []
    for ref in refsList:
        if 'links' in ref:
            linksDict = ref['links']
            if 'documentLink' in linksDict:
                print(linksDict['documentLink'])
                refId = list(filter(None, linksDict['documentLink'].split('/')))[1]
                refDocIds.append(refId)
    
    # print(searchResults['records'][0]['documentLink'])
    # print(docId, type(docId))




# print(get_refs_by_direct_link('https://ieeexplore.ieee.org/document/4810674'))
# print(search_by_doc_name('Statistical Machine Learning in Natural Language Understanding: Object Constraint Language Translator for Business Process'))
# print(search_by_doc_id('4810674'))
get_refs_by_doc_name('Advanced Robotics Mechatronics System: emerging technologies for interplanetary robotics')