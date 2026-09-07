import json
import logging
from typing import Any, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger("LLMService")

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model = settings.LLM_MODEL
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.api_key = settings.LLM_API_KEY

    async def is_available(self) -> bool:
        """Check if the configured LLM provider is active and responding."""
        if self.provider == "mock":
            return True
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                if self.provider == "ollama":
                    resp = await client.get(f"{self.base_url}/api/tags")
                    return resp.status_code == 200
                elif self.provider in ["openai", "openai-compatible"]:
                    headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                    resp = await client.get(f"{self.base_url}/v1/models", headers=headers)
                    return resp.status_code == 200
        except Exception:
            return False
        return False

    async def generate_reasoning(self, evidence: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze multi-agent findings and produce grounded rationale.
        Uses real LLM if accessible, else uses our deterministic evidence synthesizer.
        """
        prompt = (
            "You are an expert AI Accounts Payable Reasoning Agent. "
            "Analyze the following evidence from specialized verification agents and produce a decision summary:\n"
            f"EVIDENCE:\n{json.dumps(evidence, indent=2)}\n\n"
            "Return a JSON object with keys: "
            "'decision' ('APPROVE', 'REVIEW', or 'REJECT'), "
            "'risk_score' (0-100), "
            "'confidence' (0.0-1.0), "
            "'reasons' (list of concise evidence-backed bullet points), "
            "'recommended_action' (concrete recommendation for finance team)."
        )

        llm_response = None
        if self.provider in ["ollama", "openai", "openai-compatible"]:
            try:
                llm_response = await self._call_llm_json(prompt)
            except Exception as e:
                logger.warning(f"LLM call failed, falling back to local reasoning engine: {e}")

        if llm_response and isinstance(llm_response, dict) and "decision" in llm_response:
            return llm_response

        # High-fidelity Fallback Reasoning Engine
        return self._deterministic_reasoning(evidence)

    async def ask_assistant(self, query: str, context: dict[str, Any]) -> str:
        """
        Answer user questions grounded strictly in database context and invoice records.
        """
        system_prompt = (
            "You are an Intelligent Invoice Processing AI Assistant. "
            "Answer the user query accurately using ONLY the provided application data and tools. "
            "Do not invent facts or invoice amounts."
        )
        user_message = f"APPLICATION CONTEXT:\n{json.dumps(context, indent=2, default=str)}\n\nUSER QUESTION: {query}"

        if self.provider in ["ollama", "openai", "openai-compatible"]:
            try:
                reply = await self._call_llm_text(system_prompt, user_message)
                if reply:
                    return reply
            except Exception as e:
                logger.warning(f"LLM assistant call failed, using grounded fallback: {e}")

        # Grounded contextual fallback response generator
        return self._grounded_chat_fallback(query, context)

    async def _call_llm_json(self, prompt: str) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if self.provider == "ollama":
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "format": "json",
                        "stream": False
                    }
                )
                if resp.status_code == 200:
                    raw = resp.json().get("response", "{}")
                    return json.loads(raw)
            elif self.provider in ["openai", "openai-compatible"]:
                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a JSON-only response engine."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"}
                    }
                )
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"]
                    return json.loads(content)
        return None

    async def _call_llm_text(self, system_prompt: str, user_content: str) -> Optional[str]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if self.provider == "ollama":
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "stream": False
                    }
                )
                if resp.status_code == 200:
                    return resp.json()["message"]["content"]
            elif self.provider in ["openai", "openai-compatible"]:
                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ]
                    }
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
        return None

    def _deterministic_reasoning(self, evidence: dict[str, Any]) -> dict[str, Any]:
        """Evidence-backed deterministic reasoning engine adhering to system rules."""
        reasons = []
        risk_score = 15.0
        confidence = 0.95

        val = evidence.get("validation", {})
        tax = evidence.get("tax", {})
        duplicate = evidence.get("duplicate", {})
        po = evidence.get("po_matching", {})
        fraud = evidence.get("fraud", {})
        vendor = evidence.get("vendor", {})

        # Validation Checks
        if val.get("math_status") == "MISMATCH":
            reasons.append(f"Mathematical calculation mismatch: diff of ₹{val.get('math_difference', 0):,.2f}")
            risk_score += 25
            confidence -= 0.1

        if val.get("required_fields_status") == "FAIL":
            reasons.append(f"Missing mandatory invoice fields: {', '.join(val.get('missing_fields', []))}")
            risk_score += 20
            confidence -= 0.15

        # Tax Checks
        if tax.get("tax_status") in ["WARNING", "FAIL"]:
            reasons.append(
                f"Tax discrepancy detected: expected {tax.get('expected_tax_rate', 0)}% vs invoice {tax.get('detected_tax_rate', 0)}% "
                f"(diff: ₹{tax.get('tax_difference', 0):,.2f})"
            )
            risk_score += 30

        # Duplicate Checks
        if duplicate.get("duplicate_status") in ["POSSIBLE_DUPLICATE", "EXACT_DUPLICATE"]:
            sim = duplicate.get("similarity_score", 0) * 100
            reasons.append(f"Potential duplicate invoice detected with {sim:.1f}% similarity to existing records")
            risk_score += 45

        # PO Matching Checks
        if po.get("po_match_status") == "MISMATCH":
            discrepancies = po.get("po_discrepancies", [])
            reasons.append(f"Purchase order mismatch: {'; '.join(discrepancies) if discrepancies else 'Quantity or price exceeds tolerance'}")
            risk_score += 35
        elif po.get("po_match_status") == "NOT_FOUND":
            reasons.append("No matching Purchase Order referenced or found")
            risk_score += 15

        # Vendor Anomaly
        if vendor.get("deviation_percentage", 0) > 100:
            reasons.append(f"Vendor invoice amount deviates by {vendor.get('deviation_percentage'):.1f}% from historical average")
            risk_score += 20

        # Fraud agent score incorporation
        fraud_risk = fraud.get("risk_score", 0)
        if fraud_risk > risk_score:
            risk_score = fraud_risk

        risk_score = min(100.0, max(0.0, risk_score))
        confidence = max(0.50, min(0.99, confidence))

        # Routing decision
        if risk_score <= 30.0 and confidence >= 0.90 and not reasons:
            decision = "APPROVE"
            reasons.append("All automated validations, tax compliance, and PO matching checks passed with high confidence.")
            recommended_action = "Automatic approval recommended for payment processing."
        elif risk_score >= 85.0 and ("Missing mandatory" in " ".join(reasons) or "EXACT_DUPLICATE" in duplicate.get("duplicate_status", "")):
            decision = "REJECT"
            recommended_action = "Reject invoice and notify vendor of non-compliance / duplicate submission."
        else:
            decision = "REVIEW"
            recommended_action = "Routing to Accounts Payable Human-in-the-Loop review queue for verification."

        return {
            "decision": decision,
            "risk_score": round(risk_score, 1),
            "confidence": round(confidence, 2),
            "reasons": reasons,
            "recommended_action": recommended_action
        }

    def _grounded_chat_fallback(self, query: str, context: dict[str, Any]) -> str:
        q = query.lower()
        active_inv = context.get("active_invoice")
        summary_stats = context.get("stats", {})

        if "why was this invoice flagged" in q or "flagged" in q or "risk" in q:
            if active_inv:
                reasons = active_inv.get("decision_reasons", [])
                risk = active_inv.get("risk_score", 0)
                reasons_str = "\n".join([f"• {r}" for r in reasons]) if reasons else "• No critical anomalies flagged."
                return (
                    f"Invoice **{active_inv.get('invoice_number', active_inv.get('invoice_id'))}** has a Risk Score of **{risk}/100** ({active_inv.get('risk_level')}).\n\n"
                    f"**Identified Evidence:**\n{reasons_str}\n\n"
                    f"**Recommended Action:** {active_inv.get('recommended_action', 'Review discrepancy before releasing payment.')}"
                )
            return "Please select an invoice or specify an Invoice ID (e.g., INV-10025) so I can retrieve its risk breakdown."

        if "tax" in q:
            if active_inv:
                val = active_inv.get("validations", {})
                return (
                    f"For invoice **{active_inv.get('invoice_number', active_inv.get('invoice_id'))}**:\n"
                    f"- **Extracted Tax Amount:** ₹{active_inv.get('tax_amount', 0):,.2f}\n"
                    f"- **Detected Tax Rate:** {val.get('detected_tax_rate', active_inv.get('tax_percentage', 18))}%\n"
                    f"- **Expected Tax Rate:** {val.get('expected_tax_rate', 18)}%\n"
                    f"- **Tax Status:** {val.get('tax_status', 'PASS')}\n"
                    f"- **Notes:** {val.get('tax_notes', 'Tax complies with configured rules.')}"
                )
            return "Please specify an invoice number to inspect tax calculations."

        if "compare" in q or "po" in q:
            if active_inv:
                val = active_inv.get("validations", {})
                return (
                    f"**Purchase Order Matching for {active_inv.get('invoice_number')}**:\n"
                    f"- **Associated PO:** {active_inv.get('po_number') or 'None detected'}\n"
                    f"- **Match Status:** {val.get('po_match_status', 'PASS')}\n"
                    f"- **Discrepancies:** {', '.join(val.get('po_discrepancies', ['None - exact match within tolerance']))}\n"
                    f"- **Configured Tolerance:** ±{settings.PO_QUANTITY_TOLERANCE_PCT}% Quantity, ±{settings.PO_PRICE_TOLERANCE_PCT}% Unit Price."
                )
            return "Specify an invoice to compare against its Purchase Order record."

        if "duplicate" in q:
            if active_inv:
                val = active_inv.get("validations", {})
                sim = val.get("similarity_score", 0) * 100
                return (
                    f"**Duplicate Analysis for {active_inv.get('invoice_number')}**:\n"
                    f"- **Status:** {val.get('duplicate_status', 'PASS')}\n"
                    f"- **Similarity Score:** {sim:.1f}%\n"
                    f"- **Matched Invoice:** {val.get('matched_invoice_id') or 'None'}\n"
                    f"- **Assessment:** {val.get('duplicate_notes', 'No duplicate signatures detected.')}"
                )
            return "I can inspect any invoice for duplicates using fuzzy matching and document hashing."

        if "review" in q or "need review" in q or "queue" in q:
            pending = summary_stats.get("pending_review", 0)
            return f"There are currently **{pending}** invoices awaiting Human-in-the-Loop review. You can inspect them in the **Review Queue** tab."

        # General summary
        total = summary_stats.get("total_invoices", 0)
        approved = summary_stats.get("approved", 0)
        return (
            f"I am connected to the Agentic Invoice Database.\n"
            f"- **Total Invoices Processed:** {total}\n"
            f"- **Approved:** {approved}\n"
            f"- **Pending Review:** {summary_stats.get('pending_review', 0)}\n"
            f"- **High Risk Flagged:** {summary_stats.get('high_risk', 0)}\n\n"
            f"You can ask me to analyze specific invoices, compare line items with purchase orders, investigate tax mismatches, or explain why an invoice was routed to human review."
        )

llm_service = LLMService()
