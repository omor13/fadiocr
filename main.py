# app.py

import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

st.title("Azure Document Intelligence - Receipt OCR")

# Add text input for endpoint & key (for dev only, or use env vars in prod)
endpoint = st.text_input("Endpoint", "https://<YOUR-RESOURCE-NAME>.cognitiveservices.azure.com/")
key = st.text_input("Key", "YOUR_KEY", type="password")

# Add text input for document URL
document_url = st.text_input(
    "Document URL",
    "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
)

if st.button("Analyze Receipt"):
    if not endpoint or not key:
        st.error("Please enter your Azure Document Intelligence endpoint and key.")
    else:
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )

        with st.spinner("Analyzing document..."):
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-receipt",
                AnalyzeDocumentRequest(url_source=document_url)
            )
            receipts = poller.result()

            for idx, receipt in enumerate(receipts.documents):
                st.subheader(f"Recognizing receipt #{idx + 1}")
                receipt_type = receipt.doc_type
                if receipt_type:
                    st.write(f"**Receipt Type:** {receipt_type}")

                merchant_name = receipt.fields.get("MerchantName")
                if merchant_name:
                    st.write(f"**Merchant Name:** {merchant_name.value_string} (confidence: {merchant_name.confidence:.2f})")

                transaction_date = receipt.fields.get("TransactionDate")
                if transaction_date:
                    st.write(f"**Transaction Date:** {transaction_date.value_date} (confidence: {transaction_date.confidence:.2f})")

                if receipt.fields.get("Items"):
                    st.write("**Items:**")
                    for idx, item in enumerate(receipt.fields.get("Items").value_array):
                        st.write(f"- **Item #{idx + 1}**")
                        item_description = item.value_object.get("Description")
                        if item_description:
                            st.write(f"  - Description: {item_description.value_string} (confidence: {item_description.confidence:.2f})")
                        item_quantity = item.value_object.get("Quantity")
                        if item_quantity:
                            st.write(f"  - Quantity: {item_quantity.value_number} (confidence: {item_quantity.confidence:.2f})")
                        item_price = item.value_object.get("Price")
                        if item_price:
                            st.write(f"  - Price: {item_price.value_currency.amount} (confidence: {item_price.confidence:.2f})")
                        item_total_price = item.value_object.get("TotalPrice")
                        if item_total_price:
                            st.write(f"  - Total Price: {item_total_price.value_currency.amount} (confidence: {item_total_price.confidence:.2f})")

                subtotal = receipt.fields.get("Subtotal")
                if subtotal:
                    st.write(f"**Subtotal:** {subtotal.value_currency.amount} (confidence: {subtotal.confidence:.2f})")

                tax = receipt.fields.get("TotalTax")
                if tax:
                    st.write(f"**Tax:** {tax.value_currency.amount} (confidence: {tax.confidence:.2f})")

                tip = receipt.fields.get("Tip")
                if tip:
                    st.write(f"**Tip:** {tip.value_currency.amount} (confidence: {tip.confidence:.2f})")

                total = receipt.fields.get("Total")
                if total:
                    st.write(f"**Total:** {total.value_currency.amount} (confidence: {total.confidence:.2f})")
