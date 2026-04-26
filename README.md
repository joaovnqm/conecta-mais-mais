# Conecta++ 🚀

O **Conecta++** é uma aplicação de interface de terminal (TUI) desenvolvida como projeto prático para o curso de **Sistemas de Informação** da **UFRPE**. A plataforma visa conectar a comunidade acadêmica a eventos, permitindo a gestão de perfis e a personalização de experiências com base em interesses específicos.

---

## 📋 Funcionalidades

O sistema oferece uma experiência robusta via terminal, focada em usabilidade e segurança:

*   **Gestão de Usuários**: Sistema de cadastro com verificação de e-mail via código numérico, login seguro e fluxo de recuperação de senha.
*   **Perfil Personalizado**: Visualização de dados, edição de nome em tempo real, alteração de credenciais e opção de exclusão de conta (com deleção em cascata no banco de dados).
*   **Filtros por Interesse**: Seleção de categorias para personalizar a exibição de eventos relevantes ao usuário.
*   **Exploração de Eventos**: Listagem completa de atividades com detalhes como local, data, hora e criador do evento.
*   **Sistema de Favoritos**: Permite salvar eventos específicos em uma lista dedicada para acompanhamento rápido.

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagem**: Python 3.14
*   **Interface**: [Textual](https://textual.textualize.io/) (TUI Framework)
*   **Banco de Dados**: SQLite3
*   **Segurança**: PBKDF2-HMAC com SHA-256 para hashing de senhas e `hmac.compare_digest` contra ataques de timing.
*   **Comunicação**: Protocolo SMTP para envio de e-mails de verificação.

---

## 📂 Estrutura do Projeto

O código está organizado para facilitar a manutenção e escalabilidade:

| Diretório/Arquivo | Descrição |
| :--- | :--- |
| `main.py` | Ponto de entrada que inicializa a aplicação. |
| `screens/` | Contém as classes de visualização (views) da interface. |
| `services/` | Lógica de negócio: autenticação, eventos, banco de dados e validações. |
| `conecta++.db` | Arquivo do banco de dados relacional. |
| `.env` | Variáveis de ambiente sensíveis (credenciais de e-mail). |

---

## 🚀 Como Executar

### Pré-requisitos
*   Python 3.14 ou superior.
*   Conta Gmail com "Senha de App" configurada.

### Instalação

1.  **Clone o repositório**:
    ```bash
    git clone https://github.com/joaovictornqm/conecta-mais-mais.git
    ```

2.  **Instale as dependências**:
    ```bash
    pip install textual unidecode python-dotenv
    ```

3.  **Configure o ambiente**:
    Crie um arquivo `.env` na raiz do projeto:
    ```env
    APP_EMAIL=seu-email@gmail.com
    APP_EMAIL_PASSWORD=sua-senha-de-app
    ```

4.  **Inicie a aplicação**:
    ```bash
    python main.py
    ```

---

## 🎓 Contexto Acadêmico

Este projeto integra as atividades da disciplina **PISI I (Projeto Interdisciplinar para Sistemas de Informação I)** na **UFRPE**. O desenvolvimento focou na aplicação de conceitos de Engenharia de Software, persistência de dados e segurança da informação.

**Desenvolvedores:** João Victor Macêdo e Wellison Cavalcante  
**Instituição:** Universidade Federal Rural de Pernambuco (UFRPE)  
**Curso:** Bacharelado em Sistemas de Informação  
