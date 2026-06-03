# Conecta++ Release 3.0 🚀

O **Conecta++** é uma aplicação de interface de terminal (TUI) desenvolvida como projeto prático para o curso de **Sistemas de Informação** da **UFRPE**. A plataforma visa conectar a comunidade acadêmica a eventos, permitindo a gestão de perfis, personalização de experiências com base em interesses, interação entre usuários, acompanhamento de presença, emissão de certificados, integração com calendário e ranqueamento por participação.

## 🖼️ Visualização da Tela de Eventos

Abaixo estão algumas capturas da tela responsável por listar os eventos disponíveis no sistema.
Nessa interface, o usuário pode filtrar os eventos por interesse, visualizar a lista de eventos cadastrados, acompanhar informações relevantes e acessar mais detalhes clicando em uma opção.

<div align="center">

<table>
  <tr>
    <td align="center">
      <img src=".idea/assets/tela-eventos-1.png" alt="Tela de eventos com filtro por interesse" width="350"/>
      <br>
      <strong>Filtro de eventos por interesse</strong>
    </td>
    <td align="center">
      <img src=".idea/assets/tela-eventos-2.png" alt="Tela de eventos com lista completa e botão voltar" width="350"/>
      <br>
      <strong>Lista de eventos disponíveis</strong>
    </td>
  </tr>
</table>

</div>

### 📌 Funcionalidade exibida

A tela apresenta uma vitrine de eventos cadastrados no sistema, permitindo que o usuário visualize conferências, simpósios, encontros acadêmicos e eventos sociais relacionados aos seus interesses.

Entre os elementos exibidos estão:

* Filtro por área de interesse;
* Lista de eventos disponíveis;
* Cards individuais para cada evento;
* Barra de rolagem para navegação;
* Botão de retorno para a tela anterior;
* Informações detalhadas sobre cada evento;
* Possibilidade de favoritar eventos;
* Confirmação de presença;
* Acompanhamento de amigos presentes;
* Informações sobre datas de submissão de artigos, quando disponíveis.

Essa funcionalidade faz parte da proposta principal do projeto, que é facilitar a descoberta, o acompanhamento e a participação em eventos acadêmicos e tecnológicos de forma simples, organizada e interativa.

---

## Bibliotecas usadas

### Bibliotecas externas

| Biblioteca      | Objetivo no projeto                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| `textual`       | Criar a interface gráfica em terminal, com telas, botões, inputs, labels, tabelas e navegação entre páginas. |
| `python-dotenv` | Carregar variáveis de ambiente do arquivo `.env`, como e-mail e senha de app.                                |
| `unidecode`     | Remover acentos de textos usados em identificadores de componentes da interface.                             |
| `reportlab`     | Gerar certificados em PDF para participantes e apresentadores de eventos.                                    |
| `ics`           | Criar arquivos de calendário no formato `.ics`, permitindo salvar eventos no calendário do usuário.          |

### Bibliotecas nativas do Python

| Biblioteca      | Objetivo no projeto                                                              |
| --------------- | -------------------------------------------------------------------------------- |
| `sqlite3`       | Criar e manipular o banco de dados local SQLite.                                 |
| `hashlib`       | Gerar hash seguro de senhas e códigos.                                           |
| `hmac`          | Comparar hashes de forma mais segura.                                            |
| `secrets`       | Gerar salt aleatório para aumentar a segurança das senhas.                       |
| `smtplib`       | Enviar e-mails usando servidor SMTP.                                             |
| `email.message` | Montar a mensagem de e-mail enviada ao usuário.                                  |
| `datetime`      | Controlar data e hora de expiração dos códigos de verificação, eventos e prazos. |
| `random`        | Gerar códigos numéricos aleatórios.                                              |
| `re`            | Validar campos como nome, e-mail, senha, username, data, hora e links sociais.   |
| `os`            | Ler variáveis de ambiente configuradas no sistema ou arquivo `.env`.             |
| `pathlib`       | Manipular caminhos de arquivos e diretórios do projeto.                          |
| `typing`        | Melhorar a organização do código com anotações de tipo.                          |

---

## ⚙️ Funcionalidades elaboradas e seus objetivos

