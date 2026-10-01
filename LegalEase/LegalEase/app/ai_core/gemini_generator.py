from __future__ import annotations

import re

from app.config import Settings


class GeminiDocumentGenerator:
    """Gemini-backed legal-document generator."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def configured(self) -> bool:
        """Return True when a Gemini API key is configured."""
        return bool(self.settings.gemini_api_key)

    def _build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        language: str,
    ) -> str:
        """Build the prompt sent to Gemini."""

        term_items = [
            item.strip()
            for item in re.split(r"[;\n]+", terms)
            if item.strip()
        ]

        formatted_terms = "\n".join(
            f"- {item}" for item in term_items
        )

        return f"""
You are the document-drafting component of LegalEase,
an AI-assisted legal document generator.

Create a professional, editable {document_type} in {language}.

USER-PROVIDED FACTS

Document type:
{document_type}

Parties:
{parties}

Effective date / date details:
{dates}

Requested terms:
{formatted_terms}

OUTPUT REQUIREMENTS

1. Return only the document body.
   Do not explain how you created the document.

2. Use clear headings and numbered sections.

3. Include appropriate clauses for the document type, such as:
   - Parties
   - Effective date
   - Definitions where useful
   - Obligations
   - Payment or consideration where applicable
   - Confidentiality where applicable
   - Term and termination
   - Governing law as [TO BE COMPLETED] if not supplied
   - Notices
   - Signatures
   - Other clauses appropriate to the document type

4. Never invent:
   - Names
   - Addresses
   - Amounts
   - Dates
   - Governing jurisdictions
   - Other material facts

   If information is missing, use:
   [TO BE COMPLETED]

5. Preserve all user-provided facts faithfully.

6. Do not claim that the document is guaranteed to be legally valid
   or suitable for a particular jurisdiction.

7. Add a short section titled:

   IMPORTANT NOTICE

   State that the document is AI-generated and should be reviewed
   by a qualified legal professional before use.

8. Do not use Markdown code fences.

9. Make the document formal, practical, internally consistent,
   and easy to edit.

10. Do not add facts that were not supplied by the user.
""".strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        language: str = "English",
    ) -> str:
        """Generate a legal document using Gemini."""

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
            language=language,
        )

        # ---------------------------------------------------------
        # DEMO MODE
        # ---------------------------------------------------------
        # If there is no Gemini API key, return a local demo document.
        # This allows the rest of the application to be tested.
        # ---------------------------------------------------------

        if not self.configured:
            return self._demo_document(
                document_type=document_type,
                parties=parties,
                terms=terms,
                dates=dates,
                language=language,
            )

        # ---------------------------------------------------------
        # IMPORT GEMINI SDK
        # ---------------------------------------------------------

        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "The google-genai package is not installed. "
                "Run: pip install -r requirements.txt"
            ) from exc

        # ---------------------------------------------------------
        # CREATE GEMINI CLIENT
        # ---------------------------------------------------------

        try:
            client = genai.Client(
                api_key=self.settings.gemini_api_key
            )

            # -----------------------------------------------------
            # GEMINI INTERACTIONS API
            # -----------------------------------------------------
            #
            # Current Gemini API usage:
            #
            # client.interactions.create(
            #     model="gemini-3.8-flash",
            #     input="..."
            # )
            #
            # The model is read from .env through settings.
            # -----------------------------------------------------

            interaction = client.interactions.create(
                model=self.settings.gemini_model,
                input=prompt,
                generation_config={
                    "thinking_level": "low"
                },
            )

        except Exception as exc:
            raise RuntimeError(
                f"Gemini API request failed: {exc}"
            ) from exc

        # ---------------------------------------------------------
        # GET RESPONSE TEXT
        # ---------------------------------------------------------

        text = getattr(
            interaction,
            "output_text",
            None,
        )

        # Some SDK versions may not expose output_text directly.
        # Try to safely extract text from the final model step.
        if not text:
            steps = getattr(
                interaction,
                "steps",
                None,
            )

            if steps:
                for step in reversed(steps):
                    content = getattr(
                        step,
                        "content",
                        None,
                    )

                    if not content:
                        continue

                    if isinstance(content, list):
                        for item in reversed(content):
                            item_text = getattr(
                                item,
                                "text",
                                None,
                            )

                            if item_text:
                                text = item_text
                                break

                    if text:
                        break

        # ---------------------------------------------------------
        # EMPTY RESPONSE CHECK
        # ---------------------------------------------------------

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        # ---------------------------------------------------------
        # CLEAN RESPONSE
        # ---------------------------------------------------------

        return self._clean_response(text)

    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove accidental Markdown code fences."""

        text = text.strip()

        # Remove opening code fence.
        text = re.sub(
            r"^```(?:text|markdown)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Remove closing code fence.
        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        return text.strip()

    @staticmethod
    def _demo_document(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        language: str,
    ) -> str:
        """Create a local demo document when Gemini is not configured."""

        items = [
            item.strip()
            for item in re.split(r"[;\n]+", terms)
            if item.strip()
        ]

        bullet_lines = "\n".join(
            f"{index}. {item}"
            for index, item in enumerate(items, start=1)
        )

        if not bullet_lines:
            bullet_lines = "1. [TO BE COMPLETED]"

        return f"""LEGAL {document_type.upper()}

This is a local demo document generated by LegalEase because
no Gemini API key is configured.

It is intended to verify the complete UI, API, editing,
and export workflow.

Configure GEMINI_API_KEY in the .env file for AI-generated drafting.


1. PARTIES

{parties}


2. EFFECTIVE DATE

{dates}


3. REQUESTED TERMS

{bullet_lines}


4. ADDITIONAL PROVISIONS

[TO BE COMPLETED]


5. GOVERNING LAW

[TO BE COMPLETED]


6. SIGNATURES

Party / Authorized Representative:

________________________________________

Name: [TO BE COMPLETED]

Date: [TO BE COMPLETED]


Party / Authorized Representative:

________________________________________

Name: [TO BE COMPLETED]

Date: [TO BE COMPLETED]


IMPORTANT NOTICE

This document is a local demo generated by LegalEase.
It is not legal advice and should be reviewed by a qualified
legal professional before use.
"""