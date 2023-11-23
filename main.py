from nltk import sent_tokenize, word_tokenize
import seaborn as sns
import PyPDF2

tokenized_pagees = []
with open("ai-act-01.pdf", "rb") as f:
    pdf = PyPDF2.PdfReader(f)
    print(len(pdf.pages))
    print(pdf.metadata)
    print(pdf.pages[0].extract_text())
    print(dir(pdf.pages[0]))

    for page in pdf.pages:
        tokenized_pagees.append(sent_tokenize(page.extract_text()))

    lens = [len(page) for page in tokenized_pagees]
    sns.distplot(lens)
    print(lens)
    print(sum(lens))
    print(len(tokenized_pagees))
    sns.plt.show()