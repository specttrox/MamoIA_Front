# Registro de Correções Iniciais (Setup do Projeto)

## 1. Desativação Temporária do WeasyPrint

- **Arquivo:** `api_rest/views.py`
- **Problema:** Erro de `cannot load library 'libgobject-2.0-0'` ao iniciar o servidor ou rodar migrações, causado pela dependência do WeasyPrint que exige bibliotecas GTK3 nativas do sistema operacional.
- **Solução:** As importações e linhas de geração de PDF usando `weasyprint` foram comentadas temporariamente para permitir que a equipe de front-end rode o servidor e foque na integração visual e na limpeza dos templates.

## 2. Reset do Histórico de Migrations

- **Arquivos:** `api_rest/migrations/`
- **Problema:** Erro `table "api_rest_user" already exists`. O histórico de migrações original estava quebrado, com arquivos duplicando a criação de tabelas.
- **Solução:** As migrações corrompidas (`0001`, `0002`, `0003`) foram deletadas (mantendo apenas o `__init__.py`). Um novo `makemigrations` foi rodado para criar um histórico limpo a partir do zero (`0001_initial.py`).

## 3. Correção na Criação de Superusuário

- **Arquivo:** `api_rest/models.py`
- **Problema:** Erro `missing 1 required positional argument: 'nome'` ao tentar rodar `python manage.py createsuperuser`. O model customizado exigia um nome, mas o terminal não perguntava.
- **Solução:** Adicionado `REQUIRED_FIELDS = ['nome']` na classe `User` para garantir que o Django solicite os campos obrigatórios via linha de comando.
