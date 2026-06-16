import re

CNPJ_PATTERN = r"^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$"
CPF_PATTERN = r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$"
CEL_PATTERN = r"^\(\d{2}\) \d{4,5}-\d{4}$"
CEP_PATTERN = r"^\d{5}-\d{3}$"


def limpar_string(string: str) -> str:
    return re.sub(r"\D", "", string)


def formatar_cpf(cpf: str) -> str:
    if re.fullmatch(CPF_PATTERN, cpf):
        return cpf

    cpf_limpo = re.sub(r"\D", "", cpf)
    if len(cpf_limpo) != 11:
        raise ValueError("CPF deve ter 11 dígitos.")

    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf_formatado


def formatar_cnpj(cnpj: str) -> str:
    if re.fullmatch(CNPJ_PATTERN, cnpj):
        return cnpj

    cnpj_limpo = re.sub(r"\D", "", cnpj)
    if len(cnpj_limpo) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos.")

    cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return cnpj_formatado


def formatar_cnpj_cpf(cnpj_cpf: str) -> str:
    cnpj_cpf_limpo = re.sub(r"\D", "", cnpj_cpf)

    tamanho = len(cnpj_cpf_limpo)

    if tamanho == 11:
        if re.fullmatch(CPF_PATTERN, cnpj_cpf):
            return cnpj_cpf
        return formatar_cpf(cnpj_cpf_limpo)
    elif tamanho == 14:
        if re.fullmatch(CNPJ_PATTERN, cnpj_cpf):
            return cnpj_cpf
        return formatar_cnpj(cnpj_cpf_limpo)
    else:
        raise ValueError("CNPJ/CPF inválido. Deve ter 11 (CPF) ou 14 (CNPJ) dígitos.")


def formatar_cel(cel: str) -> str:
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
    if re.fullmatch(CEP_PATTERN, cep):
        return cep

    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        raise ValueError("CEP deve ter 8 dígitos.")

    cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return cep_formatado


def formatar_data(data: str) -> str:
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", data):
        return data
    ano = data[:4]
    mes = data[5:7]
    dia = data[8:]
    return f"{dia}/{mes}/{ano}"
