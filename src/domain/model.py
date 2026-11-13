from domain.claim import Claim
from domain.document import Document
from domain.document_classification import DocumentClassification
from domain.extraction_result import ExtractionResult
from domain.insurance_policy import InsurancePolicy
from domain.policy_holder import PolicyHolder

# Rebuild models after all are imported
Claim.model_rebuild()
Document.model_rebuild()
DocumentClassification.model_rebuild()
ExtractionResult.model_rebuild()
InsurancePolicy.model_rebuild()
PolicyHolder.model_rebuild()


__all__ = ["Claim", "Document", "DocumentClassification", "ExtractionResult", "InsurancePolicy", "PolicyHolder"]
