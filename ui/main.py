import streamlit as st
import requests
import PyPDF2
import concurrent.futures
import io
import os
import re
import base64
from pdf2image import convert_from_bytes
from PIL import Image
import html

st.set_page_config(
    page_title="KYC Ops Document Service Hub",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "current_service" not in st.session_state:
    st.session_state.current_service = "overview"
if "last_extraction_result" not in st.session_state:
    st.session_state.last_extraction_result = {}


SERVICES = {
    "doc-classify": {
        "name": "Document Classifier",
        "description": "Classify document types and pages",
        "port": 8004,
        "endpoint": "/classify-pdf",
        "features": [
            "Multi-page classification",
            "Confidence scoring",
            "Document type detection",
            "Reasoning provided",
        ],
    },
    "image-data-extractor": {
        "name": "Document Extraction",
        "description": "Extract structured data from documents and images",
        "port": 8005,
        "endpoint": "/extract",
        "features": [
            "Document classification",
            "Data extraction",
            "Schema generation",
            "Multi-format support",
        ],
    },
    "analyzer": {
        "name": "Ops Document Query Tool",
        "description": "Analyze PDF content with custom queries",
        "port": 8001,
        "endpoint": "/analyze",
        "features": [
            "Vector search",
            "Multimodal analysis",
            "Custom queries",
            "Content retrieval",
        ],
    },
    "sentiment": {
        "name": "PDF Sentiment Analysis",
        "description": "Analyze sentiment in PDF documents",
        "port": 8002,
        "endpoint": "/sentiment-pdf",
        "features": [
            "Multimodal analysis",
            "Vector analysis",
            "Sentiment scoring",
            "Summary generation",
        ],
    },
    "summarizer": {
        "name": "PDF Summarizer",
        "description": "Generate summaries from PDF documents",
        "port": 8003,
        "endpoint": "/summarize",
        "features": [
            "Comprehensive summaries",
            "Brief summaries",
            "Detailed summaries",
            "Key points extraction",
        ],
    },
    "member-search": {
        "name": "Member Document Search",
        "description": "Search and trace extracted fields in member documents (PAN, Passport, Aadhar)",
        "port": None,
        "endpoint": None,
        "features": [
            "Prefilled extracted fields",
            "Field-level source tracing",
            "Quick access to document sources",
        ],
    },
    "workflow": {
        "name": "Workflow",
        "description": "Upload, classify, split, extract, and review documents in a single flow",
        "port": None,
        "endpoint": None,
        "features": [
            "Document upload",
            "Classification",
            "PDF splitting",
            "Extraction",
            "Dropdown review of results",
        ],
    },
}


def get_page_images(uploaded_file):
    uploaded_file.seek(0)
    images = convert_from_bytes(uploaded_file.read())
    return {i + 1: img for i, img in enumerate(images)}


def display_sentiment_analysis():
    st.header("PDF Sentiment Analysis")

    uploaded_file = st.file_uploader(
        "Upload PDF for sentiment analysis", type=["pdf"], key="sentiment_upload"
    )

    if uploaded_file:
        col1, col2 = st.columns(2)

        with col1:
            analysis_mode = st.selectbox(
                "Analysis Mode", ["multimodal", "vector"])

        with col2:
            st.write("")
            st.write("")
            analyze_button = st.button(
                "Analyze Sentiment", type="primary", use_container_width=True
            )

        if analyze_button:
            with st.spinner("Analyzing sentiment..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                    }
                    data = {"mode": analysis_mode}
                    response = requests.post(
                        "http://localhost:8002/sentiment-pdf",
                        files=files,
                        data=data,
                        timeout=240,
                    )
                    response.raise_for_status()
                    response_json = response.json()
                    result = response_json.get("result", {})
                    st.success(response_json.get(
                        "message", "Analysis completed!"))

                    with st.container():
                        st.markdown("### Sentiment Analysis Result")
                        st.divider()
                        col1, col2 = st.columns(2)
                        with col1:
                            sentiment = result.get("sentiment", "N/A")
                            st.metric("Sentiment", value=sentiment)
                        with col2:
                            st.metric("Score", str(result.get("score", "N/A")))
                        st.divider()
                        st.markdown(
                            f"**Summary:**<br>{result.get('summary', 'No summary provided.')}",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"**Mode:** `{response_json.get('mode', 'N/A')}`")
                        st.markdown(
                            f"**Filename:** `{response_json.get('filename', 'N/A')}`"
                        )
                except requests.exceptions.RequestException as e:
                    st.error(f"Sentiment analysis failed: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")


def display_document_classification():
    st.header("Document Classification")

    uploaded_file = st.file_uploader(
        "Upload PDF for classification", type=["pdf"], key="classify_upload"
    )

    if uploaded_file:
        bytes_data = uploaded_file.read()
        page_images = get_page_images(io.BytesIO(bytes_data))
        if st.button("Classify Document", type="primary"):
            with st.spinner("Classifying document..."):
                try:
                    file_obj = io.BytesIO(bytes_data)
                    files = {
                        "file": (uploaded_file.name, file_obj, uploaded_file.type)
                    }
                    response = requests.post(
                        "http://localhost:8004/classify-pdf", files=files, timeout=240
                    )
                    response.raise_for_status()
                    result = response.json()
                    st.success("Classification completed!")
                    classifications = result.get("page_classifications", [])
                    if not classifications:
                        st.warning("No classifications returned.")
                    for classification in classifications:
                        with st.expander(
                            f"Page {classification.get('page', '?')} - {classification.get('document_type', 'Unknown')}"
                        ):
                            page_num = classification.get('page', 1)
                            img = page_images.get(page_num)
                            if img:
                                st.image(
                                    img, caption=f"Page {page_num} Image", width=500)
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(
                                    "Confidence",
                                    f"{classification.get('confidence', 0):.2%}",
                                )
                            with col2:
                                st.metric(
                                    "Document Type",
                                    classification.get(
                                        "document_type", "Unknown"),
                                )
                            st.write(
                                "**Reasoning:**",
                                classification.get(
                                    "reasoning", "No reasoning provided."
                                ),
                            )
                except requests.exceptions.RequestException as e:
                    st.error(f"Classification failed: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")


def display_summarizer():
    st.header("PDF Summarizer")

    uploaded_file = st.file_uploader(
        "Upload PDF for summarization", type=["pdf"], key="summarize_upload"
    )

    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            analysis_mode = st.selectbox(
                "Analysis Mode", ["vector", "multimodal"])
        with col2:
            summary_type = st.selectbox(
                "Summary Type", ["comprehensive", "brief", "detailed"]
            )

        if st.button("Generate Summary", type="primary"):
            with st.spinner("Generating summary..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                    }
                    data = {"mode": analysis_mode,
                            "summary_type": summary_type}
                    response = requests.post(
                        "http://localhost:8003/summarize",
                        files=files,
                        data=data,
                        timeout=240,
                    )
                    response.raise_for_status()
                    result = response.json()
                    st.success("Summary generated!")
                    st.subheader("Generated Summary")
                    st.write(result.get("summary", "No summary provided."))
                    key_points = result.get("key_points", [])
                    if key_points:
                        st.subheader("Key Points")
                        for i, point in enumerate(key_points, 1):
                            st.write(f"{i}. {point}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Summary generation failed: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")


def display_analyzer():
    st.header("Ops Document Query Tool")
    tabs = st.tabs(["Analyze", "Ingest", "Query"])

    with tabs[0]:
        uploaded_file = st.file_uploader(
            "Upload PDF for analysis", type=["pdf"], key="analyze_upload"
        )
        if uploaded_file:
            col1, col2 = st.columns(2)
            with col1:
                analysis_mode = st.selectbox(
                    "Analysis Mode", ["vector", "multimodal"], key="analyze_mode"
                )
            with col2:
                search_query = st.text_input(
                    "Search Query",
                    value="List if any criminal activity is there by the person mentioned",
                    key="analyze_query",
                )
            if st.button("Analyze Document", type="primary", key="analyze_btn"):
                with st.spinner("Analyzing document..."):
                    try:
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file,
                                uploaded_file.type,
                            )
                        }
                        data = {"search_query": search_query,
                                "mode": analysis_mode}
                        response = requests.post(
                            "http://localhost:8001/analyze",
                            files=files,
                            data=data,
                            timeout=240,
                        )
                        response.raise_for_status()
                        result = response.json()
                        st.success("Analysis completed!")
                        st.subheader("Analysis Results")
                        analysis_text = (
                            result.get("response")
                            or result.get("analysis")
                            or "No analysis provided."
                        )
                        st.write(analysis_text)
                        retrieved_vectors = result.get("retrieved_vectors", [])
                        if retrieved_vectors:
                            st.subheader("Retrieved Vectors")
                            with st.expander("Show retrieved vectors", expanded=True):
                                for i, vector in enumerate(retrieved_vectors, 1):
                                    page_content = vector.get(
                                        "page_content", "")
                                    metadata = vector.get("metadata", {})
                                    source = metadata.get("source")
                                    page = metadata.get("page")
                                    label = f"Vector {i} (Page: {page if page is not None else 'N/A'})"
                                    with st.expander(label, expanded=False):
                                        st.write(page_content)
                                        if source:
                                            filename = source.split("/")[-1]
                                            pdf_url = (
                                                f"http://localhost:9000/{filename}"
                                            )
                                            st.markdown(
                                                f'<a href="{pdf_url}" target="_blank">View Source</a>',
                                                unsafe_allow_html=True,
                                            )
                        retrieved = result.get("retrieved_content", [])
                        if retrieved:
                            st.subheader("Retrieved Content")
                            with st.expander("View retrieved document chunks"):
                                for chunk in retrieved:
                                    st.write(chunk)
                    except requests.exceptions.RequestException as e:
                        st.error(f"Analysis failed: {str(e)}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")

    with tabs[1]:
        ingest_file = st.file_uploader(
            "Upload PDF to Ingest into Vector Store", type=["pdf"], key="ingest_upload"
        )
        if ingest_file:
            if st.button("Ingest Document", type="primary", key="ingest_btn"):
                with st.spinner("Ingesting document into vector store..."):
                    try:
                        files = {
                            "file": (ingest_file.name, ingest_file, ingest_file.type)
                        }
                        response = requests.post(
                            "http://localhost:8001/vectorstore/ingest",
                            files=files,
                            timeout=240,
                        )
                        response.raise_for_status()
                        result = response.json()
                        st.success(
                            result.get(
                                "message", "PDF ingested and index updated.")
                        )
                        st.markdown(
                            f"**Filename:** `{result.get('filename', 'N/A')}`")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Ingestion failed: {str(e)}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")

    with tabs[2]:
        query_text = st.text_input(
            "Query String", value="What is the summary?", key="vector_query"
        )
        k_val = st.number_input(
            "Number of Results (k)",
            min_value=1,
            max_value=20,
            value=4,
            step=1,
            key="vector_k",
        )
        if st.button("Query Vector Store", type="primary", key="vector_query_btn"):
            with st.spinner("Querying vector store..."):
                try:
                    payload = {"query": query_text, "k": int(k_val)}
                    response = requests.post(
                        "http://localhost:8001/vectorstore/query",
                        json=payload,
                        timeout=240,
                    )
                    response.raise_for_status()
                    result = response.json()
                    results = result.get("results", [])
                    if not results:
                        st.info("No results found.")
                    else:
                        st.subheader("Query Results")
                        for i, res in enumerate(results, 1):
                            with st.expander(f"Result {i}", expanded=False):
                                st.write(res.get("page_content", ""))
                                meta = res.get("metadata", {})
                                source_path = meta.get("source_path") or meta.get(
                                    "source"
                                )
                                if meta:
                                    st.caption(
                                        f"Source: {source_path if source_path else 'N/A'}"
                                    )
                                    st.json(meta)
                                if source_path and source_path.endswith(".pdf"):
                                    filename = source_path.split("/")[-1]
                                    pdf_url = f"http://localhost:9000/{filename}"
                                    st.markdown(
                                        f'<a href="{pdf_url}" target="_blank">View Source</a>',
                                        unsafe_allow_html=True,
                                    )
                except requests.exceptions.RequestException as e:
                    st.error(f"Query failed: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")


def display_document_extraction():
    st.header("Document Extraction")

    st.subheader("All Schemas in System")
    if (
        st.button("Refresh Schemas List", key="refresh_schemas_btn")
        or "all_schemas" not in st.session_state
    ):
        try:
            resp = requests.get("http://localhost:8005/schemas", timeout=240)
            resp.raise_for_status()
            schemas_data = resp.json()
            st.session_state.all_schemas = schemas_data.get("schemas", [])
        except Exception as e:
            st.error(f"Failed to fetch schemas: {str(e)}")
            st.session_state.all_schemas = []
    all_schemas = st.session_state.get("all_schemas", [])

    if all_schemas:
        schema_labels = [
            f"{schema.get('document_type', 'Unknown')} ({schema.get('country', '??')}) - v{schema.get('version', '?')} [{schema.get('status', '').upper()}]"
            for schema in all_schemas
        ]
        selected_idx = st.selectbox(
            "Select a schema to view details:",
            options=list(range(len(all_schemas))),
            format_func=lambda i: schema_labels[i],
            key="schema_selectbox"
        )
        schema = all_schemas[selected_idx]
        schema_fields = schema.get("schema", {})
        with st.expander(schema_labels[selected_idx], expanded=True):
            for field, props in schema_fields.items():
                with st.container():
                    st.markdown(f"**{field}**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.caption(f"Type: {props.get('type', '')}")
                    with col2:
                        st.caption(f"Required: {props.get('required', False)}")
                    with col3:
                        st.caption(f"Example: {props.get('example', '')}")
                    with col4:
                        st.caption(
                            f"Pattern: {props.get('pattern', '') if 'pattern' in props else '-'}"
                        )
                    st.caption(f"Description: {props.get('description', '')}")
            if st.button("Modify This Schema", key=f"modify_schema_{schema['id']}"):
                st.session_state.last_extraction_result = {
                    "status": "pending_review",
                    "schema_id": schema["id"],
                    "schema": schema,
                    "classification": {
                        "document_type": schema.get("document_type", ""),
                        "country": schema.get("country", ""),
                        "confidence": schema.get("confidence", 1.0),
                    },
                }
                st.session_state.schema_modification = {
                    k: v.copy() for k, v in schema.get("schema", {}).items()
                }
                st.session_state.fields_to_remove = set()
                st.rerun()
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Document (PDF, JPEG, PNG)",
        type=["pdf", "jpeg", "jpg", "png"],
        key="extract_upload",
    )

    if uploaded_file:
        # st.write("### Document Preview:")
        # if uploaded_file.type == "application/pdf":
        #     st.info(f"📄 PDF File: {uploaded_file.name}")
        #     uploaded_file.seek(0)
        #     base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
        #     pdf_display = f'<div style="display: flex; justify-content: center;"><iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="600" type="application/pdf"></iframe></div>'
        #     st.markdown(pdf_display, unsafe_allow_html=True)
        #     uploaded_file.seek(0)
        # else:
        #     st.image(uploaded_file, caption=uploaded_file.name, width=400)
        # st.divider()
        if st.button("Extract Data", type="primary"):
            with st.spinner("Extracting data from document..."):
                try:
                    files = {
                        "document": (
                            uploaded_file.name,
                            uploaded_file,
                            uploaded_file.type,
                        )
                    }
                    response = requests.post(
                        "http://localhost:8005/extract",
                        files=files,
                        timeout=240,
                    )
                    response.raise_for_status()
                    result = response.json()
                    st.session_state.last_extraction_result = result
                except Exception as e:
                    st.error(f"Extraction failed: {str(e)}")
                    return

    result = st.session_state.get("last_extraction_result", {})
    if not result:
        return

    status = result.get("status")
    if status == "extracted":
        st.success("Extraction successful!")
        data = result.get("data", {})
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.markdown("#### Document Preview")
            if uploaded_file and uploaded_file.type == "application/pdf":
                st.info(f"📄 PDF File: {uploaded_file.name}")
                uploaded_file.seek(0)
                base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
                pdf_display = f'<div style=\"display: flex; justify-content: center;\"><iframe src=\"data:application/pdf;base64,{base64_pdf}\" width=\"500\" height=\"500\" type=\"application/pdf\"></iframe></div>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                uploaded_file.seek(0)
            elif uploaded_file:
                st.image(uploaded_file, caption=uploaded_file.name, width=300)
            else:
                st.info("No file uploaded or file was removed.")
        with col2:
            st.markdown("#### Extracted Fields")
            import streamlit.components.v1 as components
            html_content = """
            <style>
            .extract-scroll-area {
                height: 500px;
                overflow-y: auto;
                padding: 0.5em 0.5em 0.5em 0;
                background: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            .extract-card {
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(60,60,60,0.06);
                margin-bottom: 1.2em;
                padding: 1em 1.2em;
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                transition: box-shadow 0.2s;
            }
            .extract-card:hover {
                box-shadow: 0 4px 16px rgba(60,60,60,0.12);
            }
            .extract-field-name {
                font-weight: 600;
                color: #333;
                flex: 1 1 40%;
                padding-right: 1em;
                word-break: break-word;
            }
            .extract-field-value {
                flex: 2 1 60%;
                word-break: break-word;
                font-family: 'JetBrains Mono', 'Fira Mono', 'Menlo', monospace;
                font-size: 1em;
                color: #222;
            }
            .extract-badge {
                display: inline-block;
                padding: 0.2em 0.7em;
                border-radius: 12px;
                font-size: 0.95em;
                font-weight: 600;
                color: #fff;
                margin-left: 0.5em;
            }
            .extract-badge-true {
                background: #27ae60;
            }
            .extract-badge-false {
                background: #c0392b;
            }
            .extract-divider {
                border: none;
                border-top: 1px solid #f0f0f0;
                margin: 0.7em 0 0.2em 0;
            }
            </style>
            <div class='extract-scroll-area'>
            """
            if data:
                for key, value in data.items():
                    html_content += "<div class='extract-card'>"
                    html_content += f"<div class='extract-field-name'>{key.replace('_', ' ').title()}</div>"
                    html_content += "<div class='extract-field-value'>"
                    if isinstance(value, bool):
                        badge_class = "extract-badge-true" if value else "extract-badge-false"
                        badge_text = "✅ True" if value else "❌ False"
                        html_content += f"<span class='extract-badge {badge_class}'>{badge_text}</span>"
                    elif "date" in key and isinstance(value, str):
                        html_content += f"<code>{value}</code>"
                    elif isinstance(value, list):
                        html_content += f"<pre style='margin:0;background:transparent;border:none;padding:0;'>{html.escape('\n'.join(map(str, value)))}</pre>"
                    elif "address" in key.lower() and isinstance(value, str):
                        normalized = value.replace("\n", " ").replace("\r", " ")
                        html_content += f"<div style='white-space:pre-wrap;'>{html.escape(normalized)}</div>"
                    else:
                        html_content += f"<pre style='margin:0;background:transparent;border:none;padding:0;'>{html.escape(str(value))}</pre>"
                    html_content += "</div>"
                    html_content += "</div>"
            else:
                html_content += "<div style='padding:1em;color:#888;'>No fields extracted.</div>"
            html_content += "</div>"
            components.html(html_content, height=520, scrolling=False)
            with st.expander("Show Raw JSON"):
                st.json(result)
        return

    if status in ("pending_review", "schema_generated"):
        schema_id = result.get("schema_id") or result.get("new_schema_info", {}).get(
            "id"
        )
        schema = result.get("generated_schema") or result.get("schema")
        classification = result.get("classification", {})
        st.warning("Schema is in review. Approve or modify the schema below.")
        st.markdown(
            f"**Document Type:** `{classification.get('document_type', 'N/A')}`  "
        )
        st.markdown(f"**Country:** `{classification.get('country', 'N/A')}`  ")
        st.markdown(
            f"**Confidence:** `{classification.get('confidence', 'N/A')}`  ")
        if schema:
            st.subheader("Current Schema Fields")
            if "schema_modification" not in st.session_state:
                st.session_state.schema_modification = {
                    k: v.copy() for k, v in schema.get("schema", {}).items()
                }
            mod_schema = st.session_state.schema_modification
            if not isinstance(mod_schema, dict):
                st.error(
                    "No schema fields available for modification. The schema may be missing or malformed."
                )
                return
            if "fields_to_remove" not in st.session_state:
                st.session_state.fields_to_remove = set()
            fields_to_remove = st.session_state.fields_to_remove
            for field, props in list(mod_schema.items()):
                with st.expander(f"Field: {field}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        new_desc = st.text_input(
                            f"Description for {field}",
                            value=props.get("description", ""),
                            key=f"desc_{field}",
                        )
                        default_types = [
                            "string", "boolean", "integer", "number"]
                        current_type = props.get("type", "string")
                        type_options = (
                            default_types
                            if current_type in default_types
                            else default_types + [current_type]
                        )
                        new_type = st.selectbox(
                            f"Type for {field}",
                            type_options,
                            index=type_options.index(current_type),
                            key=f"type_{field}",
                        )
                        new_example = st.text_input(
                            f"Example for {field}",
                            value=str(props.get("example", "")),
                            key=f"ex_{field}",
                        )
                        new_required = st.checkbox(
                            "Required?",
                            value=props.get("required", False),
                            key=f"req_{field}",
                        )
                        mod_schema[field]["description"] = new_desc
                        mod_schema[field]["type"] = new_type
                        mod_schema[field]["example"] = new_example
                        mod_schema[field]["required"] = new_required
                        if new_type == "string":
                            new_pattern = st.text_input(
                                f"Pattern for {field}",
                                value=props.get("pattern", ""),
                                key=f"pat_{field}",
                            )
                            mod_schema[field]["pattern"] = new_pattern
                    with col2:
                        remove_checked = st.checkbox(
                            "Remove this field",
                            value=(field in fields_to_remove),
                            key=f"remove_{field}",
                        )
                        if remove_checked:
                            fields_to_remove.add(field)
                        else:
                            fields_to_remove.discard(field)
            st.divider()
            st.subheader("Add New Field")
            with st.form("add_field_form"):
                new_field = st.text_input("Field Name", key="add_field_name")
                new_type = st.selectbox(
                    "Type",
                    ["string", "boolean", "integer", "number"],
                    key="add_field_type",
                )
                new_desc = st.text_input("Description", key="add_field_desc")
                new_example = st.text_input("Example", key="add_field_example")
                new_required = st.checkbox(
                    "Required", key="add_field_required")
                new_pattern = st.text_input(
                    "Pattern (for string)", key="add_field_pattern"
                )
                add_clicked = st.form_submit_button("Add Field")
                if add_clicked and new_field:
                    mod_schema[new_field] = {
                        "type": new_type,
                        "description": new_desc,
                        "required": new_required,
                        "example": new_example,
                    }
                    if new_type == "string" and new_pattern:
                        mod_schema[new_field]["pattern"] = new_pattern
                    st.success(f"Field '{new_field}' added.")
            st.divider()
            if st.button("Save Modifications", type="primary"):
                modifications = {}
                orig_schema = schema.get("schema", {})
                for k, v in mod_schema.items():
                    if k not in orig_schema:
                        modifications[k] = v
                    elif v != orig_schema[k]:
                        modifications[k] = v
                for k in fields_to_remove:
                    modifications[k] = None
                if not modifications:
                    st.info("No changes to save.")
                else:
                    try:
                        payload = {
                            "modifications": modifications,
                            "change_description": "Schema modified via UI",
                        }
                        resp = requests.put(
                            f"http://localhost:8005/schemas/{schema_id}/modify",
                            json=payload,
                            timeout=240,
                        )
                        resp.raise_for_status()
                        mod_result = resp.json()
                        st.session_state.last_extraction_result = mod_result
                        st.session_state.schema_modification = None
                        st.session_state.fields_to_remove = set()
                        st.success(
                            "Schema modification submitted. Please approve the new schema."
                        )
                        st.markdown("**Modification Response:**")
                        st.json(mod_result)
                    except Exception as e:
                        st.error(f"Modification failed: {str(e)}")
            if st.button("Approve Schema", type="secondary"):
                try:
                    resp = requests.put(
                        f"http://localhost:8005/schemas/{schema_id}/approve",
                        timeout=240,
                    )
                    resp.raise_for_status()
                    approve_result = resp.json()
                    st.session_state.last_extraction_result = approve_result
                    st.session_state.schema_modification = None
                    st.session_state.fields_to_remove = set()
                    st.success("Schema approved! You can now extract data.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Approval failed: {str(e)}")


def display_member_search():
    st.title("Member Document Search")

    # sample data 
    pan_fields = {
        "pan_number": "TESTPAN1234",
        "name": "TEST TEST",
        "father_s_name": "TEST TEST",
        "date_of_birth": "01/01/1990",
        "registration_number": "TEST-REGD-000000",
        "document_reference_number": "000000000",
        "other_document_reference": None,
        "qr_code_present": True,
        "signature_present": True,
        "photo_present": True,
        "information_unreadable": False,
        "is_document_correct": True
    }
    passport_fields = {
        "issuing_country_name": "TESTLAND",
        "type": "T",
        "code": "TST",
        "passport_number": "T1234567",
        "surname": "TEST",
        "given_names": "TEST",
        "nationality": "TESTIAN",
        "date_of_birth": "01 Jan 1990",
        "place_of_birth": "TEST CITY, TESTLAND",
        "date_of_issue": "01 Jan 2020",
        "date_of_expiration": "01 Jan 2030",
        "endorsements": "TEST",
        "sex": "T",
        "authority": "Test Authority",
        "usa_stamp_present": False,
        "photo_present": True,
        "mrz_line_1": "T<TSTTEST<<TEST<<<<<<<<<<<<<<<<<<<<<<<<<<<",
    }
    aadhar_fields = {
        "aadhaar_logo_present": True,
        "enrolment_number": "0000/00000/00000",
        "date_of_issue": "01/01/2020",
        "name": "TEST TEST",
        "father_or_husband_name": "TEST TEST",
        "address": "TEST ADDRESS, TEST CITY, TEST STATE - 000000",
        "aadhaar_number": "0000 0000 0000",
        "qr_code_present": True,
        "photo_present": True,
        "date_of_birth": "01/01/1990",
        "gender": "TEST",
    }
    doc_sections = [
        ("PAN Card", pan_fields),
        ("Passport", passport_fields),
        ("Aadhar Card", aadhar_fields),
    ]

    if "member_search_queries" not in st.session_state:
        st.session_state.member_search_queries = {}

    for doc_name, fields in doc_sections:
        concatenated_query = ' '.join(
            [str(v) for v in fields.values() if v is not None])
        pdf_display_key = f"member_search_pdf_displayed_{doc_name}"
        pdf_url_key = f"member_search_pdf_url_{doc_name}"
        with st.expander(doc_name, expanded=(doc_name == "Passport")):
            if st.session_state.get(pdf_display_key, False):
                cols = st.columns([2, 3])
                with cols[0]:
                    for field, value in fields.items():
                        col1, col2 = st.columns([2, 4])
                        with col1:
                            st.markdown(f"**{field.replace('_', ' ').title()}**")
                        with col2:
                            if isinstance(value, bool):
                                st.markdown(
                                    ":green[✅ True]" if value else ":red[❌ False]")
                            else:
                                st.code(str(value), language="text")
                with cols[1]:
                    pdf_url = st.session_state.get(pdf_url_key)
                    if pdf_url:
                        st.markdown(
                            f'<iframe src="{pdf_url}" width="100%" height="600" type="application/pdf"></iframe>',
                            unsafe_allow_html=True,
                        )
                        if st.button(f"Hide PDF for {doc_name}", key=f"hide_pdf_{doc_name}"):
                            st.session_state[pdf_display_key] = False
                            st.session_state[pdf_url_key] = None
                            st.rerun()
            else:
                for field, value in fields.items():
                    col1, col2, col3 = st.columns([2, 4, 2])
                    with col1:
                        st.markdown(f"**{field.replace('_', ' ').title()}**")
                    with col2:
                        if isinstance(value, bool):
                            st.markdown(
                                ":green[✅ True]" if value else ":red[❌ False]")
                        else:
                            st.code(str(value), language="text")
                    key = f"{doc_name}_{field}_queried"
                    loading_key = f"{key}_loading"
                    with col3:
                        if st.session_state.member_search_queries.get(loading_key, False):
                            st.button(
                                "View Source", key=f"view_{doc_name}_{field}", disabled=True)
                            st.spinner("Searching...")
                        else:
                            if st.button("View Source", key=f"view_{doc_name}_{field}"):
                                st.session_state.member_search_queries[loading_key] = True
                                try:
                                    resp = requests.post(
                                        "http://localhost:8001/vectorstore/query",
                                        json={"query": concatenated_query, "k": 1},
                                        timeout=240,
                                    )
                                    resp.raise_for_status()
                                    data = resp.json()
                                    results = data.get("results", [])
                                    if results:
                                        source_path = results[0].get("source_path") or results[0].get(
                                            "metadata", {}).get("source_path")
                                        if source_path:
                                            filename = source_path.split("/")[-1]
                                            file_url = f"http://localhost:9000/{filename}"
                                        else:
                                            file_url = None
                                    else:
                                        file_url = None
                                    st.session_state.member_search_queries[loading_key] = False
                                    if file_url:
                                        st.session_state[pdf_display_key] = True
                                        st.session_state[pdf_url_key] = file_url
                                    else:
                                        st.caption("No source found.")
                                except Exception as e:
                                    st.session_state.member_search_queries[loading_key] = False
                                    st.error(f"Query failed: {e}")
                                st.rerun()


def display_workflow():
    st.header("Document Workflow")
    st.write("Upload a PDF, classify, split, extract, and review results.")

    uploaded_file = st.file_uploader(
        "Upload PDF Document", type=["pdf"], key="workflow_upload"
    )

    if uploaded_file:
        if st.button("Start Workflow", type="primary"):
            with st.spinner("Classifying document..."):
                try:
                    files = {"file": (uploaded_file.name,
                                      uploaded_file, uploaded_file.type)}
                    response = requests.post(
                        "http://localhost:8004/classify-pdf", files=files, timeout=240
                    )
                    response.raise_for_status()
                    classify_result = response.json()
                    st.success("Classification completed!")
                except Exception as e:
                    st.error(f"Classification failed: {str(e)}")
                    return

            page_classifications = classify_result.get(
                "page_classifications", [])
            if not page_classifications:
                st.warning("No page classifications found.")
                return

            st.subheader("Classification Results")
            for classification in page_classifications:
                with st.expander(f"Page {classification.get('page', '?')} - {classification.get('document_type', 'Unknown')}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Confidence",
                                  f"{classification.get('confidence', 0):.2%}")
                    with col2:
                        st.metric("Document Type", classification.get(
                            "document_type", "Unknown"))
                    st.write(
                        "**Reasoning:**", classification.get("reasoning", "No reasoning provided."))
            st.divider()

            uploaded_file.seek(0)
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            page_classifications_sorted = sorted(
                page_classifications, key=lambda x: x["page"])
            groups = []
            current_group = []
            last_doc_type = None
            for page_info in page_classifications_sorted:
                doc_type = page_info.get("document_type", "Unknown")
                if last_doc_type is None or doc_type == last_doc_type:
                    current_group.append(page_info)
                else:
                    groups.append((last_doc_type, current_group))
                    current_group = [page_info]
                last_doc_type = doc_type
            if current_group:
                groups.append((last_doc_type, current_group))

            os.makedirs("temp", exist_ok=True)
            grouped_pdfs = []
            for idx, (doc_type, group) in enumerate(groups):
                pdf_writer = PyPDF2.PdfWriter()
                pages = [page_info["page"] for page_info in group]
                for page_num in pages:
                    pdf_writer.add_page(pdf_reader.pages[page_num - 1])
                pdf_buffer = io.BytesIO()
                pdf_writer.write(pdf_buffer)
                pdf_buffer.seek(0)
                safe_doc_type = re.sub(r'[^A-Za-z0-9]+', '_', doc_type)
                group_filename = f"temp/group_{idx+1}_{safe_doc_type}.pdf"
                with open(group_filename, "wb") as f:
                    f.write(pdf_buffer.getvalue())
                grouped_pdfs.append({
                    "doc_type": doc_type,
                    "pages": pages,
                    "pdf_buffer": pdf_buffer,
                    "confidence": group[0].get("confidence", 0),
                    "reasoning": group[0].get("reasoning", ""),
                    "file_path": os.path.abspath(group_filename),
                })

            group_to_file = {
                (tuple(g["pages"]), g["doc_type"]): g["file_path"] for g in grouped_pdfs}

            displayed = set()

            def extract_one(group):
                try:
                    files = {"document": (
                        f"group_{group['doc_type']}_{'_'.join(map(str, group['pages']))}.pdf", group["pdf_buffer"], "application/pdf")}
                    response = requests.post(
                        "http://localhost:8005/extract",
                        files=files,
                        timeout=240,
                    )
                    response.raise_for_status()
                    extract_result = response.json()
                    return {
                        "doc_type": group["doc_type"],
                        "pages": group["pages"],
                        "confidence": group["confidence"],
                        "reasoning": group["reasoning"],
                        "extracted": extract_result.get("data", {}),
                        "raw": extract_result,
                    }
                except Exception as e:
                    return {
                        "doc_type": group["doc_type"],
                        "pages": group["pages"],
                        "confidence": group["confidence"],
                        "reasoning": group["reasoning"],
                        "extracted": {},
                        "raw": {"error": str(e)},
                    }

            st.subheader(
                "Extracted Documents (Results update as soon as available)")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(extract_one, group)
                           for group in grouped_pdfs]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    key = (tuple(res["pages"]), res["doc_type"])
                    if key in displayed:
                        continue
                    displayed.add(key)
                    label = f"{res['doc_type']} (Pages: {', '.join(map(str, res['pages']))}) (Confidence: {res['confidence']:.2%})"
                    with st.expander(label, expanded=False):
                        col1, col2 = st.columns([1, 2], gap="large")
                        with col1:
                            pdf_file_path = group_to_file.get(
                                (tuple(res["pages"]), res["doc_type"]))
                            if pdf_file_path:
                                with open(pdf_file_path, "rb") as f:
                                    base64_pdf = base64.b64encode(
                                        f.read()).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="350" height="500" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                                st.markdown(
                                    f'[Download PDF]({pdf_file_path})', unsafe_allow_html=True)
                        with col2:
                            if res["raw"].get("status") == "pending_review":
                                st.warning(
                                    "Status: pending_review. This document requires review before approval.")
                            st.markdown(f"**Reasoning:** {res['reasoning']}")
                            if res["extracted"]:
                                st.json(res["extracted"])
                            else:
                                st.warning(
                                    "No data extracted or extraction failed.")
                            with st.expander("Show Raw Response"):
                                st.json(res["raw"])


