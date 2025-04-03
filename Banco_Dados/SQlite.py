import sqlite3 # Bancos de dados SQLite
import re  # Expressões regulares

# Cria um banco de dados e a tabela usuarios
def criar_banco():
    database_path = "database.db"
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        senha TEXT NOT NULL
                    )''')
    
    connection.commit() # Salvar as alterações no banco de dados
    connection.close()

# Verificar se o email está em um formato válido
def validar_email(email):
    padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'  # Expressão regular para email
    return re.match(padrao, email)

# Insere o usuário no banco de dados, desde que o email não esteja repetido
def inserir_usuario(nome, email, senha): 
    if not validar_email(email):   # Verifica se o email é válido antes de inserir
        print("Erro: Email inválido. Tente novamente.")
        return
    
    database_path = "database.db"
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        connection.commit()
        print("Usuário cadastrado com sucesso!")
    except sqlite3.IntegrityError: # Captura erro caso o email já esteja cadastrado
        print("Erro: Este email já está cadastrado.")
    
    connection.close()

# Função principal que executa o programa
def main():
    criar_banco()  # Garante que o banco de dados e a tabela existam antes de cadastrar usuários
    while True:
        nome = input("Digite seu nome: ")
        email = input("Digite seu email: ")
        senha = input("Digite sua senha: ")
        inserir_usuario(nome, email, senha) # Tenta inserir o usuário no banco

        continuar = input("Deseja cadastrar outro usuário? (s/n): ")
        if continuar.lower() != 's':
            break

# Executa o programa se este arquivo for rodado diretamente
if __name__ == "__main__":
    main()
