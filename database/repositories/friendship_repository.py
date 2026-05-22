import sqlite3
from typing import List, Optional
from models.friendship import Friend, FriendRequest


class FriendshipServices:
    """
    Classe responsável pelas operações sociais de amizade:
    - criar tabela de amizades;
    - busca de usuários por e-mail;
    - enviar solicitação;
    - aceitar solicitação;
    - recusar solicitação;
    - listar amigos;
    - listar solicitações pendentes;
    - remoção de amizades.
    A amizade é armazenada usando os campos user_low_id e user_high_id para evitar duplicidade 
    entre os mesmos dois usuários.
    """

    def __init__(self, database_path: str = "conecta++.db") -> None:
        """
        Inicializa o serviço de amizades;
        - abre conexão com o banco;
        - ativa o suporte a chaves estrangeiras;
        - cria um cursor para executar comandos SQL;
        - garante que a tabela friendships exista.
        """
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self) -> None:
        """
        Cria a tabela friendships caso ela ainda não exista.
        A tabela representa uma relação social entre dois usuários

        Coluna principal:
        friendship_id: 
            Identificador único da relação de amizade
        user_low_id:
            Menor ID entre os dois usuários envolvidos na amizade
        user_high_id:
            Maior ID entre os dois usuários envolvidos na amizade
        status:
        - pending: solicitação enviada, mas ainda não respondida
        - accepted: amizade aceita
        - rejected: solicitação recusada
        - blocked: relação bloqueada

        created_at:
        Data e hora em que a solicitação foi criada.

        updated_at
        Data e hora da última atualização da relação

        Restrições:
        - UNIQUE(user_low_id, user_high_id) impede amizade duplicada;
        - CHECK(user_low_id < user_high_id) força os IDs a ficarem em ordem;
        - FOREIGN KEY garante que os usuários existam na tabela users;
        - ON DELETE CASCADE remove as amizades caso um usuário seja apagado.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS friendships (
                friendship_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                
                user_low_id INTEGER NOT NULL,
                user_high_id INTEGER NOT NULL,  
                requester_id INTEGER NOT NULL,
                
                status TEXT NOT NULL CHECK (
                    status IN ('pending', 'accepted', 'rejected', 'blocked')
                ),
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(user_low_id, user_high_id),
                
                FOREIGN KEY (user_low_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                
                FOREIGN KEY (user_high_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,
                    
                FOREIGN KEY (requester_id)
                    REFERENCES users(user_id)
                    ON DELETE  CASCADE,
                
                CHECK(user_low_id < user_high_id)
            )
            """
        )
        self.connection.commit()

    def make_user_pair(self, user_id_1: int, user_id_2: int) -> tuple[int, int]:
        """
        Organiza dois IDs de usuário em ordem crescente

        Parâmetros:
            user_id_1 (int): ID do primeiro usuário
            user_id_2 (int): ID do segundo usuário
        Retorno:
            tuple[int, int]: Uma tupla contendo o menor ID primeiro e o maior ID depois
            Isso garante que a amizade não seja cadastrada duas vezes no banco

        Exceção:
            Levanta ValueError se os dois IDs forem iguais, porque o usuário não pode adicionar a si mesmo
        """
        if user_id_1 == user_id_2:
            raise ValueError("Usuário não pode adicionar a si mesmo")

        return min(user_id_1, user_id_2), max(user_id_1, user_id_2)

    def find_user_by_email(self, email: str) -> Optional[dict]:
        """
        Busca um usuário cadastrado a partir do e-mail

        Parâmetro:
            email(str): E-mail informado na busca
        Retorno:
            Optional[dict]:
                Retorna um dicionário com user_id, name e email se o usuário existir.
                Retorna None se nenhum usuário for encontrado
        Tratamento:
            - remove espaços no início e fim
            - converte e-mail para lower
            - usa parâmetro SQL como ? para evitar SQL Injection
        """
        email = email.strip().lower()

        self.cursor.execute(
            """
            SELECT user_id, name, email
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        user = self.cursor.fetchone()

        if user is None:
            return None

        return {
            "user_id": user[0],
            "name": user[1],
            "email": user[2]
        }

    def send_friend_request(self, requester_id: int, target_email: str) -> tuple[bool, str]:
        """
        Envia uma solicitação de amizade para  outro usuário usando o e-mail dele

        Parâmetro:
            requester_id (int): ID do usuário que está enviando a solicitação
            target_email (str): E-mail do usuário que irá receber a solicitação

        Retorno:
            tuple[bool, str]:
                O primeiro valor indica se a operação deu certo
                O segundo valor contém a mensagem explicativa para exibir na interface

        Regras de negócio:
            - O usuário de destino precisa existir;
            - O usuário não pode enviar solicitação para si;
            - Se já houver solicitação pendente, não cria outra;
            - Se já forem amigos, não cria outra amizade;
            - Se a relação estiver bloqueada, impede envio;
            - Se a solicitação anterior tiver sido recusada, permite reenviar;
            - Se não existir relação anterior, cria uma nova solicitação pendente;
        """

        target_user = self.find_user_by_email(target_email)

        if target_user is None:
            return False, "Usuário não encontrado"

        target_id = target_user["user_id"]

        if requester_id == target_id:
            return False, "Você não pode enviar solicitação para si mesmo"

        user_low_id, user_high_id = self.make_user_pair(
            requester_id, target_id)

        self.cursor.execute(
            """
            SELECT friendship_id, status
            FROM friendships
            WHERE user_low_id = ?
                AND user_high_id = ?
            """,
            (user_low_id, user_high_id)
        )

        friendship = self.cursor.fetchone()

        if friendship is not None:
            friendship_id, status = friendship

            if status == "pending":
                return False, "Já existe uma solicitação pendente entre vocês"

            if status == "accepted":
                return False, "Vocês já são amigos"

            if status == "blocked":
                return False, "Não é possível enviar solicitação para este usuário"

            if status == "rejected":
                self.cursor.execute(
                    """
                    UPDATE friendships
                    SET status = 'pending',
                        requester_id = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE friendship_id = ?
                    """,
                    (requester_id, friendship_id)
                )

                self.connection.commit()
                return True, "Solicitação reenviada com sucesso"

        self.cursor.execute(
            """
            INSERT INTO friendships (
                user_low_id,
                user_high_id,
                requester_id,
                status
            )
            VALUES (?, ?, ?, 'pending')
            """,
            (user_low_id, user_high_id, requester_id)
        )

        self.connection.commit()

        return True, "Solicitação de amizade enviada com sucesso"

    def list_pending_requests(self, user_id: int) -> List[FriendRequest]:
        """
        Lista as solicitações de amizade pendentes recebidas por um usuário.
        Retorna objetos FriendRequest.
        """
        self.cursor.execute(
            """
            SELECT
                f.friendship_id,
                u.user_id,
                u.name,
                u.email
            FROM friendships f
            JOIN users u
            ON u.user_id = f.requester_id
            WHERE f.status = 'pending'
            AND f.requester_id != ?
            AND ? IN (f.user_low_id, f.user_high_id)
            ORDER BY f.created_at DESC
            """,
            (user_id, user_id)
        )

        requests = self.cursor.fetchall()

        return [
            FriendRequest(
                friendship_id=row[0],
                requester_id=row[1],
                requester_name=row[2],
                requester_email=row[3]
            )
            for row in requests
        ]

    def list_pending_request(self, user_id: int) -> List[FriendRequest]:
        return self.list_pending_requests(user_id)

    def accept_friend_request(self, current_user_id: int, requester_id: int) -> tuple[bool, str]:
        """
        Aceita uma solicitação de amizade pendente

        Parâmetro:
            current_user_id (int): ID do usuário logado, ou seja, quem está aceitando
            requester_id (int): ID do usuário que enviou a solicitação

        Retorno:
            tuple[bool, str]:
                Retorna True e mensagem de sucesso se a amizade for aceita
                Retorna False e mensagem de erro se houver algum problema

        Regra de negócio:
            - a solicitação precisa existir;
            - o status precisa estar como pending;
            - o usuário não podo aceitar uma solicitação enviada por ele mesmo

        No banco atualiza o status da relação para accepted.
        """
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id, requester_id)

        self.cursor.execute(
            """
            SELECT friendship_id, requester_id, status
            FROM friendships
            WHERE user_low_id = ?
            AND user_high_id = ?
            """,
            (user_low_id, user_high_id)
        )

        friendship = self.cursor.fetchone()

        if friendship is None:
            return False, "Solicitação não encontrada"

        friendship_id, original_requester_id, status = friendship

        if status != "pending":
            return False, "Essa solicitação não está pendente"

        if original_requester_id == current_user_id:
            return False, "Você não pode aceitar uma solicitação enviada por você mesmo"

        self.cursor.execute(
            """
            UPDATE friendships
            SET status = 'accepted',
                updated_at = CURRENT_TIMESTAMP
            WHERE friendship_id = ?
            """,
            (friendship_id,)
        )

        self.connection.commit()

        return True, "Solicitação aceita. Vocês agora são amigos"

    def reject_friend_request(self, current_user_id: int, requester_id: int):
        """
        Recusa uma solicitação de amizade pendente.

        Parâmetro:
            current_user_id (int): ID do usuário logado, ou seja, quem está recusando
            requester_id(int): ID do usuário que enviou uma solicitação

        Retorno:
            tuple[bool, str]:
                Retorna True e mensagem de sucesso se a solicitação for recusada.
                Retorna False e mensagem de erro se não houver solicitação pendente.

        No banco atualiza a relação para rejected. A solicitação não é apagada, ela fica no banco de dados para permitir
        o controle histórico e possível reenvio no futuro.
        """
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id, requester_id)

        self.cursor.execute(
            """
            UPDATE friendships
            SET status = 'rejected',
                updated_at = CURRENT_TIMESTAMP
            WHERE user_low_id = ?
            AND user_high_id = ?
            AND requester_id = ?
            AND status = 'pending'
            """,
            (user_low_id, user_high_id, requester_id)
        )

        if self.cursor.rowcount == 0:
            return False, "Solicitação pendente não encontrada"

        self.connection.commit()

        return True, "Solicitação recusada"

    def list_friends(self, user_id: int) -> List[Friend]:
        """
        Lista todos os amigos aceitos de um usuário.
        Retorna objetos Friend.
        """
        self.cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email
            FROM friendships f
            JOIN users u
            ON u.user_id = CASE
                WHEN f.user_low_id = ? THEN f.user_high_id
                ELSE f.user_low_id
                END
            WHERE f.status = 'accepted'
            AND ? IN (f.user_low_id, f.user_high_id)
            ORDER BY u.name ASC
            """,
            (user_id, user_id)
        )

        friends = self.cursor.fetchall()

        return [
            Friend(
                user_id=row[0],
                name=row[1],
                email=row[2]
            )
            for row in friends
        ]

    def remove_friend(self, current_user_id: int, friend_id: int) -> tuple[bool, str]:
        """
        Remove uma amizade aceita entre dois usuários. A função organiza os dois IDs como make_user_pair e remove
        a relação da tabela friendships apenas se o status estiver como accepted

        Parâmetros:
            current_user_id (int): ID do usuário logado.
            friend_id (int): ID do amigo que será removido.

        Retorno:
            tuple[bool, str]:
                Retorna True e mensagem de sucesso se a amizade for removida
                Retorna False e mensagem de erro se a amizade não existir

        """
        user_low_id, user_high_id = self.make_user_pair(
            current_user_id, friend_id)

        self.cursor.execute(
            """
            DELETE FROM friendships
            WHERE user_low_id = ?
            AND user_high_id = ?
            AND status = 'accepted'
            """,
            (user_low_id, user_high_id)
        )

        if self.cursor.rowcount == 0:
            return False, "Amizade não encontrada"

        self.connection.commit()

        return True, "Amizade removida com sucesso"

    
    def block_user(self, current_user_id: int, target_id: int) -> tuple[bool, str]:
        """
        Bloqueia o usuário
        """
        if current_user_id == target_id:
            return False, 'Você não pode bloquear a si mesmo'
        
        user_low_id, user_high_id = self.make_user_pair(current_user_id, target_id)
        
        self.cursor.execute(
            """
            SELECT friendship_id, status
            FROM friendships
            WHERE user_low_id = ?
            AND user_high_id = ?
            """,
            (user_low_id, user_high_id)
        )
        
        friendship = self.cursor.fetchone()
        
        if friendship is not None:
            friendship_id, status = friendship

            if status == 'blocked':
                return False, 'Este usuário já está bloqueado'
            
            self.cursor.execute(
                """
                UPDATE friendships
                SET status = 'blocked',
                    requester_id = ?,
                    update_at = CURRENT_TIMESTAMP
                WHERE friendship_id = ?
                """,
                (current_user_id, friendship_id)
            )
            
            self.connection.commit()
            return True, 'Usuário bloqueado com sucesso'
        
        self.cursor.execute(
            """
            INSERT INTO friendships (
                user_low_id,
                user_high_id,
                requester_id,
                status
            )
            VALUES (?, ?, ?, ?, 'blocked')
            """,
            (user_low_id, user_high_id, current_user_id)
        )
        
        self.connection.commit()
        
        return True, 'Usuário bloqueado com sucesso'
    
    
    def unblock_user(self, current_user_id: int, target_id: int) -> tuple[bool, str]:
        """
        Desbloqueia um usuário bloqueado pelo usuário logado
        Só quem bloqueiou pode desbloquear
        Ao desbloquear, a relação é removida da tabela.
        """
        user_low_id, user_high_id = self.make_user_pair(current_user_id, target_id)
        
        self.cursor.execute(
            """
            DELETE FROM friendships
            WHERE user_low_id = ?
            AND user_high_id = ?
            AND requester_id = ?
            AND status = 'blocked'
            """,
        )
        
        if self.cursor.rowcount == 0:
            return False, 'Bloqueio não encontrado para este usuário'
        
        self.connection.commit()
        
        return True, 'Usuário desbloqueado com sucesso'
    
    def list_blocked_users(self, user_id: int) -> List[Friend]:
        """
        Lista usuários bloqueados pelo usuário logado
        """
        self.cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email
            FROM friendships f
            JOIN users u
            ON u.user_id = CASE
                WHEN f.user_low_id = ? THEN f.user_high_id
                ELSE f.user_low_id
                END
            WHERE f.status = 'blocked'
            AND f.requester_id = ?
            AND ? IN (f.user_low_id, f.user_high_id)
            ORDER BY u.name ASC
            """,
            (user_id, user_id, user_id)
        )
        
        blocked_users = self.cursor.fetchall()
        
        return [
            Friend(
                user_id = row[0],
                name=row[1],
                email=row[2]
            )
            for row in blocked_users
        ]
        
friendship_services = FriendshipServices()
