from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date

class Transacao(ABC):

    @property
    @abstractmethod
    def valor(self) -> float:
        pass

    @abstractmethod
    def registrar(self, conta) -> None:
        pass


@dataclass(frozen=True)
class Deposito(Transacao):
    _valor: float

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta) -> None:
        if conta.depositar(self._valor):
            conta.historico.adicionar_transacao(self)


@dataclass(frozen=True)
class Saque(Transacao):
    _valor: float

    @property
    def valor(self) -> float:
        return self._valor

    def registrar(self, conta) -> None:
        if conta.sacar(self._valor):
            conta.historico.adicionar_transacao(self)


@dataclass
class Historico:
    _transacoes: list[dict] = field(default_factory=list)

    @property
    def transacoes(self) -> list[dict]:
        return self._transacoes

    def adicionar_transacao(self, transacao: Transacao) -> None:
        self._transacoes.append(
            {
                "tipo":  type(transacao).__name__,
                "valor": transacao.valor,
                "data":  datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )


class Conta:

    def __init__(self, numero: int, cliente) -> None:
        self._saldo:     float     = 0.0
        self._numero:    int       = numero
        self._agencia:   str       = "0001"
        self._cliente              = cliente
        self._historico: Historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero: int) -> "Conta":
        return cls(numero, cliente)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def agencia(self) -> str:
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self) -> Historico:
        return self._historico

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n⚠  Valor inválido para depósito.")
            return False
        self._saldo += valor
        print(f"\n✔  Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            print("\n⚠  Valor inválido para saque.")
            return False
        if valor > self._saldo:
            print("\n⚠  Saldo insuficiente.")
            return False
        self._saldo -= valor
        print(f"\n✔  Saque de R$ {valor:.2f} realizado com sucesso!")
        return True

    def __str__(self) -> str:
        return (
            f"  Agência:  {self._agencia}\n"
            f"  C/C:      {self._numero}\n"
            f"  Titular:  {self._cliente.nome}\n"
            f"  Saldo:    R$ {self._saldo:.2f}"
        )


class ContaCorrente(Conta):

    LIMITE_PADRAO:        float = 500.0
    LIMITE_SAQUES_PADRAO: int   = 3

    def __init__(
        self,
        numero:        int,
        cliente,
        limite:        float = LIMITE_PADRAO,
        limite_saques: int   = LIMITE_SAQUES_PADRAO,
    ) -> None:
        super().__init__(numero, cliente)
        self._limite:        float = limite
        self._limite_saques: int   = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero: int) -> "ContaCorrente":
        return cls(numero, cliente)

    def sacar(self, valor: float) -> bool:
        saques_hoje = sum(
            1 for t in self.historico.transacoes if t["tipo"] == "Saque"
        )
        if valor > self._limite:
            print(f"\n⚠  Valor excede o limite por saque de R$ {self._limite:.2f}.")
            return False
        if saques_hoje >= self._limite_saques:
            print(f"\n⚠  Limite de {self._limite_saques} saques diários atingido.")
            return False
        return super().sacar(valor)

    def __str__(self) -> str:
        saques_hoje = sum(
            1 for t in self.historico.transacoes if t["tipo"] == "Saque"
        )
        return (
            super().__str__()
            + f"\n  Limite:   R$ {self._limite:.2f}"
            + f"\n  Saques restantes: {self._limite_saques - saques_hoje}"
        )


class Cliente:

    def __init__(self, endereco: str) -> None:
        self._endereco: str         = endereco
        self._contas:   list[Conta] = []

    @property
    def contas(self) -> list[Conta]:
        return self._contas

    @property
    def endereco(self) -> str:
        return self._endereco

    def realizar_transacao(self, conta: Conta, transacao: Transacao) -> None:
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta) -> None:
        self._contas.append(conta)


@dataclass
class PessoaFisica(Cliente):

    nome:            str
    cpf:             str
    data_nascimento: date
    _endereco_pf:    str   

    def __post_init__(self) -> None:
        super().__init__(self._endereco_pf)

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        numeros = cpf.replace(".", "").replace("-", "").strip()
        return len(numeros) == 11 and numeros.isdigit()

    def __str__(self) -> str:
        return f"{self.nome} — CPF: {self.cpf}"


# ─────────────────────────────────────────────────────────────
#  MENU / INTERFACE TERMINAL
# ─────────────────────────────────────────────────────────────

def menu() -> str:
    print("""
╔══════════════════════════════╗
║       BANCO PYTHON           ║
╠══════════════════════════════╣
║  [d]  Depositar              ║
║  [s]  Sacar                  ║
║  [e]  Extrato                ║
║  [nc] Nova conta             ║
║  [lc] Listar contas          ║
║  [nu] Novo usuário           ║
║  [q]  Sair                   ║
╚══════════════════════════════╝""")
    return input("  Opção: ").strip().lower()


def _buscar_cliente(cpf: str, clientes: list) -> Cliente | None:
    resultado = [c for c in clientes if c.cpf == cpf]
    return resultado[0] if resultado else None


