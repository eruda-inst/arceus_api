import re
from typing import ClassVar


class Formatter:
    CNPJ_RE: ClassVar[re.Pattern[str]] = re.compile(
        pattern=r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$"
    )
    CPF_RE: ClassVar[re.Pattern[str]] = re.compile(
        pattern=r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$"
    )
    CELL_RE: ClassVar[re.Pattern[str]] = re.compile(
        pattern=r"^\(\d{2}\) \d{4,5}-\d{4}$"
    )
    CEP_RE: ClassVar[re.Pattern[str]] = re.compile(pattern=r"^\d{5}-\d{3}$")
    BRAZILIAN_DATE_RE: ClassVar[re.Pattern[str]] = re.compile(
        pattern=r"(\d{2})\/(\d{2})\/(\d{4})"
    )
    ISO_DATE_RE: ClassVar[re.Pattern[str]] = re.compile(
        pattern=r"(\d{4})-(\d{2})-(\d{2})"
    )

    @staticmethod
    def _only_digits(string: str) -> str:
        return re.sub(r"\D", "", string)

    @classmethod
    def cpf(cls, cpf: str) -> str:
        if cls.CPF_RE.fullmatch(string=cpf):
            return cpf

        cpf_limpo = cls._only_digits(string=cpf)
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve ter 11 dígitos")

        cpf_formatado = (
            f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        )
        return cpf_formatado

    @classmethod
    def cnpj(cls, cnpj: str) -> str:
        if cls.CNPJ_RE.fullmatch(string=cnpj):
            return cnpj

        cnpj_limpo = cls._only_digits(string=cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos")

        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        return cnpj_formatado

    @classmethod
    def cnpj_cpf(cls, cnpj_cpf: str) -> str:
        cnpj_cpf_limpo = cls._only_digits(string=cnpj_cpf)

        tamanho = len(cnpj_cpf_limpo)

        if tamanho == 11:
            if cls.CPF_RE.fullmatch(string=cnpj_cpf):
                return cnpj_cpf
            return cls.cpf(cnpj_cpf_limpo)
        elif tamanho == 14:
            if cls.CNPJ_RE.fullmatch(string=cnpj_cpf):
                return cnpj_cpf
            return cls.cnpj(cnpj_cpf_limpo)
        else:
            raise ValueError(
                "CNPJ/CPF inválido. Deve ter 11 (CPF) ou 14 (CNPJ) dígitos"
            )

    @classmethod
    def cell(cls, cell: str) -> str:
        cell_limpo = cls._only_digits(string=cell)

        if cls.CELL_RE.fullmatch(string=cell):
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

    @classmethod
    def cep(cls, cep: str) -> str:
        if cls.CEP_RE.fullmatch(string=cep):
            return cep

        cep_limpo = cls._only_digits(string=cep)
        if len(cep_limpo) != 8:
            raise ValueError("CEP deve ter 8 dígitos")

        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep_formatado

    @classmethod
    def date(cls, date: str) -> str:
        if cls.BRAZILIAN_DATE_RE.match(string=date):
            return date

        return re.sub(cls.ISO_DATE_RE.pattern, r"\3/\2/\1", date)

    @staticmethod
    def sanitize(string: str) -> str:
        l1 = string.strip()
        l2 = l1.replace("\\", "")
        l3 = l2.replace("\n", "")
        l4 = re.sub(pattern=r"\s{2,}", repl=" ", string=l3)
        l5 = l4 + "." if not l4.endswith(".") else l4
        l6 = l5.capitalize()

        return l6
