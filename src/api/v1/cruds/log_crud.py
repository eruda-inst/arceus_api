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
        metodo: str,
        endpoint: str,
        codigo: int,
        duracao: float,
        protocolo: str | None,
        payload: str | None,
        resposta: str | None,
        url: str,
        setor: str | None,
        nome_cliente: str | None,
    ) -> models.LogModel:
        # Build the log model instance with rounded duration to 4 decimal places
        log_entry = models.LogModel(
            metodo=metodo,
            endpoint=endpoint,
            codigo=codigo,
            duracao=round(duracao, 4),
            protocolo=protocolo,
            payload=payload,
            resposta=resposta,
            url=url,
            setor=setor,
            nome_cliente=nome_cliente,
        )
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)  # Load generated fields like id and timestamps
        return log_entry

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: PositiveInt,
        items_per_page: PositiveInt,
        metodo: str | None,
        endpoint: str | None,
        codigo: PositiveInt | None,
        data_inicio: str | None,
        data_fim: str | None,
        hora_inicio: str | None,
        hora_fim: str | None,
        protocolo: str | None,
        setor: str | None,
        nome_cliente: str | None,
    ) -> tuple[NonNegativeInt, Sequence[models.LogModel]]:
        # Start with a base query selecting all log records
        stmt = select(models.LogModel)

        # Apply filters only if the corresponding parameter is provided
        if metodo:
            stmt = stmt.where(models.LogModel.metodo.ilike(f"%{metodo}%"))
        if endpoint:
            stmt = stmt.where(models.LogModel.endpoint.ilike(f"%{endpoint}%"))
        if codigo:
            stmt = stmt.where(models.LogModel.codigo == codigo)

        # Date filters: use SQLite date function to compare date part of criado_em
        if data_inicio:
            data_inicio_obj = date.fromisoformat(data_inicio)
            stmt = stmt.where(func.date(models.LogModel.criado_em) >= data_inicio_obj)
        if data_fim:
            data_fim_obj = date.fromisoformat(data_fim)
            stmt = stmt.where(func.date(models.LogModel.criado_em) <= data_fim_obj)

        # Time filters: use SQLite time function to compare time part of criado_em
        if hora_inicio:
            hora_inicio_obj = time.fromisoformat(hora_inicio)
            stmt = stmt.where(func.time(models.LogModel.criado_em) >= hora_inicio_obj)
        if hora_fim:
            hora_fim_obj = time.fromisoformat(hora_fim)
            stmt = stmt.where(func.time(models.LogModel.criado_em) <= hora_fim_obj)

        if protocolo:
            stmt = stmt.where(models.LogModel.protocolo.ilike(f"%{protocolo}%"))
        if setor:
            stmt = stmt.where(models.LogModel.setor.ilike(f"%{setor}%"))
        if nome_cliente:
            stmt = stmt.where(models.LogModel.nome_cliente.ilike(f"%{nome_cliente}%"))

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
