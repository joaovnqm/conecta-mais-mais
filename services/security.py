import hashlib, hmac, secrets

# Quantidade de vezes que o algoritmo se repete.
ITERATIONS = 200_000


# Função que recebe um valor em texto puro e devolve esse valor convertido em hash
def hash_value(value: str) -> str:
    # Gera um salt aleatório em hexadecinal. O salt garante que duas senhas escritas iguais não possuam o mesmo hash
    salt = secrets.token_hex(16)
    
    """
    Gera a chave derivada usando PBKDF2-HMAC com SHA-256
    value.encode("utf-8") transforma o texto em bytes
    salt.encode("utf-8") transforma o salt em bytes
    ITERATIONS é quantas vezes o algoritmo se repete
    """
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        value.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    ).hex()
    
    # Retorna uma string em salt$hash.
    return f"{salt}${derived_key}"

# Função que verifica se um valor digitado pelo usuário corresponde ao hash salvo no banco de dados
def verify_value(value: str, stored_hash: str) -> bool:
    try:
        # Divide a string salva em duas partes: salt e hash
        salt, original_hash = stored_hash.split("$", 1)
        
    # Se o formato estiver errado e não tiver o separador $, a função retorna False
    except ValueError:
        return False
    
    # Recalcula o hash usando o mesmo salt que foi salvo anteriormente
    new_hash  = hashlib.pbkdf2_hmac(
        "sha256",
        value.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    ).hex()
    """
    Compare o hash recem gerado com o hash original salvo no banco.
    """
    return hmac.compare_digest(new_hash, original_hash)