def _selecionar_conta(cliente: Cliente) -> Conta | None:
    if not cliente.contas:
        print("\n⚠  Cliente sem contas cadastradas.")
        return None
    if len(cliente.contas) == 1:
        return cliente.contas[0]
    print("\n  Contas disponíveis:")
    for i, c in enumerate(cliente.contas):
        print(f"  [{i}] Ag: {c.agencia}  C/C: {c.numero}")
    try:
        idx = int(input("  Número da conta: "))
        return cliente.contas[idx]
    except (ValueError, IndexError):
        print("\n⚠  Opção inválida.")
        return None


def op_depositar(clientes: list) -> None:
    cpf = input("  CPF do cliente: ").strip()
    cliente = _buscar_cliente(cpf, clientes)
    if not cliente:
        print("\n⚠  Cliente não encontrado.")
        return
    conta = _selecionar_conta(cliente)
    if not conta:
        return
    try:
        valor = float(input("  Valor do depósito: R$ "))
    except ValueError:
        print("\n⚠  Valor inválido.")
        return
    cliente.realizar_transacao(conta, Deposito(valor))


def op_sacar(clientes: list) -> None:
    cpf = input("  CPF do cliente: ").strip()
    cliente = _buscar_cliente(cpf, clientes)
    if not cliente:
        print("\n⚠  Cliente não encontrado.")
        return
    conta = _selecionar_conta(cliente)
    if not conta:
        return
    try:
        valor = float(input("  Valor do saque: R$ "))
    except ValueError:
        print("\n⚠  Valor inválido.")
        return
    cliente.realizar_transacao(conta, Saque(valor))


def op_extrato(clientes: list) -> None:
    cpf = input("  CPF do cliente: ").strip()
    cliente = _buscar_cliente(cpf, clientes)
    if not cliente:
        print("\n⚠  Cliente não encontrado.")
        return
    conta = _selecionar_conta(cliente)
    if not conta:
        return
    print("\n" + "=" * 44)
    print("                 EXTRATO")
    print("=" * 44)
    transacoes = conta.historico.transacoes
    if not transacoes:
        print("  Nenhuma movimentação registrada.")
    else:
        for t in transacoes:
            sinal = "+" if t["tipo"] == "Deposito" else "-"
            print(f"  {t['data']}  {t['tipo']:<10} {sinal} R$ {t['valor']:>9.2f}")
    print("-" * 44)
    print(f"  Saldo atual:               R$ {conta.saldo:>9.2f}")
    print("=" * 44)


def op_novo_cliente(clientes: list) -> None:
    cpf = input("  CPF (somente números): ").strip()
    if not PessoaFisica.validar_cpf(cpf):
        print("\n⚠  CPF inválido. Informe 11 dígitos.")
        return
    if _buscar_cliente(cpf, clientes):
        print("\n⚠  CPF já cadastrado.")
        return
    nome       = input("  Nome completo: ").strip()
    nascimento = input("  Data de nascimento (dd/mm/aaaa): ").strip()
    endereco   = input("  Endereço (logradouro, nº - bairro - cidade/UF): ").strip()
    try:
        data = datetime.strptime(nascimento, "%d/%m/%Y").date()
    except ValueError:
        print("\n⚠  Data inválida.")
        return
    cliente = PessoaFisica(
        nome=nome, cpf=cpf, data_nascimento=data, _endereco_pf=endereco
    )
    clientes.append(cliente)
    print(f"\n✔  Cliente {nome} cadastrado com sucesso!")


def op_nova_conta(numero: int, clientes: list, contas: list) -> int:
    cpf = input("  CPF do titular: ").strip()
    cliente = _buscar_cliente(cpf, clientes)
    if not cliente:
        print("\n⚠  Cliente não encontrado. Cadastre-o primeiro.")
        return numero
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero)
    cliente.adicionar_conta(conta)
    contas.append(conta)
    print(f"\n✔  Conta corrente nº {numero} criada com sucesso!")
    return numero + 1


def op_listar_contas(contas: list) -> None:
    if not contas:
        print("\n  Nenhuma conta cadastrada.")
        return
    print("\n" + "=" * 44)
    for conta in contas:
        print(str(conta))
        print("-" * 44)


def main() -> None:
    clientes:     list[Cliente] = []
    contas:       list[Conta]   = []
    numero_conta: int           = 1

    opcoes = {
        "d":  lambda: op_depositar(clientes),
        "s":  lambda: op_sacar(clientes),
        "e":  lambda: op_extrato(clientes),
        "nu": lambda: op_novo_cliente(clientes),
        "lc": lambda: op_listar_contas(contas),
    }

    while True:
        opcao = menu()

        if opcao == "q":
            print("\n  Até logo!\n")
            break

        elif opcao == "nc":
            numero_conta = op_nova_conta(numero_conta, clientes, contas)

        elif opcao in opcoes:
            opcoes[opcao]()

        else:
            print("\n⚠  Opção inválida.")


if __name__ == "__main__":
    main()