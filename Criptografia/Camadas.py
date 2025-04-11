import os # Manipular caminhos de arquivos e diretórios
import sqlite3 # Bancos de dados SQLite
import base64  # Codifica e decodifica dados em Base64
import hashlib  # Gera hashes
import hmac  # Cria HMACs
import secrets  # Gera valores aleatórios seguros

# Importa funções da biblioteca ECIES para ECC
from ecies.utils import generate_key  # Gera chaves ECC
from ecies import encrypt  # Funções para criptografar dados

from Crypto.Cipher import AES, ChaCha20_Poly1305, Salsa20   # Importando três algoritmos de criptografia
from Crypto.Random import get_random_bytes   # Gera bytes aleatórios
from Crypto.Util.Padding import pad   # Adiciona padding em dados para cifradores de bloco

# Caminho do banco
db_path = os.path.join(os.getcwd(), 'database.db')

def ler_usuarios():
    # Conecta ao banco SQLite
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Pegar todos os usuários
    cur.execute("SELECT id, nome, email, senha FROM usuarios")
    dados = cur.fetchall()
    conn.close()
    return dados

# =========== FUNÇÕES DE GERAÇÃO DE CHAVES ===========

def gerar_chave_aes():
    # Gera uma chave AES de 256 bits (32 bytes) aleatória
    return get_random_bytes(32)

def gerar_chave_chacha():
    #Gera uma chave ChaCha20 de 256 bits (32 bytes) aleatória
    return get_random_bytes(32)

def gerar_chave_salsa():
    #Gera uma chave Salsa20 de 256 bits (32 bytes) aleatória
    return get_random_bytes(32)

# =========== Camada 1: HASH COM SAL E HMAC ===========

def aplicar_primeira_camada(texto):
    # Aplica HMAC-SHA256 ao texto com um sal aleatório
    salt = secrets.token_bytes(16)
    chave = secrets.token_bytes(32)
    texto_bytes = texto.encode('utf-8') if isinstance(texto, str) else texto
    
    # Cria um HMAC com a chave secreta
    assinatura = hmac.new(chave, texto_bytes + salt, hashlib.sha256).digest()

    # Resultado
    resultado = salt + chave + assinatura + texto_bytes
    return resultado

# =========== Camada 2: CHACHA20-POLY1305 ===========

def aplicar_segunda_camada(dados):
    chave = gerar_chave_chacha()
    
    cipher = ChaCha20_Poly1305.new(key=chave)
    nonce = cipher.nonce
    
    # Criptografa os dados
    ciphertext, tag = cipher.encrypt_and_digest(dados)
    
    # Resultado
    return nonce + tag + ciphertext + chave

# =========== Camada 3: SALSA20 ===========

def aplicar_terceira_camada(dados):
    #Criptografa dados usando Salsa20
    chave = gerar_chave_salsa()
    
    nonce = get_random_bytes(8)
    cipher = Salsa20.new(key=chave, nonce=nonce)
    
    # Criptografa os dados
    ciphertext = cipher.encrypt(dados)
    
    # Resultado
    return nonce + ciphertext + chave

# =========== Camada 4: AES-256-CBC ===========

def aplicar_quarta_camada(dados):
    #Criptografa usando AES-256-CBC
    chave = gerar_chave_aes()
    
    iv = get_random_bytes(16)
    cipher = AES.new(chave, AES.MODE_CBC, iv)
    
    # Adiciona padding aos dados
    dados_com_padding = pad(dados, AES.block_size)
    
    # Criptografa os dados
    ciphertext = cipher.encrypt(dados_com_padding)
    
    # Resultado
    return iv + ciphertext + chave

# =========== Camada 5: ECC (Elliptic Curve Cryptography) ===========

def aplicar_quinta_camada(dados, public_key_hex):
    #Criptografa usando ECC
    return encrypt(public_key_hex, dados)

# =========== FUNÇÕES DE CRIPTOGRAFIA EM 5 CAMADAS ===========

