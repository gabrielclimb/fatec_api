import os
from flask import Flask, jsonify, request
import requests as r
import pandas as pd


class Scraping:

    s = r.Session()
    notas = ''
    URL = "http://san.fatecsp.br/index.php"
    URL_HIST = "http://san.fatecsp.br/index.php?task=historico_disciplinar"

    def __init__(self, user, password):
        self.user = user
        self.password = password

        self.login()
        self.get_pagina_notas()

    def login(self):

        payload = {
            "userid": self.user,
            "password": self.password,
            "submit": "Enviar"
        }

        resp = self.s.post(self.URL, data=payload)

    def get_pagina_notas(self):
        resp = self.s.get(self.URL_HIST)
        self.notas = self.to_dataframe(resp)

    def to_dataframe(self, html):
        lista = pd.read_html(html.content)
        df = lista[0]
        return df

    def __limpa_notas(self):
        self.notas.columns = self.notas.iloc[0, :]
        self.notas = self.notas.drop([0])
        self.notas[u'Média'] = self.notas[u'Média'].apply(float)

    def media_ponderada(self):
        self.__limpa_notas()
        df = self.notas[~self.notas[u'Média'].isnull()]
        # return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"
        return (df[u'Média'].mean())
    
    def get_df(self):
        df = self.notas[~self.notas[u'Média'].isnull()]
        df = df.drop(['Conceito'], axis=1)
        return df.to_html()


app = Flask(__name__)


@app.route('/fatecapi/', methods=['GET'])
def home():

    parametros = request.args.to_dict()
    login = parametros['login']
    senha = parametros['senha']
    nota = Scraping(login, senha)
    # <h1>Login {login} - Senha {senha}</h1>
    return f"<h1>Média Ponderada -> {nota.media_ponderada()}</h1>"\
        f"<p>{nota.get_df()}</p>"


if __name__ == "__main__":
    app.run(debug=True)
    # nota = Scraping("16100722", "fatimabs")
