"""Structured extraction of clinically useful facts from a raw transcript."""

import json
import os
from typing import Any

from mistralai import Mistral

from models.prompts import TRANSCRIPTION_EXTRACTION_PROMPT


API_KEY_VAR = "MISTRAL_API_KEY"
DEFAULT_EXTRACTION_MODEL = "mistral-medium-latest"
ALLOWED_CERTAINTIES = {"confirmed", "uncertain", "denied"}
ALLOWED_TRANSCRIPTION_QUALITIES = {"good", "fair", "poor", "unknown"}

EXPECTED_KEYS = {
    "meta": {
        "language",
        "source_type",
        "transcription_quality",
        "has_relevant_medical_content",
    },
    "medical_history": {
        "allergies",
        "past_medical_history",
        "surgical_history",
        "anesthesia_history",
        "family_history",
    },
    "current_treatment": {"medications", "treatments_to_stop"},
    "procedure_context": {
        "surgery_name",
        "surgery_side",
        "scheduled_date",
        "scheduled_time",
        "operator_name",
        "hospitalization_type",
    },
    "anesthesia_related": {
        "previous_anesthesia_problem",
        "airway_risk_factors",
        "fasting_instructions",
        "anesthesia_preferences",
        "questions_or_concerns",
    },
    "risk_factors": {
        "smoking",
        "alcohol",
        "weight",
        "bmi",
        "sleep_apnea",
        "diabetes",
        "cardiac_disease",
        "respiratory_disease",
    },
    "operational_notes": {
        "important_quotes",
        "uncertainties",
        "missing_but_expected",
    },
}

MEDICAL_LIST_PATHS = {
    ("medical_history", key) for key in EXPECTED_KEYS["medical_history"]
} | {
    ("anesthesia_related", key) for key in EXPECTED_KEYS["anesthesia_related"]
}
OPERATIONAL_LIST_PATHS = {
    ("operational_notes", key) for key in EXPECTED_KEYS["operational_notes"]
}
STRING_OR_NULL_PATHS = {
    ("procedure_context", key) for key in EXPECTED_KEYS["procedure_context"]
}


class TranscriptExtractionError(RuntimeError):
    """Raised when transcript extraction or validation fails."""


