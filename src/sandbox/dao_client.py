from domain.model import PolicyHolder, InsurancePolicy, Claim, Document, DocumentClassification, ExtractionResult
from data.generic_dao import GenericDAO

if __name__ == "__main__":

    import json

    dao = GenericDAO()

    for record in dao.fetch(entity=Claim, expand=["holderId"]):
        print(json.dumps(record.model_dump(), indent=4, default=str))