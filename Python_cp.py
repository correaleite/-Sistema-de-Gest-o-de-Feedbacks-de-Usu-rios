import json
import os

def menu():
    opcao = 0
    while opcao != 4:
        print("FeedSmart\n---------\nFeedbacks de Usuários\n1 - Cadastrar usuário\n2 - Dar feedback\n3 - Ver feedbacks\n4 - Sair")
        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            print("Apenas números são válidos")
        else:
            match opcao:
                case 1: 
                    add_usuário()
                case 2: 
                    feedback()
                case 3: 
                    ver_feedback()
                case 4: 
                    print("Obrigado por usar nossos serviços!")
                case _: 
                    print('')
             
def add_usuário():
    """
    Essa função serve para armazenar os usuarios que se registram no sistema

    Parâmetros: (tuple,string,int,string,string)
    Retorna:   (txt, json)
    """
    try:
        nome = input("Digite o nome do usuário: ")
        idade = int(input('Digite sua idade: '))
        prof = input("Digite sua profissão: ")
        tipo = input("Digite o tipo de conta:")
    except ValueError:
        print("Digite uma idade válida")
    else:
        with open("Armazenamento_Usuarios.txt","a") as ids:
            ids
        with open("Armazenamento_Usuarios.txt","a") as ArquivoTxt:          
             ArquivoTxt.write(f"{id},{nome},{idade},{prof},{tipo}\n")             
        id += 1
        with open("Armazenamento_Usuarios.txt","r") as Arquivo:
            Ujson = {}
            for i in Arquivo:
                dados = i.split(",")
                id = dados[0]
                nome = dados[1]
                idade = dados[2]
                prof = dados[3]
                tipo = dados[4].replace("\n","")
                Ujson[id]={"nome":nome,"idade":idade,"prof":prof,"tipo":tipo}
            dadosJson = json.dumps(Ujson, indent=4, ensure_ascii=False)
        with open("Armazenamento_Usuarios.json", 'w', encoding='utf-8') as arquivoJson:
            arquivoJson.write(dadosJson)

        print("Dados do Usuario foram cadastrados")
            
def feedback():
            notas = []
            try:
                id_user = int(input('Digite o id do usuário: '))
                with open("Armazenamento_Usuarios.json","r",encoding='utf-8') as arquivo:
                    conve = json.load(arquivo)
                    if '1' in id_user(): # Apenas o id 1
                        texto = input("Digite a sua análise: ")
                        nota = int(input('Digite sua nota(0/10): '))
                    if nota < 0 and nota > 10:
                        print('Digite nota de 0 a 10 apenas.')
                    feedback = {}
                    feedback = {'id_user': id_user, 'texto': texto, 'nota': nota}
                    with open("Armazenamento_Feedback.txt",'a', encoding='utf-8') as feedbackTxt:
                        feedJson = json.dumps(feedback, indent=4, ensure_ascii=False)
                        feedbackTxt.write(feedJson)
                    with open('Armazenamento_Feedback.json','a',encoding='utf-8') as feedbackJson:  
                        feedJson = json.dumps(feedback, indent=4, ensure_ascii=False)
                        feedbackTxt.write(feedJson)
                    print('Feedback adicionado')
            except TypeError: 
                print("Digite valores válidos")
            else:
                print('Não usuário cadastrados')

def ver_feedback():
    try: 
        if os.path.exists('Armazenamento_Feedback.json'):
                with open('Armazenamento_Feedback.json', 'r', encoding='utf-8') as arquivo: 
                       for linha in arquivo:
                           print(linha)                            
    except FileExistsError:
        print('ERRO: Não foi possível abrir o arquivo.')
                

menu()