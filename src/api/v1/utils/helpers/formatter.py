import re
from typing import ClassVar


class Formatter:
    _cnpj_pattern: ClassVar[str] = (
        r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$"  # 11.111.111/1111-11
    )
    _cpf_pattern: ClassVar[str] = r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$"  # 111.111.111-11
    _cell_pattern: ClassVar[str] = (
        r"^\(\d{2}\) \d{4,5}-\d{4}$"  # (11) 1111-1111 or (11) 11111-1111
    )
    _cep_pattern: ClassVar[str] = r"^\d{5}-\d{3}$"  # 11111-111

    # 111.111.111-11 -> 11111111111
    @staticmethod
    def _only_digits(string: str) -> str:
        return re.sub(r"\D", "", string)

    # 11111111111 -> 111.111.111-11
    @classmethod
    def cpf(cls, cpf: str) -> str:
        if re.fullmatch(cls._cpf_pattern, cpf):
            return cpf

        cpf_limpo = cls._only_digits(string=cpf)
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve ter 11 dígitos")

        cpf_formatado = (
            f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        )
        return cpf_formatado

    # 11111111111111 -> 11.111.111/1111-11
    @classmethod
    def cnpj(cls, cnpj: str) -> str:
        if re.fullmatch(cls._cnpj_pattern, cnpj):
            return cnpj

        cnpj_limpo = cls._only_digits(string=cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos")

        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        return cnpj_formatado

    # 11111111111 -> 111.111.111-11
    # 11111111111111 -> 11.111.111/1111-11
    @classmethod
    def cnpj_cpf(cls, cnpj_cpf: str) -> str:
        cnpj_cpf_limpo = cls._only_digits(string=cnpj_cpf)

        tamanho = len(cnpj_cpf_limpo)

        if tamanho == 11:
            if re.fullmatch(cls._cpf_pattern, cnpj_cpf):
                return cnpj_cpf
            return cls.cpf(cnpj_cpf_limpo)
        elif tamanho == 14:
            if re.fullmatch(cls._cnpj_pattern, cnpj_cpf):
                return cnpj_cpf
            return cls.cnpj(cnpj_cpf_limpo)
        else:
            raise ValueError(
                "CNPJ/CPF inválido. Deve ter 11 (CPF) ou 14 (CNPJ) dígitos"
            )

    # 1111111111 -> (11) 1111-1111
    # 1111111111 -> (11) 11111-1111
    @classmethod
    def cell(cls, cell: str) -> str:
        cell_limpo = cls._only_digits(string=cell)

        if re.fullmatch(cls._cell_pattern, cell):
            return cell

        if len(cell_limpo) not in (10, 11):
            raise ValueError(
                "Celular deve ter 10 (sem nono dígito) ou 11 dígitos (com nono dígito)"
            )

        ddd = cell_limpo[:2]
        numero = cell_limpo[2:]
        if len(numero) == 8:
            parte1 = numero[:4]
            parte2 = numero[4:]
            return f"({ddd}) {parte1}-{parte2}"
        else:
            parte1 = numero[:5]
            parte2 = numero[5:]
            return f"({ddd}) {parte1}-{parte2}"

    # 11111111 -> 11111-11
    @classmethod
    def cep(cls, cep: str) -> str:
        if re.fullmatch(cls._cep_pattern, cep):
            return cep

        cep_limpo = cls._only_digits(string=cep)
        if len(cep_limpo) != 8:
            raise ValueError("CEP deve ter 8 dígitos")

        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep_formatado

    @staticmethod
    # YYYY-MM-DD -> DD/MM/AAAA
    def data(data: str) -> str:
        FORMATO_BR = r"(\d{2})\/(\d{2})\/(\d{4})"
        FORMATO_ISO = r"(\d{4})-(\d{2})-(\d{2})"

        # Se já está no formato desejado, não faz nada
        if re.match(FORMATO_BR, data):
            return data

        # Se não estiver, converte
        return re.sub(FORMATO_ISO, r"\3/\2/\1", data)

    # " str  \ning\\ " -> "String."
    @staticmethod
    def sanitize(string: str) -> str:
        # Remove espaços do início e fim
        l1 = string.strip()
        # Remove barras invertidas
        l2 = l1.replace("\\", "")
        # Remove quebras de linha
        l3 = l2.replace("\n", "")
        # Substítui dois ou mais espaços do meio por um
        l4 = re.sub(pattern=r"\s{2,}", repl=" ", string=l3)
        # Adiciona ponto no fim
        l5 = l4 + "." if not l4.endswith(".") else l4
        # Capitaliza
        l6 = l5.capitalize()
        return l6
