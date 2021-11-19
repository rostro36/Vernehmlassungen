from requests_html import HTMLSession


def get_page(url):
    # create the session
    with HTMLSession() as session:
        r = session.get(url)
        print('found URL')
        # Render the page, up the number on scrolldown to page down multiple times on a page
        r.html.render(sleep=1, keep_page=True, scrolldown=1, timeout=30)
        print('rendered')
        # take the rendered html and find the element that we are interested in
        html = r.html.find('body')[0].html
        session.close()
    return str(html)
