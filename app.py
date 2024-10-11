from flask import Flask, render_template, session, request, redirect, url_for
import requests
import random

#Cria uma instância da aplicação Flask
app = Flask(__name__)

#Define uma chave secreta para aplicação
app.secret_key = 'test-environment'

#Define uma variável API que armazena o URL da API do "dicionário aberto".
#O endpoint "/random" da API retorna uma palavra aleatória.
API_URL = 'https://api.dicionario-aberto.net/random'

#Função para obter uma palavra aleatória da API
def get_palavra_aleatoria():
    response = requests.get(API_URL) #Faz uma requisição GET para a API
    if response.status_code == 200: #Código 200 indica que a requisição foi bem sucedida
        return response.json()['word'].upper() #Retorna a palavra contida na chave 'word' em letras maiúsculas
    return None


#Rota principal
@app.route('/')
def index():
    #Se a palavra não estiver na sessão, obtém uma nova palavra aleatória
    if 'palavra' not in session:
        session['palavra'] = get_palavra_aleatoria()
        session['tentativas'] = []
        session['erros'] = 0
        session['mensagem'] = ''
        session['dica_usada'] = False

    #Cria uma string com as letras da palavra que foram tentadas
    palavra_display = ''.join([letra if letra in session['tentativas'] else '_' for letra in session['palavra']])

    #Renderiza o template index.html com a palavra a ser exibida, o número de tentativas e erros, e uma mensagem
    return render_template('index.html', palavra_display=palavra_display, tentativas=session['tentativas'], erros=session['erros'],
                           mensagem=session.get('mensagem', ''))

#Rota para reiniciar o jogo
@app.route('/reiniciar')
def reiniciar():
    session.pop('palavra', None)
    session.pop('tentativas', None)
    session.pop('erros', None)
    session.pop('mensagem', None)
    return redirect(url_for('index'))

#Rota para tentar uma letra
@app.route('/tentativa', methods=['POST'])
def tentativa():
    #Obtém a letra tentada do formulário e a converte para maiúsculas
    tentativa = request.form['tentativa'].upper()

    if tentativa not in session['tentativas']:
        session['tentativas'].append(tentativa)
        
        #Verifica se a letra tentada está na palavra
        if tentativa in session['palavra']:
            session['mensagem'] = f"Bom chute! '{tentativa}' está na palavra."
        else:
            session['erros'] += 1
            session['mensagem'] = f"Que pena! '{tentativa}' não está na palavra."
    else:
        session['mensagem'] = f"Você já chutou '{tentativa}'."
    return redirect(url_for('index'))

#Rota para obter uma dica(revelar uma letra)
@app.route('/dica')
def dica():

    if session.get('dica_usada', False):
        session['mensagem'] = "Você já usou a dica."
        return redirect(url_for('index'))

    #Verifica se há letras que ainda não foram reveladas
    letras_nao_tentadas = [letra for letra in session['palavra'] if letra not in session['tentativas']]

    if letras_nao_tentadas:
        #Seleciona uma letra que ainda não foi tentada
        letra_dica = letras_nao_tentadas[random.randint(0, len(letras_nao_tentadas) - 1)]
        session['tentativas'].append(letra_dica)

        session['dica_usada'] = True
        session['erros'] += 1
        session['mensagem'] = f"Dica: '{letra_dica}' foi utilizada, mas você perdeu uma dica."
    else:
        session['mensagem'] = "Não há mais dicas disponíveis."
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)