def criptografar_cinco_camadas(public_key_hex, texto):
    #Aplica 5 camadas de criptografia ao texto
    print(f"\nCriptografando: '{texto}'")
    
    # Camada 1: Hash com sal e HMAC
    print("  Aplicando Camada 1: HMAC-SHA256 com sal...")
    dados = aplicar_primeira_camada(texto)
    print(f"  → Tamanho após Camada 1: {len(dados)} bytes")
    
    # Camada 2: ChaCha20-Poly1305
    print("  Aplicando Camada 2: ChaCha20-Poly1305...")
    dados = aplicar_segunda_camada(dados)
    print(f"  → Tamanho após Camada 2: {len(dados)} bytes")
    
    # Camada 3: Salsa20
    print("  Aplicando Camada 3: Salsa20...")
    dados = aplicar_terceira_camada(dados)
    print(f"  → Tamanho após Camada 3: {len(dados)} bytes")
    
    # Camada 4: AES-256-CBC
    print("  Aplicando Camada 4: AES-256-CBC...")
    dados = aplicar_quarta_camada(dados)
    print(f"  → Tamanho após Camada 4: {len(dados)} bytes")
    
    # Camada 5: ECC
    print("  Aplicando Camada 5: ECC (Criptografia de Curva Elíptica)...")
    dados_finais = aplicar_quinta_camada(dados, public_key_hex)
    print(f"  → Tamanho após Camada 5: {len(dados_finais)} bytes")
    
    # Codifica em base64 para armazenamento/transmissão
    resultado_base64 = base64.b64encode(dados_finais).decode('utf-8')
    print(f"  → Tamanho final (Base64): {len(resultado_base64)} caracteres")
    
    return resultado_base64

def main():
    # Gerar chaves ECC
    chave_privada = generate_key()
    chave_privada_hex = chave_privada.secret.hex()
    chave_publica_hex = chave_privada.public_key.format().hex()

    print("\n🔐 Chave Pública ECC:", chave_publica_hex)
    print("🔑 Chave Privada ECC:", chave_privada_hex)

    usuarios = ler_usuarios()
    print(f"\n📋 Lidos {len(usuarios)} usuários")

    resultados = []

    for id_, nome, email, senha in usuarios:
        print(f"\n👤 Usuário ID {id_}")
        print(f"  Nome: {nome}")
        print(f"  Email: {email}")
        print(f"  Senha: {'*' * len(senha)}")

        try:
            # Criptografar com 5 camadas
            print("\n🔒 Criptografando dados...")
            nome_cript = criptografar_cinco_camadas(chave_publica_hex, nome)
            email_cript = criptografar_cinco_camadas(chave_publica_hex, email)
            senha_cript = criptografar_cinco_camadas(chave_publica_hex, senha)

            # Exibir resultados da criptografia
            print("\n📦 DADOS CRIPTOGRAFADOS:")
            print(f"\n  Nome ({len(nome)} caracteres → {len(nome_cript)} caracteres criptografados):")
            print(f"  {nome_cript[:50]}..." if len(nome_cript) > 50 else f"  {nome_cript}")
            
            print(f"\n  Email ({len(email)} caracteres → {len(email_cript)} caracteres criptografados):")
            print(f"  {email_cript[:50]}..." if len(email_cript) > 50 else f"  {email_cript}")
            
            print(f"\n  Senha ({len(senha)} caracteres → {len(senha_cript)} caracteres criptografados):")
            print(f"  {senha_cript[:50]}..." if len(senha_cript) > 50 else f"  {senha_cript}")
            
            # Armazena os resultados
            resultados.append({
                'id': id_,
                'nome_original': nome,
                'nome_cript': nome_cript,
                'email_original': email,
                'email_cript': email_cript,
                'senha_original': senha,
                'senha_cript': senha_cript
            })
                
        except Exception as e:
            print(f"\n❌ ERRO no processamento do usuário {id_}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ RESUMO DA CRIPTOGRAFIA:")
    print(f"  Total de usuários processados: {len(resultados)}")
    
    # Calcular taxas de expansão médias
    taxa_nome = sum(len(r['nome_cript'])/len(r['nome_original']) for r in resultados)/len(resultados)
    taxa_email = sum(len(r['email_cript'])/len(r['email_original']) for r in resultados)/len(resultados)
    taxa_senha = sum(len(r['senha_cript'])/len(r['senha_original']) for r in resultados)/len(resultados)
    
    print(f"  Taxa média de expansão (Nome): {taxa_nome:.2f}x")
    print(f"  Taxa média de expansão (Email): {taxa_email:.2f}x")
    print(f"  Taxa média de expansão (Senha): {taxa_senha:.2f}x")
    
    print("\n⚠️ IMPORTANTE: A chave privada é necessária para descriptografar os dados.")
    print("  Mantenha sua chave privada ECC em local seguro:")
    print(f"  {chave_privada_hex}")

if __name__ == "__main__":
    main()