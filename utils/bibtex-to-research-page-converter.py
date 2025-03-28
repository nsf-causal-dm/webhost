import bibtexparser
from pylatexenc.latex2text import LatexNodes2Text
from pathlib import Path

startingRefNum = 0
md = False

researchPage_metaData_template ="""---
title: Research Updates
layout: page
permalink: research.html
---"""

researchPage_entry_template="""
**[C{ref}]** [PDF]({pdf}) \\\\
{author}. \\\\
"{title}". \\\\
*{booktitle}*, {year}.
"""

html_research_entry_template="""
                    <p>
                      <b>[C{ref}]</b>
                      <a href="{pdf}"  target="_blank" rel="noopener">
                        PDF
                      </a>
                      <br>
                      {author}.
                      <br>
                      "{title}".
                      <br>
                      <i>{booktitle}</i>, {year}.
                    </p>     
"""

html_research_year_heading_template="""
                <p>
                  <i><h5>{year}</h5></i>
                </p>
"""

def createAuthorString(authorField):
    rawSplitAuthors = authorField.split(' and ')
    authorsList = []
    for rawSplitAuthor in rawSplitAuthors:
        rawSplitAuthor = rawSplitAuthor.strip()
        authorBirthAndSurNames = rawSplitAuthor.split(',')
        if len(authorBirthAndSurNames) == 1:
            authorsList.append(authorBirthAndSurNames[0])
        elif len(authorBirthAndSurNames) == 2:
            ss = [None]*2
            ss[0] = authorBirthAndSurNames[-1].strip()
            ss[1] = authorBirthAndSurNames[0].strip()
            authorsList.append(" ".join(ss))
        else:
            raise()
    return ", ".join(authorsList)

p = Path()
# bibFile = p/"test.bib"
bibFilesFolder = p.absolute().parent / "bibtex"
if md:
    outfile = p / "research.md"
else:
    outfile = p / "researchEntries.txt"

nonBibFilePaths = []
bibFilePaths = []
for file in bibFilesFolder.glob("*"):
    if file.suffix != ".bib":
        nonBibFilePaths.append(file)
    else:
        bibFilePaths.append(file)

if len(nonBibFilePaths) > 0:
    print("The following are non '.bib' files that were skipped in the bibtex dir:")
    for file in nonBibFilePaths:
        print("\t", file)
    print()

print("Now parsing bib files...")
entries = []
keysToExtract = {"author", "title", "booktitle"}  # "year" will also be extracted
for bibFile in bibFilePaths:
    print("\t", bibFile.name)
    library = bibtexparser.parse_file(bibFile)
    for entry in library.entries:
        entryDict = {}
        year = None
        for field in entry.fields:
            if field.key == "year":
                year = int(field.value)
                entryDict["year"] = str(year)
            else:
                unicode_value = LatexNodes2Text().latex_to_text(field.value).replace("$","")
                if field.key == "journal":
                    entryDict["booktitle"] = unicode_value
                elif field.key == "author":
                    entryDict["author"] = createAuthorString(unicode_value)
                else:
                    entryDict[field.key] = unicode_value
        entries.append((year,entryDict,))

# def compareEntries(e1, e2):
#     if e2[0] - e1[0] != 0:
#         return e2[0] - e1[0]
#     else:
#         return e2[1]["author"] 
entries.sort(key=lambda x: (x[0], x[1]["author"]), reverse=True)

with outfile.open('w') as fout:
    if md:
        print(researchPage_metaData_template, file=fout)
        print(file=fout)
        n = len(entries) + startingRefNum
        for year,entry in entries:
            print(\
                researchPage_entry_template.format(\
                    ref=str(n).zfill(3), \
                    pdf="papers/"+"C"+str(n).zfill(3)+".pdf", \
                    author=entry["author"], \
                    title=entry["title"], \
                    booktitle=entry["booktitle"], \
                    year=entry["year"]\
                ), \
            file=fout)
            n = n-1
    else:
        n = len(entries) + startingRefNum
        curYear = None
        for year,entry in entries:
            if year != curYear:
                curYear = year
                print(html_research_year_heading_template.format(year=entry["year"]), file=fout)
            print(\
                html_research_entry_template.format(\
                    ref=str(n).zfill(3), \
                    pdf="papers/"+"C"+str(n).zfill(3)+".pdf", \
                    author=entry["author"], \
                    title=entry["title"], \
                    booktitle=entry["booktitle"], \
                    year=entry["year"]\
                ), \
            file=fout)
            n = n-1

# with outfile.open('w') as fout:
#     for bibFile in bibFilePaths:
#         print("\t", bibFile.name)
#         library = bibtexparser.parse_file(bibFile)
#         # library = bibtexparser.load(bibtex_file, parser=parser)
#         for entry in library.entries:
#             for field in entry.fields:
#                 unicode_field = LatexNodes2Text().latex_to_text(field.value)
#                 print(unicode_field, file=fout)
#             print(file=fout)
#             print(file=fout)