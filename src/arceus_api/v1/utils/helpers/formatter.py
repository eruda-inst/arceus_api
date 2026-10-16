"""
Utility class for formatting and sanitizing strings (CPF, CNPJ, phone, CEP, dates).
"""

import re
from typing import ClassVar


class Formatter:
    """
    Provides static/class methods to format and sanitize common Brazilian
    documents and data (CPF, CNPJ, cellphone, CEP, dates) and to sanitize
    arbitrary strings.
    """

    _cnpj_pattern: ClassVar[str] = r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$"
    _cpf_pattern: ClassVar[str] = r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$"
    _cell_pattern: ClassVar[str] = r"^\(\d{2}\) \d{4,5}-\d{4}$"
    _cep_pattern: ClassVar[str] = r"^\d{5}-\d{3}$"

    @staticmethod
    def _only_digits(string: str) -> str:
        """
        Remove all non-digit characters from a string.

        Args:
            string: Input string.

        Returns:
            String containing only digits.
        """
        return re.sub(r"\D", "", string)

    @classmethod
    def cpf(cls, cpf: str) -> str:
        """
        Format a CPF string to the standard pattern (XXX.XXX.XXX-XX).

        Args:
            cpf: CPF string, with or without formatting.

        Returns:
            Formatted CPF string.

        Raises:
            ValueError: If the CPF does not have exactly 11 digits.
        """
        if re.fullmatch(cls._cpf_pattern, cpf):
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
        """
        Format a CNPJ string to the standard pattern (XX.XXX.XXX/XXXX-XX).

        Args:
            cnpj: CNPJ string, with or without formatting.

        Returns:
            Formatted CNPJ string.

        Raises:
            ValueError: If the CNPJ does not have exactly 14 digits.
        """
        if re.fullmatch(cls._cnpj_pattern, cnpj):
            return cnpj

        cnpj_limpo = cls._only_digits(string=cnpj)
        if len(cnpj_limpo) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos")

        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        return cnpj_formatado

    @classmethod
    def cnpj_cpf(cls, cnpj_cpf: str) -> str:
        """
        Format a CNPJ or CPF string based on its length.

        Args:
            cnpj_cpf: CNPJ or CPF string, with or without formatting.

        Returns:
            Formatted CNPJ or CPF string.

        Raises:
            ValueError: If the string is neither a valid CPF (11 digits) nor
                a valid CNPJ (14 digits).
        """
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

    @classmethod
    def cell(cls, cell: str) -> str:
        """
        Format a cellphone number to the standard pattern ((XX) XXXXX-XXXX).

        Accepts 10 or 11 digits (with or without the ninth digit).

        Args:
            cell: Cellphone number string.

        Returns:
            Formatted cellphone string.

        Raises:
            ValueError: If the number does not have 10 or 11 digits.
        """
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

    @classmethod
    def cep(cls, cep: str) -> str:
        """
        Format a CEP (postal code) to the standard pattern (XXXXX-XXX).

        Args:
            cep: CEP string, with or without formatting.

        Returns:
            Formatted CEP string.

        Raises:
            ValueError: If the CEP does not have exactly 8 digits.
        """
        if re.fullmatch(cls._cep_pattern, cep):
            return cep

        cep_limpo = cls._only_digits(string=cep)
        if len(cep_limpo) != 8:
            raise ValueError("CEP deve ter 8 dígitos")

        cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep_formatado

    @staticmethod
    def date(date: str) -> str:
        """
        Convert a date string from ISO format (YYYY-MM-DD) to Brazilian format (DD/MM/YYYY).

        If the input is already in Brazilian format, it is returned unchanged.

        Args:
            date: Date string in ISO or Brazilian format.

        Returns:
            Date string in Brazilian format (DD/MM/YYYY).
        """
        FORMATO_BR = r"(\d{2})\/(\d{2})\/(\d{4})"
        FORMATO_ISO = r"(\d{4})-(\d{2})-(\d{2})"

        if re.match(FORMATO_BR, date):
            return date

        return re.sub(FORMATO_ISO, r"\3/\2/\1", date)

    @staticmethod
    def sanitize(string: str) -> str:
        """
        Sanitize a string by trimming, removing backslashes and newlines,
        collapsing multiple spaces, ensuring it ends with a period, and
        capitalizing the first letter.

        Args:
            string: The string to sanitize.

        Returns:
            The sanitized string.
        """
        l1 = string.strip()
        l2 = l1.replace("\\", "")
        l3 = l2.replace("\n", "")
        l4 = re.sub(pattern=r"\s{2,}", repl=" ", string=l3)
        l5 = l4 + "." if not l4.endswith(".") else l4
        l6 = l5.capitalize()
        return l6