### ✅ Funcionalidades entregues na versão 1.0 — Primeira VA

As funcionalidades da **Release 1.0** foram organizadas para oferecer uma experiência inicial completa ao usuário, desde o cadastro até a visualização e gerenciamento de eventos personalizados por interesse.

---

### 🔐 Autenticação e segurança

| Funcionalidade                       | Descrição                                                                   | Objetivo                                                                               |
| ------------------------------------ | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Cadastro de usuário**              | Permite que novos usuários criem uma conta informando nome, e-mail e senha. | Registrar usuários no sistema de forma organizada e segura.                            |
| **Validação de dados**               | Valida nome, e-mail, senha e confirmação de senha durante o cadastro.       | Evitar dados inválidos, incompletos ou inconsistentes no banco de dados.               |
| **Verificação de e-mail por código** | Envia um código para o e-mail informado antes de finalizar o cadastro.      | Confirmar que o e-mail realmente pertence ao usuário.                                  |
| **Login de usuário**                 | Permite o acesso ao sistema usando e-mail e senha cadastrados.              | Garantir que apenas usuários autenticados acessem as telas internas.                   |
| **Recuperação de senha**             | Envia um código por e-mail para permitir a criação de uma nova senha.       | Recuperar o acesso à conta caso o usuário esqueça a senha.                             |
| **Criptografia de senhas**           | Armazena as senhas usando hash com `PBKDF2-HMAC-SHA256` e salt aleatório.   | Proteger as credenciais dos usuários e evitar o armazenamento de senhas em texto puro. |
| **Mostrar e ocultar senha**          | Adiciona um botão para alternar a visibilidade dos campos de senha.         | Melhorar a usabilidade nas telas de login, cadastro e alteração de senha.              |

---

### 👤 Gerenciamento de perfil

| Funcionalidade          | Descrição                                                                | Objetivo                                                               |
| ----------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| **Atualização de nome** | Permite que o usuário altere o nome exibido no perfil.                   | Manter os dados do usuário atualizados.                                |
| **Alteração de senha**  | Permite trocar a senha informando a senha atual e uma nova senha válida. | Oferecer uma forma segura de atualizar as credenciais da conta.        |
| **Exclusão de conta**   | Permite que o usuário remova sua conta do sistema.                       | Dar ao usuário controle sobre seus próprios dados dentro da aplicação. |

---

### ⭐ Interesses e personalização

| Funcionalidade                        | Descrição                                                           | Objetivo                                                                           |
| ------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Seleção de interesses**             | Permite que o usuário escolha áreas de interesse após o cadastro.   | Personalizar a experiência e direcionar eventos mais relevantes para cada usuário. |
| **Listagem de eventos por interesse** | Exibe eventos relacionados aos interesses cadastrados pelo usuário. | Tornar a navegação mais útil e alinhada ao perfil do usuário.                      |
| **Filtro de eventos**                 | Permite filtrar eventos por uma área de interesse específica.       | Facilitar a busca por eventos dentro da aplicação.                                 |

---

### 📅 Eventos

| Funcionalidade                       | Descrição                                                                                        | Objetivo                                                                                   |
| ------------------------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| **Cadastro de eventos**              | Permite criar eventos com nome, descrição, local, data, hora, criador e interesses relacionados. | Armazenar eventos no banco de dados e associá-los às áreas de interesse.                   |
| **Detalhes do evento**               | Exibe informações completas de um evento selecionado.                                            | Permitir que o usuário consulte descrição, local, data, hora e criador antes de favoritar. |
| **Favoritar e desfavoritar eventos** | Permite adicionar ou remover eventos da lista de favoritos.                                      | Salvar eventos importantes para consulta posterior.                                        |
| **Listagem de eventos favoritos**    | Exibe todos os eventos marcados como favoritos pelo usuário.                                     | Organizar em uma tela própria os eventos que o usuário deseja acompanhar.                  |

---

### ✅ Funcionalidades entregues na versão 2.0 — Segunda VA

As funcionalidades da **Release 2.0** ampliaram o Conecta++ com recursos de interação entre usuários, networking, gerenciamento de amizades, bloqueios e controle de presença em eventos.

