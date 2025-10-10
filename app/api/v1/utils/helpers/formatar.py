import re

CNPJ_PATTERN = r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$"
CPF_PATTERN = r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$"
CEL_PATTERN = r"^\(\d{2}\) \d{4,5}-\d{4}$"
CEP_PATTERN = r"^\d{5}-\d{3}$"


def formatar_cpf(cpf: str) -> str:
    """
    Formata uma string de CPF, adicionando a pontuação padrão.

    Args:
        cpf: A string do CPF a ser formatada (pode conter ou não pontuação).

    Returns:
        O CPF formatado (ex: '123.456.789-00').

    Raises:
        ValueError: Se o CPF não contiver 11 dígitos após a limpeza.
    """
    if re.fullmatch(CPF_PATTERN, cpf):
        return cpf

    cpf_limpo = re.sub(r"\D", "", cpf)
    if len(cpf_limpo) != 11:
        raise ValueError("CPF deve ter 11 dígitos.")

    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf_formatado


def formatar_cnpj(cnpj: str) -> str:
    """
    Formata uma string de CNPJ, adicionando a pontuação padrão.

    Args:
        cnpj: A string do CNPJ a ser formatada (pode conter ou não pontuação).

    Returns:
        O CNPJ formatado (ex: '12.345.678/0001-90').

    Raises:
        ValueError: Se o CNPJ não contiver 14 dígitos após a limpeza.
    """
    if re.fullmatch(CNPJ_PATTERN, cnpj):
        return cnpj

    cnpj_limpo = re.sub(r"\D", "", cnpj)
    if len(cnpj_limpo) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos.")

    cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return cnpj_formatado


def formatar_cpf_ou_cnpj(cpf_ou_cnpj: str) -> str:
    """
    Formata uma string que pode ser um CPF ou CNPJ, aplicando a máscara correta.

    Args:
        cpf_ou_cnpj: A string do CPF ou CNPJ a ser formatada.

    Returns:
        O CPF ou CNPJ formatado.

    Raises:
        ValueError: Se a string não tiver 11 (CPF) ou 14 (CNPJ) dígitos.
    """
    cpf_ou_cnpj_limpo = re.sub(r"\D", "", cpf_ou_cnpj)

    tamanho = len(cpf_ou_cnpj_limpo)

    if tamanho == 11:
        if re.fullmatch(CPF_PATTERN, cpf_ou_cnpj):
            return cpf_ou_cnpj
        return formatar_cpf(cpf_ou_cnpj_limpo)
    elif tamanho == 14:
        if re.fullmatch(CNPJ_PATTERN, cpf_ou_cnpj):
            return cpf_ou_cnpj
        return formatar_cnpj(cpf_ou_cnpj_limpo)
    else:
        raise ValueError("CNPJ/CPF inválido. Deve ter 11 (CPF) ou 14 (CNPJ) dígitos.")


def formatar_cel(cel: str) -> str:
    """
    Formata um número de celular, adicionando parênteses no DDD e hífen.

    Args:
        cel: A string do celular a ser formatada.

    Returns:
        O celular formatado (ex: '(11) 98765-4321').

    Raises:
        ValueError: Se o número não tiver 10 ou 11 dígitos.
    """
    tel_limpo = re.sub(r"\D", "", cel)

    if re.fullmatch(r"^\(\d{2}\) \d{4,5}-\d{4}$", cel):
        return cel

    if len(tel_limpo) not in (10, 11):
        raise ValueError(
            "Celular deve ter 10 (sem nono dígito) ou 11 dígitos (com nono dígito)."
        )

    ddd = tel_limpo[:2]
    numero = tel_limpo[2:]
    if len(numero) == 8:
        parte1 = numero[:4]
        parte2 = numero[4:]
        return f"({ddd}) {parte1}-{parte2}"
    else:
        parte1 = numero[:5]
        parte2 = numero[5:]
        return f"({ddd}) {parte1}-{parte2}"


def formatar_cep(cep: str) -> str:
    """
    Formata uma string de CEP, adicionando o hífen.

    Args:
        cep: A string do CEP a ser formatada.

    Returns:
        O CEP formatado (ex: '12345-678').

    Raises:
        ValueError: Se o CEP não tiver 8 dígitos após a limpeza.
    """
    if re.fullmatch(CEP_PATTERN, cep):
        return cep

    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        raise ValueError("CEP deve ter 8 dígitos.")

    cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return cep_formatado
