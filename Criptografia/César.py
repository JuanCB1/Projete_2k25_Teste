def cifra_cesar(texto, deslocamento):
    resultado = ""
    for char in texto:
        if char.isalpha():  # Verifica se o caractere é uma letra
            deslocamento_base = 65 if char.isupper() else 97  # Definindo a base para maiúsculas ou minúsculas
            # Aplica o deslocamento mantendo a letra dentro do alfabeto
            novo_char = chr((ord(char) - deslocamento_base + deslocamento) % 26 + deslocamento_base)
            resultado += novo_char
        else:
            resultado += char  # Mantém os caracteres não alfabéticos inalterados
    return resultado

# Exemplo de uso
texto_original = "Mensagem Secreta!"
deslocamento = 3  # Número de posições para o deslocamento

texto_cifrado = cifra_cesar(texto_original, deslocamento)
print(f"Texto Original: {texto_original}")
print(f"Texto Cifrado: {texto_cifrado}")
