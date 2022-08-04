from os.path import join
from gensim.models import FastText
from utils.tsne_plot import tsne_plot
import re
import nltk
from config import trained_model_path, results_root_path

STOP_WORDS = nltk.corpus.stopwords.words('english')


def clean_sentence(val):
    "remove chars that are not letters or numbers, downcase, then remove stop words"
    val = val.replace('.', ' ')
    regex = re.compile('([^\s\w]|_)+')
    sentence = regex.sub('', val).lower()
    sentence = sentence.split(" ")

    for word in list(sentence):
        if word in STOP_WORDS:
            sentence.remove(word)

    sentence = " ".join(sentence)
    return sentence


def build_corpus(lines):
    """
    returns list of lists as a corpus
    :param lines: raw lines from training data
    :return:
    """
    corpus = []
    [corpus.append(nltk.word_tokenize(clean_sentence(line))) for line in lines]

    return corpus


if __name__ == '__main__':
    train_path = join(results_root_path, 'train.txt')

    with open(train_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    corpus = build_corpus(lines)
    print(len(corpus))

    # pre-train model on the train corpus
    model = FastText(vector_size=300, window=5, min_count=3, workers=4, sg=1)
    model.build_vocab(corpus_iterable=corpus)
    model.train(corpus_iterable=corpus, total_examples=len(corpus), epochs=10)  # train

    w1 = 'license'
    w2 = 'contactPerson.surName'
    w3 = 'givenName'
    w4 = 'Author.givenName'
    w5 = 'Creator'
    w6 = 'x-axis'
    w7 = 'x-axis'
    words = [w1, w2, w3, w4, w5, w6, w7]
    vecs = [model.wv[w] for w in words]
    tsne_plot(model, words)

    model.save(join(trained_model_path, 'trained_fasttext.bin'))
