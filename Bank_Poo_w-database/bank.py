import sqlite3
from database.connection import get_connection, init_db
from models.account import Account
from models.customer import Customer
from models.plan import Plan
from models.transcation import Transaction


def header(title: str) -> None:
    print(f"\n{'═' * 48}")
    print(f"  {title}")
    print(f"{'═' * 48}")

def ok(msg: str)  -> None: print(f"  ✔  {msg}")
def err(msg: str) -> None: print(f"  ✘  {msg}")
def info(msg: str)-> None: print(f"  →  {msg}")

def ask(prompt: str) -> str:
    return input(f"  {prompt}: ").strip()

def ask_int(prompt: str) -> int | None:
    try:
        return int(ask(prompt))
    except ValueError:
        err("Valor inválido — digite um número inteiro.")
        return None

def ask_float(prompt: str) -> float | None:
    try:
        return float(ask(prompt))
    except ValueError:
        err("Valor inválido — digite um número.")
        return None

def pause() -> None:
    input("\n  [ Enter para continuar ]")

def print_rows(rows: list[sqlite3.Row], empty_msg: str = "Nenhum registro encontrado.") -> None:
    if not rows:
        info(empty_msg)
        return
    for row in rows:
        print("  " + "  |  ".join(f"{k}: {row[k]}" for k in row.keys()))

# ── Menus ─────────────────────────────────────────────────────────────────────

def menu_planos(conn: sqlite3.Connection) -> None:
    plan = Plan(conn)
    while True:
        header("PLANOS")
        print("  1  Listar planos")
        print("  2  Criar plano")
        print("  0  Voltar")
        op = ask("Opção")

        if op == "1":
            header("Lista de Planos")
            print_rows(plan.get_all())

        elif op == "2":
            header("Novo Plano")
            name         = ask("Nome")
            description  = ask("Descrição (opcional)")
            credit_limit = ask_float("Limite de crédito")
            if credit_limit is None:
                continue
            if plan.create(name, description, credit_limit):
                ok("Plano criado com sucesso.")
            else:
                err("Não foi possível criar o plano.")

        elif op == "0":
            break

        pause()


def menu_clientes(conn: sqlite3.Connection) -> None:
    customer = Customer(conn)
    plan     = Plan(conn)
    while True:
        header("CLIENTES")
        print("  1  Listar clientes")
        print("  2  Buscar por ID")
        print("  3  Criar cliente")
        print("  4  Alterar email")
        print("  5  Deletar cliente")
        print("  0  Voltar")
        op = ask("Opção")

        if op == "1":
            header("Lista de Clientes")
            print_rows(customer.get_all())

        elif op == "2":
            cid = ask_int("ID do cliente")
            if cid is None:
                continue
            row = customer.get_by_id(cid)
            if row:
                header(f"Cliente #{cid}")
                print_rows([row])
            else:
                err("Cliente não encontrado.")

        elif op == "3":
            header("Novo Cliente")
            planos = plan.get_all()
            if not planos:
                err("Nenhum plano cadastrado. Crie um plano primeiro.")
                pause()
                continue
            info("Planos disponíveis:")
            print_rows(planos)
            name     = ask("Nome")
            email    = ask("Email")
            cpf      = ask("CPF")
            plan_id  = ask_int("ID do plano")
            if plan_id is None:
                continue
            if customer.create(name, email, cpf, plan_id):
                ok("Cliente criado com sucesso.")
            else:
                err("Não foi possível criar o cliente.")

        elif op == "4":
            cid = ask_int("ID do cliente")
            if cid is None:
                continue
            new_email = ask("Novo email")
            if customer.change_email(cid, new_email):
                ok("Email atualizado.")
            else:
                err("Não foi possível atualizar o email.")

        elif op == "5":
            cid = ask_int("ID do cliente")
            if cid is None:
                continue
            confirm = ask(f"Confirma exclusão do cliente {cid}? (s/N)")
            if confirm.lower() == "s":
                if customer.delete(cid):
                    ok("Cliente deletado (contas vinculadas também foram removidas).")
                else:
                    err("Cliente não encontrado.")

        elif op == "0":
            break

        pause()


