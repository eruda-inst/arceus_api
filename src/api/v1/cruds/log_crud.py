from collections.abc import Sequence
from datetime import date, time

from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models


class LogCrud:
    @staticmethod
    async def create_log(
        db: AsyncSession,
        method: str,
        endpoint: str,
        code: int,
        duration: float,
        protocol: str | None,
        payload: str | None,
        response: str | None,
        url: str,
        sector: str | None,
        customer_name: str | None,
    ) -> models.LogModel:
        # Build the log model instance with rounded duration to 4 decimal places
        log_entry = models.LogModel(
            metodo=method,
            endpoint=endpoint,
            codigo=code,
            duracao=round(duration, 4),
            protocolo=protocol,
            payload=payload,
            resposta=response,
            url=url,
            setor=sector,
            nome_cliente=customer_name,
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: PositiveInt = 1,
        items_per_page: PositiveInt = 10,
        method: str | None = None,
        endpoint: str | None = None,
        code: PositiveInt | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        start_hour: str | None = None,
        end_hour: str | None = None,
        protocol: str | None = None,
        department: str | None = None,
        customer_name: str | None = None,
    ) -> tuple[NonNegativeInt, Sequence[models.LogModel]]:
        # Start with a base query selecting all log records
        stmt = select(models.LogModel)

        # Apply filters only if the corresponding parameter is provided
        if method:
            stmt = stmt.where(models.LogModel.metodo.ilike(f"%{method}%"))
        if endpoint:
            stmt = stmt.where(models.LogModel.endpoint.ilike(f"%{endpoint}%"))
        if code:
            stmt = stmt.where(models.LogModel.codigo == code)

        # Date filters: use SQLite date function to compare date part of criado_em
        if start_date:
            start_date_obj = date.fromisoformat(start_date)
            stmt = stmt.where(func.date(models.LogModel.criado_em) >= start_date_obj)
        if end_date:
            end_date_obj = date.fromisoformat(end_date)
            stmt = stmt.where(func.date(models.LogModel.criado_em) <= end_date_obj)

        # Time filters: use SQLite time function to compare time part of criado_em
        if start_hour:
            start_hour_obj = time.fromisoformat(start_hour)
            stmt = stmt.where(func.time(models.LogModel.criado_em) >= start_hour_obj)
        if end_hour:
            end_hour_obj = time.fromisoformat(end_hour)
            stmt = stmt.where(func.time(models.LogModel.criado_em) <= end_hour_obj)

        if protocol:
            stmt = stmt.where(models.LogModel.protocolo.ilike(f"%{protocol}%"))
        if department:
            stmt = stmt.where(models.LogModel.setor.ilike(f"%{department}%"))
        if customer_name:
            stmt = stmt.where(models.LogModel.nome_cliente.ilike(f"%{customer_name}%"))

        # Build a separate query to count total matching rows (ignoring pagination)
        # Using subquery to count from the filtered statement
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_items = (await db.execute(count_stmt)).scalar_one()

        # Order by newest first (most recent logs appear first)
        stmt = stmt.order_by(models.LogModel.id.desc())

        # Apply pagination (offset and limit)
        offset = (page - 1) * items_per_page
        paginated_stmt = stmt.offset(offset).limit(items_per_page)

        # Execute the paginated query and collect results
        result = await db.execute(paginated_stmt)
        logs = result.scalars().all()

        return total_items, logs
