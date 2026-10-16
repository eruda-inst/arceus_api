"""
CRUD operations for Log model.
"""

import datetime as dt
from collections.abc import Sequence

from pydantic import NonNegativeInt, PositiveInt
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import models


class LogCrud:
    """
    Provides static methods for log-related database operations.
    """

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
        """
        Create a new log entry.

        Args:
            db: Async database session.
            method: HTTP method.
            endpoint: Request endpoint.
            code: HTTP status code.
            duration: Request duration in seconds.
            protocol: Protocol identifier.
            payload: Request payload.
            response: Response body.
            url: Full request URL.
            sector: Department or sector.
            customer_name: Customer name.

        Returns:
            The newly created LogModel instance.
        """
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
    async def get_all_unpaginated(db: AsyncSession) -> Sequence[models.LogModel]:
        """
        Retrieve all log entries without filtering or pagination.

        Intended for consumers that need the full dataset in memory (e.g. the
        WebSocket broadcast routine, which applies filters and pagination in
        Python across many simultaneous filter combinations).

        Args:
            db: Async database session.

        Returns:
            All log entries, ordered by id descending.
        """
        stmt = select(models.LogModel).order_by(models.LogModel.id.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

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
        """
        Retrieve logs with optional filters and pagination.

        Args:
            db: Async database session.
            page: Page number (1-based).
            items_per_page: Number of items per page.
            method: Filter by HTTP method (partial match).
            endpoint: Filter by endpoint (partial match).
            code: Filter by HTTP status code.
            start_date: Filter logs from this date (inclusive, ISO format).
            end_date: Filter logs up to this date (inclusive, ISO format).
            start_hour: Filter logs from this time (inclusive, ISO format).
            end_hour: Filter logs up to this time (inclusive, ISO format).
            protocol: Filter by protocol (partial match).
            department: Filter by department (partial match).
            customer_name: Filter by customer name (partial match).

        Returns:
            A tuple with total number of matching logs and the paginated sequence.
        """
        stmt = select(models.LogModel)

        if method:
            stmt = stmt.where(models.LogModel.metodo.ilike(f"%{method}%"))
        if endpoint:
            stmt = stmt.where(models.LogModel.endpoint.ilike(f"%{endpoint}%"))
        if code:
            stmt = stmt.where(models.LogModel.codigo == code)

        if start_date:
            start_date_obj = dt.date.fromisoformat(start_date)
            stmt = stmt.where(func.date(models.LogModel.criado_em) >= start_date_obj)
        if end_date:
            end_date_obj = dt.date.fromisoformat(end_date)
            stmt = stmt.where(func.date(models.LogModel.criado_em) <= end_date_obj)

        if start_hour:
            start_hour_obj = dt.time.fromisoformat(start_hour)
            stmt = stmt.where(func.time(models.LogModel.criado_em) >= start_hour_obj)
        if end_hour:
            end_hour_obj = dt.time.fromisoformat(end_hour)
            stmt = stmt.where(func.time(models.LogModel.criado_em) <= end_hour_obj)

        if protocol:
            stmt = stmt.where(models.LogModel.protocolo.ilike(f"%{protocol}%"))
        if department:
            stmt = stmt.where(models.LogModel.setor.ilike(f"%{department}%"))
        if customer_name:
            stmt = stmt.where(models.LogModel.nome_cliente.ilike(f"%{customer_name}%"))

        # Count total matching rows using a subquery
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_items = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(models.LogModel.id.desc())

        offset = (page - 1) * items_per_page
        paginated_stmt = stmt.offset(offset).limit(items_per_page)

        result = await db.execute(paginated_stmt)
        logs = result.scalars().all()

        return total_items, logs
