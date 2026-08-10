from collections.abc import Sequence

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
    ):
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
        await db.refresh(log_entry)
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
        # Base query: select all logs
        stmt = select(models.LogModel)

        # Apply optional filters using case-insensitive partial matching (ILike)
        if metodo:
            stmt = stmt.where(models.LogModel.metodo.ilike(f"%{metodo}%"))
        if endpoint:
            stmt = stmt.where(models.LogModel.endpoint.ilike(f"%{endpoint}%"))
        if codigo:
            stmt = stmt.where(models.LogModel.codigo == codigo)
        if data_inicio:
            # Compare only the date part of criado_em against the given string
            stmt = stmt.where(func.date(models.LogModel.criado_em) >= data_inicio)
        if data_fim:
            stmt = stmt.where(func.date(models.LogModel.criado_em) <= data_fim)
        if hora_inicio:
            # Compare only the time part of criado_em against the given string
            stmt = stmt.where(func.time(models.LogModel.criado_em) >= hora_inicio)
        if hora_fim:
            stmt = stmt.where(func.time(models.LogModel.criado_em) <= hora_fim)
        if protocolo:
            stmt = stmt.where(models.LogModel.protocolo.ilike(f"%{protocolo}%"))
        if setor:
            stmt = stmt.where(models.LogModel.setor.ilike(f"%{setor}%"))
        if nome_cliente:
            stmt = stmt.where(models.LogModel.nome_cliente.ilike(f"%{nome_cliente}%"))

        # Build a subquery for counting total number of items after filters
        # This avoids counting the paginated slice
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_items = (await db.execute(count_stmt)).scalar_one()

        # Order results
        stmt = stmt.order_by(models.LogModel.id.desc())

        # Calculate offset based on page and items_per_page
        offset = (page - 1) * items_per_page
        paginated_stmt = stmt.offset(offset).limit(items_per_page)

        # Execute the paginated query
        result = await db.execute(paginated_stmt)
        logs = result.scalars().all()

        # Return total count and the actual log records for the current page
        return total_items, logs
