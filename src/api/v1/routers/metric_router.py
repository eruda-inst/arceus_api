from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import NonNegativeInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db, deps, models, schemas, utils

metric_router = APIRouter(prefix="/metricas", tags=["Métricas"])

db_dep = Annotated[AsyncSession, Depends(db.get_db)]
current_user_dep = Annotated[models.User, Depends(deps.get_curr_user)]
read_metric_perm_dep = Annotated[
    models.User, Depends(deps.has_perm(utils.PermCodes.READ_METRIC))
]


@metric_router.get(path="/total-requisicoes", summary="Obtém o total de requisições")
async def get_total_reqs(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[NonNegativeInt]:
    """
    Obtém o total de requisições de hoje e sempre
    """
    return await cruds.MetricCrud.get_total_reqs(db=db)


@metric_router.get(path="/total-atendimentos", summary="Obtém o total de atendimentos")
async def get_total_services(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[NonNegativeInt]:
    """
    Obtém o total de atendimentos de hoje e sempre
    """
    return await cruds.MetricCrud.get_total_services(db=db)


@metric_router.get(
    path="/top-endpoints", summary="Obtém os 10 endpoints mais acessados"
)
async def get_top_endpoints(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopEndpoint]]:
    """
    Obtém os 10 endpoints mais acessados de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_endpoints(db=db)


@metric_router.get(
    path="/top-status-codes", summary="Obtém os 10 status codes mais recebidos"
)
async def get_top_status_codes(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopStatusCode]]:
    """
    Obtém os 10 status codes mais recebidos de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_status_codes(db=db)


@metric_router.get(
    path="/top-horas", summary="Obtém as 10 horas de maior pico de acessos"
)
async def get_top_hours(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopHour]]:
    """
    Obtém as 10 horas de maior pico de acessos de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_hours(db=db)


@metric_router.get(
    path="/top-dias-semana",
    summary="Obtém os dias da semana de maior pico de acessos",
)
async def get_top_weekdays(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopWeekday]]:
    """
    Obtém os dias da semana de maior pico de acessos de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_weekdays(db=db)


@metric_router.get(
    path="/top-piores-endpoints", summary="Obtém os 10 endpoints com mais erros"
)
async def get_worst_endpoints(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopWorstEndpoint]]:
    """
    Obtém os 10 endpoints com mais erros de hoje e sempre
    """
    return await cruds.MetricCrud.get_worst_endpoints(db=db)


@metric_router.get(
    path="/top-dias-mes", summary="Obtém os 10 dias do mês com mais requisições"
)
async def get_top_month_days(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopMonthDay]]:
    """
    Obtém os 10 dias do mês com maior número de requisições no mês atual e em todo o período
    """
    return await cruds.MetricCrud.get_top_month_days(db=db)


@metric_router.get(
    path="/top-endpoints-mais-lentos", summary="Obtém os 10 endpoints mais lentos"
)
async def get_top_slowest_endpoints(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopSlowestEndpoint]]:
    """
    Obtém os 10 endpoints mais lentos de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_slowest_endpoints(db=db)


@metric_router.get(
    path="/top-metodos-http", summary="Obtém os métodos HTTP mais utilizados"
)
async def get_top_http_methods(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopHttpMethod]]:
    """
    Obtém os métodos HTTP mais utilizados de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_http_methods(db=db)


@metric_router.get(path="/top-setores", summary="Obtém os setores mais utilizados")
async def get_top_departments(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[list[schemas.TopDepartment]]:
    """
    Obtém os setores mais utilizados de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_departments(db=db)


@metric_router.get(
    path="/sucessos", summary="Obtém total e percentual de sucessos (hoje/sempre)"
)
async def get_success_stats(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[schemas.SuccessStats]:
    """
    Retorna, para hoje e para todo o histórico:
    - Total de requisições com sucesso (código 200-299)
    - Percentual de sucesso (0 a 100)
    """
    return await cruds.MetricCrud.get_success_stats(db=db)


@metric_router.get(
    path="/erros", summary="Obtém total e percentual de erros (hoje/sempre)"
)
async def get_error_stats(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[schemas.ErrorStats]:
    """
    Retorna, para hoje e para todo o histórico:
    - Total de requisições com erro (código 400-499 ou 500-599)
    - Percentual de erro (0 a 100)
    """
    return await cruds.MetricCrud.get_error_stats(db=db)


@metric_router.get(
    path="/tempo-resposta",
    summary="Obtém estatísticas de tempo de resposta (mínimo, média, máximo)",
)
async def get_res_time(
    db: db_dep, current_user: current_user_dep, perm: read_metric_perm_dep
) -> schemas.TodayAlwaysOut[schemas.ResponseTimeStats]:
    """
    Retorna, para hoje e para todo o histórico (entre requisições bem-sucedidas):
    - Tempo mínimo de resposta
    - Tempo médio de resposta
    - Tempo máximo de resposta
    """
    return await cruds.MetricCrud.get_res_time(db=db)


@metric_router.get(
    path="/top-clientes", summary="Obtém os 10 clientes que mais fizeram requisições"
)
async def get_top_clients(
    db: db_dep,
    current_user: current_user_dep,
    perm: read_metric_perm_dep,
) -> schemas.TodayAlwaysOut[list[schemas.TopClientName]]:
    """
    Obtém os 10 clientes que mais fizeram requisições de hoje e sempre
    """
    return await cruds.MetricCrud.get_top_clients(db=db)
