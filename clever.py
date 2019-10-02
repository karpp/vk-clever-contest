from random import randint
import wikipedia
import pandas as pd
import numpy as np
import re
from gensim.models import Word2Vec
from gensim.matutils import unitvec
from vkml.toolkit import tokenize


def get_word_vector(sentence_tokens):
    vectors_available = [word for word in sentence_tokens if word in word_model.vocab]
    result = np.zeros((word_model.vector_size))
    if len(vectors_available) > 0:
        result = np.mean([word_model[word] for word in vectors_available], axis=0)
    return result


MODEL_FILENAME = "/d3/models/w2v.model"
word_model = Word2Vec.load(MODEL_FILENAME)

# with open('output.csv', 'a') as f, open('fail.txt', 'a') as fail:
df = pd.read_csv('clever_qa_validation.csv', encoding="utf-8")
# f.write('question_id,correct_answer\n')

wikipedia.set_lang('ru')

city = re.compile('(?:\s[a-zA-Zа-яА-Я]+)?\s[A-ZА-Я][\-a-zа-яA-ZА-Я]+')
year = re.compile('\d\d\d\d')
quotes = re.compile('\s[\'\"].*[\'\"]')
family = re.compile('[А-Я]\.[А-Я]\.[А-Я][а-я]')

for i, testrow in df.iterrows():
    if i < 6500:
        continue
    f = open('output.csv', 'a')
    fail = open('fail.txt', 'a')
    t_id = testrow['question_id']
    q = testrow['question']
    ans0 = testrow['answer_0']
    ans1 = testrow['answer_1']
    ans2 = testrow['answer_2']
    keywords = re.findall(city, q) + re.findall(year, q) + re.findall(quotes, q)
    print(q, keywords)
    query = ''.join(keywords)
    c0, c1, c2 = 0, 0, 0
    if query != '':
        try:
            search_results = wikipedia.search(query)
        except:
            search_results = []

        j = 0
        for page in search_results:
            j += 1

            print(j)
            try:
                p = wikipedia.page(page)
            except:
                break

            page_vector = get_word_vector(tokenize(str(p.content)))
            c0 = np.dot(unitvec(page_vector), unitvec(get_word_vector(tokenize(ans[0]))))
            c1 = np.dot(unitvec(page_vector), unitvec(get_word_vector(tokenize(ans[1]))))
            c2 = np.dot(unitvec(page_vector), unitvec(get_word_vector(tokenize(ans[2]))))
            if j > 0:
                break
        # print(ans0, c0, ans1, c1, ans2, c2, testrow['correct_answer'])
    q = q.lower()
    if ' не ' in q or ' нет ' in q:
        m = min(c0, c1, c2)
    else:
        m = max(c0, c1, c2)
    if m == 0:
        res = randint(0, 2)
        fail.write(str(i) + '\n')
    else:
        if m == c0:
            res = 0
        elif m == c1:
            res = 1
        else:
            res = 2
    print(res)
    f.write('{},{}\n'.format(t_id, res))
    f.close()
    fail.close()
