import re


class Formatter:
    CNPJ_PATTERN = r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$"
    CPF_PATTERN = r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$"
    CELL_PATTERN = r"^\(\d{2}\) \d{4,5}-\d{4}$"
    CEP_PATTERN = r"^\d{5}-\d{3}$"

    @staticmethod
    def only_digits(string: str) -> str:
        return re.sub(r"\D", "", string)

    @classmethod
    def cpf(cls, cpf: str) -> str:
        if re.fullmatch(cls.CPF_PATTERN, cpf):
            return cpf

        cpf_limpo = cls.only_digits(string=cpf)
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve ter 11 dígitos.")

        cpf_formatado = (
            f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        )
        return cpf_formatado

    @classmethod
    def cnpj(cls, cnpj: str) -> str:
        if re.fullmatch(cls.CNPJ_PATTERN, cnpj):
            return cnpj

        cnpj_limpo = cls.only_digits(string=cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos.")

        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        return cnpj_formatado

    @classmethod
    def cnpj_cpf(cls, cnpj_cpf: str) -> str:
        cnpj_cpf_limpo = cls.only_digits(string=cnpj_cpf)

        tamanho = len(cnpj_cpf_limpo)

        if tamanho == 11:
            if re.fullmatch(cls.CPF_PATTERN, cnpj_cpf):
                return cnpj_cpf
            return cls.cpf(cnpj_cpf_limpo)
        elif tamanho == 14:
            if re.fullmatch(cls.CNPJ_PATTERN, cnpj_cpf):
                return cnpj_cpf
            return cls.cnpj(cnpj_cpf_limpo)
        else:
            raise ValueError(
                "CNPJ/CPF inválido. Deve ter 11 (CPF) ou 14 (CNPJ) dígitos."
            )

    @classmethod
    def cell(cls, cell: str) -> str:
        cell_limpo = cls.only_digits(string=cell)

        if re.fullmatch(cls.CELL_PATTERN, cell):
            return cell

        if len(cell_limpo) not in (10, 11):
            raise ValueError(
                "Celular deve ter 10 (sem nono dígito) ou 11 dígitos (com nono dígito)."
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
        if re.fullmatch(cls.CEP_PATTERN, cep):
            return cep

        cep_limpo = cls.only_digits(string=cep)
        if len(cep_limpo) != 8:
            raise ValueError("CEP deve ter 8 dígitos.")

        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep_formatado

    @staticmethod
    # De YYYY-MM-DD para DD/MM/AAAA
    def data(data: str) -> str:
        FORMATO_BR = r"(\d{2})\/(\d{2})\/(\d{4})"
        FORMATO_ISO = r"(\d{4})-(\d{2})-(\d{2})"

        # Se já está no formato desejado, não faz nada
        if re.match(FORMATO_BR, data):
            return data

        # Se não estiver, converte
        return re.sub(FORMATO_ISO, r"\3/\2/\1", data)
