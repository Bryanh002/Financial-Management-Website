from server import *  

def test_get_news_returns_list():
    getNewsArticles = newsAPI()         #Create an instance of the newsAPI
    result = getNewsArticles.getNews()  #Get the result from the newsAPI
    assert isinstance(result, list)     #Check if a list is returned

    # Check if the list returned is empty or not 
    if result:
        assert 'title' in result[0]         
        assert 'description' in result[0]
        assert 'url' in result[0]
