from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from pydantic import NonNegativeInt
from sqlalchemy import case, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models, schemas


class MetricCrud:
    @staticmethod
    async def get_total_reqs(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[NonNegativeInt]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(func.count())
                .select_from(models.Log)
                .where(func.date(models.Log.criado_em) == today)
            )
            hoje_count = (await db.execute(stmt_today)).scalar_one_or_none() or 0

            stmt_always = select(func.count()).select_from(models.Log)
            always_count = (await db.execute(stmt_always)).scalar_one_or_none() or 0

            return schemas.TodayAlwaysOut[NonNegativeInt](
                hoje=hoje_count, sempre=always_count
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_res_time(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[schemas.ResponseTimeStats]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            success_filter = models.Log.codigo.between(200, 299)

            stmt_today = select(
                func.min(models.Log.duracao).label("min"),
                func.avg(models.Log.duracao).label("avg"),
                func.max(models.Log.duracao).label("max"),
            ).where(
                func.date(models.Log.criado_em) == today,
                success_filter,
            )
            result_today = await db.execute(stmt_today)
            row_today = result_today.one()

            min_today = float(row_today.min) if row_today.min is not None else 0.0
            avg_today = float(row_today.avg) if row_today.avg is not None else 0.0
            max_today = float(row_today.max) if row_today.max is not None else 0.0

            stmt_always = select(
                func.min(models.Log.duracao).label("min"),
                func.avg(models.Log.duracao).label("avg"),
                func.max(models.Log.duracao).label("max"),
            ).where(success_filter)
            result_always = await db.execute(stmt_always)
            row_always = result_always.one()

            min_always = float(row_always.min) if row_always.min is not None else 0.0
            avg_always = float(row_always.avg) if row_always.avg is not None else 0.0
            max_always = float(row_always.max) if row_always.max is not None else 0.0

            return schemas.TodayAlwaysOut[schemas.ResponseTimeStats](
                hoje=schemas.ResponseTimeStats(
                    min=min_today, avg=avg_today, max=max_today
                ),
                sempre=schemas.ResponseTimeStats(
                    min=min_always, avg=avg_always, max=max_always
                ),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_total_services(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[NonNegativeInt]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(func.count(func.distinct(models.Log.protocolo)))
                .select_from(models.Log)
                .where(
                    func.date(models.Log.criado_em) == today,
                    models.Log.protocolo is not None,  # type: ignore
                )
            )
            result_today = await db.execute(stmt_today)
            today_count = result_today.scalar_one_or_none() or 0

            stmt_always = (
                select(func.count(func.distinct(models.Log.protocolo)))
                .select_from(models.Log)
                .where(models.Log.protocolo is not None)  # type: ignore
            )
            result_always = await db.execute(stmt_always)
            always_count = result_always.scalar_one_or_none() or 0

            return schemas.TodayAlwaysOut[NonNegativeInt](
                hoje=today_count, sempre=always_count
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_endpoints(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopEndpoint]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    models.Log.endpoint,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(func.date(models.Log.criado_em) == today)
                .group_by(models.Log.endpoint)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopEndpoint(
                    endpoint=row.endpoint, total_requisicoes=row.total_requisicoes
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    models.Log.endpoint,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .group_by(models.Log.endpoint)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopEndpoint(
                    endpoint=row.endpoint, total_requisicoes=row.total_requisicoes
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopEndpoint]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_status_codes(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopStatusCode]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    models.Log.codigo.label("status_code"),
                    func.count(models.Log.id).label("total_respostas"),
                )
                .where(func.date(models.Log.criado_em) == today)
                .group_by(models.Log.codigo)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopStatusCode(
                    status_code=row.status_code, total_respostas=row.total_respostas
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    models.Log.codigo.label("status_code"),
                    func.count(models.Log.id).label("total_respostas"),
                )
                .group_by(models.Log.codigo)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopStatusCode(
                    status_code=row.status_code, total_respostas=row.total_respostas
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopStatusCode]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_hours(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopHour]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    func.extract("hour", models.Log.criado_em).label("hora"),
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(func.date(models.Log.criado_em) == today)
                .group_by(func.extract("hour", models.Log.criado_em))
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopHour(
                    hora=int(row.hora), total_requisicoes=row.total_requisicoes
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    func.extract("hour", models.Log.criado_em).label("hora"),
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .group_by(func.extract("hour", models.Log.criado_em))
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopHour(
                    hora=int(row.hora), total_requisicoes=row.total_requisicoes
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopHour]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_weekdays(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopWeekday]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()
            dow_map = {
                0: "Dom",
                1: "Seg",
                2: "Ter",
                3: "Qua",
                4: "Qui",
                5: "Sex",
                6: "Sáb",
            }

            days_since_sunday = (today.weekday() + 1) % 7
            start_of_week = today - timedelta(days=days_since_sunday)
            end_of_week = start_of_week + timedelta(days=6)

            stmt_today = (
                select(
                    func.extract("dow", models.Log.criado_em).label("dow"),
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(
                    func.date(models.Log.criado_em) >= start_of_week,
                    func.date(models.Log.criado_em) <= end_of_week,
                )
                .group_by("dow")
                .order_by("dow")
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopWeekday(
                    dia_semana=dow_map[int(row.dow)],
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    func.extract("dow", models.Log.criado_em).label("dow"),
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .group_by("dow")
                .order_by("dow")
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopWeekday(
                    dia_semana=dow_map[int(row.dow)],
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopWeekday]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_worst_endpoints(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopWorstEndpoint]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    models.Log.endpoint,
                    func.count(models.Log.id).label("total_erros"),
                )
                .where(
                    func.date(models.Log.criado_em) == today,
                    (models.Log.codigo.between(400, 499))
                    | (
                        models.Log.codigo.between(
                            status.HTTP_500_INTERNAL_SERVER_ERROR, 599
                        )
                    ),
                )
                .group_by(models.Log.endpoint)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopWorstEndpoint(
                    endpoint=row.endpoint, total_erros=row.total_erros
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    models.Log.endpoint,
                    func.count(models.Log.id).label("total_erros"),
                )
                .where(
                    (models.Log.codigo.between(400, 499))
                    | (
                        models.Log.codigo.between(
                            status.HTTP_500_INTERNAL_SERVER_ERROR, 599
                        )
                    )
                )
                .group_by(models.Log.endpoint)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopWorstEndpoint(
                    endpoint=row.endpoint, total_erros=row.total_erros
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopWorstEndpoint]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_month_days(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopMonthDay]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    func.extract("day", models.Log.criado_em).label("day"),
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(
                    func.extract("year", models.Log.criado_em) == today.year,
                    func.extract("month", models.Log.criado_em) == today.month,
                )
                .group_by("day")
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopMonthDay(
                    dia_mes=int(row.day), total_requisicoes=row.total_requisicoes
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    func.extract("day", models.Log.criado_em).label("day"),
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .group_by("day")
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopMonthDay(
                    dia_mes=int(row.day), total_requisicoes=row.total_requisicoes
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopMonthDay]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_slowest_endpoints(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopSlowestEndpoint]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    models.Log.endpoint,
                    func.avg(models.Log.duracao).label("avg_duracao"),
                )
                .where(
                    func.date(models.Log.criado_em) == today,
                    models.Log.codigo.between(200, 299),
                )
                .group_by(models.Log.endpoint)
                .order_by(func.avg(models.Log.duracao).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list: list[schemas.TopSlowestEndpoint] = []
            for row in result_today.all():
                avg = row.avg_duracao
                if avg is None:
                    avg = 0.0
                else:
                    avg = float(avg)
                hoje_list.append(
                    schemas.TopSlowestEndpoint(endpoint=row.endpoint, duracao=avg)
                )

            stmt_always = (
                select(
                    models.Log.endpoint,
                    func.avg(models.Log.duracao).label("avg_duracao"),
                )
                .where(models.Log.codigo.between(200, 299))
                .group_by(models.Log.endpoint)
                .order_by(func.avg(models.Log.duracao).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list: list[schemas.TopSlowestEndpoint] = []
            for row in result_always.all():
                avg = row.avg_duracao
                if avg is None:
                    avg = 0.0
                else:
                    avg = float(avg)
                sempre_list.append(
                    schemas.TopSlowestEndpoint(endpoint=row.endpoint, duracao=avg)
                )

            return schemas.TodayAlwaysOut[list[schemas.TopSlowestEndpoint]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_http_methods(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopHttpMethod]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    models.Log.metodo,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(func.date(models.Log.criado_em) == today)
                .group_by(models.Log.metodo)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopHttpMethod(
                    metodo_http=row.metodo,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    models.Log.metodo,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .group_by(models.Log.metodo)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopHttpMethod(
                    metodo_http=row.metodo,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopHttpMethod]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_departments(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopDepartment]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = (
                select(
                    models.Log.setor,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(func.date(models.Log.criado_em) == today)
                .group_by(models.Log.setor)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopDepartment(
                    setor=row.setor,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            stmt_always = (
                select(
                    models.Log.setor,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .group_by(models.Log.setor)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopDepartment(
                    setor=row.setor,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopDepartment]](
                hoje=hoje_list, sempre=sempre_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_success_stats(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[schemas.SuccessStats]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            stmt_today = select(
                func.count().label("total"),
                func.sum(case((models.Log.codigo.between(200, 299), 1), else_=0)).label(
                    "sucessos"
                ),
            ).where(func.date(models.Log.criado_em) == today)
            result_today = await db.execute(stmt_today)
            row_today = result_today.one()
            total_today = row_today.total or 0
            success_today = row_today.sucessos or 0
            perc_today = (success_today / total_today * 100) if total_today > 0 else 0.0

            stmt_always = select(
                func.count().label("total"),
                func.sum(case((models.Log.codigo.between(200, 299), 1), else_=0)).label(
                    "sucessos"
                ),
            )
            result_always = await db.execute(stmt_always)
            row_always = result_always.one()
            total_always = row_always.total or 0
            success_always = row_always.sucessos or 0
            perc_always = (
                (success_always / total_always * 100) if total_always > 0 else 0.0
            )

            return schemas.TodayAlwaysOut[schemas.SuccessStats](
                hoje=schemas.SuccessStats(total=success_today, percentual=perc_today),
                sempre=schemas.SuccessStats(
                    total=success_always, percentual=perc_always
                ),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_error_stats(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[schemas.ErrorStats]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            error_condition = (models.Log.codigo.between(400, 499)) | (
                models.Log.codigo.between(status.HTTP_500_INTERNAL_SERVER_ERROR, 599)
            )

            stmt_today = select(
                func.count().label("total"),
                func.sum(case((error_condition, 1), else_=0)).label("erros"),
            ).where(func.date(models.Log.criado_em) == today)
            result_today = await db.execute(stmt_today)
            row_today = result_today.one()
            total_today = row_today.total or 0
            error_today = row_today.erros or 0
            perc_today = (error_today / total_today * 100) if total_today > 0 else 0.0

            stmt_always = select(
                func.count().label("total"),
                func.sum(case((error_condition, 1), else_=0)).label("erros"),
            )
            result_always = await db.execute(stmt_always)
            row_always = result_always.one()
            total_always = row_always.total or 0
            error_always = row_always.erros or 0
            perc_always = (
                (error_always / total_always * 100) if total_always > 0 else 0.0
            )

            return schemas.TodayAlwaysOut[schemas.ErrorStats](
                hoje=schemas.ErrorStats(total=error_today, percentual=perc_today),
                sempre=schemas.ErrorStats(total=error_always, percentual=perc_always),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_clients(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOut[list[schemas.TopClientName]]:
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top clientes de hoje (limitado a 10, mas pegamos só o primeiro)
            stmt_today = (
                select(
                    models.Log.nome_cliente,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(
                    func.date(models.Log.criado_em) == today,
                    models.Log.nome_cliente.is_not(None),
                )
                .group_by(models.Log.nome_cliente)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)  # mantido para consistência, mas usaremos só o top 1
            )
            result_today = await db.execute(stmt_today)
            hoje_list = [
                schemas.TopClientName(
                    nome_cliente=row.nome_cliente,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            # Top clientes de todo o histórico
            stmt_always = (
                select(
                    models.Log.nome_cliente,
                    func.count(models.Log.id).label("total_requisicoes"),
                )
                .where(models.Log.nome_cliente.is_not(None))
                .group_by(models.Log.nome_cliente)
                .order_by(func.count(models.Log.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            sempre_list = [
                schemas.TopClientName(
                    nome_cliente=row.nome_cliente,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOut[list[schemas.TopClientName]](
                hoje=hoje_list,
                sempre=sempre_list,
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )
