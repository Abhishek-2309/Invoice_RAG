from models.rag_service import index_pdf, search_image
from models.vl_model import load_model, run_answer
import json, re
from app.schema import KVResult, InvoiceSchema


model, tokenizer = load_model()

Invoice_queries = [
    {"key": "Invoice_Number", "question": "Find the Invoice Number in the image. Return in json with the key as 'Invoice_Number' "},

    {"key": "Invoice_Date", "question": "Find the Invoice Date in the image. Return in json with the key as 'Invoice_Date' "},

    {"key": "Buyer's_Information", "question": """Identify the Buyer and extract the following buyer details:
    Name(either Buyer or Company), Address, Contact, GSTIN(GSTIN Number of Buyer's company)
    Output should be in JSON format with the key as 'Buyer's_Information' and values as the above details. """},

    {"key": "Seller's_Information", "question": """Identify the Seller and extract the following seller details:
    Name(either seller or Company), Address, Contact, GSTIN(GSTIN Number of Seller's company)
    Output should be in JSON format with the key as 'Seller's_Information' and values as the above details. """},

    {"key": "Main_Table", "question": """From the provided image of the invoice document, extract the **entire main line-item table** which lists individual products or services that are invoiced.
Instructions:
- Only extract the itemized list of products or services (do not include totals, subtotals or summary rows).
- Each row must include all relevant fields such as description, quantity, rate, amount, etc.
- Do not omit any rows. The output must cover **all rows in the table**.
- If the table spans multiple columns or pages, combine them properly into a single list.
- Ensure every item is accurately represented and nothing is skipped.
- Double-check and confirm that the table is complete before finishing.
Output format:
{
  "items": [
    {
      "Field1": "Value1",
      "Field2": "Value2",
      ...
    },
    ...
  ]
}
"""
},

    {"key": "Payment_Terms", "question": """Identify the following Payment terms from the given image:
    Bank_details, consisting of: Bank_Name, IFSC_Code, Bank_account_no
    Payment Due Date,
    Payment Methods
    Output should be in JSON format with the key as 'Payment Terms' and values as the above details"""},
    
    {"key": "Summary", "question": """Identify The following summary details:
    Subtotal(Total amount of goods before taxes), Taxes(Total value of all taxes in the total amount), Discounts, Total_Amount_Due(Total amount due including Taxes)
    Output should be in JSON format with the key as 'Summary' and values as the above details in string format of their value"""},   
    
    {"key": "Other_Important_Sections", "question": """Identify The following details:
    Terms and conditions, Notes/Comments, Signature.
    Output should be in JSON format with the key as 'Other_Important_Sections' and values as the above details. """},   
]

def strip_prompt_from_output(text: str) -> str:
    """
    Removes everything before and including the last occurrence of 'assistant\n' in the model output.
    Assumes that the JSON starts right after this.
    """
    split_pattern = r"(?:^|\n)assistant\s*\n"
    parts = re.split(split_pattern, text, maxsplit=1)
    if len(parts) == 2:
        return parts[1].strip()
    return text.strip()

def extract_json(text: str):
    """
    Strips prompt using 'strip_prompt_from_output' and tries to load clean JSON.
    Also unwraps markdown fences like ```json ... ``` if needed.
    """
    text = strip_prompt_from_output(text)

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        fallback = re.search(r"(\{.*\})", text, re.DOTALL)
        json_str = fallback.group(1).strip() if fallback else text

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return json_str  

def Process_Invoice(pdf_path: str) -> dict:
    print("Processing", pdf_path)
    RAG = index_pdf(pdf_path)
    result_json = {}
    header = {}
    for q in Invoice_queries:
        try:
            image = search_image(RAG, q["question"])
            result_text = run_answer(model, tokenizer, q["question"], image)
            print(result_text)
            extracted = extract_json(result_text)
            if isinstance(extracted, dict) and q["key"] in extracted:
                val = extracted[q["key"]]
                if isinstance(val, str):
                    try:
                        val = json.loads(val)
                    except json.JSONDecodeError:
                        pass
                if q["key"] in ["Invoice_Number", "Invoice_Date", "Buyer's_Information", "Seller's_Information"]:
                    header[q['key']] = val
                else:
                    result_json[q["key"]] = val
            else:
                if q["key"] in ["Invoice_Number", "Invoice_Date", "Buyer's_Information", "Seller's_Information"]:
                    header[q["key"]] = extracted
                else:
                    result_json[q["key"]] = extracted
        except Exception as e:
            result_json[q["key"]] = f"Error: {str(e)}"
            
    print(header)
    print("RESULT_JSON", result_json)
    
    print(result_json["Main_Table"], result_json["Payment_Terms"], result_json["Summary"], result_json["Other_Important_Sections"])
    return InvoiceSchema(
        Header= header,
        Main_Table= result_json['Main_Table'],
        Payment_Terms= result_json['Payment_Terms'],
        Summary= result_json['Summary'],
        Other_Important_Sections= result_json['Other_Important_Sections'],
    ).model_dump()
    
