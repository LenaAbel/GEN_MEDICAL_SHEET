import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from services.transcript_extraction_service import (  # noqa: E402
    TranscriptExtractionError,
    TranscriptExtractionService,
)
from services.transcript_extraction_request_thread import (  # noqa: E402
    TranscriptExtractionRequestThread,
)
from services.transcription_request_thread import TranscriptionRequestThread  # noqa: E402
from services.transcription_service import (  # noqa: E402
    TranscriptionError,
    TranscriptionService,
)


def empty_extraction() -> dict:
    return {
        "meta": {
            "language": "fr",
            "source_type": "preop_transcription",
            "transcription_quality": "good",
            "has_relevant_medical_content": False,
        },
        "medical_history": {
            "allergies": [],
            "past_medical_history": [],
            "surgical_history": [],
            "anesthesia_history": [],
            "family_history": [],
        },
        "current_treatment": {"medications": [], "treatments_to_stop": []},
        "procedure_context": {
            "surgery_name": None,
            "surgery_side": None,
            "scheduled_date": None,
            "scheduled_time": None,
            "operator_name": None,
            "hospitalization_type": None,
        },
        "anesthesia_related": {
            "previous_anesthesia_problem": [],
            "airway_risk_factors": [],
            "fasting_instructions": [],
            "anesthesia_preferences": [],
            "questions_or_concerns": [],
        },
        "risk_factors": {
            "smoking": None,
            "alcohol": None,
            "weight": None,
            "bmi": None,
            "sleep_apnea": None,
            "diabetes": None,
            "cardiac_disease": None,
            "respiratory_disease": None,
        },
        "operational_notes": {
            "important_quotes": [],
            "uncertainties": [],
            "missing_but_expected": [],
        },
    }


def populated_extraction() -> dict:
    item = {
        "value": "information",
        "certainty": "confirmed",
        "evidence": "Information confirmée.",
    }
    extraction = empty_extraction()
    extraction["meta"]["has_relevant_medical_content"] = True
    for field in extraction["medical_history"]:
        extraction["medical_history"][field] = [deepcopy(item)]
    extraction["current_treatment"]["medications"] = [
        {
            "name": "Kardegic",
            "dosage": "75 mg",
            "schedule": "le matin",
            "certainty": "confirmed",
            "evidence": "Je prends du Kardegic 75 mg le matin.",
        }
    ]
    extraction["current_treatment"]["treatments_to_stop"] = [
        {
            "name": "Kardegic",
            "reason": "arrêt préopératoire",
            "certainty": "confirmed",
            "evidence": "Je dois arrêter le Kardegic.",
        }
    ]
    extraction["procedure_context"] = {
        "surgery_name": "intervention",
        "surgery_side": "gauche",
        "scheduled_date": "20/06/2026",
        "scheduled_time": "08:00",
        "operator_name": "Dr Martin",
        "hospitalization_type": "ambulatoire",
    }
    for field in extraction["anesthesia_related"]:
        extraction["anesthesia_related"][field] = [deepcopy(item)]
    for field in extraction["risk_factors"]:
        extraction["risk_factors"][field] = deepcopy(item)
    extraction["risk_factors"]["weight"] = {
        "value": 80,
        "certainty": "confirmed",
        "evidence": "Je pèse 80 kg.",
    }
    extraction["risk_factors"]["sleep_apnea"] = {
        "value": False,
        "certainty": "denied",
        "evidence": "Je ne fais pas d'apnée du sommeil.",
    }
    extraction["risk_factors"]["bmi"] = "24.7"
    extraction["operational_notes"] = {
        "important_quotes": ["Information importante."],
        "uncertainties": ["Information à confirmer."],
        "missing_but_expected": ["Date de naissance."],
    }
    return extraction


class TranscriptionServiceTest(unittest.TestCase):
    def test_requires_api_key_without_injected_client(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "MISTRAL_API_KEY"):
                TranscriptionService()

    def test_transcribes_existing_file(self) -> None:
        client = Mock()
        client.audio.transcriptions.complete.return_value = SimpleNamespace(
            text="  Bonjour docteur.  "
        )
        service = TranscriptionService(client=client)

        with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
            result = service.transcribe_audio(audio.name)

        self.assertEqual(result, "Bonjour docteur.")
        call = client.audio.transcriptions.complete.call_args.kwargs
        self.assertEqual(call["model"], "voxtral-mini-latest")
        self.assertEqual(call["file"]["file_name"], Path(audio.name).name)

    def test_rejects_missing_file(self) -> None:
        service = TranscriptionService(client=Mock())

        with self.assertRaisesRegex(FileNotFoundError, "introuvable"):
            service.transcribe_audio("/tmp/audio-qui-n-existe-pas.wav")

    def test_wraps_api_error(self) -> None:
        client = Mock()
        client.audio.transcriptions.complete.side_effect = RuntimeError("API indisponible")
        service = TranscriptionService(client=client)

        with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
            with self.assertRaisesRegex(TranscriptionError, "a échoué"):
                service.transcribe_audio(audio.name)


class TranscriptExtractionServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TranscriptExtractionService(client=Mock())

    def test_requires_api_key_without_injected_client(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "MISTRAL_API_KEY"):
                TranscriptExtractionService()

    def test_extracts_and_validates_json(self) -> None:
        client = Mock()
        extraction = empty_extraction()
        client.chat.complete.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=json.dumps(extraction)))
            ]
        )
        service = TranscriptExtractionService(client=client)

        result = service.extract_structured_data("Aucun antécédent signalé.")

        self.assertEqual(result, extraction)
        call = client.chat.complete.call_args.kwargs
        self.assertEqual(call["response_format"], {"type": "json_object"})
        self.assertEqual(call["temperature"], 0)

    def test_validates_every_populated_section(self) -> None:
        self.service._validate_schema(populated_extraction())

    def test_rejects_missing_or_extra_keys_at_every_level(self) -> None:
        invalid_cases = []

        missing_root = empty_extraction()
        del missing_root["meta"]
        invalid_cases.append((missing_root, "racine"))

        extra_root = empty_extraction()
        extra_root["unexpected"] = {}
        invalid_cases.append((extra_root, "racine"))

        missing_section_field = empty_extraction()
        del missing_section_field["procedure_context"]["surgery_name"]
        invalid_cases.append((missing_section_field, "procedure_context"))

        extra_section_field = empty_extraction()
        extra_section_field["risk_factors"]["unexpected"] = None
        invalid_cases.append((extra_section_field, "risk_factors"))

        for extraction, expected_path in invalid_cases:
            with self.subTest(path=expected_path):
                with self.assertRaisesRegex(TranscriptExtractionError, expected_path):
                    self.service._validate_schema(extraction)

    def test_rejects_invalid_field_in_each_section_family(self) -> None:
        invalid_cases = [
            ("meta", "transcription_quality", "excellent", "transcription_quality"),
            ("medical_history", "allergies", "pénicilline", "medical_history.allergies"),
            ("current_treatment", "medications", [{}], "current_treatment.medications"),
            ("procedure_context", "scheduled_date", False, "procedure_context.scheduled_date"),
            (
                "anesthesia_related",
                "airway_risk_factors",
                [{"value": "ronflement", "certainty": "confirmed"}],
                "anesthesia_related.airway_risk_factors",
            ),
            ("risk_factors", "smoking", [], "risk_factors.smoking"),
            ("operational_notes", "uncertainties", [""], "operational_notes.uncertainties"),
        ]

        for section, field, invalid_value, expected_path in invalid_cases:
            with self.subTest(path=expected_path):
                extraction = empty_extraction()
                extraction[section][field] = invalid_value
                with self.assertRaisesRegex(TranscriptExtractionError, expected_path):
                    self.service._validate_schema(extraction)

    def test_rejects_patient_identifiers_for_privacy(self) -> None:
        extraction = empty_extraction()
        extraction["patient_identifiers"] = {
            "name": "Jean Dupont",
            "birth_date": "01/01/1970",
            "age": 56,
        }

        with self.assertRaisesRegex(TranscriptExtractionError, "patient_identifiers"):
            self.service._validate_schema(extraction)

    def test_rejects_non_string_certainty_cleanly(self) -> None:
        extraction = empty_extraction()
        extraction["medical_history"]["allergies"] = [
            {
                "value": "pénicilline",
                "certainty": ["confirmed"],
                "evidence": "Je suis allergique à la pénicilline.",
            }
        ]

        with self.assertRaisesRegex(TranscriptExtractionError, "certainty"):
            self.service._validate_schema(extraction)

    def test_rejects_empty_optional_medication_field(self) -> None:
        extraction = empty_extraction()
        extraction["current_treatment"]["medications"] = [
            {
                "name": "Kardegic",
                "dosage": "",
                "schedule": None,
                "certainty": "confirmed",
                "evidence": "Je prends du Kardegic.",
            }
        ]

        with self.assertRaisesRegex(TranscriptExtractionError, "dosage"):
            self.service._validate_schema(extraction)

    def test_rejects_invalid_json(self) -> None:
        client = Mock()
        client.chat.complete.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="pas du json"))]
        )
        service = TranscriptExtractionService(client=client)

        with self.assertRaisesRegex(TranscriptExtractionError, "JSON valide"):
            service.extract_structured_data("Bonjour")

    def test_rejects_invalid_certainty(self) -> None:
        client = Mock()
        extraction = empty_extraction()
        extraction["medical_history"]["allergies"] = [
            {
                "value": "pénicilline",
                "certainty": "probable",
                "evidence": "Peut-être la pénicilline.",
            }
        ]
        client.chat.complete.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=json.dumps(extraction)))
            ]
        )
        service = TranscriptExtractionService(client=client)

        with self.assertRaisesRegex(TranscriptExtractionError, "certainty"):
            service.extract_structured_data("Peut-être la pénicilline.")

    def test_accepts_risk_factor_with_evidence(self) -> None:
        client = Mock()
        extraction = empty_extraction()
        extraction["risk_factors"]["smoking"] = {
            "value": "actif",
            "certainty": "confirmed",
            "evidence": "Je fume dix cigarettes par jour.",
        }
        client.chat.complete.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=json.dumps(extraction)))
            ]
        )
        service = TranscriptExtractionService(client=client)

        result = service.extract_structured_data("Je fume dix cigarettes par jour.")

        self.assertEqual(result["risk_factors"]["smoking"], extraction["risk_factors"]["smoking"])

    def test_rejects_incomplete_risk_factor_object(self) -> None:
        client = Mock()
        extraction = empty_extraction()
        extraction["risk_factors"]["smoking"] = {"value": "actif"}
        client.chat.complete.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=json.dumps(extraction)))
            ]
        )
        service = TranscriptExtractionService(client=client)

        with self.assertRaisesRegex(TranscriptExtractionError, "Clés invalides"):
            service.extract_structured_data("Je fume.")

    def test_rejects_incomplete_api_response(self) -> None:
        client = Mock()
        client.chat.complete.return_value = SimpleNamespace(choices=[])
        service = TranscriptExtractionService(client=client)

        with self.assertRaisesRegex(TranscriptExtractionError, "incomplète"):
            service.extract_structured_data("Bonjour")

    def test_rejects_empty_transcript(self) -> None:
        service = TranscriptExtractionService(client=Mock())

        with self.assertRaisesRegex(ValueError, "vide"):
            service.extract_structured_data(" ")


class AudioRequestThreadTest(unittest.TestCase):
    def test_transcription_thread_emits_result(self) -> None:
        service = Mock()
        service.transcribe_audio.return_value = "Bonjour docteur."
        results = []
        thread = TranscriptionRequestThread(service, "/tmp/audio.wav")
        thread.transcription_finished.connect(results.append)

        thread.run()

        self.assertEqual(results, ["Bonjour docteur."])

    def test_extraction_thread_emits_result(self) -> None:
        service = Mock()
        service.extract_structured_data.return_value = {"meta": {"language": "fr"}}
        results = []
        thread = TranscriptExtractionRequestThread(service, "Bonjour docteur.")
        thread.extraction_finished.connect(results.append)

        thread.run()

        self.assertEqual(results, [{"meta": {"language": "fr"}}])


if __name__ == "__main__":
    unittest.main()
