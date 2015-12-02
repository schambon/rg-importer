import re, warnings

def clean(content):
    content = despan(content)
    content = re.sub(r'<p[^>]*>', r'', content)
    content = re.sub(r'</p>', r'\n\n', content)
    content = re.sub(r'  +', r' ', content) # remove double spaces
    content = re.sub(r'\t', '', content) # remove tabs
    content = re.sub(r'<blockquote>', r'> ', content)
    content = re.sub(r'<[^>]+>', r'', content)
    return content

def despan(text):
    spans = [m.start() for m in re.finditer(r'<span class="rg_texte-modificateur"', text)]

    if len(spans) == 0:
        return text

    remove = []

    for span in spans:
        ct = None
        for i in range(span + 1, len(text)):
            if text[i] == "«":
                if ct != None:
                    ct = ct + 1
                else:
                    ct = 1
                    remove.append(i)
            elif text[i] == "»":
                if ct != None:
                    ct = ct - 1
                if ct == 0:
                    remove.append(i)
                    break

    remove.sort()
    idx = 0
    result = ""
    for pos in remove:
        result = result + text[idx:pos]
        idx = pos + 1
    result = result + text[idx:]

    return re.sub(r'<span class="rg_texte-modificateur"[^/]*</span>', r'', result)

if __name__ == "__main__":
    text = '''L'AMF, consultée par écrit préalablement à la réalisation d'une opération et sur une question relative à l'interprétation <span class="rg_texte-modificateur">(Arrêté du 15 avril 2005)</span> « du présent règlement (ci-après désigné « le RG ») », rend un avis sous forme de rescrit. Cet avis précise si, au regard des éléments communiqués par l'intéressé, l'opération n'est pas contraire au présent règlement. L'AMF, consultée par écrit préalablement à la réalisation d'une opération et sur une question relative à l'interprétation <span class="rg_texte-modificateur">(Arrêté du 15 avril 2005)</span> « du <span class="rg_texte-modificateur">(pouet)</span> « présent » règlement », rend un avis sous forme de rescrit. Cet avis précise si, au regard des éléments communiqués par l'intéressé, l'opération n'est pas contraire au présent règlement.'''

    print("Initial text:\n{}".format(text))
    print("\nFinal text:\n{}".format(clean(text)))
