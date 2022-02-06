import json
import urllib.request


# download "confusables" from unicode and parse into a much friendlier dict

def cstus(codepoint_string: str) -> str:
    # codepoint string to unicode string
    codepoint_string = codepoint_string.strip()
    unicode_string = u""
    for codepoint in codepoint_string.split(" "):
        unicode_string += chr(int(codepoint, 16))
    return unicode_string


rps = {}
for line in urllib.request.urlopen("https://www.unicode.org/Public/security/latest/confusables.txt"):
    line = line.decode("utf-8").split(";")
    if len(line) != 3:
        continue
    rps[cstus(line[0])] = cstus(line[1])


def utf8len(s):
    return len(s.encode('utf-8'))


rps = {k: rps[k] for k in sorted(rps, key=utf8len, reverse=True)}
print(rps)
with open("confusables.json", "w+") as f:
    json.dump(rps, f)
