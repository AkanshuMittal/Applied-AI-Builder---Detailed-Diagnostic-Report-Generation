import streamlit as st
import os
from app import run_pipeline

st.title("AI DDR Report Generator")

# Ensure directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

inspection = st.file_uploader("Upload Inspection Report", type=["pdf"])
thermal = st.file_uploader("Upload Thermal Report", type=["pdf"])

if inspection is not None and thermal is not None:

    if st.button("Generate DDR"):

        try:
            with st.spinner("Processing reports..."):
                inspection_path = "uploads/inspection.pdf"
                thermal_path = "uploads/thermal.pdf"

                # Save inspection file
                with open(inspection_path, "wb") as f:
                    f.write(inspection.getvalue())

                # Save thermal file
                with open(thermal_path, "wb") as f:
                    f.write(thermal.getvalue())

                st.success("✓ Files saved successfully")

                # Run pipeline
                run_pipeline(inspection_path, thermal_path)

            st.success("✓ Report Generated Successfully!")
            
            # Download buttons with error checking
            col1, col2 = st.columns(2)
            
            # DOCX download
            if os.path.exists("reports/ddr_report.docx"):
                with col1:
                    with open("reports/ddr_report.docx", "rb") as f:
                        st.download_button(
                            label="📄 Download DOCX",
                            data=f,
                            file_name="ddr_report.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
            else:
                with col1:
                    st.warning("DOCX not available")
            
            # PDF download
            if os.path.exists("reports/ddr_report.pdf"):
                with col2:
                    with open("reports/ddr_report.pdf", "rb") as f:
                        st.download_button(
                            label="📕 Download PDF",
                            data=f,
                            file_name="ddr_report.pdf",
                            mime="application/pdf"
                        )
            else:
                with col2:
                    st.info("PDF conversion in progress or failed. Use DOCX version.")
                    
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
            st.info("Please check the console for detailed error messages.")