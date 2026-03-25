# Bank_Poo - Sistema Bancário com POO

Projeto de desafio da [DIO.me](https://www.dio.me/) para praticar **Programação Orientada a Objetos (POO)** em Python, implementando um sistema bancário completo em duas versões: uma simples em memória e uma avançada com persistência em banco de dados SQLite.

---

## Estrutura do Projeto

```
Bank_Poo/
├── desafio_sistema_bancario.py        # Versão simples (em memória)
│
└── Bank_Poo_w-database/               # Versão com banco de dados
    ├── bank.py                        # Aplicação principal (menus CLI)
    │
    ├── database/
    │   ├── connection.py              # Conexão e schema do banco
    │   └── bank_database.db          # Banco SQLite (gerado na 1ª execução)
    │
    └── models/
        ├── plan.py                    # DAO de Planos
        ├── customer.py               # DAO de Clientes
        ├── account.py                # DAO de Contas
        └── transcation.py            # DAO de Transações
```

---

## Versão 1 — Sistema em Memória (`desafio_sistema_bancario.py`)

Implementação simples com classes abstratas, herança e dataclasses. Os dados existem apenas enquanto a aplicação está em execução.

### Hierarquia de Classes

```
Transacao (ABC)
├── Deposito (frozen dataclass)
└── Saque    (frozen dataclass)

Cliente
└── PessoaFisica (dataclass)

Conta
└── ContaCorrente

Historico
```

### Classes Principais

| Classe | Descrição |
|--------|-----------|
| `Transacao` | Classe abstrata base para todas as transações |
| `Deposito` | Transação de depósito (imutável via `frozen dataclass`) |
| `Saque` | Transação de saque (imutável via `frozen dataclass`) |
| `Historico` | Armazena o histórico de transações com tipo, valor e timestamp |
| `Conta` | Conta bancária base com saldo, número e agência |
| `ContaCorrente` | Conta corrente com limite por saque (R$ 500) e limite diário (3 saques) |
| `Cliente` | Classe base de cliente com lista de contas |
| `PessoaFisica` | Cliente pessoa física com nome, CPF e data de nascimento |

### Menu de Operações

```
[d]  Depositar
[s]  Sacar
[e]  Extrato
[nc] Nova conta
[lc] Listar contas
[nu] Novo usuário
[q]  Sair
```

### Como Executar

```bash
python desafio_sistema_bancario.py
```

---

## Versão 2 — Sistema com Banco de Dados (`Bank_Poo_w-database/`)

Implementação completa com persistência em SQLite, usando o padrão **DAO (Data Access Object)** e transações atômicas para operações financeiras.

### Schema do Banco de Dados

```sql
-- Planos de conta
plan (id, name UNIQUE, description, credit_limit DEFAULT 0.0)

-- Clientes
customer (id, name, email UNIQUE, cpf UNIQUE, plan_id FK→plan, created_at)

-- Contas bancárias
account (id, customer_id FK→customer, type CHECK('checking','savings'), balance, created_at)

-- Transações
bank_transaction (id, account_id FK→account, type CHECK('deposit','withdraw','transfer_in','transfer_out'), amount CHECK(>0), created_at)

-- View de histórico completo
history (JOIN de transactions + accounts + customers)
```

### Classes DAO

Todas herdam de `CursorSqlite` (injeção de dependência da conexão):

| Classe | Responsabilidade |
|--------|-----------------|
| `Plan` | CRUD de planos de conta |
| `Customer` | CRUD de clientes com validação de CPF e e-mail |
| `Account` | CRUD de contas corrente e poupança |
| `Transaction` | Depósito, saque e transferência com atomicidade |

### Funcionalidades da Versão 2

**Planos**
- Listar todos os planos
- Criar novo plano com limite de crédito

**Clientes**
- Listar / buscar por ID
- Criar com vinculação a um plano
- Atualizar e-mail
- Deletar (cascata nas contas)

**Contas**
- Listar / buscar por ID ou CPF
- Criar conta corrente ou poupança
- Deletar conta

**Transações**
- Depósito
- Saque (valida saldo suficiente)
- Transferência entre contas (atômica)
- Extrato por conta
- Histórico completo

### Como Executar

```bash
cd Bank_Poo_w-database
python bank.py
```

O banco de dados é criado automaticamente na primeira execução.

---

## Conceitos de POO Aplicados

| Conceito | Onde é aplicado |
|----------|----------------|
| **Abstração** | Classe `Transacao` (ABC) com método abstrato `registrar()` |
| **Herança** | `ContaCorrente → Conta`, `PessoaFisica → Cliente`, `Deposito/Saque → Transacao` |
| **Encapsulamento** | Atributos privados com `_` e acesso via `@property` |
| **Polimorfismo** | `sacar()` com comportamento diferente em `Conta` e `ContaCorrente` |
| **Dataclasses** | `Deposito`, `Saque` e `PessoaFisica` com `@dataclass` |
| **Imutabilidade** | `Deposito` e `Saque` com `frozen=True` |
| **Injeção de Dependência** | `CursorSqlite` recebe conexão do banco externamente |
| **DAO Pattern** | Separação entre lógica de negócio e acesso a dados |

---

## Tecnologias Utilizadas

- **Python 3.10+**
- **sqlite3** — banco de dados embutido (standard library)
- **abc** — classes abstratas (standard library)
- **dataclasses** — declaração simplificada de classes (standard library)
- **datetime** — timestamps de transações (standard library)
- **pathlib** — manipulação de caminhos (standard library)

Nenhuma dependência externa — apenas a biblioteca padrão do Python.

---

## Regras de Negócio

- CPF deve ter exatamente 11 dígitos
- E-mail e CPF são únicos por cliente
- Tipo de conta: `checking` (corrente) ou `savings` (poupança)
- Saldo nunca pode ser negativo
- Valor de transação deve ser maior que zero
- Não é possível deletar um plano enquanto houver clientes vinculados
- Deletar um cliente remove suas contas em cascata
- Transferências são atômicas: debitam e creditam no mesmo commit

---

## Origem do Projeto

Desafio do bootcamp **Python Back-End** da [DIO.me](https://www.dio.me/), focado em Programação Orientada a Objetos com Python.