Essa versão teve como foco transformar o sistema em uma plataforma mais social, permitindo que os usuários não apenas encontrem eventos, mas também se conectem com outras pessoas, acompanhem amigos e indiquem sua participação nos eventos.

---

### 🤝 Amigos e networking

| Funcionalidade                   | Descrição                                                                                           | Objetivo                                                                                |
| -------------------------------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Adicionar amigos**             | Permite que o usuário adicione outro usuário como amigo por meio do username cadastrado no sistema. | Criar conexões entre usuários e fortalecer o networking acadêmico dentro da plataforma. |
| **Lista de amigos**              | Exibe todos os usuários adicionados como amigos pelo usuário logado.                                | Facilitar a visualização e o gerenciamento da rede de contatos do usuário.              |
| **Remover amigos**               | Permite remover um usuário da lista de amigos.                                                      | Dar ao usuário controle sobre suas conexões dentro da aplicação.                        |
| **Bloquear usuários**            | Permite bloquear usuários indesejados.                                                              | Evitar interações não desejadas e aumentar a segurança social da plataforma.            |
| **Lista de usuários bloqueados** | Exibe os usuários bloqueados pelo usuário logado.                                                   | Permitir que o usuário acompanhe e gerencie seus bloqueios.                             |
| **Desbloquear usuários**         | Permite remover o bloqueio de um usuário anteriormente bloqueado.                                   | Possibilitar a retomada de interações entre usuários quando desejado.                   |

---

### ✅ Presença em eventos

| Funcionalidade         | Descrição                                                                                                                 | Objetivo                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Marcar presença**    | Permite que o usuário confirme presença em um evento disponível.                                                          | Registrar a intenção de participação do usuário em determinado evento.             |
| **Lista de presença**  | Exibe informações sobre usuários que confirmaram presença no evento, incluindo amigos do usuário logado quando aplicável. | Permitir acompanhamento da participação nos eventos e aumentar a interação social. |
| **Desmarcar presença** | Permite cancelar uma presença anteriormente confirmada.                                                                   | Dar flexibilidade ao usuário para alterar sua decisão de participação.             |

---

### 📌 Eventos favoritos e acompanhamento

| Funcionalidade                              | Descrição                                                                       | Objetivo                                                                            |
| ------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Lista de eventos favoritados**            | Exibe os eventos que o usuário marcou como favoritos.                           | Centralizar eventos de interesse para facilitar o acompanhamento posterior.         |
| **Busca de eventos favoritados por amigos** | Permite identificar eventos de interesse dentro da rede de contatos do usuário. | Aproximar usuários com interesses semelhantes e incentivar a participação conjunta. |

---

### 🧱 Organização e melhoria técnica

| Funcionalidade       | Descrição                                                                                                                                                                | Objetivo                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| **POO na aplicação** | Refatora partes do código para aplicar conceitos de Programação Orientada a Objetos, organizando melhor responsabilidades entre telas, serviços, modelos e repositórios. | Melhorar a manutenção, a organização, a reutilização e a escalabilidade do projeto. |

---

### ✅ Funcionalidades entregues na versão 3.0 — Terceira VA

As funcionalidades da **Release 3.0** tornaram o Conecta++ mais completo para uso acadêmico e profissional, com foco em emissão de certificados, dados sociais do usuário, integração com calendário, acompanhamento de datas de submissão e ranqueamento.

Essa versão passou a valorizar não apenas a participação em eventos, mas também ações como apresentação, emissão de certificado e engajamento contínuo na plataforma.

---

### 📄 Acompanhamento acadêmico de eventos

| Funcionalidade                        | Descrição                                                                                        | Objetivo                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| **Datas de submissão de artigos**     | Automatiza o acompanhamento de datas relacionadas à submissão de artigos científicos em eventos. | Ajudar o usuário a identificar prazos importantes para envio de trabalhos acadêmicos.              |
| **Retorno para datas não publicadas** | Informa quando uma data de submissão não foi encontrada ou ainda não foi publicada.              | Evitar que o usuário receba uma informação incorreta ou fique sem retorno sobre a busca realizada. |
| **Status de submissão**               | Exibe informações sobre o estado da submissão, como prazo aberto, encerrado ou não encontrado.   | Facilitar a tomada de decisão sobre participação e envio de artigos.                               |

