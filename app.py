import os
from extractors.text_extractor import extract_text
from extractors.image_extractor import extract_images

from agents.inspection_parser import parse_inspection
from agents.thermal_parser import parse_thermal
from agents.merge_agent import merge_data
from agents.conflict_detector import detect_conflicts
from agents.missing_detector import detect_missing
from agents.ddr_generator import generate_ddr
from agents.image_mapper import map_images

from report.report_builder import build_report
from workflow.graph_builder import build_graph


def run_pipeline(inspection_pdf, thermal_pdf):
    """Main pipeline with langgraph workflow orchestration"""
    try:
        print("="*70)
        print("Starting DDR Report Generation Pipeline")
        print("="*70)
        
        print("\n[STAGE 1] Loading PDFs...")
        print(f"  Inspection PDF: {inspection_pdf}")
        print(f"  Thermal PDF: {thermal_pdf}")
        
        if not os.path.exists(inspection_pdf):
            raise FileNotFoundError(f"Inspection PDF not found: {inspection_pdf}")
        if not os.path.exists(thermal_pdf):
            raise FileNotFoundError(f"Thermal PDF not found: {thermal_pdf}")

        print("\n[STAGE 2] Extracting text...")
        inspection_text = extract_text(inspection_pdf)
        thermal_text = extract_text(thermal_pdf)
        print(f"  Inspection text length: {len(inspection_text)} chars")
        print(f"  Thermal text length: {len(thermal_text)} chars")

        print("\n[STAGE 3] Extracting images...")
        images1 = extract_images(inspection_pdf, pdf_type="inspection")
        print(f"  Images from inspection PDF: {len(images1)}")
        images2 = extract_images(thermal_pdf, pdf_type="thermal")
        print(f"  Images from thermal PDF: {len(images2)}")

        images = images1 + images2
        print(f"  Total images extracted: {len(images)}")
        
        if len(images) == 0:
            print("  WARNING: No images found in PDFs")

        print("\n[STAGE 4] Mapping images to areas...")
        if images:
            mapped_images = map_images(images)
            print(f"  Images mapped: {len(mapped_images)}")
        else:
            print("  Skipping image mapping (no images found)")
            mapped_images = []

        print("\n[STAGE 5] Building Execution Workflow...")
        # Initialize langgraph workflow
        workflow = build_graph()
        print(f"  Workflow compiled and ready")

        # Initial state with extracted data
        initial_state = {
            "inspection_text": inspection_text,
            "thermal_text": thermal_text,
            "inspection_data": None,
            "thermal_data": None,
            "merged_data": None,
            "conflicts": None,
            "missing": None,
            "report": None,
            "images": mapped_images
        }

        print("\n[STAGE 6] Executing Workflow Nodes...")
        print(f"  Entry point: parse_inspection")

        # Execute workflow
        result = workflow.invoke(initial_state)

        print(f"  Exit point: generate (report generation complete)")

        # Extract results
        inspection_data = result.get("inspection_data", "")
        thermal_data = result.get("thermal_data", "")
        merged = result.get("merged_data", "")
        conflicts = result.get("conflicts", [])
        missing = result.get("missing", [])
        report = result.get("report", "")

        print(f"\n[STAGE 7] Building Report Document...")
        build_report(report, mapped_images)
        print(f"  Report document built")

        print("\n" + "="*70)
        print("✓ Report generation complete!")
        print("="*70)
        
    except FileNotFoundError as e:
        print(f"\n✗ FILE ERROR: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR in pipeline: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise