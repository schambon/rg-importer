import re, warnings

DEBUG = False

def clean(content):
    content = despan(content)
    if DEBUG: print("\n1. -> %s " % content)
    content = re.sub(r'<p[^>]*>', r'', content)
    if DEBUG: print("\n2. -> %s " % content)
    content = re.sub(r'</p>', r'\n\n', content)
    if DEBUG: print("\n3. -> %s " % content)
    content = re.sub(r'  +', r' ', content) # remove double spaces
    if DEBUG: print("\n4. -> %s " % content)
    content = re.sub(r'\t', '', content) # remove tabs
    if DEBUG: print("\n5. -> %s " % content)
    content = re.sub(r'<blockquote>', r'> ', content)
    if DEBUG: print("\n6. -> %s " % content)
    content = re.sub(r'<[^>]+>', r'', content)
    if DEBUG: print("\n7. -> %s " % content)
    content = re.sub(r'[ \t]*\n', r'\n', content)
    if DEBUG: print("\n8. -> %s " % content)
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
    DEBUG = True

    text = '''<p class="rg_modif-partie"></p><p class="rg_modif-partie">(modifié par arrêté du 20 août 2010, Journal officiel du 28 août 2010)</p><p class="rg_modif-partie">(modifié par arrêté du 2 avril 2009, Journal officiel du 5 avril 2009)</p><p class="rg_modif-partie">(modifié par arrêté du 27 décembre 2007, Journal officiel du 30 décembre 2007)</p><p class="rg_modif-partie">(modifié par arrêté du 11 septembre 2007, Journal officiel du 27 septembre 2007)</p><p class="rg_modif-partie">(modifié par arrêté du 1er septembre 2005, Journal officiel du 8 septembre 2005)</p><p class="rg_modif-partie">(modifié par arrêté du 15 avril 2005, Journal officiel du 22 avril 2005)</p><p class="rg_modif-partie">(modifié par arrêté du 12 novembre 2004, Journal officiel du 24 novembre 2004)</p><p class="rg_modif-partie">(homologué par arrêté du 12 octobre 2004, Journal officiel du 29 octobre 2004)'''

    print("Initial text:\n{}".format(text))
    print("\nFinal text:\n{}".format(clean(text)))