---

### 🎨 Visualização e experiência na lista de eventos

| Funcionalidade                                 | Descrição                                                                                                              | Objetivo                                                                       |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Lista de eventos estilizada**                | Melhora a apresentação visual da lista de eventos, adaptando a exibição das informações e destacando dados relevantes. | Tornar a navegação mais clara, organizada e agradável para o usuário.          |
| **Adaptação à data limite de envio de artigo** | Exibe informações relacionadas ao prazo de submissão quando disponíveis.                                               | Facilitar a identificação de eventos que ainda aceitam submissão de trabalhos. |

---

### 👤 Dados sociais do usuário

| Funcionalidade          | Descrição                                                            | Objetivo                                                                |
| ----------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Username do usuário** | Adiciona um identificador único para cada usuário dentro do sistema. | Permitir busca, identificação e adição de amigos de forma mais precisa. |
| **LinkedIn do usuário** | Permite cadastrar o link do perfil profissional do usuário.          | Favorecer conexões acadêmicas e profissionais entre usuários.           |
| **GitHub do usuário**   | Permite cadastrar o link do perfil técnico do usuário.               | Valorizar o portfólio, os projetos e a identidade técnica do usuário.   |

---

### 🧾 Certificados

| Funcionalidade                               | Descrição                                                                         | Objetivo                                                              |
| -------------------------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Emissão de certificado de participação**   | Permite gerar certificado para usuários que participaram de um evento.            | Comprovar a presença do usuário em eventos cadastrados na plataforma. |
| **Emissão de certificado de apresentação**   | Permite gerar certificado para usuários que realizaram apresentação em um evento. | Valorizar a participação ativa do usuário em atividades acadêmicas.   |
| **Envio de certificado por e-mail**          | Envia o certificado gerado para o e-mail do usuário.                              | Facilitar o acesso, armazenamento e uso posterior do certificado.     |
| **Controle contra duplicidade de pontuação** | Impede que o usuário receba pontuação repetida pela mesma ação no mesmo evento.   | Manter a consistência do sistema de ranqueamento.                     |

---

### 📆 Integração com calendário

| Funcionalidade                     | Descrição                                                                      | Objetivo                                                                     |
| ---------------------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| **Salvar evento no calendário**    | Permite salvar um evento no calendário vinculado ao e-mail do usuário.         | Ajudar o usuário a organizar sua agenda e lembrar dos eventos confirmados.   |
| **Envio de convite de calendário** | Gera e envia um arquivo de calendário com as informações do evento.            | Facilitar a importação do evento para ferramentas de agenda.                 |
| **Tratamento de falhas no envio**  | Mantém a presença confirmada mesmo quando ocorre falha no envio do calendário. | Evitar que uma falha secundária impeça a confirmação de presença do usuário. |

---

### 🏆 Ranqueamento e gamificação

| Funcionalidade                 | Descrição                                                                                                          | Objetivo                                                                       |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| **Ranqueamento de usuários**   | Classifica os usuários com base em sua participação em eventos, certificados recebidos e apresentações realizadas. | Estimular o engajamento dos usuários dentro da plataforma.                     |
| **Pontuação por presença**     | Adiciona pontos quando o usuário participa de eventos.                                                             | Valorizar a participação recorrente na comunidade acadêmica.                   |
| **Pontuação por certificado**  | Adiciona pontos quando o usuário recebe certificados.                                                              | Recompensar participações comprovadas em eventos.                              |
| **Pontuação por apresentação** | Adiciona uma pontuação maior quando o usuário realiza apresentações.                                               | Valorizar usuários que contribuem ativamente com conhecimento e apresentações. |
| **Níveis de experiência**      | Organiza os usuários em níveis conforme a pontuação acumulada.                                                     | Tornar o progresso do usuário mais visível e motivador.                        |

### Níveis do ranque

