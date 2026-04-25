import hashlib, hmac, secrets

# Quantidade de vezes que o algoritmo se repete.
ITERATIONS = 200_000

def hash_value(value: str) -> str:
    """
    Essa função gera um hash seguro para um valor usando PBKDF2-HMAC com SHA-256. Ela gera um salt aleatório,
    e retorna uma string no formato salt$hash, onde salt é o salt gerado e hash é o hash derivado do valor usando o salt.
    """
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

    return f"{salt}${derived_key}"

def verify_value(value: str, stored_hash: str) -> bool:
    """
    Essa função verifica se um valor corresponde a um hash armazenado. Ela divide o hash armazenado para obter o salt e o hash original,
    recalcula o hash do valor usando o mesmo salt, e compara o hash recalculado com o hash original usando hmac.compare_digest 
    para evitar ataques de timing. A função retorna True se os hashes corresponderem, e False caso contrário.
    """
    try:
        salt, original_hash = stored_hash.split("$", 1)
        
    except ValueError:
        return False
    
    # Recalcula o hash usando o mesmo salt que foi salvo anteriormente
    new_hash  = hashlib.pbkdf2_hmac(
        "sha256",
        value.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    ).hex()
    
    #Compare o hash recem gerado com o hash original salvo no banco.
    return hmac.compare_digest(new_hash, original_hash)