import requests
from eu_parse import parse
from import_rg import do_import

def import_eu(celex, lang, output):
    '''
    Download and import a European text from eur-lex.europa.eu into git
    If the git repo already exists, the document will be added as a version
    Otherwise a new git repo will be created
    Arguments:
        celex: the CELEX argument in the URL (eg 32014R0600 for MIFIR)
        lang: the 2-letter iso 639 code for the text language, e.g. en, fr, it, ga
        output: where to create the git repository if it doesn't already exist
    '''
    url = "http://eur-lex.europa.eu/legal-content/%s/TXT/HTML/?uri=CELEX:%s" % (lang, celex)
    print("Fetching %s" % url)
    r = requests.get(url)
    if r.status_code != 200:
        print("--- Impossible to download: %d %s" % (r.status_code, r.reason))
        return

    date, items, main_doc = parse(r.text)
    print("At date %s, found %d items" % (str(date), len(items)))
    for i, item in enumerate(items):
        print("%03d: (%s) %s\t(%s)" % (i, str(item["leaf"]), item["path"], item["titre"]))

    do_import([(date, items, main_doc)], output, True, author="EU <eu@europa.eu>")

if __name__=="__main__":
    import_eu("32014R0600", "fr", "../mifir-fr")
    import_eu("32014R0600", "en", "../mifir-en")
    import_eu("32014L0065", "fr", "../mifid-fr")
    import_eu("32014L0065", "en", "../mifid-en")
