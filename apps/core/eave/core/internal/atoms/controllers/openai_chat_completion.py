import dataclasses
from typing import Any, cast

from eave.core.internal.atoms.models.api_payload_types import (
    OpenAIChatCompletionPayload,
)
from eave.core.internal.atoms.models.atom_types import OpenAIChatCompletionAtom
from eave.core.internal.atoms.models.db_record_fields import (
    AccountRecordField,
    Numeric,
    OpenAIRequestPropertiesRecordField,
    SessionRecordField,
    StackFramesRecordField,
    TrafficSourceRecordField,
)
from eave.core.internal.atoms.models.openai_pricing import CHAT_MODELS, FINE_TUNING_MODELS
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.stdlib.deidentification import redact_atoms
from eave.stdlib.logging import LOGGER, LogContext

from .base_atom_controller import BaseAtomController


class OpenAIChatCompletionController(BaseAtomController):
    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        table = self.get_or_create_bq_table(table_def=OpenAIChatCompletionAtom.table_def(), ctx=ctx)

        atoms: list[OpenAIChatCompletionAtom] = []

        for payload in events:
            e = OpenAIChatCompletionPayload.from_api_payload(payload, decryption_key=self._client.decryption_key)

            session = None
            traffic_source = None
            account = None
            visitor_id = None

            if e.corr_ctx:
                visitor_id = e.corr_ctx.visitor_id

                if e.corr_ctx.session:
                    session = SessionRecordField.from_api_resource(
                        resource=e.corr_ctx.session, event_timestamp=e.timestamp
                    )

                if e.corr_ctx.traffic_source:
                    traffic_source = TrafficSourceRecordField.from_api_resource(e.corr_ctx.traffic_source)

                if e.corr_ctx.account:
                    account = AccountRecordField.from_api_resource(e.corr_ctx.account)

            input_cost_usd_cents = None
            output_cost_usd_cents = None
            total_cost_usd_cents = None

            if e.model:
                model_pricing = None
                if e.model.startswith("ft:"):
                    # fine-tuning model usage
                    split = e.model.split(":")
                    if len(split) >= 2:
                        base_model = split[1]
                        model_pricing = FINE_TUNING_MODELS.get(base_model.lower())
                else:
                    model_pricing = CHAT_MODELS.get(e.model.lower())

                if model_pricing is not None:
                    if e.prompt_tokens is not None:
                        input_cost_usd_cents = model_pricing.calculate_input_cost_usd_cents(
                            prompt_tokens=e.prompt_tokens
                        )

                    if e.completion_tokens is not None:
                        output_cost_usd_cents = model_pricing.calculate_output_cost_usd_cents(
                            completion_tokens=e.completion_tokens
                        )

                    if input_cost_usd_cents is not None and output_cost_usd_cents is not None:
                        total_cost_usd_cents = input_cost_usd_cents + output_cost_usd_cents

            openai_request = None

            if e.openai_request:
                openai_request = OpenAIRequestPropertiesRecordField.from_api_resource(e.openai_request)

            stack_frames = None
            if e.stack_frames:
                stack_frames = [StackFramesRecordField.from_api_resource(sf) for sf in e.stack_frames]

            atom = OpenAIChatCompletionAtom(
                event_id=e.event_id,
                timestamp=e.timestamp,
                session=session,
                account=account,
                traffic_source=traffic_source,
                visitor_id=visitor_id,
                completion_id=e.completion_id,
                completion_system_fingerprint=e.completion_system_fingerprint,
                completion_created_timestamp=e.completion_created_timestamp,
                completion_user_id=e.completion_user_id,
                service_tier=e.service_tier,
                model=e.model,
                prompt_tokens=e.prompt_tokens,
                completion_tokens=e.completion_tokens,
                total_tokens=e.total_tokens,
                input_cost_usd_cents=(Numeric(input_cost_usd_cents) if input_cost_usd_cents is not None else None),
                output_cost_usd_cents=(Numeric(output_cost_usd_cents) if output_cost_usd_cents is not None else None),
                total_cost_usd_cents=(Numeric(total_cost_usd_cents) if total_cost_usd_cents is not None else None),
                stack_frames=stack_frames,
                openai_request=openai_request,
                metadata=self.get_record_metadata(),
            )

            atoms.append(atom)

        if len(atoms) == 0:
            return

        await redact_atoms(atoms)

        errors = EAVE_INTERNAL_BIGQUERY_CLIENT.append_rows(
            table=table,
            rows=[dataclasses.asdict(atom) for atom in atoms],
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)
