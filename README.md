<h1 align="center">
<p align="center">Sistema REST para Cadastro e Login</p>
</h1>

<div align="center">
<img src="https://img.shields.io/badge/Python-3.10-success?style=for-the-badge">
<img src="https://img.shields.io/badge/FastAPI-0.78-informational?style=for-the-badge">
</div>

## Endpoints

 - `/login (POST)`: Recebe as credenciais de acesso (email e senha) e retorna um JWT para acesso do usuário na aplicação
 - `/signup (POST)`: Cadastra um novo usuário no banco de dados
 - `/forgot-my-password/<email> (POST)`: Envia um e-mail de redefinição de senha para o usuário caso o mesmo conste no banco de dados
 - `/password-reset (POST)`: Altera a senha de um usuário a partir de JWT enviado para o e-mail do mesmo
 - `/users (GET)`: Lista todos os usuários cadastrados na aplicação (requer login)
 - `/users/me (GET)`: Retorna o usuário atual caso o mesmo esteja autenticado (requer login)

## Tecnologias utilizadas

 - `Python 3.10`
 - `FastAPI 0.78`
 - `PostgreSQL 14.2`

## Rodando a aplicação localmente

### Crie um ambiente virtual

---

#### Windows:
Criando ambiente virtual

```sh
py -m venv .\env
```

Ativando ambiente virtual

```sh
env\Scripts\activate
```

---

#### macOS ou distribuições Linux:
Criando ambiente virtual

```sh
python3 -m venv env
```

Ativando ambiente virtual

```sh
source env/bin/activate
```

---

### Instalando dependências
````sh
pip install -r requirements.txt
````

---

### Configurações
1. Renomeie o arquivo `example.env` localizado na pasta raiz para `.env` e preencha as variáveis de acordo com sua necessidade.
2. `DATABASE_URL`: Insire o endereço do banco de dados que você deseja utilizar.
3. No seu terminal, com o ambiente virtual ativado, execute o comando `python -c "import secrets; print(secrets.token_hex(32))"` para gerar uma chave secreta.
4. `JWT_SECRET`: Coloque aqui a chave gerada no passo anterior.
6. `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER` e `SMTP_PASSWORD`: Preencha os dados referentes ao servidor SMTP de sua preferência, para a funcionalidade de envio de e-mails.

---

### Servidor de desenvolvimento

#### Execute o comando:

```sh
uvicorn app.main:app --reload
```

#### Você deverá ver a seguinte resposta no terminal:

```sh
INFO:     Will watch for changes in these directories: []
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [9532] using statreload
WARNING:  The --reload flag should not be used in production on Windows.
INFO:     Started server process [8060]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Caso tudo esteja certo, visite http://127.0.0.1:8000/ para acessar a aplicação