def menu_contas(conn: sqlite3.Connection) -> None:
    account  = Account(conn)
    customer = Customer(conn)
    while True:
        header("CONTAS")
        print("  1  Listar contas")
        print("  2  Buscar por ID")
        print("  3  Contas de um cliente")
        print("  4  Criar conta")
        print("  5  Deletar conta")
        print("  0  Voltar")
        op = ask("Opção")

        if op == "1":
            header("Lista de Contas")
            print_rows(account.get_all())

        elif op == "2":
            aid = ask_int("ID da conta")
            if aid is None:
                continue
            row = account.get_by_id(aid)
            if row:
                header(f"Conta #{aid}")
                print_rows([row])
            else:
                err("Conta não encontrada.")

        elif op == "3":
            cid = ask_int("ID do cliente")
            if cid is None:
                continue
            rows = account.get_by_customer(cid)
            header(f"Contas do cliente #{cid}")
            print_rows(rows, "Nenhuma conta vinculada a este cliente.")

        elif op == "4":
            header("Nova Conta")
            clientes = customer.get_all()
            if not clientes:
                err("Nenhum cliente cadastrado. Crie um cliente primeiro.")
                pause()
                continue
            info("Clientes disponíveis:")
            print_rows(clientes)
            cid     = ask_int("ID do cliente")
            if cid is None:
                continue
            print("  1  checking  (corrente)")
            print("  2  savings   (poupança)")
            tipo_op = ask("Tipo de conta (1 ou 2)")
            if tipo_op == "1":
                type_ = "checking"
            elif tipo_op == "2":
                type_ = "savings"
            else:
                err("Opção inválida. Digite 1 ou 2.")
                continue
            balance = ask_float("Saldo inicial (0 para nenhum)")
            if balance is None:
                continue
            if account.create(cid, type_, balance):
                ok("Conta criada com sucesso.")
            else:
                err("Não foi possível criar a conta.")

        elif op == "5":
            aid = ask_int("ID da conta")
            if aid is None:
                continue
            confirm = ask(f"Confirma exclusão da conta {aid}? (s/N)")
            if confirm.lower() == "s":
                if account.delete(aid):
                    ok("Conta deletada.")
                else:
                    err("Conta não encontrada.")

        elif op == "0":
            break

        pause()


def menu_transacoes(conn: sqlite3.Connection) -> None:
    transaction = Transaction(conn)
    account     = Account(conn)
    while True:
        header("TRANSAÇÕES")
        print("  1  Depósito")
        print("  2  Saque")
        print("  3  Transferência")
        print("  4  Extrato de uma conta")
        print("  5  Todas as transações")
        print("  0  Voltar")
        op = ask("Opção")

        if op == "1":
            header("Depósito")
            aid    = ask_int("ID da conta")
            if aid is None: continue
            amount = ask_float("Valor")
            if amount is None: continue
            if transaction.deposit(aid, amount):
                row = account.get_by_id(aid)
                ok(f"Depósito realizado. Saldo atual: R$ {row['balance']:.2f}")
            else:
                err("Depósito não realizado.")

        elif op == "2":
            header("Saque")
            aid    = ask_int("ID da conta")
            if aid is None: continue
            amount = ask_float("Valor")
            if amount is None: continue
            if transaction.withdraw(aid, amount):
                row = account.get_by_id(aid)
                ok(f"Saque realizado. Saldo atual: R$ {row['balance']:.2f}")
            else:
                err("Saque não realizado.")

        elif op == "3":
            header("Transferência")
            from_id = ask_int("ID da conta de origem")
            if from_id is None: continue
            to_id   = ask_int("ID da conta de destino")
            if to_id is None: continue
            amount  = ask_float("Valor")
            if amount is None: continue
            if transaction.transfer(from_id, to_id, amount):
                origem  = account.get_by_id(from_id)
                destino = account.get_by_id(to_id)
                ok(f"Transferência realizada.")
                info(f"Conta {from_id} → saldo: R$ {origem['balance']:.2f}")
                info(f"Conta {to_id}   → saldo: R$ {destino['balance']:.2f}")
            else:
                err("Transferência não realizada.")

        elif op == "4":
            aid = ask_int("ID da conta")
            if aid is None: continue
            rows = transaction.get_by_account(aid)
            header(f"Extrato da conta #{aid}")
            print_rows(rows, "Nenhuma transação encontrada.")

        elif op == "5":
            header("Todas as Transações")
            print_rows(transaction.get_all())

        elif op == "0":
            break

        pause()


# ── Menu principal ────────────────────────────────────────────────────────────

def main() -> None:
    init_db()
    conn = get_connection()

    while True:
        header("BANCO PyBank  —  Menu Principal")
        print("  1  Planos")
        print("  2  Clientes")
        print("  3  Contas")
        print("  4  Transações")
        print("  0  Sair")
        op = ask("Opção")

        if   op == "1": menu_planos(conn)
        elif op == "2": menu_clientes(conn)
        elif op == "3": menu_contas(conn)
        elif op == "4": menu_transacoes(conn)
        elif op == "0":
            print("\n  Até logo!\n")
            conn.close()
            break
        else:
            err("Opção inválida.")
            pause()


if __name__ == "__main__":
    main()