class TranscriptExtractionService:
    """Extract compact structured data without using the chat conversation."""

    def __init__(
        self,
        client: Any | None = None,
        model: str = DEFAULT_EXTRACTION_MODEL,
    ) -> None:
        self._client = client if client is not None else self._create_client()
        self._model = model

    def _create_client(self) -> Mistral:
        api_key = os.getenv(API_KEY_VAR)
        if not api_key:
            raise RuntimeError(
                f"La variable d'environnement requise '{API_KEY_VAR}' n'est pas définie."
            )
        return Mistral(api_key=api_key)

    def extract_structured_data(self, transcript_text: str) -> dict[str, Any]:
        """Extract and validate compact SFAR-relevant data from raw text."""
        if not isinstance(transcript_text, str) or not transcript_text.strip():
            raise ValueError("La transcription à extraire ne peut pas être vide.")

        try:
            response = self._client.chat.complete(
                model=self._model,
                messages=[
                    {"role": "system", "content": TRANSCRIPTION_EXTRACTION_PROMPT},
                    {"role": "user", "content": transcript_text.strip()},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
        except Exception as exc:
            raise TranscriptExtractionError(
                f"L'extraction structurée de la transcription a échoué : {exc}"
            ) from exc

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise TranscriptExtractionError(
                "La réponse d'extraction retournée par Mistral est incomplète."
            ) from exc
        if not isinstance(content, str):
            raise TranscriptExtractionError(
                "La réponse d'extraction ne contient pas de texte JSON."
            )

        try:
            extracted_data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise TranscriptExtractionError(
                f"La réponse d'extraction n'est pas un JSON valide : {exc.msg}."
            ) from exc

        self._validate_schema(extracted_data)
        return extracted_data

    def _validate_schema(self, data: Any) -> None:
        if not isinstance(data, dict):
            raise TranscriptExtractionError("Le JSON d'extraction doit être un objet.")

        self._require_exact_keys(data, set(EXPECTED_KEYS), "racine")
        for section, expected_keys in EXPECTED_KEYS.items():
            section_data = data[section]
            if not isinstance(section_data, dict):
                raise TranscriptExtractionError(
                    f"La section '{section}' doit être un objet JSON."
                )
            self._require_exact_keys(section_data, expected_keys, section)

        for section, field in MEDICAL_LIST_PATHS:
            self._validate_list(data[section][field], section, field, "value")

        self._validate_list(
            data["current_treatment"]["medications"],
            "current_treatment",
            "medications",
            "name",
            extra_keys={"dosage", "schedule"},
        )
        self._validate_list(
            data["current_treatment"]["treatments_to_stop"],
            "current_treatment",
            "treatments_to_stop",
            "name",
            extra_keys={"reason"},
        )

        for section, field in OPERATIONAL_LIST_PATHS:
            self._validate_string_list(data[section][field], f"{section}.{field}")

        for field, value in data["risk_factors"].items():
            self._validate_risk_factor(value, field)

        for section, field in STRING_OR_NULL_PATHS:
            self._validate_optional_string(data[section][field], f"{section}.{field}")
        self._validate_non_empty_string(data["meta"]["language"], "meta.language")
        self._validate_non_empty_string(data["meta"]["source_type"], "meta.source_type")
        self._validate_non_empty_string(
            data["meta"]["transcription_quality"],
            "meta.transcription_quality",
        )
        if data["meta"]["source_type"] != "preop_transcription":
            raise TranscriptExtractionError(
                "Le champ 'meta.source_type' doit valoir 'preop_transcription'."
            )
        if data["meta"]["transcription_quality"] not in ALLOWED_TRANSCRIPTION_QUALITIES:
            raise TranscriptExtractionError(
                "Le champ 'meta.transcription_quality' doit valoir good, fair, poor "
                "ou unknown."
            )
        if type(data["meta"]["has_relevant_medical_content"]) is not bool:
            raise TranscriptExtractionError(
                "Le champ 'meta.has_relevant_medical_content' doit être booléen."
            )

    @staticmethod
    def _require_exact_keys(data: dict[str, Any], expected: set[str], path: str) -> None:
        actual = set(data)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise TranscriptExtractionError(
                f"Clés invalides dans '{path}' (manquantes={missing}, supplémentaires={extra})."
            )

    def _validate_list(
        self,
        values: Any,
        section: str,
        field: str,
        primary_key: str,
        extra_keys: set[str] | None = None,
    ) -> None:
        if not isinstance(values, list):
            raise TranscriptExtractionError(
                f"Le champ '{section}.{field}' doit être une liste."
            )

        for index, item in enumerate(values):
            path = f"{section}.{field}[{index}]"
            if not isinstance(item, dict):
                raise TranscriptExtractionError(f"L'élément '{path}' doit être un objet.")
            self._validate_evidence_item(item, path, primary_key, extra_keys)

    def _validate_evidence_item(
        self,
        item: dict[str, Any],
        path: str,
        primary_key: str,
        extra_keys: set[str] | None = None,
        allow_scalar_primary: bool = False,
    ) -> None:
        """Validate an extracted value carrying certainty and textual evidence."""
        expected_keys = {primary_key, "certainty", "evidence"} | (extra_keys or set())
        self._require_exact_keys(item, expected_keys, path)
        if (
            not isinstance(item["certainty"], str)
            or item["certainty"] not in ALLOWED_CERTAINTIES
        ):
            raise TranscriptExtractionError(
                f"La certainty de '{path}' doit être confirmed, uncertain ou denied."
            )
        for key in expected_keys:
            if key == "certainty":
                continue
            if key == primary_key and allow_scalar_primary:
                if not self._is_non_empty_scalar(item[key]):
                    raise TranscriptExtractionError(
                        f"Le champ '{path}.{key}' doit être une valeur simple non vide."
                    )
                continue
            if key in {primary_key, "evidence"}:
                self._validate_non_empty_string(item[key], f"{path}.{key}")
                continue
            if item[key] is not None and (
                not isinstance(item[key], str) or not item[key].strip()
            ):
                raise TranscriptExtractionError(
                    f"Le champ '{path}.{key}' doit être une chaîne non vide ou null."
                )

    def _validate_risk_factor(self, value: Any, field: str) -> None:
        """Validate a risk factor represented as null, a scalar or evidence object."""
        path = f"risk_factors.{field}"
        if value is None:
            return
        if isinstance(value, dict):
            self._validate_evidence_item(
                value,
                path,
                "value",
                allow_scalar_primary=True,
            )
            return
        if isinstance(value, bool) or self._is_number(value):
            return
        if isinstance(value, str) and value.strip():
            return
        raise TranscriptExtractionError(
            f"Le champ '{path}' doit être une valeur simple non vide, "
            "un objet avec preuve ou null."
        )

    def _validate_string_list(self, values: Any, path: str) -> None:
        if not isinstance(values, list):
            raise TranscriptExtractionError(
                f"Le champ '{path}' doit être une liste de chaînes."
            )
        for index, value in enumerate(values):
            self._validate_non_empty_string(value, f"{path}[{index}]")

    def _validate_optional_string(self, value: Any, path: str) -> None:
        if value is not None:
            self._validate_non_empty_string(value, path)

    @staticmethod
    def _validate_non_empty_string(value: Any, path: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise TranscriptExtractionError(
                f"Le champ '{path}' doit être une chaîne non vide."
            )

    @staticmethod
    def _is_number(value: Any) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @classmethod
    def _is_non_empty_scalar(cls, value: Any) -> bool:
        if isinstance(value, bool) or cls._is_number(value):
            return True
        return isinstance(value, str) and bool(value.strip())