| Nível | Nome          |
| ----- | ------------- |
| 1     | Recém-chegado |
| 2     | Participante  |
| 3     | Explorador    |
| 4     | Engajado      |
| 5     | Experiente    |
| 6     | Influente     |
| 7     | Referência    |
| 8     | Elite         |
| 9     | Mestre        |
| 10    | Lendário      |

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem**: Python 3.14
* **Interface**: [Textual](https://textual.textualize.io/) (TUI Framework)
* **Banco de Dados**: SQLite3
* **Segurança**: PBKDF2-HMAC com SHA-256 para hashing de senhas e `hmac.compare_digest` contra ataques de timing.
* **Comunicação**: Protocolo SMTP para envio de e-mails de verificação, recuperação de senha, certificados e convites de calendário.
* **Certificados**: Geração de documentos em PDF para participação e apresentação em eventos.
* **Calendário**: Geração de arquivos `.ics` para adicionar eventos à agenda do usuário.
* **Gamificação**: Sistema de pontuação e níveis com base em participação, certificados e apresentações.

---

## 📂 Estrutura do Projeto

O código está organizado para facilitar a manutenção e escalabilidade:

| Diretório/Arquivo | Descrição                                                                                                                   |
| :---------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| `main.py`         | Ponto de entrada que inicializa a aplicação.                                                                                |
| `screens/`        | Contém as classes de visualização da interface, organizadas por telas como autenticação, eventos, perfil, amigos e ranking. |
| `services/`       | Contém a lógica de negócio, incluindo autenticação, eventos, e-mails, certificados, calendário e ranqueamento.              |
| `models/`         | Contém as classes e estruturas que representam entidades do sistema, como usuário, evento, amizade e ranking.               |
| `database/`       | Contém scripts, conexões e repositórios responsáveis pela persistência dos dados.                                           |
| `utils/`          | Contém funções auxiliares, validações, segurança e recursos reutilizáveis.                                                  |
| `assets/`         | Contém arquivos visuais usados no sistema, como modelos de certificados e imagens auxiliares.                               |
| `tools/`          | Contém scripts auxiliares para criação de tabelas ou preparação de recursos do sistema.                                     |
| `conecta++.db`    | Arquivo do banco de dados relacional SQLite.                                                                                |
| `.env`            | Variáveis de ambiente sensíveis, como credenciais de e-mail.                                                                |

---

## 🚀 Como Executar

### Pré-requisitos

* Python 3.14 ou superior.
* Conta Gmail com "Senha de App" configurada.
* Dependências externas usadas pelo projeto.

### Instalação

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/joaovictornqm/conecta-mais-mais.git
   ```

2. **Acesse a pasta do projeto**:

   ```bash
   cd conecta-mais-mais
   ```

3. **Crie e ative o ambiente virtual**:

   ```bash
   python -m venv .venv
   ```

   No Windows:

   ```bash
   .venv\Scripts\activate
   ```

   No Linux ou macOS:

   ```bash
   source .venv/bin/activate
   ```

4. **Instale as dependências**:

   ```bash
   pip install textual unidecode python-dotenv reportlab ics
   ```

5. **Configure o ambiente**:
   Crie um arquivo `.env` na raiz do projeto:

   ```env
   APP_EMAIL=seu-email@gmail.com
   APP_EMAIL_PASSWORD=sua-senha-de-app
   ```

6. **Inicie a aplicação**:

   ```bash
   python main.py
   ```

---

## 🎓 Contexto Acadêmico

Este projeto integra as atividades da disciplina **PISI I (Projeto Interdisciplinar para Sistemas de Informação I)** na **UFRPE**. O desenvolvimento focou na aplicação de conceitos de Engenharia de Software, persistência de dados, segurança da informação, Programação Orientada a Objetos e evolução incremental por releases.

**Desenvolvedores:** João Victor Macêdo e Wellison Cavalcante
**Instituição:** Universidade Federal Rural de Pernambuco (UFRPE)
**Curso:** Bacharelado em Sistemas de Informação

---

## 📊 Planilha de Features

A documentação das funcionalidades do projeto também está organizada em uma planilha, contendo as features planejadas, fluxos principais, fluxos alternativos, fluxos de erro, status de desenvolvimento, prioridade e escopo de entrega.

🔗 **Acesse a planilha de features aqui:**
[Planilha de Features do Projeto](https://docs.google.com/spreadsheets/d/1Aaw829HiQKvhQ1wD777NaCNEmsDNXbLNe9va6_c-bOA/edit?gid=1939892147#gid=1939892147)
