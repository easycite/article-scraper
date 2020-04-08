import requests 
# import json
# import logging

def direct_link_scrape(doc_link):
    # doc = 'https://ieeexplore.ieee.org/document/8862080'
    docRefs = doc_link + '/references'
    headers={'Referer':docRefs + '#references'}
    r = requests.get(docRefs, headers=headers)
    f = open('test.json','w')
    #look into r.json()
    f.write(r.text)
    f.close()

def search_by_doc_name(doc_name='test'):

    # logging.basicConfig(level=logging.DEBUG)
    headers ={
    'Host': 'ieeexplore.ieee.org',
    # 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
    # 'Accept': 'application/json, text/plain, */*',
    # 'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Origin': 'https://ieeexplore.ieee.org',
    # 'Connection': 'keep-alive',
    'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=Statistical%20Machine%20Learning%20in%20Natural%20Language%20Understanding:%20Object%20Constraint%20Language%20Translator%20for%20Business%20Process',
    # 'Cookie': 'utag_main=v_id:0170170e0d3b0018929470b2a4790004c002e00900bd0$_sn:7$_ss:0$_st:1583210798045$vapi_domain:ieee.org$ses_id:1583207935322%3Bexp-session$_pn:11%3Bexp-session; fp=d3d38efc375052499988d5b9344bfc76; AMCV_8E929CC25A1FB2B30A495C97%40AdobeOrg=1687686476%7CMCIDTS%7C18298%7CMCMID%7C33952294964878049284616340716101851568%7CMCAID%7CNONE%7CMCAAMLH-1583812736%7C7%7CMCAAMB-1583812736%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-18330%7CvVersion%7C3.0.0%7CMCOPTOUT-1583215136s%7CNONE; __gads=ID=0603ea239d409332:T=1580934764:S=ALNI_MZU_HUoDqb2XOqpqLRMGXDsmLNkCQ; s_ecid=MCMID%7C33950315543300341764617464384795579374; _ga=GA1.2.1749927524.1582211079; cookieconsent_status=dismiss; WLSESSION=237134476.20480.0000; JSESSIONID=cNOejPhyKr-IiDxcjyXRZqmZLoXON-6RQ0CvdgGkLZ-HpVV9slEf!-45784366; ipCheck=47.218.213.141; TS01dcb973=012f35062361ec7ef5e0955a1addc7e5431c46d455e3b236ab1be135fcdfe715943c72e5912d4dd5a5ec6de1ce8a607cff7e2484818c32817ba38881c70857b6185f769155cd9069fb46fae3db91eaf25b0fe81f20; TS01109a32=012f3506233f949ba5ecedbc6e292f18a24f9ff1bfa4cec9adc295f37743cf6392dd0abb47c1527f68a1f52598a8e2cddeeee158942059a5e60cb5092d68869263a3508edeec8195e4756d795e5cfad265f0b4a9fc2174b62875004954a77f57be0ed14fea02ebea0b793bf9e975fcabc87874d816; TS01dcb973_26=014082121d69aab79cac5b7fc0d2733314b7bc097c039c8fd0889a055cfe0d87f57f20518e9cc955b1e34a43710260d369e855e7bc4d4129c98c9d76944c555d2c87ea2050; AMCVS_8E929CC25A1FB2B30A495C97%40AdobeOrg=1; s_cc=true; s_sq=%5B%5BB%5D%5D'
    }


    payload = {"newsearch":True,
                "queryText":"Statistical Machine Learning in Natural Language Understanding: Object Constraint Language Translator for Business Process",
                "highlight":True,
                "returnFacets":["ALL"],
                "returnType":"SEARCH"}


    r = requests.post('https://ieeexplore.ieee.org/rest/search', headers=headers,params=payload)
    # requests.packages.urllib3.add_stderr_logger()
    print(f'text: {r.text}, content: {r.content}, raw:{r.raw}, status:{r.status_code}, json: {r.json}')

def sessions_test():
    s = requests.session()
    g = s.get('https://ieeexplore.ieee.org/Xplore/home.jsp')
    print(f'g status: {g.status_code}')
    headers ={
    'Host': 'ieeexplore.ieee.org',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Origin': 'https://ieeexplore.ieee.org',
    'Connection': 'keep-alive',
    'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=Statistical%20Machine%20Learning%20in%20Natural%20Language%20Understanding:%20Object%20Constraint%20Language%20Translator%20for%20Business%20Process',
    'Cookie': 'utag_main=v_id:0170170e0d3b0018929470b2a4790004c002e00900bd0$_sn:7$_ss:0$_st:1583210798045$vapi_domain:ieee.org$ses_id:1583207935322%3Bexp-session$_pn:11%3Bexp-session; fp=d3d38efc375052499988d5b9344bfc76; AMCV_8E929CC25A1FB2B30A495C97%40AdobeOrg=1687686476%7CMCIDTS%7C18298%7CMCMID%7C33952294964878049284616340716101851568%7CMCAID%7CNONE%7CMCAAMLH-1583812736%7C7%7CMCAAMB-1583812736%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-18330%7CvVersion%7C3.0.0%7CMCOPTOUT-1583215136s%7CNONE; __gads=ID=0603ea239d409332:T=1580934764:S=ALNI_MZU_HUoDqb2XOqpqLRMGXDsmLNkCQ; s_ecid=MCMID%7C33950315543300341764617464384795579374; _ga=GA1.2.1749927524.1582211079; cookieconsent_status=dismiss; WLSESSION=237134476.20480.0000; JSESSIONID=cNOejPhyKr-IiDxcjyXRZqmZLoXON-6RQ0CvdgGkLZ-HpVV9slEf!-45784366; ipCheck=47.218.213.141; TS01dcb973=012f35062361ec7ef5e0955a1addc7e5431c46d455e3b236ab1be135fcdfe715943c72e5912d4dd5a5ec6de1ce8a607cff7e2484818c32817ba38881c70857b6185f769155cd9069fb46fae3db91eaf25b0fe81f20; TS01109a32=012f3506233f949ba5ecedbc6e292f18a24f9ff1bfa4cec9adc295f37743cf6392dd0abb47c1527f68a1f52598a8e2cddeeee158942059a5e60cb5092d68869263a3508edeec8195e4756d795e5cfad265f0b4a9fc2174b62875004954a77f57be0ed14fea02ebea0b793bf9e975fcabc87874d816; TS01dcb973_26=014082121d69aab79cac5b7fc0d2733314b7bc097c039c8fd0889a055cfe0d87f57f20518e9cc955b1e34a43710260d369e855e7bc4d4129c98c9d76944c555d2c87ea2050; AMCVS_8E929CC25A1FB2B30A495C97%40AdobeOrg=1; s_cc=true; s_sq=%5B%5BB%5D%5D'
    }


    payload = {"newsearch":True,
                "queryText":"Statistical Machine Learning in Natural Language Understanding: Object Constraint Language Translator for Business Process",
                "highlight":True,
                "returnFacets":["ALL"],
                "returnType":"SEARCH"
                }


    r = s.post('https://ieeexplore.ieee.org/rest/search', headers=headers, data=payload)
    
    
    print(f'text: {r.text}, content: {r.content}, raw:{r.raw}, status:{r.status_code}, json: {r.json}')

sessions_test()
# search_by_doc_name()