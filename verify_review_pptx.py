import zipfile
import xml.etree.ElementTree as ET

pptx_path = r"d:\review\Review_1_SafePass.pptx"

with zipfile.ZipFile(pptx_path, "r") as z:
    slides = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
    slides.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
    print(f"Verified {len(slides)} slides in {pptx_path}:")
    for s in slides:
        xml = z.read(s)
        root = ET.fromstring(xml)
        texts = [elem.text for elem in root.iter() if elem.text and elem.text.strip()]
        title = texts[0] if texts else "EMPTY"
        print(f"[{s}] {title} (Total items: {len(texts)})")
