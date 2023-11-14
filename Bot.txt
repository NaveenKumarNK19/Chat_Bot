import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import numpy as np
import random
import nltk
import pickle
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()

intents = json.loads(open("D:\MY_PROJ\intents.json").read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotmodel.h5')

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot App")
        self.root.configure(bg='black')

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(fill='both', expand=True)

        self.chat_text = scrolledtext.ScrolledText(self.chat_frame, state='disabled', wrap=tk.WORD, bg='black',
                                                   fg='white')
        self.chat_text.pack(fill='both', expand=True)

        self.entry = tk.Entry(self.root)
        self.entry.pack(fill='x', padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)

        self.chat_history = []

    def send_message(self, event=None):
        user_message = self.entry.get()

        if user_message.lower() == "terminate":
            self.root.destroy()

        self.chat_history.append(("USER", user_message))

        intents_list = predict_class(user_message)
        response = get_response(intents_list, intents)
        self.chat_history.append(("BOT", response))

        self.update_chat_history()
        self.entry.delete(0, 'end')

    def update_chat_history(self):
        self.chat_text.config(state='normal')
        self.chat_text.delete('1.0', tk.END)
        for sender, message in self.chat_history:
            if sender == "USER":
                self.chat_text.insert('end', f"You:\n"
                                             f"{message}\n", 'user')
            else:
                self.chat_text.insert('end', f"Bot:\n"
                                             f"{message}\n", 'bot')
        self.chat_text.config(state='disabled')


def clean_up_sentence(sentence):
    sentence = sentence.lower()
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    result = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    result.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in result:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tags'] == tag:
            result = random.choice(i['responses'])
            break
    return result


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.configure(bg='black')

        self.username = None
        self.password = None

        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=50)

        self.username_label = tk.Label(self.login_frame, text="Username:", fg='white', bg='black')
        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = tk.Label(self.login_frame, text="Password:", fg='white', bg='black')
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.perform_login)
        self.login_button.grid(row=2, columnspan=2, padx=10, pady=10)

    def perform_login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        if self.username == "user" and self.password == "123":
            self.root.destroy()
            chat_root = tk.Tk()
            app = ChatbotApp(chat_root)
            app.chat_text.tag_configure('user', justify='right')
            app.chat_text.tag_configure('bot')
            chat_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginApp(root)
    root.mainloop()

