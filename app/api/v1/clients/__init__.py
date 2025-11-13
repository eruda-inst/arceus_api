from app.api.v1.core import settings
from app.api.v1.utils import SortOrder
from app.api.v1.schemas import AtendimentoIn
from .comercial import ComercialIXCCliente
from .suporte import SuporteIXCCliente
from .financeiro import FinanceiroIXCCliente, FinanceiroAZ7Cliente
from .ixc import IXCCliente
from .opa import OpaCliente
from .triagem import TriagemIXCCliente
from .cobranca import CobrancaIXCCliente
