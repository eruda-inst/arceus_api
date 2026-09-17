"""
CRUD operations for aggregated metrics based on Log model.
"""

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
    """
    Provides static methods for computing metrics from logs.
    """

    @staticmethod
    async def get_total_reqs(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[NonNegativeInt]:
        """
        Get total number of requests for today and for all time.

        Returns:
            A TodayAlwaysOutSchema with counts for 'hoje' (today) and 'sempre' (always).
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Count requests made today
            stmt_today = (
                select(func.count())
                .select_from(models.LogModel)
                .where(func.date(models.LogModel.criado_em) == today)
            )
            today_count = (await db.execute(stmt_today)).scalar_one_or_none() or 0

            # Count all requests ever
            stmt_always = select(func.count()).select_from(models.LogModel)
            always_count = (await db.execute(stmt_always)).scalar_one_or_none() or 0

            return schemas.TodayAlwaysOutSchema[NonNegativeInt](
                hoje=today_count, sempre=always_count
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_res_time(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[schemas.ResponseTimeStatsSchema]:
        """
        Get response time statistics (min, avg, max) for successful requests (2xx)
        for today and all time.

        Returns:
            A TodayAlwaysOutSchema with ResponseTimeStatsSchema for 'hoje' and 'sempre'.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            success_filter = models.LogModel.codigo.between(200, 299)

            # Stats for today
            stmt_today = select(
                func.min(models.LogModel.duracao).label("min"),
                func.avg(models.LogModel.duracao).label("avg"),
                func.max(models.LogModel.duracao).label("max"),
            ).where(
                func.date(models.LogModel.criado_em) == today,
                success_filter,
            )
            result_today = await db.execute(stmt_today)
            row_today = result_today.one()

            min_today = float(row_today.min) if row_today.min is not None else 0.0
            avg_today = float(row_today.avg) if row_today.avg is not None else 0.0
            max_today = float(row_today.max) if row_today.max is not None else 0.0

            # Stats for all time
            stmt_always = select(
                func.min(models.LogModel.duracao).label("min"),
                func.avg(models.LogModel.duracao).label("avg"),
                func.max(models.LogModel.duracao).label("max"),
            ).where(success_filter)
            result_always = await db.execute(stmt_always)
            row_always = result_always.one()

            min_always = float(row_always.min) if row_always.min is not None else 0.0
            avg_always = float(row_always.avg) if row_always.avg is not None else 0.0
            max_always = float(row_always.max) if row_always.max is not None else 0.0

            return schemas.TodayAlwaysOutSchema[schemas.ResponseTimeStatsSchema](
                hoje=schemas.ResponseTimeStatsSchema(
                    min=min_today, avg=avg_today, max=max_today
                ),
                sempre=schemas.ResponseTimeStatsSchema(
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
    ) -> schemas.TodayAlwaysOutSchema[NonNegativeInt]:
        """
        Get total number of distinct services (by protocol) for today and all time.

        Returns:
            A TodayAlwaysOutSchema with counts for 'hoje' and 'sempre'.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Distinct protocols today
            stmt_today = (
                select(func.count(func.distinct(models.LogModel.protocolo)))
                .select_from(models.LogModel)
                .where(
                    func.date(models.LogModel.criado_em) == today,
                    models.LogModel.protocolo is not None,  # type: ignore
                )
            )
            result_today = await db.execute(stmt_today)
            today_count = result_today.scalar_one_or_none() or 0

            # Distinct protocols all time
            stmt_always = (
                select(func.count(func.distinct(models.LogModel.protocolo)))
                .select_from(models.LogModel)
                .where(models.LogModel.protocolo is not None)  # type: ignore
            )
            result_always = await db.execute(stmt_always)
            always_count = result_always.scalar_one_or_none() or 0

            return schemas.TodayAlwaysOutSchema[NonNegativeInt](
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
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopEndpointSchema]]:
        """
        Get top 10 most requested endpoints for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopEndpointSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top endpoints today
            stmt_today = (
                select(
                    models.LogModel.endpoint,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(func.date(models.LogModel.criado_em) == today)
                .group_by(models.LogModel.endpoint)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopEndpointSchema(
                    endpoint=row.endpoint, total_requisicoes=row.total_requisicoes
                )
                for row in result_today.all()
            ]

            # Top endpoints all time
            stmt_always = (
                select(
                    models.LogModel.endpoint,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .group_by(models.LogModel.endpoint)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopEndpointSchema(
                    endpoint=row.endpoint, total_requisicoes=row.total_requisicoes
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopEndpointSchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_status_codes(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopStatusCodeSchema]]:
        """
        Get top 10 most frequent HTTP status codes for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopStatusCodeSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top status codes today
            stmt_today = (
                select(
                    models.LogModel.codigo.label("status_code"),
                    func.count(models.LogModel.id).label("total_respostas"),
                )
                .where(func.date(models.LogModel.criado_em) == today)
                .group_by(models.LogModel.codigo)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopStatusCodeSchema(
                    status_code=row.status_code, total_respostas=row.total_respostas
                )
                for row in result_today.all()
            ]

            # Top status codes all time
            stmt_always = (
                select(
                    models.LogModel.codigo.label("status_code"),
                    func.count(models.LogModel.id).label("total_respostas"),
                )
                .group_by(models.LogModel.codigo)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopStatusCodeSchema(
                    status_code=row.status_code, total_respostas=row.total_respostas
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopStatusCodeSchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_hours(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopHourSchema]]:
        """
        Get top 10 hours with most requests for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopHourSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top hours today
            stmt_today = (
                select(
                    func.extract("hour", models.LogModel.criado_em).label("hora"),
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(func.date(models.LogModel.criado_em) == today)
                .group_by(func.extract("hour", models.LogModel.criado_em))
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopHourSchema(
                    hora=int(row.hora), total_requisicoes=row.total_requisicoes
                )
                for row in result_today.all()
            ]

            # Top hours all time
            stmt_always = (
                select(
                    func.extract("hour", models.LogModel.criado_em).label("hora"),
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .group_by(func.extract("hour", models.LogModel.criado_em))
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopHourSchema(
                    hora=int(row.hora), total_requisicoes=row.total_requisicoes
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopHourSchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_weekdays(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopWeekdaySchema]]:
        """
        Get request counts per weekday for the current week and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopWeekdaySchema.
        """
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

            # Calculate the start and end of the current week (Sunday to Saturday)
            days_since_sunday = (today.weekday() + 1) % 7
            start_of_week = today - timedelta(days=days_since_sunday)
            end_of_week = start_of_week + timedelta(days=6)

            # Weekday counts for current week
            stmt_today = (
                select(
                    func.extract("dow", models.LogModel.criado_em).label("dow"),
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(
                    func.date(models.LogModel.criado_em) >= start_of_week,
                    func.date(models.LogModel.criado_em) <= end_of_week,
                )
                .group_by("dow")
                .order_by("dow")
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopWeekdaySchema(
                    dia_semana=dow_map[int(row.dow)],
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            # Weekday counts all time
            stmt_always = (
                select(
                    func.extract("dow", models.LogModel.criado_em).label("dow"),
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .group_by("dow")
                .order_by("dow")
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopWeekdaySchema(
                    dia_semana=dow_map[int(row.dow)],
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopWeekdaySchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_worst_endpoints(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopWorstEndpointSchema]]:
        """
        Get top 10 endpoints with most errors (4xx and 5xx) for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopWorstEndpointSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Worst endpoints today
            stmt_today = (
                select(
                    models.LogModel.endpoint,
                    func.count(models.LogModel.id).label("total_erros"),
                )
                .where(
                    func.date(models.LogModel.criado_em) == today,
                    (models.LogModel.codigo.between(400, 499))
                    | (
                        models.LogModel.codigo.between(
                            status.HTTP_500_INTERNAL_SERVER_ERROR, 599
                        )
                    ),
                )
                .group_by(models.LogModel.endpoint)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopWorstEndpointSchema(
                    endpoint=row.endpoint, total_erros=row.total_erros
                )
                for row in result_today.all()
            ]

            # Worst endpoints all time
            stmt_always = (
                select(
                    models.LogModel.endpoint,
                    func.count(models.LogModel.id).label("total_erros"),
                )
                .where(
                    (models.LogModel.codigo.between(400, 499))
                    | (
                        models.LogModel.codigo.between(
                            status.HTTP_500_INTERNAL_SERVER_ERROR, 599
                        )
                    )
                )
                .group_by(models.LogModel.endpoint)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopWorstEndpointSchema(
                    endpoint=row.endpoint, total_erros=row.total_erros
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopWorstEndpointSchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_month_days(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopMonthDaySchema]]:
        """
        Get top 10 days of the month with most requests for the current month and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopMonthDaySchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top days of current month
            stmt_today = (
                select(
                    func.extract("day", models.LogModel.criado_em).label("day"),
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(
                    func.extract("year", models.LogModel.criado_em) == today.year,
                    func.extract("month", models.LogModel.criado_em) == today.month,
                )
                .group_by("day")
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopMonthDaySchema(
                    dia_mes=int(row.day), total_requisicoes=row.total_requisicoes
                )
                for row in result_today.all()
            ]

            # Top days all time
            stmt_always = (
                select(
                    func.extract("day", models.LogModel.criado_em).label("day"),
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .group_by("day")
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopMonthDaySchema(
                    dia_mes=int(row.day), total_requisicoes=row.total_requisicoes
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopMonthDaySchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_slowest_endpoints(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopSlowestEndpointSchema]]:
        """
        Get top 10 slowest endpoints by average duration for successful requests (2xx)
        for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopSlowestEndpointSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Slowest endpoints today
            stmt_today = (
                select(
                    models.LogModel.endpoint,
                    func.avg(models.LogModel.duracao).label("avg_duracao"),
                )
                .where(
                    func.date(models.LogModel.criado_em) == today,
                    models.LogModel.codigo.between(200, 299),
                )
                .group_by(models.LogModel.endpoint)
                .order_by(func.avg(models.LogModel.duracao).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list: list[schemas.TopSlowestEndpointSchema] = []
            for row in result_today.all():
                avg = row.avg_duracao
                if avg is None:
                    avg = 0.0
                else:
                    avg = float(avg)
                today_list.append(
                    schemas.TopSlowestEndpointSchema(endpoint=row.endpoint, duracao=avg)
                )

            # Slowest endpoints all time
            stmt_always = (
                select(
                    models.LogModel.endpoint,
                    func.avg(models.LogModel.duracao).label("avg_duracao"),
                )
                .where(models.LogModel.codigo.between(200, 299))
                .group_by(models.LogModel.endpoint)
                .order_by(func.avg(models.LogModel.duracao).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list: list[schemas.TopSlowestEndpointSchema] = []
            for row in result_always.all():
                avg = row.avg_duracao
                if avg is None:
                    avg = 0.0
                else:
                    avg = float(avg)
                always_list.append(
                    schemas.TopSlowestEndpointSchema(endpoint=row.endpoint, duracao=avg)
                )

            return schemas.TodayAlwaysOutSchema[list[schemas.TopSlowestEndpointSchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_http_methods(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopHttpMethodSchema]]:
        """
        Get top 10 HTTP methods by request count for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopHttpMethodSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top methods today
            stmt_today = (
                select(
                    models.LogModel.metodo,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(func.date(models.LogModel.criado_em) == today)
                .group_by(models.LogModel.metodo)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopHttpMethodSchema(
                    metodo_http=row.metodo,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            # Top methods all time
            stmt_always = (
                select(
                    models.LogModel.metodo,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .group_by(models.LogModel.metodo)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopHttpMethodSchema(
                    metodo_http=row.metodo,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopHttpMethodSchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_departments(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopDepartmentSchema]]:
        """
        Get top 10 departments (setor) by request count for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopDepartmentSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top departments today
            stmt_today = (
                select(
                    models.LogModel.setor,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(func.date(models.LogModel.criado_em) == today)
                .group_by(models.LogModel.setor)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopDepartmentSchema(
                    setor=row.setor,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            # Top departments all time
            stmt_always = (
                select(
                    models.LogModel.setor,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .group_by(models.LogModel.setor)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopDepartmentSchema(
                    setor=row.setor,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopDepartmentSchema]](
                hoje=today_list, sempre=always_list
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_success_stats(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[schemas.SuccessStatsSchema]:
        """
        Get success statistics (total count and percentage) for today and all time.
        Success is defined as status codes between 200 and 299.

        Returns:
            A TodayAlwaysOutSchema with SuccessStatsSchema for 'hoje' and 'sempre'.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Success stats today
            stmt_today = select(
                func.count().label("total"),
                func.sum(
                    case((models.LogModel.codigo.between(200, 299), 1), else_=0)
                ).label("sucessos"),
            ).where(func.date(models.LogModel.criado_em) == today)
            result_today = await db.execute(stmt_today)
            row_today = result_today.one()
            total_today = row_today.total or 0
            success_today = row_today.sucessos or 0
            perc_today = (success_today / total_today * 100) if total_today > 0 else 0.0

            # Success stats all time
            stmt_always = select(
                func.count().label("total"),
                func.sum(
                    case((models.LogModel.codigo.between(200, 299), 1), else_=0)
                ).label("sucessos"),
            )
            result_always = await db.execute(stmt_always)
            row_always = result_always.one()
            total_always = row_always.total or 0
            success_always = row_always.sucessos or 0
            perc_always = (
                (success_always / total_always * 100) if total_always > 0 else 0.0
            )

            return schemas.TodayAlwaysOutSchema[schemas.SuccessStatsSchema](
                hoje=schemas.SuccessStatsSchema(
                    total=success_today, percentual=perc_today
                ),
                sempre=schemas.SuccessStatsSchema(
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
    ) -> schemas.TodayAlwaysOutSchema[schemas.ErrorStatsSchema]:
        """
        Get error statistics (total count and percentage) for today and all time.
        Errors are defined as 4xx or 5xx status codes.

        Returns:
            A TodayAlwaysOutSchema with ErrorStatsSchema for 'hoje' and 'sempre'.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            error_condition = (models.LogModel.codigo.between(400, 499)) | (
                models.LogModel.codigo.between(
                    status.HTTP_500_INTERNAL_SERVER_ERROR, 599
                )
            )

            # Error stats today
            stmt_today = select(
                func.count().label("total"),
                func.sum(case((error_condition, 1), else_=0)).label("erros"),
            ).where(func.date(models.LogModel.criado_em) == today)
            result_today = await db.execute(stmt_today)
            row_today = result_today.one()
            total_today = row_today.total or 0
            error_today = row_today.erros or 0
            perc_today = (error_today / total_today * 100) if total_today > 0 else 0.0

            # Error stats all time
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

            return schemas.TodayAlwaysOutSchema[schemas.ErrorStatsSchema](
                hoje=schemas.ErrorStatsSchema(total=error_today, percentual=perc_today),
                sempre=schemas.ErrorStatsSchema(
                    total=error_always, percentual=perc_always
                ),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )

    @staticmethod
    async def get_top_clients(
        db: AsyncSession,
    ) -> schemas.TodayAlwaysOutSchema[list[schemas.TopClientNameSchema]]:
        """
        Get top 10 client names by request count for today and all time.

        Returns:
            A TodayAlwaysOutSchema with lists of TopClientNameSchema.
        """
        try:
            timezone = ZoneInfo("America/Bahia")
            today = datetime.now(tz=timezone).date()

            # Top clients today
            stmt_today = (
                select(
                    models.LogModel.nome_cliente,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(
                    func.date(models.LogModel.criado_em) == today,
                    models.LogModel.nome_cliente.is_not(None),
                )
                .group_by(models.LogModel.nome_cliente)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_today = await db.execute(stmt_today)
            today_list = [
                schemas.TopClientNameSchema(
                    nome_cliente=row.nome_cliente,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_today.all()
            ]

            # Top clients all time
            stmt_always = (
                select(
                    models.LogModel.nome_cliente,
                    func.count(models.LogModel.id).label("total_requisicoes"),
                )
                .where(models.LogModel.nome_cliente.is_not(None))
                .group_by(models.LogModel.nome_cliente)
                .order_by(func.count(models.LogModel.id).desc())
                .limit(10)
            )
            result_always = await db.execute(stmt_always)
            always_list = [
                schemas.TopClientNameSchema(
                    nome_cliente=row.nome_cliente,
                    total_requisicoes=row.total_requisicoes,
                )
                for row in result_always.all()
            ]

            return schemas.TodayAlwaysOutSchema[list[schemas.TopClientNameSchema]](
                hoje=today_list,
                sempre=always_list,
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro desconhecido no banco de dados",
            )
