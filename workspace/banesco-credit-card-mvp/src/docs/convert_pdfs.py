import os
import pypdf

def convert_pdf_to_md(pdf_path, md_path):
    print(f"Convertiendo: {os.path.basename(pdf_path)} -> {os.path.basename(md_path)}")
    
    reader = pypdf.PdfReader(pdf_path)
    markdown_content = []
    
    # Add metadata header
    filename = os.path.basename(pdf_path)
    title = os.path.splitext(filename)[0]
    markdown_content.append(f"# {title}\n")
    markdown_content.append(f"**Archivo Original:** `{filename}`")
    markdown_content.append(f"**Total Páginas:** {len(reader.pages)}\n")
    markdown_content.append("---\n")
    
    for page_num, page in enumerate(reader.pages, 1):
        markdown_content.append(f"## Página {page_num}\n")
        text = page.extract_text()
        
        # Add basic formatting for line breaks to make it look clean for LLM processing
        markdown_content.append(text)
        markdown_content.append("\n---\n")
        
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(markdown_content))

def main():
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Buscando archivos PDF en: {docs_dir}")
    
    pdf_files = [f for f in os.listdir(docs_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No se encontraron archivos PDF.")
        return
        
    for pdf_file in pdf_files:
        pdf_path = os.path.join(docs_dir, pdf_file)
        md_filename = os.path.splitext(pdf_file)[0] + ".md"
        md_path = os.path.join(docs_dir, md_filename)
        
        try:
            convert_pdf_to_md(pdf_path, md_path)
            print(f"Éxito al convertir {pdf_file}")
        except Exception as e:
            print(f"Error al convertir {pdf_file}: {e}")

if __name__ == "__main__":
    main()
