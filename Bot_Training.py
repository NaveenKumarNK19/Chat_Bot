import json
import pickle
import random
import string
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Uncomment the following line if you haven't downloaded 'wordnet' resource before
nltk.download('wordnet')
Lemmatizer = WordNetLemmatizer()
intents = json.loads(open("D:\MY_PROJ\intents.json").read())

words = []
classes = []
documents = []
ignore_letters = [string.punctuation]

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tags']))
        if intent['tags'] not in classes:
            classes.append(intent['tags'])
#print(documents)
#print(len(documents))
words = [Lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    words_patterns = document[0]
    words_patterns = [Lemmatizer.lemmatize(word.lower()) for word in words_patterns]
    for word in words:
        bag.append(1) if word in words_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
train_x = np.array([bag for bag, _ in training])
train_y = np.array([output_row for _, output_row in training])

train_x = pad_sequences(train_x, padding='post')

model = Sequential()
model.add(Dense(128, input_shape=(train_x.shape[1],), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(classes), activation='softmax'))

sgd = SGD(learning_rate=0.001, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

model.fit(train_x, train_y, epochs=1000, batch_size=5, verbose=1)
model.save('chatbotmodel.h5')
print("Done")