def display_overview():
    st.title("KYC Ops Document Service Hub")

    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Document Classifier", use_container_width=True, type="primary"):
            st.session_state.current_service = "doc-classify"
            st.rerun()

    with col2:
        if st.button("Document Extraction", use_container_width=True, type="primary"):
            st.session_state.current_service = "image-data-extractor"
            st.rerun()

    with col3:
        if st.button("Ops Document Query Tool", use_container_width=True, type="primary"):
            st.session_state.current_service = "analyzer"
            st.rerun()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("PDF Summarizer", use_container_width=True, type="primary"):
            st.session_state.current_service = "summarizer"
            st.rerun()

    with col2:
        if st.button("Member Document Search", use_container_width=True, type="primary"):
            st.session_state.current_service = "member-search"
            st.rerun()

    with col3:
        if st.button("Sentiment Analysis", use_container_width=True, type="primary"):
            st.session_state.current_service = "sentiment"
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Document Workflow", use_container_width=True, type="primary"):
            st.session_state.current_service = "workflow"
            st.rerun()
    with col2:
        st.link_button(
            "CSV Analyzer",
            "http://localhost:8501",
            use_container_width=True,
            type="primary"
        )


def main():
    with st.sidebar:
        st.title("Navigation")

        sidebar_options = ["overview"] + list(SERVICES.keys())
        st.selectbox(
            "Select Service",
            sidebar_options,
            index=0
            if st.session_state.current_service == "overview"
            else sidebar_options.index(st.session_state.current_service)
            if st.session_state.current_service in sidebar_options
            else 0,
            key="sidebar_service"
        )

        if st.session_state.sidebar_service != st.session_state.current_service:
            st.session_state.current_service = st.session_state.sidebar_service
            st.rerun()

        if st.session_state.current_service in SERVICES:
            service_config = SERVICES[st.session_state.current_service]
            st.markdown(f"""
            {service_config["description"]}
            
            **Features:**
            """)
            for feature in service_config["features"]:
                st.write(f"• {feature}")

        st.markdown("---")
        if st.button("Clear All Data", type="secondary"):
            st.rerun()

    if st.session_state.current_service == "overview":
        display_overview()
    elif st.session_state.current_service == "image-data-extractor":
        display_document_extraction()
    elif st.session_state.current_service == "sentiment":
        display_sentiment_analysis()
    elif st.session_state.current_service == "doc-classify":
        display_document_classification()
    elif st.session_state.current_service == "summarizer":
        display_summarizer()
    elif st.session_state.current_service == "analyzer":
        display_analyzer()
    elif st.session_state.current_service == "member-search":
        display_member_search()
    elif st.session_state.current_service == "workflow":
        display_workflow()


if __name__ == "__main__":
    main()
