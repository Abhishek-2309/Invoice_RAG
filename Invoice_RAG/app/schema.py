from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Union

class PartyInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    Name: Optional[str] = Field(None, alias="Company Name")
    Address: Optional[str] = None
    Contact: Optional[Union[str, float, int]] = None
    GSTIN: Optional[Union[str, float, int]] = None


class HeaderSection(BaseModel):
    model_config = ConfigDict(extra='allow')
    Unique_Invoice_Number: Optional[Union[str, float, int]] = Field(None, alias="Invoice_Number")
    Invoice_Date: Optional[str] = Field(None, alias="Invoice_Date")
    Seller_Info: Optional[PartyInfo] = Field(None, alias="Seller's_Information")
    Buyer_Info: Optional[PartyInfo] = Field(None, alias="Buyer's_Information")


class PaymentTerms(BaseModel):
    model_config = ConfigDict(extra='allow')
    Bank_details: Optional[Dict[str, str]] = None
    Payment_Due_Date: Optional[str] = Field(None, alias="Payment Due Date")
    Payment_Methods: Optional[str] = Field(None, alias="Payment Methods")


class SummarySection(BaseModel):
    model_config = ConfigDict(extra='allow')
    Subtotal: Optional[Union[str, float, int]] = None
    Taxes: Optional[Union[str, float, int]] = None
    Discounts: Optional[Union[str, float, int]] = None
    Total_Amount_Due: Optional[Union[str, float, int]] = Field(None, alias="Total Amount Due")


class OtherImportantSections(BaseModel):
    model_config = ConfigDict(extra='allow')
    Terms_and_conditions: Optional[str] = Field(None, alias="Terms and conditions")
    Notes_or_Comments: Optional[str] = Field(None, alias="Notes/Comments")
    Signature: Optional[str] = None


class MainTable(BaseModel):
    items: List[Dict[str, Any]]
    model_config = ConfigDict(extra='allow')


class KVResult(BaseModel):
    Header: HeaderSection
    Main_Table: Optional[MainTable] = None
    Payment_Terms: PaymentTerms = Field(..., alias="Payment Terms")
    Summary: SummarySection
    Other_Important_Sections: OtherImportantSections = Field(..., alias="Other Important Sections")
    model_config = ConfigDict(extra='allow')


class InvoiceSchema(BaseModel):
    model_config = ConfigDict(extra='allow')
    Header: Optional[HeaderSection]
    Main_Table: Optional[MainTable]
    Payment_Terms: Optional[PaymentTerms] = Field(None, alias="Payment Terms")
    Summary: Optional[SummarySection]
    Other_Important_Sections: Optional[OtherImportantSections] = Field(None, alias="Other Important Sections")
